import logging
from typing import Literal
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Path, Query, status
from src.api.permissions import require_admin
from src.api.schemas.seller_accounts import (
    AdminSellerAccountDetailSchema,
    AdminSellerAccountListResponseSchema,
    AdminSellerAccountSetStatusSchema,
    AdminVerificationSetStatusSchema,
)
from src.application.dtos.additionals import JWTPayloadDTO
from src.application.dtos.seller_accounts import (
    AdminSellerAccountListQueryDTO,
    AdminSellerAccountSetStatusDTO,
    AdminVerificationSetStatusDTO,
)
from src.application.enums import SellerStatus, VerificationStatus
from src.application.use_cases.seller_accounts import (
    AdminSellerAccountDetailUseCase,
    AdminSellerAccountListUseCase,
    AdminSellerAccountSetStatusUseCase,
    AdminVerificationSetStatusUseCase,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    route_class=DishkaRoute,
    tags=["Seller Account Admin"],
    prefix="/admin/seller_accounts",
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[AdminSellerAccountListResponseSchema],
)
async def get_accounts_list(
    status: SellerStatus | None = Query(None),
    verification_status: VerificationStatus | None = Query(None),
    search: str | None = Query(None),
    order: Literal["asc", "desc"] = Query("desc"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_case: FromDishka[AdminSellerAccountListUseCase] = Depends(),
    _: JWTPayloadDTO = Depends(require_admin),
):
    dto = AdminSellerAccountListQueryDTO(
        status=status,
        verification_status=verification_status,
        search=search,
        order=order,
        limit=limit,
        offset=offset,
    )
    return await use_case(dto)


@router.get(
    "/{seller_account_id}",
    status_code=status.HTTP_200_OK,
    response_model=AdminSellerAccountDetailSchema,
)
async def get_account_detail(
    use_case: FromDishka[AdminSellerAccountDetailUseCase],
    _: JWTPayloadDTO = Depends(require_admin),
    seller_account_id: UUID = Path(...),
):
    return await use_case(seller_account_id=seller_account_id)


@router.patch(
    "/{seller_account_id}/status",
    status_code=status.HTTP_200_OK,
    response_model=None,
)
async def set_account_status(
    use_case: FromDishka[AdminSellerAccountSetStatusUseCase],
    body: AdminSellerAccountSetStatusSchema,
    seller_account_id: UUID = Path(...),
    _: JWTPayloadDTO = Depends(require_admin),
) -> None:
    await use_case(
        AdminSellerAccountSetStatusDTO(
            id=seller_account_id, status=SellerStatus(body.status), text=body.text
        )
    )


@router.patch(
    "/{seller_account_id}/verification/status",
    status_code=status.HTTP_200_OK,
    response_model=None,
)
async def set_account_verification_status(
    use_case: FromDishka[AdminVerificationSetStatusUseCase],
    body: AdminVerificationSetStatusSchema,
    seller_account_id: UUID = Path(...),
    _: JWTPayloadDTO = Depends(require_admin),
) -> None:
    await use_case(
        AdminVerificationSetStatusDTO(
            id=seller_account_id, status=VerificationStatus(body.status), text=body.text
        )
    )
