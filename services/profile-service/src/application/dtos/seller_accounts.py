from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from src.application.enums import (
    SellerStatus,
    VerificationStatus,
)


@dataclass(slots=True, frozen=True)
class CreateSellerAccountDTO:
    company_phone: str
    company_name: str
    company_address: str


@dataclass(slots=True, frozen=True)
class UpdateSellerAccountDTO:
    company_phone: str
    company_name: str
    company_address: str


@dataclass(slots=True, frozen=True)
class VerifySellerAccountDTO:
    tin: str | None
    legal_address: str | None


@dataclass(slots=True, frozen=True)
class AdminSellerAccountListQueryDTO:
    search: str | None = None
    status: SellerStatus | None = None
    verification_status: VerificationStatus | None = None
    order: Literal["asc", "desc"] = "desc"
    limit: int = 20
    offset: int = 0


@dataclass(slots=True, frozen=True)
class AdminSellerAccountListDTO:
    id: UUID
    full_name: str | None
    user_id: UUID
    email: str | None
    status: SellerStatus
    verification_status: VerificationStatus | None
    created_at: datetime
    company_phone: str
    company_name: str
    company_address: str


@dataclass(slots=True, frozen=True)
class AdminSellerAccountDetailDTO(AdminSellerAccountListDTO):
    passport_front: str | None
    passport_back: str | None
    additional_document: str | None
    tin: str | None
    legal_address: str | None


@dataclass(slots=True, frozen=True)
class AdminSellerAccountSetStatusDTO:
    id: UUID
    status: SellerStatus
    text: str | None = None


@dataclass(slots=True, frozen=True)
class AdminVerificationSetStatusDTO:
    id: UUID
    status: VerificationStatus
    text: str | None = None
