import logging
from dataclasses import asdict
from uuid import UUID

from fastapi import UploadFile
from faststream.rabbit import RabbitBroker
from src.application.constants import (
    REQUIRED_PROFILE_FIELDS,
    SELLER_ACCOUNT_MAX_FILE_SIZE,
    SELLER_ACCOUNTS_FOLDER,
)
from src.application.dtos.additionals import SendNotificationDTO
from src.application.dtos.seller_accounts import (
    AdminSellerAccountDetailDTO,
    AdminSellerAccountListDTO,
    AdminSellerAccountListQueryDTO,
    AdminSellerAccountSetStatusDTO,
    AdminVerificationSetStatusDTO,
    CreateSellerAccountDTO,
    UpdateSellerAccountDTO,
    VerifySellerAccountDTO,
)
from src.application.enums import (
    STATUS_TO_ACTION,
    STATUS_TO_TITLE,
    VERIFICATION_STATUS_TO_ACTION,
    VERIFICATION_STATUS_TO_TITLE,
    NotificationAction,
    NotificationTitle,
    NotificationType,
    SellerStatus,
    VerificationStatus,
)
from src.application.events import NotificationRoutingKeys
from src.application.exceptions import (
    ApplicationError,
    ProfileNotCompleted,
    SellerAccountAlreadyExists,
    SellerAccountInvalidStatus,
    SellerAccountNotFound,
)
from src.application.interfaces import (
    ProfileRepository,
    SellerAccountRepository,
    UnitOfWork,
    UUIDGenerator,
)
from src.application.services import ImageService, MediaURLBuilder
from src.infrastructure.models import SellerAccount
from src.infrastructure.resources.exchanges import NOTIFICATION_EXCHANGE

logger = logging.getLogger(__name__)


class UpdateSellerAccountUseCase:
    def __init__(
        self,
        repo: SellerAccountRepository,
        uow: UnitOfWork,
        image_service: ImageService,
        broker: RabbitBroker,
    ) -> None:
        self._repo = repo
        self._uow = uow
        self._image_service = image_service
        self._broker = broker

    async def __call__(
        self,
        dto: UpdateSellerAccountDTO,
        user_id: UUID,
    ) -> None:
        seller_account = await self._repo.get_by_user_id(user_id)
        if not seller_account:
            raise SellerAccountNotFound()
        if seller_account.status not in {
            SellerStatus.ON_CORRECTION,
            SellerStatus.REJECTED,
        }:
            raise SellerAccountInvalidStatus()

        data = {k: v for k, v in asdict(dto).items() if v is not None}

        for field, value in data.items():
            setattr(seller_account, field, value)

        action = NotificationAction.SELLER_ACCOUNT_APPROVED
        title = NotificationTitle.SELLER_ACCOUNT_APPROVED
        status = SellerStatus.APPROVED
        if seller_account.status == SellerStatus.REJECTED:
            status = SellerStatus.PENDING
            action = NotificationAction.SELLER_ACCOUNT_PENDING
            title = NotificationTitle.SELLER_ACCOUNT_PENDING

        seller_account.status = status
        await self._uow.commit()

        event = SendNotificationDTO(
            title=title,
            body=None,
            user_id=str(user_id),
            type=NotificationType.NOTIFICATION,
            action=action,
        )
        logger.info("Seller account updated, publishing event")
        await self._broker.publish(
            asdict(event),
            exchange=NOTIFICATION_EXCHANGE,
            routing_key=NotificationRoutingKeys.PUSH,
        )


class CreateSellerAccountUseCase:
    def __init__(
        self,
        repo: SellerAccountRepository,
        profile_repo: ProfileRepository,
        uow: UnitOfWork,
        uuid_generator: UUIDGenerator,
        image_service: ImageService,
        broker: RabbitBroker,
    ):
        self._repo = repo
        self._profile_repo = profile_repo
        self._uow = uow
        self._uuid_generator = uuid_generator
        self._image_service = image_service
        self._broker = broker

    async def __call__(
        self,
        user_id: UUID,
        dto: CreateSellerAccountDTO,
    ) -> None:
        exists = await self._repo.exists_by_user_id(user_id)
        if exists:
            raise SellerAccountAlreadyExists()

        profile = await self._profile_repo.get_by_user_id(user_id)

        if not all(getattr(profile, f) for f in REQUIRED_PROFILE_FIELDS):
            raise ProfileNotCompleted()

        uuid = self._uuid_generator()

        seller_account = SellerAccount(
            id=uuid,
            user_id=user_id,
            status=SellerStatus.APPROVED,
            company_phone=dto.company_phone,
            company_name=dto.company_name,
            company_address=dto.company_address,
        )

        await self._repo.save(seller_account)
        await self._uow.commit()
        event = SendNotificationDTO(
            title=NotificationTitle.SELLER_ACCOUNT_APPROVED,
            body=None,
            user_id=str(user_id),
            type=NotificationType.NOTIFICATION,
            action=NotificationAction.SELLER_ACCOUNT_APPROVED,
        )
        logger.info("Seller account created, publishing event")
        await self._broker.publish(
            asdict(event),
            exchange=NOTIFICATION_EXCHANGE,
            routing_key=NotificationRoutingKeys.PUSH,
        )


class VerifySellerAccountUseCase:
    def __init__(
        self,
        repo: SellerAccountRepository,
        uow: UnitOfWork,
        image_service: ImageService,
        broker: RabbitBroker,
    ):
        self._repo = repo
        self._uow = uow
        self._image_service = image_service
        self._broker = broker

    async def __call__(
        self,
        user_id: UUID,
        passport_front: UploadFile | None,
        passport_back: UploadFile | None,
        additional_document: UploadFile | None,
        dto: VerifySellerAccountDTO,
    ) -> None:
        seller_account = await self._repo.get_by_user_id(user_id)
        if not seller_account:
            raise SellerAccountNotFound()

        images = {
            "passport_front": passport_front,
            "passport_back": passport_back,
            "additional_document": additional_document,
        }
        old_images = {
            "passport_front": seller_account.passport_front,
            "passport_back": seller_account.passport_back,
            "additional_document": seller_account.additional_document,
        }

        new_files = {}
        try:
            for field, file in images.items():
                if not file:
                    continue

                new_path = await self._image_service.save_image(
                    file,
                    max_size=SELLER_ACCOUNT_MAX_FILE_SIZE,
                    folder=SELLER_ACCOUNTS_FOLDER,
                )
                new_files[field] = new_path

            for field, path in new_files.items():
                setattr(seller_account, field, path)

            data = {k: v for k, v in asdict(dto).items() if v is not None}

            for field, value in data.items():
                setattr(seller_account, field, value)

            seller_account.verification_status = VerificationStatus.PENDING

            await self._uow.commit()

        except Exception:
            await self._uow.rollback()

            for path in new_files.values():
                try:
                    await self._image_service.delete(path)
                except Exception:
                    logger.exception("Failed to cleanup uploaded file")

            raise ApplicationError()

        for field, old_path in old_images.items():
            if field not in new_files or not old_path:
                continue

            try:
                await self._image_service.delete(old_path)
            except Exception:
                logger.exception("Failed to delete old file")

        event = SendNotificationDTO(
            title=NotificationTitle.VERIFICATION_PENDING,
            body=None,
            user_id=str(user_id),
            type=NotificationType.NOTIFICATION,
            action=NotificationAction.VERIFICATION_PENDING,
        )
        logger.info("Seller account verifying, publishing event")
        await self._broker.publish(
            asdict(event),
            exchange=NOTIFICATION_EXCHANGE,
            routing_key=NotificationRoutingKeys.PUSH,
        )


class AdminSellerAccountListUseCase:
    def __init__(self, repo: SellerAccountRepository):
        self._repo = repo

    async def __call__(
        self, query: AdminSellerAccountListQueryDTO
    ) -> list[AdminSellerAccountListDTO]:
        accounts = await self._repo.list(query)
        return [
            AdminSellerAccountListDTO(
                id=UUID(str(a.id)),
                full_name=a.profile.full_name,
                user_id=UUID(str(a.user_id)),
                email=a.profile.email,
                status=SellerStatus(a.status),
                verification_status=VerificationStatus(a.verification_status)
                if a.verification_status
                else None,
                created_at=a.created_at,
                company_phone=a.company_phone,
                company_name=a.company_name,
                company_address=a.company_address,
            )
            for a in accounts
        ]


class AdminSellerAccountDetailUseCase:
    def __init__(
        self,
        repo: SellerAccountRepository,
        media_url_builder: MediaURLBuilder,
    ) -> None:
        self._repo = repo
        self._media_url_builder = media_url_builder

    async def __call__(
        self, seller_account_id: UUID
    ) -> AdminSellerAccountDetailDTO | None:
        account = await self._repo.get_by_id(account_id=seller_account_id)
        if not account:
            raise SellerAccountNotFound()

        user_id = UUID(str(account.user_id))
        account_id = UUID(str(account.id))
        return AdminSellerAccountDetailDTO(
            id=account_id,
            full_name=account.profile.full_name,
            user_id=user_id,
            email=account.profile.email,
            status=SellerStatus(account.status),
            verification_status=VerificationStatus(account.verification_status)
            if account.verification_status
            else None,
            created_at=account.created_at,
            company_address=account.company_address,
            company_name=account.company_name,
            company_phone=account.company_phone,
            passport_front=self._media_url_builder.build(account.passport_front)
            if account.passport_front
            else None,
            passport_back=self._media_url_builder.build(account.passport_back)
            if account.passport_back
            else None,
            additional_document=self._media_url_builder.build(
                account.additional_document
            )
            if account.additional_document
            else None,
            tin=account.tin,
            legal_address=account.legal_address,
        )


class AdminSellerAccountSetStatusUseCase:
    def __init__(
        self, repo: SellerAccountRepository, uow: UnitOfWork, broker: RabbitBroker
    ) -> None:
        self._repo = repo
        self._uow = uow
        self._broker = broker

    async def __call__(self, dto: AdminSellerAccountSetStatusDTO) -> None:
        account = await self._repo.get_by_id(dto.id)
        if not account:
            raise SellerAccountNotFound()

        account.status = dto.status.value
        await self._uow.commit()

        event = SendNotificationDTO(
            title=STATUS_TO_TITLE[dto.status],
            body=dto.text,
            user_id=str(account.user_id),
            type=NotificationType.NOTIFICATION,
            action=STATUS_TO_ACTION[dto.status],
        )
        logger.info(f"Seller account changed to: {event.title}, publishing event")
        await self._broker.publish(
            asdict(event),
            exchange=NOTIFICATION_EXCHANGE,
            routing_key=NotificationRoutingKeys.PUSH,
        )


class AdminVerificationSetStatusUseCase:
    def __init__(
        self, repo: SellerAccountRepository, uow: UnitOfWork, broker: RabbitBroker
    ) -> None:
        self._repo = repo
        self._uow = uow
        self._broker = broker

    async def __call__(self, dto: AdminVerificationSetStatusDTO) -> None:
        account = await self._repo.get_by_id(dto.id)
        if not account:
            raise SellerAccountNotFound()

        account.verification_status = dto.status.value
        await self._uow.commit()

        event = SendNotificationDTO(
            title=VERIFICATION_STATUS_TO_TITLE[dto.status],
            body=dto.text,
            user_id=str(account.user_id),
            type=NotificationType.NOTIFICATION,
            action=VERIFICATION_STATUS_TO_ACTION[dto.status],
        )
        logger.info(
            f"Seller account verification changed to: {event.title}, publishing event"
        )
        await self._broker.publish(
            asdict(event),
            exchange=NOTIFICATION_EXCHANGE,
            routing_key=NotificationRoutingKeys.PUSH,
        )
