from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Path, Query, status
from src.api.permissions import require_admin
from src.api.schemas.stores import (
    AdminPaginatedStoresListSchema,
    AdminStoreDetailSchema,
    AdminStoreQuerySchema,
)
from src.application.dtos.additionals import JWTPayloadDTO
from src.application.dtos.stores import StoreQueryDTO
from src.application.use_cases.stores import (
    AdminListStoresUseCase,
    AdminStoreUseCase,
)

router = APIRouter(
    route_class=DishkaRoute, tags=["Admin Store"], prefix="/admin/stores"
)


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=AdminPaginatedStoresListSchema
)
async def admin_stores_list(
    use_case: FromDishka[AdminListStoresUseCase],
    _: JWTPayloadDTO = Depends(require_admin),
    query: AdminStoreQuerySchema = Query(),
):
    return await use_case(StoreQueryDTO(**query.model_dump()))


@router.get(
    "/{store_id}", status_code=status.HTTP_200_OK, response_model=AdminStoreDetailSchema
)
async def admin_store_detail(
    use_case: FromDishka[AdminStoreUseCase],
    _: JWTPayloadDTO = Depends(require_admin),
    store_id: int = Path(...),
):
    return await use_case(store_id=store_id)
