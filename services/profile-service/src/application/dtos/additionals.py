from dataclasses import dataclass

from src.application.enums import (
    NotificationAction,
    NotificationTitle,
    NotificationType,
)


@dataclass(slots=True, frozen=True)
class JWTPayloadDTO:
    sub: str
    role: str
    iss: str
    aud: str
    exp: int | None = None
    jti: str | None = None


@dataclass(slots=True, frozen=True)
class SendNotificationDTO:
    title: NotificationTitle
    body: str | None
    user_id: str
    type: NotificationType
    action: NotificationAction
