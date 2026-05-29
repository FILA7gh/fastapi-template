from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Query, status
from src.api.permissions import require_admin
from src.api.schemas.profiles import (
    PaginatedAdminListProfileSchema,
    ProfileListQuerySchema,
)
from src.application.dtos.additionals import JWTPayloadDTO
from src.application.dtos.profiles import ProfileListQueryDTO
from src.application.use_cases.profiles import (
    ListProfileUseCase,
)

router = APIRouter(
    route_class=DishkaRoute, tags=["Admin Profile"], prefix="/admin/profiles"
)


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=PaginatedAdminListProfileSchema
)
async def admin_list_profiles(
    use_case: FromDishka[ListProfileUseCase],
    query: ProfileListQuerySchema = Query(),
    _: JWTPayloadDTO = Depends(require_admin),
):
    return await use_case(ProfileListQueryDTO(**query.model_dump()))
