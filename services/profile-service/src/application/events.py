from uuid import UUID

from pydantic import BaseModel
from src.application.enums import NotificationAction, NotificationType


class UserExchanges:
    USER = "user_events"


class UserRoutingKeys:
    REGISTERED = "user.registered"
    DELETED = "user.deleted"


class UserRegisteredEvent(BaseModel):
    user_id: str
    registration_type: str
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None


class UserDeletedEvent(BaseModel):
    user_id: str


class NotificationExchanges:
    NOTIFICATION = "notification.events"


class NotificationRoutingKeys:
    PUSH = "notification.push"


class NotificationEvent(BaseModel):
    title: NotificationAction
    body: str
    token: str
    user_id: UUID
    type: NotificationType


class StoreExchanges:
    STORE = "store.events"


class StoreRoutingKeys:
    DELETED = "store.deleted"


class StoreDeletedEvent(BaseModel):
    store_id: int
