from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from src.application.enums import SellerStatus, VerificationStatus


class CreateSellerAccountSchema(BaseModel):
    company_phone: str
    company_name: str
    company_address: str


class UpdateSellerAccountSchema(CreateSellerAccountSchema):
    pass


class AdminSellerAccountListResponseSchema(BaseModel):
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

    class Config:
        from_attributes = True


class AdminSellerAccountDetailSchema(AdminSellerAccountListResponseSchema):
    passport_front: str | None
    passport_back: str | None
    additional_document: str | None
    tin: str | None
    legal_address: str | None


class AdminSellerAccountSetStatusSchema(BaseModel):
    status: SellerStatus
    text: str | None = None


class AdminVerificationSetStatusSchema(BaseModel):
    status: VerificationStatus
    text: str | None = None
