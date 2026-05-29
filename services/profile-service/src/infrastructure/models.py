from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy import UUID as SA_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRO(Base):
    __tablename__ = "users"
    __table_args__ = {
        "schema": "auth",
        "extend_existing": True,
    }

    id: Mapped[UUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )


class ProductRO(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index(
            "idx_products_name_trgm",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
        Index(
            "idx_products_description_trgm",
            "description",
            postgresql_using="gin",
            postgresql_ops={"description": "gin_trgm_ops"},
        ),
        {
            "schema": "product",
            "extend_existing": True,
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    stores_ids: Mapped[List[int]] = mapped_column(
        ARRAY(item_type=Integer), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "profile"}

    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key=True,
    )
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    user_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True), nullable=False, unique=True
    )
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    registration_type: Mapped[str] = mapped_column(String(20), nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=False)
    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    social_medias: Mapped[List[dict] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    role: Mapped[str] = mapped_column(String(100), nullable=True)
    region: Mapped[str] = mapped_column(String(100), nullable=True)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=True)
    seller_account: Mapped["SellerAccount"] = relationship(
        "SellerAccount",
        back_populates="profile",
        uselist=False,
    )


class SellerAccount(Base):
    __tablename__ = "seller_accounts"
    __table_args__ = {"schema": "profile"}

    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        ForeignKey("profile.profiles.user_id"),
        nullable=False,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    passport_front: Mapped[str | None] = mapped_column(String(255), nullable=True)
    passport_back: Mapped[str | None] = mapped_column(String(255), nullable=True)
    additional_document: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tin: Mapped[str | None] = mapped_column(String(20), nullable=True)  # ИНН
    legal_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    verification_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    company_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_address: Mapped[str] = mapped_column(String(255), nullable=False)

    profile: Mapped["Profile"] = relationship(
        "Profile",
        back_populates="seller_account",
        uselist=False,
    )


class Store(Base):
    __tablename__ = "stores"
    __table_args__ = {"schema": "profile"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    user_id: Mapped[UUID] = mapped_column(SA_UUID(as_uuid=True), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=True)
    social_medias: Mapped[List[dict] | None] = mapped_column(JSON, nullable=True)
