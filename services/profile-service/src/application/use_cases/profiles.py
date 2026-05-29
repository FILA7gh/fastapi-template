from dataclasses import asdict
from uuid import UUID

from fastapi import UploadFile
from faststream.rabbit import RabbitBroker
from src.application.constants import (
    PHONE,
    PROFILE_MAX_FILE_SIZE,
    PROFILES_FOLDER,
)
from src.application.dtos.profiles import (
    AdminListProfileDTO,
    CreateProfileDTO,
    PaginatedAdminListProfileDTO,
    ProfileDTO,
    ProfileListQueryDTO,
    UpdateProfileDTO,
)
from src.application.enums import (
    SellerStatus,
    SocialMediaType,
    UserLanguage,
    VerificationStatus,
)
from src.application.exceptions import (
    EmailCannotChange,
    PhoneCannotChange,
    ProfileNotFound,
)
from src.application.interfaces import (
    GeoLocator,
    ProfileRepository,
    SellerAccountRepository,
    StoreRepository,
    UnitOfWork,
    UUIDGenerator,
)
from src.application.services import ImageService, MediaURLBuilder
from src.application.utils import SocialMediaDTO, social_url_generator
from src.infrastructure.models import Profile


class GetProfileUseCase:
    def __init__(
        self,
        user_repo: ProfileRepository,
        seller_account_repo: SellerAccountRepository,
        media_url_builder: MediaURLBuilder,
    ) -> None:
        self._user_repo = user_repo
        self._seller_account_repo = seller_account_repo
        self._media_url_builder = media_url_builder

    async def __call__(self, current_user_id: UUID) -> ProfileDTO:
        profile = await self._user_repo.get_by_user_id(current_user_id)
        if not profile:
            raise ProfileNotFound()

        seller_account = await self._seller_account_repo.get_by_user_id(current_user_id)

        return ProfileDTO(
            id=UUID(str(profile.id)),
            user_id=UUID(str(profile.user_id)),
            full_name=profile.full_name,
            email=profile.email,
            created_at=profile.created_at,
            phone=profile.phone,
            avatar=self._media_url_builder.build(profile.avatar)
            if profile.avatar
            else None,
            registration_type=profile.registration_type,
            region=profile.region,
            language=UserLanguage(profile.language),
            notifications_enabled=profile.notifications_enabled,
            seller_status=SellerStatus(seller_account.status)
            if seller_account and seller_account.status
            else None,
            verification_status=VerificationStatus(seller_account.verification_status)
            if seller_account and seller_account.verification_status
            else None,
            can_edit_phone=bool(profile.registration_type != PHONE),
            can_edit_email=bool(profile.registration_type == PHONE),
            social_medias=[
                SocialMediaDTO(
                    type=SocialMediaType(sm.get("type")),
                    url=sm.get("url"),
                    detail=sm.get("detail"),
                )
                for sm in profile.social_medias
            ]
            if profile.social_medias
            else None,
            longitude=float(profile.longitude) if profile.longitude else None,
            latitude=float(profile.latitude) if profile.latitude else None,
        )


class UpdateProfileUseCase:
    def __init__(
        self, user_repo: ProfileRepository, uow: UnitOfWork, geo_locator: GeoLocator
    ) -> None:
        self._user_repo = user_repo
        self._uow = uow
        self._geo_locator = geo_locator

    async def __call__(self, user_id: UUID, dto: UpdateProfileDTO) -> None:
        profile = await self._user_repo.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFound()
        if dto.email is not None and profile.registration_type != PHONE:
            raise EmailCannotChange()
        if dto.phone is not None and profile.registration_type == PHONE:
            raise PhoneCannotChange()

        data = {k: v for k, v in asdict(dto).items() if v is not None}
        for field, value in data.items():
            setattr(profile, field, value)

        lat, lng = dto.latitude, dto.longitude
        if lat and lng:
            region = await self._geo_locator.get_region(lat=float(lat), lng=float(lng))
            if region:
                profile.region = region

        if dto.social_medias:
            profile.social_medias = social_url_generator(dto.social_medias)

        await self._uow.commit()


class UpdateProfileAvatarUseCase:
    def __init__(
        self,
        profile_repo: ProfileRepository,
        uow: UnitOfWork,
        image_service: ImageService,
    ) -> None:
        self._profile_repo = profile_repo
        self._uow = uow
        self._image_service = image_service

    async def __call__(self, user_id: UUID, avatar: UploadFile) -> None:
        profile = await self._profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFound()

        old_avatar = profile.avatar
        new_avatar = await self._image_service.save_image(
            avatar, max_size=PROFILE_MAX_FILE_SIZE, folder=PROFILES_FOLDER
        )
        profile.avatar = new_avatar

        await self._uow.commit()
        await self._image_service.delete(old_avatar)


class DeleteProfileAvatarUseCase:
    def __init__(
        self,
        profile_repo: ProfileRepository,
        uow: UnitOfWork,
        image_service: ImageService,
    ) -> None:
        self._profile_repo = profile_repo
        self._uow = uow
        self._image_service = image_service

    async def __call__(self, user_id: UUID) -> None:
        profile = await self._profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFound()

        await self._image_service.delete(profile.avatar)
        profile.avatar = None

        await self._uow.commit()


class ListProfileUseCase:
    def __init__(
        self,
        profile_repo: ProfileRepository,
        media_url_builder: MediaURLBuilder,
    ) -> None:
        self._profile_repo = profile_repo
        self._media_url_builder = media_url_builder

    async def __call__(
        self, query: ProfileListQueryDTO
    ) -> PaginatedAdminListProfileDTO:
        profiles, count = await self._profile_repo.list(query)
        return PaginatedAdminListProfileDTO(
            items=[
                AdminListProfileDTO(
                    id=p.id,
                    user_id=p.user_id,
                    full_name=p.full_name,
                    email=p.email,
                    avatar=self._media_url_builder.build(p.avatar)
                    if p.avatar
                    else None,
                    role=p.role,
                    created_at=p.created_at,
                )
                for p in profiles
            ],
            count=count,
        )


# EVENTS


class CreateProfileUseCase:
    def __init__(
        self,
        repo: ProfileRepository,
        uow: UnitOfWork,
        uuid_generator: UUIDGenerator,
    ) -> None:
        self._uuid_generator = uuid_generator
        self._repo = repo
        self._uow = uow

    async def __call__(self, dto: CreateProfileDTO) -> UUID | None:
        existing = await self._repo.get_by_user_id(dto.user_id)
        if existing:
            return existing.id

        uuid = self._uuid_generator()
        profile = Profile(
            id=uuid,
            user_id=dto.user_id,
            avatar=None,
            full_name=dto.full_name,
            phone=dto.phone,
            email=dto.email,
            registration_type=dto.registration_type,
            language=UserLanguage.RU.value,
            notifications_enabled=False,
        )
        try:
            await self._repo.save(profile)
            await self._uow.commit()
            return uuid
        except Exception:
            await self._uow.rollback()

            existing = await self._repo.get_by_user_id(dto.user_id)
            if existing:
                return existing.id

            raise


class DeleteAccountUseCase:
    """
    Сценарий для удаления всех данных пользовтеля
    """

    def __init__(
        self,
        profile_repo: ProfileRepository,
        seller_account_repo: SellerAccountRepository,
        store_repo: StoreRepository,
        uow: UnitOfWork,
        image_service: ImageService,
        broker: RabbitBroker,
    ) -> None:
        self._profile_repo = profile_repo
        self._uow = uow
        self._seller_account_repo = seller_account_repo
        self._store_repo = store_repo
        self._image_service = image_service
        self._broker = broker

    async def __call__(self, user_id: UUID) -> None:
        profile = await self._profile_repo.get_by_user_id(user_id)
        if profile:
            await self._image_service.delete(profile.avatar)
            await self._profile_repo.delete(user_id)

        seller_account = await self._seller_account_repo.get_by_id(user_id)
        if seller_account:
            await self._image_service.delete(seller_account.passport_back)
            await self._image_service.delete(seller_account.passport_front)
            await self._seller_account_repo.delete(user_id)

        await self._store_repo.delete_by_user_id(user_id)
        await self._uow.commit()
