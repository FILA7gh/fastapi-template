from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, File, Form, Path, Query, UploadFile, status
from pydantic import ValidationError
from src.api.exceptions import PresentationError
from src.api.permissions import require_seller, require_store_owner
from src.api.schemas.stores import (
    MyStoreListSchema,
    PaginatedStoresListSchema,
    StoreCreateSchema,
    StoreDetailSchema,
    StoreQuerySchema,
    StoreUpdateSchema,
)
from src.application.dtos.additionals import JWTPayloadDTO
from src.application.dtos.stores import (
    CreateStoreDTO,
    SocialMediaDTO,
    StoreQueryDTO,
    UpdateStoreDTO,
)
from src.application.use_cases.stores import (
    CreateStoreUseCase,
    DeleteStoreUseCase,
    GetStoreUseCase,
    ListMyStoresUseCase,
    ListStoresUseCase,
    UpdateStoreImageUseCase,
    UpdateStoreUseCase,
)

router = APIRouter(route_class=DishkaRoute, tags=["Store"], prefix="/stores")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=None)
async def create_store(
    use_case: FromDishka[CreateStoreUseCase],
    image: UploadFile | None = File(None),
    data: str = Form(...),
    current_user: JWTPayloadDTO = Depends(require_seller),
) -> None:
    try:
        payload = StoreCreateSchema.model_validate_json(data)
    except ValidationError as e:
        raise PresentationError(extra=str(e.errors()))
    await use_case(
        image=image,
        user_id=UUID(current_user.sub),
        dto=CreateStoreDTO(
            **payload.model_dump(exclude={"social_medias"}),
            social_medias=[
                SocialMediaDTO(**sm.model_dump()) for sm in payload.social_medias
            ]
            if payload.social_medias
            else None,
        ),
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=list[MyStoreListSchema])
async def my_stores(
    use_case: FromDishka[ListMyStoresUseCase],
    current_user: JWTPayloadDTO = Depends(require_seller),
):
    return await use_case(user_id=UUID(current_user.sub))


@router.get(
    "/all", status_code=status.HTTP_200_OK, response_model=PaginatedStoresListSchema
)
async def all_stores(
    use_case: FromDishka[ListStoresUseCase], query: StoreQuerySchema = Query()
):
    return await use_case(StoreQueryDTO(**query.model_dump()))


@router.get(
    "/{store_id}", status_code=status.HTTP_200_OK, response_model=StoreDetailSchema
)
async def get_store(
    use_case: FromDishka[GetStoreUseCase],
    store_id: int = Path(...),
    _: JWTPayloadDTO = Depends(require_store_owner),
):
    return await use_case(
        store_id=store_id,
    )


@router.delete(
    "/{store_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
async def delete_store(
    use_case: FromDishka[DeleteStoreUseCase],
    store_id: int = Path(...),
    _: JWTPayloadDTO = Depends(require_store_owner),
) -> None:
    await use_case(
        store_id=store_id,
    )


@router.patch("/{store_id}", status_code=status.HTTP_200_OK, response_model=None)
async def update_store(
    body: StoreUpdateSchema,
    use_case: FromDishka[UpdateStoreUseCase],
    store_id: int = Path(...),
    _: JWTPayloadDTO = Depends(require_store_owner),
) -> None:
    await use_case(
        store_id=store_id,
        dto=UpdateStoreDTO(
            **body.model_dump(exclude={"social_medias"}),
            social_medias=[
                SocialMediaDTO(**sm.model_dump()) for sm in body.social_medias
            ]
            if body.social_medias
            else None,
        ),
    )


@router.patch("/{store_id}/image", status_code=status.HTTP_200_OK, response_model=None)
async def update_image(
    use_case: FromDishka[UpdateStoreImageUseCase],
    image: UploadFile | None = File(None),
    store_id: int = Path(...),
    _: JWTPayloadDTO = Depends(require_store_owner),
) -> None:
    await use_case(store_id=store_id, image=image)
