import logging
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, File, Form, UploadFile, status
from src.api.dependencies import get_current_user
from src.api.schemas.seller_accounts import (
    CreateSellerAccountSchema,
    UpdateSellerAccountSchema,
)
from src.application.dtos.additionals import JWTPayloadDTO
from src.application.dtos.seller_accounts import (
    CreateSellerAccountDTO,
    UpdateSellerAccountDTO,
    VerifySellerAccountDTO,
)
from src.application.use_cases.seller_accounts import (
    CreateSellerAccountUseCase,
    UpdateSellerAccountUseCase,
    VerifySellerAccountUseCase,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    route_class=DishkaRoute, tags=["Seller Account"], prefix="/seller_accounts"
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=None)
async def create_seller_account(
    use_case: FromDishka[CreateSellerAccountUseCase],
    current_user: JWTPayloadDTO = Depends(get_current_user),
    body: CreateSellerAccountSchema = Body(),
) -> None:
    await use_case(
        dto=CreateSellerAccountDTO(**body.model_dump()),
        user_id=UUID(current_user.sub),
    )


@router.put("", status_code=status.HTTP_200_OK, response_model=None)
async def update_seller_account(
    use_case: FromDishka[UpdateSellerAccountUseCase],
    current_user: JWTPayloadDTO = Depends(get_current_user),
    body: UpdateSellerAccountSchema = Body(),
) -> None:
    await use_case(
        dto=UpdateSellerAccountDTO(**body.model_dump()),
        user_id=UUID(current_user.sub),
    )


@router.patch("/verification", status_code=status.HTTP_200_OK, response_model=None)
async def verify_seller_account(
    use_case: FromDishka[VerifySellerAccountUseCase],
    current_user: JWTPayloadDTO = Depends(get_current_user),
    passport_front: UploadFile | None = File(None),
    passport_back: UploadFile | None = File(None),
    additional_document: UploadFile | None = File(None),
    tin: str | None = Form(None),
    legal_address: str | None = Form(None),
) -> None:
    await use_case(
        user_id=UUID(current_user.sub),
        passport_front=passport_front,
        passport_back=passport_back,
        additional_document=additional_document,
        dto=VerifySellerAccountDTO(tin=tin, legal_address=legal_address),
    )
