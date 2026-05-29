from typing import Protocol, Sequence
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import Row
from src.application.dtos.additionals import (
    JWTPayloadDTO,
)
from src.application.dtos.profiles import ProfileListQueryDTO
from src.application.dtos.seller_accounts import (
    AdminSellerAccountListQueryDTO,
)
from src.application.dtos.stores import StoreQueryDTO
from src.infrastructure.models import (
    Profile,
    SellerAccount,
    Store,
)


class UnitOfWork(Protocol):
    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


class UUIDGenerator(Protocol):
    def __call__(self) -> UUID: ...


class JWTVerifier(Protocol):
    def verify_token(self, token: str) -> JWTPayloadDTO: ...


class FileStorage(Protocol):
    async def save(self, file: UploadFile, filename: str, folder: str) -> str: ...

    async def delete(self, key: str) -> None: ...


class GeoLocator(Protocol):
    async def get_region(self, lat: float, lng: float) -> str | None: ...


class ProfileRepository(Protocol):
    async def save(self, profile: Profile) -> None: ...

    async def get_by_id(self, user_id: UUID) -> Profile | None: ...

    async def get_by_user_id(self, user_id: UUID) -> Profile | None: ...

    async def delete(self, user_id: UUID) -> None: ...

    async def list(
        self, query: ProfileListQueryDTO
    ) -> tuple[Sequence[Profile], int]: ...


class SellerAccountRepository(Protocol):
    async def save(self, seller_account: SellerAccount) -> None: ...

    async def exists_by_user_id(self, user_id: UUID) -> bool: ...

    async def list(
        self, dto: AdminSellerAccountListQueryDTO
    ) -> Sequence[SellerAccount]: ...

    async def get_by_id(self, account_id: UUID) -> SellerAccount | None: ...

    async def get_by_user_id(self, user_id: UUID) -> SellerAccount | None: ...

    async def delete(self, user_id: UUID) -> None: ...


class StoreRepository(Protocol):
    async def save(self, store: Store) -> None: ...

    async def get_by_id(self, store_id: int) -> Store | None: ...

    async def get_by_user_id(self, user_id: UUID) -> Sequence[Store]: ...

    async def delete(self, store_id: int) -> None: ...

    async def delete_by_user_id(self, user_id: UUID) -> None: ...

    async def list_regions(self) -> Sequence[str]: ...

    async def list(
        self, query: StoreQueryDTO
    ) -> tuple[Sequence[Row[tuple[Store, int]]], int]: ...
