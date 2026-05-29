from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from src.application.enums import (
    SellerStatus,
    UserLanguage,
    VerificationStatus,
)
from src.application.utils import SocialMediaDTO


@dataclass(slots=True, frozen=True)
class CreateProfileDTO:
    user_id: UUID
    registration_type: str
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None


@dataclass(slots=True, frozen=True)
class ProfileDTO:
    id: UUID
    user_id: UUID
    full_name: str | None
    email: str | None
    phone: str | None
    created_at: datetime
    avatar: str | None
    registration_type: str
    language: UserLanguage
    can_edit_phone: bool
    can_edit_email: bool
    social_medias: List[SocialMediaDTO] | None
    region: str | None
    seller_status: SellerStatus | None = None
    verification_status: VerificationStatus | None = None
    notifications_enabled: bool = False
    longitude: float | None = None
    latitude: float | None = None


@dataclass(slots=True, frozen=True)
class AdminListProfileDTO:
    id: UUID
    user_id: UUID
    full_name: str | None
    email: str | None
    avatar: str | None
    role: str | None
    created_at: datetime


@dataclass(slots=True, frozen=True)
class PaginatedAdminListProfileDTO:
    items: List[AdminListProfileDTO]
    count: int


@dataclass(slots=True, frozen=True)
class PaginationDTO:
    limit: int | None = 20
    offset: int | None = 0


@dataclass(slots=True, frozen=True)
class UpdateProfileDTO:
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    language: UserLanguage | None = None
    notifications_enabled: bool | None = None
    social_medias: List[SocialMediaDTO] | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass(slots=True, frozen=True)
class ProfileListQueryDTO:
    limit: int | None = 20
    offset: int | None = 0
    search: str | None = None
