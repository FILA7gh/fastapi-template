from dishka import Provider, Scope, provide
from src.application import interfaces
from src.infrastructure.repositories import (
    SQLAlchemyProfileRepository,
    SQLAlchemySellerAccountRepository,
    SQLAlchemyStoreRepository,
)


class RepositoryProvider(Provider):
    profile_repository = provide(
        SQLAlchemyProfileRepository,
        scope=Scope.REQUEST,
        provides=interfaces.ProfileRepository,
    )

    seller_account_repository = provide(
        SQLAlchemySellerAccountRepository,
        scope=Scope.REQUEST,
        provides=interfaces.SellerAccountRepository,
    )

    store_repository = provide(
        SQLAlchemyStoreRepository,
        scope=Scope.REQUEST,
        provides=interfaces.StoreRepository,
    )
