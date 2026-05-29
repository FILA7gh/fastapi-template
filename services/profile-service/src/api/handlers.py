from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.api.exceptions import PresentationError
from src.application.exceptions import (
    AdminPermissionDenied,
    ApplicationError,
    EmailCannotChange,
    ExpiredTokenError,
    FileSizeTooLarge,
    InvalidTokenError,
    PhoneCannotChange,
    ProfileNotCompleted,
    ProfileNotFound,
    SellerAccountAlreadyExists,
    SellerAccountInvalidStatus,
    SellerAccountNotFound,
    SellerPermissionDenied,
    StoreAccessDenied,
    StoreNotFound,
    UnsupportedImageFormat,
)

HTTP_ERROR_CODES = {
    ApplicationError: 400,
    ProfileNotFound: 404,
    ProfileNotCompleted: 422,
    InvalidTokenError: 400,
    ExpiredTokenError: 401,
    AdminPermissionDenied: 403,
    SellerAccountAlreadyExists: 409,
    SellerAccountNotFound: 404,
    FileSizeTooLarge: 413,
    UnsupportedImageFormat: 415,
    SellerAccountInvalidStatus: 403,
    StoreNotFound: 404,
    SellerPermissionDenied: 403,
    StoreAccessDenied: 403,
    EmailCannotChange: 403,
    PhoneCannotChange: 403,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        request: Request,
        exc: ApplicationError,
    ):
        status_code = HTTP_ERROR_CODES.get(type(exc), 500)
        return JSONResponse(
            status_code=status_code,
            content={"detail": exc.detail, "error_code": exc.error_code},
        )


def register_presentation_handlers(app: FastAPI) -> None:
    @app.exception_handler(PresentationError)
    async def presentation_error_handler(request: Request, exc: PresentationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.detail, "error_code": exc.error_code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        error = exc.errors()[0]
        msg = error.get("msg", "Validation error")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": msg, "error_code": "profile.validation.error"},
        )
