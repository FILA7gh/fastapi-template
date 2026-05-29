class ApplicationError(Exception):
    detail = "Application error"
    error_code = "profile.application.error"

    def __init__(self, extra: str | None = None) -> None:
        self.detail = self.__class__.detail
        self.error_code = self.__class__.error_code

        if extra:
            self.detail = f"{self.detail}: {extra}"
        super().__init__(self.detail)


class ProfileNotFound(ApplicationError):
    detail = "Profile not found"
    error_code = "profile.profile.not.found"


class ProfileNotCompleted(ApplicationError):
    detail = "Profile is not completed"
    error_code = "profile.profile.not.completed"


class PhoneCannotChange(ApplicationError):
    detail = "Phone cannot be changed"
    error_code = "profile.phone.cannot.change"


class EmailCannotChange(ApplicationError):
    detail = "Email cannot be changed"
    error_code = "profile.email.cannot.change"


class InvalidTokenError(ApplicationError):
    detail = "Token invalid"
    error_code = "profile.token.invalid"


class ExpiredTokenError(ApplicationError):
    detail = "Token expired"
    error_code = "profile.token.expired"


class AdminPermissionDenied(ApplicationError):
    detail = "Admin permission required"
    error_code = "profile.permission.admin_required"


class SellerPermissionDenied(ApplicationError):
    detail = "Seller permission required"
    error_code = "profile.permission.seller_required"


class SellerAccountAlreadyExists(ApplicationError):
    detail = "Seller account already exists"
    error_code = "profile.seller.exists"


class SellerAccountNotFound(ApplicationError):
    detail = "Seller account not found"
    error_code = "profile.seller.not.found"


class SellerAccountInvalidStatus(ApplicationError):
    detail = "Seller account status must be ON_CORRECTION or REJECTED"
    error_code = "profile.seller.invalid_status"


class FileSizeTooLarge(ApplicationError):
    detail = "File size is too large, max 5MB"
    error_code = "profile.file.large"


class UnsupportedImageFormat(ApplicationError):
    detail = "Unsupported image format"
    error_code = "profile.image.unsupported"


class StoreNotFound(ApplicationError):
    detail = "Store not found"
    error_code = "profile.store.not.found"


class StoreAccessDenied(ApplicationError):
    detail = "You don't have access to this store"
    error_code = "profile.store.access.denied"


class RegionNotFound(ApplicationError):
    detail = "Region not found"
    error_code = "profile.region.not_found"
