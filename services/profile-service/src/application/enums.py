from enum import StrEnum


class DeviceType(StrEnum):
    ANDROID = "android"
    IOS = "ios"


class UserRole(StrEnum):
    CLIENT = "client"


class SellerStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ON_CORRECTION = "on_correction"


class VerificationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class UserLanguage(StrEnum):
    RU = "ru"
    KY = "ky"


class NotificationType(StrEnum):
    NOTIFICATION = "notification"


class NotificationAction(StrEnum):
    SELLER_ACCOUNT_APPROVED = "seller_account.approved"
    SELLER_ACCOUNT_REJECTED = "seller_account.rejected"
    SELLER_ACCOUNT_ON_CORRECTION = "seller_account.on_correction"
    SELLER_ACCOUNT_PENDING = "seller_account.pending"

    VERIFICATION_APPROVED = "verification.approved"
    VERIFICATION_REJECTED = "verification.rejected"
    VERIFICATION_PENDING = "verification.pending"


class NotificationTitle(StrEnum):
    SELLER_ACCOUNT_APPROVED = "Аккаунт подтвержден!"
    SELLER_ACCOUNT_REJECTED = "Профиль отклонен"
    SELLER_ACCOUNT_ON_CORRECTION = "Профиль требует доработки"
    SELLER_ACCOUNT_PENDING = "Ваш профиль на рассмотрении"

    VERIFICATION_APPROVED = "Верификация подтверждена!"
    VERIFICATION_REJECTED = "Верификация отклонена"
    VERIFICATION_PENDING = "Верификация на рассмотрении"


STATUS_TO_ACTION = {
    SellerStatus.APPROVED: NotificationAction.SELLER_ACCOUNT_APPROVED,
    SellerStatus.REJECTED: NotificationAction.SELLER_ACCOUNT_REJECTED,
    SellerStatus.PENDING: NotificationAction.SELLER_ACCOUNT_PENDING,
    SellerStatus.ON_CORRECTION: NotificationAction.SELLER_ACCOUNT_ON_CORRECTION,
}


STATUS_TO_TITLE = {
    SellerStatus.APPROVED: NotificationTitle.SELLER_ACCOUNT_APPROVED,
    SellerStatus.REJECTED: NotificationTitle.SELLER_ACCOUNT_REJECTED,
    SellerStatus.PENDING: NotificationTitle.SELLER_ACCOUNT_PENDING,
    SellerStatus.ON_CORRECTION: NotificationTitle.SELLER_ACCOUNT_ON_CORRECTION,
}


VERIFICATION_STATUS_TO_ACTION = {
    VerificationStatus.APPROVED: NotificationAction.VERIFICATION_APPROVED,
    VerificationStatus.PENDING: NotificationAction.VERIFICATION_PENDING,
    VerificationStatus.REJECTED: NotificationAction.VERIFICATION_REJECTED,
}

VERIFICATION_STATUS_TO_TITLE = {
    VerificationStatus.APPROVED: NotificationTitle.VERIFICATION_APPROVED,
    VerificationStatus.PENDING: NotificationTitle.VERIFICATION_PENDING,
    VerificationStatus.REJECTED: NotificationTitle.VERIFICATION_REJECTED,
}


class SocialMediaType(StrEnum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"
    TIKTOK = "tiktok"
    SITE = "site"
    YOUTUBE = "youtube"


WHATSAPP_URL = "https://wa.me/"

SOCIAL_BUILDERS = {
    SocialMediaType.WHATSAPP: lambda d: WHATSAPP_URL + d,
}
