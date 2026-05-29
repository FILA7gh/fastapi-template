from typing import Sequence, Tuple
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload
from src.application.dtos.profiles import ProfileListQueryDTO
from src.application.dtos.seller_accounts import AdminSellerAccountListQueryDTO
from src.application.dtos.stores import StoreQueryDTO
from src.application.interfaces import (
    ProfileRepository,
    SellerAccountRepository,
    StoreRepository,
)
from src.infrastructure.models import (
    ProductRO,
    Profile,
    SellerAccount,
    Store,
)


class SQLAlchemyProfileRepository(ProfileRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, profile: Profile) -> None:
        self._session.add(profile)

    async def get_by_id(self, user_id: UUID) -> Profile | None:
        stmt = sa.select(Profile).where(Profile.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        stmt = sa.select(Profile).where(Profile.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, user_id: UUID) -> None:
        stmt = sa.delete(Profile).where(Profile.user_id == user_id)
        await self._session.execute(stmt)

    async def list(self, query: ProfileListQueryDTO) -> tuple[Sequence[Profile], int]:
        stmt = sa.select(Profile)

        if query.search:
            stmt = stmt.where(Profile.full_name.ilike(f"%{query.search}%"))

        count_stmt = sa.select(sa.func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        stmt = (
            stmt.order_by(Profile.created_at.desc())
            .limit(query.limit)
            .offset(query.offset)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all(), count_result.scalar_one()


class SQLAlchemySellerAccountRepository(SellerAccountRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, seller_account: SellerAccount) -> None:
        self._session.add(seller_account)

    async def exists_by_user_id(self, user_id: UUID) -> bool:
        stmt = sa.select(1).where(SellerAccount.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar() is not None

    async def delete(self, user_id: UUID) -> None:
        stmt = sa.delete(SellerAccount).where(SellerAccount.user_id == user_id)
        await self._session.execute(stmt)

    async def list(
        self, dto: AdminSellerAccountListQueryDTO
    ) -> Sequence[SellerAccount]:
        stmt = (
            sa.select(SellerAccount)
            .join(SellerAccount.profile)
            .options(contains_eager(SellerAccount.profile))
        )
        if dto.status:
            stmt = stmt.where(SellerAccount.status == dto.status.value)
        if dto.verification_status:
            stmt = stmt.where(
                SellerAccount.verification_status == dto.verification_status.value
            )
        if dto.search:
            stmt = stmt.where(
                sa.or_(
                    SellerAccount.company_name.ilike(f"%{dto.search}%"),
                    SellerAccount.profile.has(
                        Profile.full_name.ilike(f"%{dto.search}%")
                    ),
                )
            )

        sort_field = SellerAccount.created_at

        stmt = stmt.order_by(
            sa.asc(sort_field) if dto.order == "asc" else sa.desc(sort_field)
        )

        stmt = stmt.limit(dto.limit).offset(dto.offset)

        result = await self._session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_id(self, account_id: UUID) -> SellerAccount | None:
        stmt = (
            sa.select(SellerAccount)
            .options(joinedload(SellerAccount.profile))
            .where(SellerAccount.id == account_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> SellerAccount | None:
        stmt = sa.select(SellerAccount).where(SellerAccount.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class SQLAlchemyStoreRepository(StoreRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, store: Store) -> None:
        self._session.add(store)

    async def get_by_id(self, store_id: int) -> Store | None:
        stmt = sa.select(Store).where(Store.id == store_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> Sequence[Store]:
        stmt = (
            sa.select(Store).where(Store.user_id == user_id).order_by(Store.id.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def delete(self, store_id: int) -> None:
        stmt = sa.delete(Store).where(Store.id == store_id)
        await self._session.execute(stmt)

    async def delete_by_user_id(self, user_id: UUID) -> None:
        stmt = sa.delete(Store).where(Store.user_id == user_id)
        await self._session.execute(stmt)

    async def list_regions(self) -> Sequence[str]:
        stmt = sa.select(Store.region).where(Store.region.is_not(None)).distinct()
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list(
        self, query: StoreQueryDTO
    ) -> tuple[Sequence[sa.Row[Tuple[Store, int]]], int]:
        total_stmt = sa.select(sa.func.count(Store.id))

        stmt = (
            sa.select(
                Store,
                sa.func.count(ProductRO.id).label("products_count"),
            )
            .outerjoin(
                ProductRO,
                Store.id == sa.any_(ProductRO.stores_ids),
            )
            .group_by(Store.id)
        )

        if query.name:
            stmt = stmt.where(Store.name.ilike(f"%{query.name}%"))
            total_stmt = total_stmt.where(Store.name.ilike(f"%{query.name}%"))

        total = await self._session.scalar(total_stmt)

        stmt = stmt.offset(query.offset).limit(query.limit)

        result = await self._session.execute(stmt)

        return result.all(), total or 0
