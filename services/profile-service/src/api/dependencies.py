from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.application.dtos.additionals import JWTPayloadDTO
from src.application.interfaces import JWTVerifier

security = HTTPBearer()


@inject
async def get_current_user(
    verifier: FromDishka[JWTVerifier],
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> JWTPayloadDTO:
    return verifier.verify_token(creds.credentials)
