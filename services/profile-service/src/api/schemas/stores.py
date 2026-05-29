from uuid import UUID

from pydantic import BaseModel
from src.api.schemas.mixins import OptionalPhoneMixin, RequiredPhoneMixin
from src.application.enums import SocialMediaType


class SocialMediaSchema(BaseModel):
    type: SocialMediaType
    url: str | None = None
    detail: str | None = None


class StoreCreateSchema(RequiredPhoneMixin):
    name: str
    address: str
    longitude: float
    latitude: float
    social_medias: list[SocialMediaSchema] | None = None


class StoreUpdateSchema(OptionalPhoneMixin):
    name: str | None = None
    address: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    social_medias: list[SocialMediaSchema] | None = None


class MyStoreListSchema(BaseModel):
    id: int
    name: str
    image: str | None
    user_id: UUID
    address: str
    region: str | None
    phone: str
    longitude: float
    latitude: float
    social_medias: list[SocialMediaSchema] | None

    class Config:
        from_attributes = True


class StoreDetailSchema(BaseModel):
    id: int
    name: str
    image: str | None
    address: str
    region: str | None
    phone: str
    longitude: float
    latitude: float
    social_medias: list[SocialMediaSchema] | None


class StoresListSchema(BaseModel):
    id: int
    name: str
    image: str | None
    address: str
    products_count: int


class PaginatedStoresListSchema(BaseModel):
    items: list[StoresListSchema]
    count: int


class StoreQuerySchema(BaseModel):
    limit: int | None = 20
    offset: int | None = 0
    name: str | None = None


class AdminStoresListSchema(BaseModel):
    id: int
    name: str
    products_count: int


class AdminPaginatedStoresListSchema(BaseModel):
    items: list[AdminStoresListSchema]
    count: int


class AdminStoreQuerySchema(StoreQuerySchema):
    pass


class AdminStoreDetailSchema(BaseModel):
    id: int
    owner_full_name: str
    name: str
    phone: str
    address: str
    social_medias: list[SocialMediaSchema] | None
    image: str | None
