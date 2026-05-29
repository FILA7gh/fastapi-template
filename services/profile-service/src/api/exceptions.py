class PresentationError(ValueError):
    detail = "Presentation error"
    error_code = "profile.presentation.error"

    def __init__(self, extra: str | None = None) -> None:
        self.detail = self.__class__.detail
        self.error_code = self.__class__.error_code

        if extra:
            self.detail = f"{self.detail}: {extra}"
        super().__init__(self.detail)


class PhoneInvalidError(PresentationError):
    detail = "Phone number must start with +996"
    error_code = "profile.phone.invalid"


class EmailInvalidError(PresentationError):
    detail = "Email must have @"
    error_code = "profile.email.invalid"
