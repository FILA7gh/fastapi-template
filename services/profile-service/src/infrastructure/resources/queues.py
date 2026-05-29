from faststream.rabbit import RabbitQueue
from src.application.events import NotificationRoutingKeys, UserRoutingKeys

USER_DELETED_QUEUE = RabbitQueue(
    name="user.deleted.profile_queue",
    durable=True,
    routing_key=UserRoutingKeys.DELETED,
)


USER_REGISTERED_QUEUE = RabbitQueue(
    name="user.registered.queue",
    durable=True,
    routing_key=UserRoutingKeys.REGISTERED,
)


NOTIFICATION_PUSH_QUEUE = RabbitQueue(
    name="notification.push.queue",
    durable=True,
    routing_key=NotificationRoutingKeys.PUSH,
)
