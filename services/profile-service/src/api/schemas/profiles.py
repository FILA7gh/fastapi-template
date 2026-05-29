from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel
from src.api.schemas.mixins import EmailValidationMixin, OptionalPhoneMixin
from src.application.enums import (
    SellerStatus,
    SocialMediaType,
    UserLanguage,
    VerificationStatus,
)


class CreateProfileSchema(BaseModel):
    user_id: UUID
    registration_type: str
    phone: str | None = None
    email: str | None = None


class SocialMediaSchema(BaseModel):
    type: SocialMediaType
    url: str | None = None
    detail: str | None = None


class UpdateProfileSchema(OptionalPhoneMixin, EmailValidationMixin):
    full_name: str | None = None
    language: UserLanguage | None = None
    notifications_enabled: bool | None = None
    social_medias: List[SocialMediaSchema] | None = None
    longitude: float | None = None
    latitude: float | None = None


class ProfileSchema(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str | None
    email: str | None
    phone: str | None
    avatar: str | None
    created_at: datetime
    registration_type: str
    language: UserLanguage
    can_edit_phone: bool
    can_edit_email: bool
    seller_status: SellerStatus | None = None
    verification_status: VerificationStatus | None = None
    notifications_enabled: bool = False
    social_medias: List[SocialMediaSchema] | None
    region: str | None
    longitude: float | None = None
    latitude: float | None = None


class AdminListProfileSchema(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str | None
    email: str | None
    avatar: str | None
    role: str | None
    created_at: datetime


class PaginatedAdminListProfileSchema(BaseModel):
    items: List[AdminListProfileSchema]
    count: int


class ProfileListQuerySchema(BaseModel):
    limit: int | None = 20
    offset: int | None = 0
    search: str | None = None
