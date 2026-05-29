from enum import Enum
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from src.api.dependencies import get_current_user
from src.application.dtos.additionals import JWTPayloadDTO
from src.application.enums import SellerStatus
from src.application.exceptions import (
    AdminPermissionDenied,
    SellerPermissionDenied,
    StoreAccessDenied,
    StoreNotFound,
)
from src.application.interfaces import SellerAccountRepository, StoreRepository


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


async def require_admin(
    user: JWTPayloadDTO = Depends(get_current_user),
) -> JWTPayloadDTO:
    if user.role != Role.ADMIN:
        raise AdminPermissionDenied()
    return user


@inject
async def require_seller(
    seller_repo: FromDishka[SellerAccountRepository],
    user: JWTPayloadDTO = Depends(get_current_user),
) -> JWTPayloadDTO:
    seller_account = await seller_repo.get_by_user_id(UUID(user.sub))
    if not seller_account or seller_account.status != SellerStatus.APPROVED:
        raise SellerPermissionDenied()
    return user


@inject
async def require_store_owner(
    store_id: int,
    store_repo: FromDishka[StoreRepository],
    user: JWTPayloadDTO = Depends(get_current_user),
) -> JWTPayloadDTO:
    store = await store_repo.get_by_id(store_id)
    if not store:
        raise StoreNotFound()

    if store.user_id != UUID(user.sub):
        raise StoreAccessDenied()

    return user
