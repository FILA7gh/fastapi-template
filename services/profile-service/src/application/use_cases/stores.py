import logging
from dataclasses import asdict
from typing import List
from uuid import UUID

from fastapi import UploadFile
from faststream.rabbit import RabbitBroker
from src.application.constants import STORE_MAX_FILE_SIZE, STORES_FOLDER
from src.application.dtos.stores import (
    AdminStoreDetailDTO,
    AdminStoresListDTO,
    CreateStoreDTO,
    MyStoreListDTO,
    PaginatedAdminStoresListDTO,
    PaginatedStoresListDTO,
    StoreDetailDTO,
    StoreQueryDTO,
    StoresListDTO,
    UpdateStoreDTO,
)
from src.application.enums import SocialMediaType
from src.application.events import StoreDeletedEvent, StoreRoutingKeys
from src.application.exceptions import (
    ApplicationError,
    ProfileNotFound,
    StoreNotFound,
)
from src.application.interfaces import (
    GeoLocator,
    ProfileRepository,
    StoreRepository,
    UnitOfWork,
)
from src.application.services import ImageService, MediaURLBuilder
from src.application.utils import SocialMediaDTO, social_url_generator
from src.infrastructure.models import Store
from src.infrastructure.resources.exchanges import STORE_EXCHANGE

logger = logging.getLogger(__name__)


class CreateStoreUseCase:
    def __init__(
        self,
        store_repo: StoreRepository,
        uow: UnitOfWork,
        geo_locator: GeoLocator,
        image_service: ImageService,
    ) -> None:
        self._store_repo = store_repo
        self._geo_locator = geo_locator
        self._uow = uow
        self._image_service = image_service

    async def __call__(
        self, user_id: UUID, dto: CreateStoreDTO, image: UploadFile | None
    ) -> None:
        image_path = None
        try:
            if image is not None:
                image_path = await self._image_service.save_image(
                    image,
                    max_size=STORE_MAX_FILE_SIZE,
                    folder=STORES_FOLDER,
                )

            store = Store(
                name=dto.name,
                address=dto.address,
                phone=dto.phone,
                user_id=user_id,
                longitude=dto.longitude,
                latitude=dto.latitude,
                image=image_path,
            )
            region = await self._geo_locator.get_region(
                lat=dto.latitude, lng=dto.longitude
            )
            if region:
                store.region = region

            if dto.social_medias:
                store.social_medias = social_url_generator(dto.social_medias)

            await self._store_repo.save(store)
            await self._uow.commit()

        except Exception:
            await self._uow.rollback()

            if image_path:
                try:
                    await self._image_service.delete(image_path)
                except Exception:
                    logger.exception("Failed to cleanup image")

            raise ApplicationError()


class UpdateStoreUseCase:
    def __init__(
        self, store_repo: StoreRepository, uow: UnitOfWork, geo_locator: GeoLocator
    ) -> None:
        self._store_repo = store_repo
        self._uow = uow
        self._geo_locator = geo_locator

    async def __call__(self, store_id: int, dto: UpdateStoreDTO) -> None:
        store = await self._store_repo.get_by_id(store_id)
        if not store:
            raise ProfileNotFound()

        data = {k: v for k, v in asdict(dto).items() if v is not None}

        for field, value in data.items():
            setattr(store, field, value)
        lat = dto.latitude if dto.latitude else store.latitude
        lng = dto.longitude if dto.longitude else store.longitude
        if lat and lng:
            region = await self._geo_locator.get_region(lat=float(lat), lng=float(lng))
            if region:
                store.region = region
        if dto.social_medias:
            store.social_medias = social_url_generator(dto.social_medias)
        await self._uow.commit()


class UpdateStoreImageUseCase:
    def __init__(
        self, store_repo: StoreRepository, uow: UnitOfWork, image_service: ImageService
    ) -> None:
        self._store_repo = store_repo
        self._uow = uow
        self._image_service = image_service

    async def __call__(self, store_id: int, image: UploadFile | None) -> None:
        store = await self._store_repo.get_by_id(store_id)
        if not store:
            raise ProfileNotFound()
        image_path = None
        old_image = store.image

        if image is None:
            try:
                store.image = None
                await self._uow.commit()
            except Exception:
                await self._uow.rollback()
                raise ApplicationError()

            try:
                await self._image_service.delete(old_image)
            except Exception:
                logger.exception("Failed to cleanup image")

            return

        try:
            image_path = await self._image_service.save_image(
                image=image, max_size=STORE_MAX_FILE_SIZE, folder=STORES_FOLDER
            )
            store.image = image_path
            await self._uow.commit()

        except Exception:
            await self._uow.rollback()
            try:
                await self._image_service.delete(image_path)
            except Exception:
                logger.exception("Failed to cleanup image")
            raise ApplicationError()

        if old_image:
            try:
                await self._image_service.delete(old_image)
            except Exception:
                logger.exception("Failed to cleanup old image")


class GetStoreUseCase:
    def __init__(
        self,
        store_repo: StoreRepository,
        media_url_builder: MediaURLBuilder,
    ) -> None:
        self._store_repo = store_repo
        self._media_url_builder = media_url_builder

    async def __call__(self, store_id: int) -> StoreDetailDTO:
        store = await self._store_repo.get_by_id(store_id)
        if not store:
            raise StoreNotFound()
        return StoreDetailDTO(
            id=store.id,
            name=store.name,
            image=self._media_url_builder.build(store.image) if store.image else None,
            address=store.address,
            phone=store.phone,
            region=store.region,
            longitude=float(store.longitude),
            latitude=float(store.latitude),
            social_medias=[
                SocialMediaDTO(
                    type=SocialMediaType(sm.get("type")),
                    url=sm.get("url"),
                    detail=sm.get("detail"),
                )
                for sm in store.social_medias
            ]
            if store.social_medias
            else None,
        )


class DeleteStoreUseCase:
    def __init__(
        self,
        store_repo: StoreRepository,
        uow: UnitOfWork,
        broker: RabbitBroker,
        image_service: ImageService,
    ) -> None:
        self._store_repo = store_repo
        self._broker = broker
        self._uow = uow
        self._image_service = image_service

    async def __call__(self, store_id: int) -> None:
        store = await self._store_repo.get_by_id(store_id)
        if not store:
            raise StoreNotFound()

        try:
            await self._store_repo.delete(store_id)
            await self._uow.commit()

        except Exception:
            await self._uow.rollback()
            raise ApplicationError()

        try:
            await self._image_service.delete(store.image)
        except Exception:
            logger.exception("Failed to cleanup image")

        logger.info("Store deleted, publishing event")
        await self._broker.publish(
            StoreDeletedEvent(store_id=store.id),
            exchange=STORE_EXCHANGE,
            routing_key=StoreRoutingKeys.DELETED,
        )


class ListMyStoresUseCase:
    def __init__(
        self, store_repo: StoreRepository, media_url_builder: MediaURLBuilder
    ) -> None:
        self._store_repo = store_repo
        self._media_url_builder = media_url_builder

    async def __call__(self, user_id: UUID) -> List[MyStoreListDTO]:
        stores = await self._store_repo.get_by_user_id(user_id)
        return [
            MyStoreListDTO(
                id=s.id,
                name=s.name,
                image=self._media_url_builder.build(s.image) if s.image else None,
                address=s.address,
                phone=s.phone,
                region=s.region,
                user_id=UUID(str(s.user_id)),
                longitude=float(s.longitude),
                latitude=float(s.latitude),
                social_medias=[
                    SocialMediaDTO(
                        type=SocialMediaType(sm.get("type")),
                        url=sm.get("url"),
                        detail=sm.get("detail"),
                    )
                    for sm in s.social_medias
                ]
                if s.social_medias
                else None,
            )
            for s in stores
        ]


class ListStoresUseCase:
    def __init__(
        self, store_repo: StoreRepository, media_url_builder: MediaURLBuilder
    ) -> None:
        self._store_repo = store_repo
        self._media_url_builder = media_url_builder

    async def __call__(self, query: StoreQueryDTO) -> PaginatedStoresListDTO:
        row, count = await self._store_repo.list(query)
        stores = [
            StoresListDTO(
                id=store.id,
                name=store.name,
                image=self._media_url_builder.build(store.image)
                if store.image
                else None,
                address=store.address,
                products_count=count,
            )
            for store, count in row
        ]

        return PaginatedStoresListDTO(items=stores, count=count)


# ADMIN


class AdminListStoresUseCase:
    def __init__(
        self,
        store_repo: StoreRepository,
    ) -> None:
        self._store_repo = store_repo

    async def __call__(self, query: StoreQueryDTO) -> PaginatedAdminStoresListDTO:
        row, count = await self._store_repo.list(query)
        stores = [
            AdminStoresListDTO(
                id=store.id,
                name=store.name,
                products_count=count,
            )
            for store, count in row
        ]

        return PaginatedAdminStoresListDTO(items=stores, count=count)


class AdminStoreUseCase:
    def __init__(
        self,
        store_repo: StoreRepository,
        profile_repo: ProfileRepository,
        media_url_builder: MediaURLBuilder,
    ) -> None:
        self._store_repo = store_repo
        self._profile_repo = profile_repo
        self._media_url_builder = media_url_builder

    async def __call__(self, store_id: int) -> AdminStoreDetailDTO:
        store = await self._store_repo.get_by_id(store_id)
        if store is None:
            raise StoreNotFound()

        profile = await self._profile_repo.get_by_user_id(store.user_id)
        if profile is None:
            raise ProfileNotFound()

        return AdminStoreDetailDTO(
            id=store.id,
            owner_full_name=profile.full_name,
            name=store.name,
            phone=store.phone,
            address=store.address,
            image=self._media_url_builder.build(store.image) if store.image else None,
            social_medias=[
                SocialMediaDTO(
                    type=SocialMediaType(sm.get("type")),
                    url=sm.get("url"),
                    detail=sm.get("detail"),
                )
                for sm in store.social_medias
            ]
            if store.social_medias
            else None,
        )
