from dataclasses import dataclass
from uuid import UUID

from src.application.utils import SocialMediaDTO


@dataclass(slots=True, frozen=True)
class CreateStoreDTO:
    name: str
    address: str
    phone: str
    longitude: float
    latitude: float
    social_medias: list[SocialMediaDTO] | None


@dataclass(slots=True, frozen=True)
class UpdateStoreDTO:
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    social_medias: list[SocialMediaDTO] | None = None


@dataclass(slots=True, frozen=True)
class StoreDetailDTO:
    id: int
    name: str
    image: str | None
    address: str
    region: str | None
    phone: str
    longitude: float
    latitude: float
    social_medias: list[SocialMediaDTO] | None


@dataclass(slots=True, frozen=True)
class MyStoreListDTO:
    id: int
    name: str
    image: str | None
    user_id: UUID
    address: str
    phone: str
    region: str | None
    longitude: float
    latitude: float
    social_medias: list[SocialMediaDTO] | None


@dataclass(slots=True, frozen=True)
class StoresListDTO:
    id: int
    name: str
    image: str | None
    address: str
    products_count: int


@dataclass(slots=True, frozen=True)
class PaginatedStoresListDTO:
    items: list[StoresListDTO]
    count: int


@dataclass(slots=True, frozen=True)
class StoreQueryDTO:
    limit: int
    offset: int
    name: str | None


# ADMIN


@dataclass(slots=True, frozen=True)
class AdminStoresListDTO:
    id: int
    name: str
    products_count: int


@dataclass(slots=True, frozen=True)
class PaginatedAdminStoresListDTO:
    items: list[AdminStoresListDTO]
    count: int


@dataclass(slots=True, frozen=True)
class AdminStoreDetailDTO:
    id: int
    owner_full_name: str | None
    name: str
    phone: str
    address: str
    social_medias: list[SocialMediaDTO] | None
    image: str | None
