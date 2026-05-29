from pydantic import BaseModel, field_validator
from src.api.exceptions import EmailInvalidError, PhoneInvalidError


class RequiredPhoneMixin(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v.startswith("+996"):
            raise PhoneInvalidError()
        return v


class OptionalPhoneMixin(BaseModel):
    phone: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith("+996"):
            raise PhoneInvalidError()
        return v


class EmailValidationMixin(BaseModel):
    email: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is not None and "@" not in v:
            raise EmailInvalidError()
        return v
