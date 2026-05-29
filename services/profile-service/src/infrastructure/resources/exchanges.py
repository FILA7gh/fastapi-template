from faststream.rabbit import ExchangeType, RabbitExchange
from src.application.events import NotificationExchanges, StoreExchanges, UserExchanges

USER_EXCHANGE = RabbitExchange(
    name=UserExchanges.USER, type=ExchangeType.DIRECT, durable=True, auto_delete=False
)


NOTIFICATION_EXCHANGE = RabbitExchange(
    name=NotificationExchanges.NOTIFICATION,
    type=ExchangeType.DIRECT,
    durable=True,
    auto_delete=False,
)

STORE_EXCHANGE = RabbitExchange(
    name=StoreExchanges.STORE, type=ExchangeType.DIRECT, durable=True, auto_delete=False
)
