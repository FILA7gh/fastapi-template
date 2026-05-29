import logging
from uuid import UUID

from dishka import FromDishka
from src.application.dtos.profiles import CreateProfileDTO
from src.application.events import (
    UserDeletedEvent,
    UserRegisteredEvent,
)
from src.application.use_cases.profiles import (
    CreateProfileUseCase,
    DeleteAccountUseCase,
)
from src.infrastructure.resources.broker import broker
from src.infrastructure.resources.exchanges import USER_EXCHANGE
from src.infrastructure.resources.queues import (
    USER_DELETED_QUEUE,
    USER_REGISTERED_QUEUE,
)

logger = logging.getLogger(__name__)


@broker.subscriber(
    queue=USER_DELETED_QUEUE,
    exchange=USER_EXCHANGE,
)
async def handle_user_deleted(
    event: UserDeletedEvent,
    use_case: FromDishka[DeleteAccountUseCase],
):
    logger.info("Deletion account")
    await use_case(user_id=UUID(event.user_id))


@broker.subscriber(queue=USER_REGISTERED_QUEUE, exchange=USER_EXCHANGE)
async def handle_user_registered(
    event: UserRegisteredEvent, use_case: FromDishka[CreateProfileUseCase]
):
    logger.info("Creating profile")
    await use_case(
        CreateProfileDTO(
            user_id=UUID(event.user_id),
            full_name=event.full_name,
            registration_type=event.registration_type,
            phone=event.phone,
            email=event.email,
        )
    )
