from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, File, UploadFile, status
from src.api.dependencies import get_current_user
from src.api.schemas.profiles import ProfileSchema, UpdateProfileSchema
from src.application.dtos.additionals import JWTPayloadDTO
from src.application.dtos.profiles import (
    SocialMediaDTO,
    UpdateProfileDTO,
)
from src.application.use_cases.profiles import (
    DeleteProfileAvatarUseCase,
    GetProfileUseCase,
    UpdateProfileAvatarUseCase,
    UpdateProfileUseCase,
)

router = APIRouter(route_class=DishkaRoute, tags=["Profile"], prefix="/profiles")


@router.get("/me", status_code=status.HTTP_200_OK, response_model=ProfileSchema)
async def get_my_profile(
    use_case: FromDishka[GetProfileUseCase],
    current_user: JWTPayloadDTO = Depends(get_current_user),
):
    return await use_case(current_user_id=UUID(current_user.sub))


@router.patch("/me", status_code=status.HTTP_200_OK, response_model=None)
async def update_my_profile(
    use_case: FromDishka[UpdateProfileUseCase],
    body: UpdateProfileSchema = Body(),
    current_user: JWTPayloadDTO = Depends(get_current_user),
) -> None:
    await use_case(
        user_id=UUID(current_user.sub),
        dto=UpdateProfileDTO(
            **body.model_dump(exclude={"social_medias"}),
            social_medias=[
                SocialMediaDTO(**sm.model_dump()) for sm in body.social_medias
            ]
            if body.social_medias
            else None,
        ),
    )


@router.patch("/me/avatar", status_code=status.HTTP_200_OK, response_model=None)
async def update_my_avatar(
    use_case: FromDishka[UpdateProfileAvatarUseCase],
    image: UploadFile = File(...),
    current_user: JWTPayloadDTO = Depends(get_current_user),
) -> None:
    await use_case(user_id=UUID(current_user.sub), avatar=image)


@router.delete(
    "/me/avatar", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
async def delete_my_avatar(
    use_case: FromDishka[DeleteProfileAvatarUseCase],
    current_user: JWTPayloadDTO = Depends(get_current_user),
) -> None:
    await use_case(UUID(current_user.sub))
