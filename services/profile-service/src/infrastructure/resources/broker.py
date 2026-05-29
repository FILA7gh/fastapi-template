import logging

from faststream.rabbit import RabbitBroker
from faststream.security import SASLPlaintext
from src.config import RabbitMQConfig, config

logger = logging.getLogger(__name__)


def new_broker(rabbitmq_config: RabbitMQConfig) -> RabbitBroker:
    try:
        broker = RabbitBroker(
            host=rabbitmq_config.host,
            port=rabbitmq_config.port,
            security=SASLPlaintext(
                username=rabbitmq_config.login,
                password=rabbitmq_config.password,
            ),
            virtualhost="/",
        )
        logger.info("RabbitMQ broker created")
        return broker
    except Exception:
        logger.exception("Failed to create RabbitMQ broker")
        raise


broker = new_broker(config.rabbitmq)
