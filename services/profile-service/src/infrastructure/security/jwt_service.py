import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from src.application.dtos.additionals import JWTPayloadDTO
from src.application.exceptions import ExpiredTokenError
from src.application.exceptions import InvalidTokenError as CustomInvalidTokenError
from src.application.interfaces import JWTVerifier


class VerifyJWTService(JWTVerifier):
    def __init__(
        self,
        public_key: str,
        algorithm: str,
        issuer: str,
        audience: str,
    ):
        self._public_key = public_key
        self._algorithm = algorithm
        self._issuer = issuer
        self._audience = audience

    def verify_token(self, token: str) -> JWTPayloadDTO:
        try:
            decoded = jwt.decode(
                token,
                self._public_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                audience=self._audience,
            )
        except ExpiredSignatureError:
            raise ExpiredTokenError()
        except InvalidTokenError:
            raise CustomInvalidTokenError()

        return JWTPayloadDTO(**decoded)
