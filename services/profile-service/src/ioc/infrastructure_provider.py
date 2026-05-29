from typing import AsyncIterable, AsyncIterator
from uuid import uuid4

from dishka import Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.application import interfaces
from src.application.services import ImageService, MediaURLBuilder
from src.config import Config
from src.infrastructure.geo import OSMGeoLocator
from src.infrastructure.resources.broker import broker
from src.infrastructure.resources.database import new_session_maker
from src.infrastructure.resources.redis_client import RedisClient
from src.infrastructure.security.jwt_service import VerifyJWTService
from src.infrastructure.storage.s3_storage import S3FileStorage
from src.infrastructure.uow import SqlAlchemyUnitOfWork


class InfrastructureProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.APP)
    def get_uuid_generator(self) -> interfaces.UUIDGenerator:
        return uuid4

    @provide(scope=Scope.REQUEST)
    def get_uow(self, session: AsyncSession) -> interfaces.UnitOfWork:
        return SqlAlchemyUnitOfWork(session)

    @provide(scope=Scope.APP)
    def get_media_url_builder(self, config: Config) -> MediaURLBuilder:
        return MediaURLBuilder(base_url=config.media.aws_s3_public_base_url)

    @provide(scope=Scope.APP)
    def provide_broker(self) -> RabbitBroker:
        return broker

    @provide(scope=Scope.APP)
    def jwt_verifier(self, config: Config) -> interfaces.JWTVerifier:
        return VerifyJWTService(
            public_key=config.jwt.public_key.replace("\\n", "\n"),
            algorithm=config.jwt.algorithm,
            issuer=config.jwt.issuer,
            audience=config.jwt.audience,
        )

    @provide(scope=Scope.APP)
    async def get_redis_client(self, config: Config) -> AsyncIterable[RedisClient]:
        client = RedisClient(
            host=config.redis.redis_host,
            port=config.redis.redis_port,
            db=config.redis.redis_db,
        )
        await client.connect()
        try:
            yield client
        finally:
            await client.disconnect()

    @provide(scope=Scope.APP)
    async def get_redis(self, redis_client: RedisClient) -> Redis:
        return redis_client.client

    @provide(scope=Scope.REQUEST)
    def get_image_service(self, file_storage: interfaces.FileStorage) -> ImageService:
        return ImageService(file_storage)

    @provide(scope=Scope.APP)
    async def get_file_storage(self, config: Config) -> interfaces.FileStorage:
        file_storage = S3FileStorage(
            access_key=config.media.aws_s3_access_key,
            secret_key=config.media.aws_s3_secret_key,
            region=config.media.aws_s3_region_name,
            bucket=config.media.aws_s3_bucket_name,
            endpoint_url=config.media.aws_s3_endpoint_url,
            upload_dir=config.media.aws_s3_media_upload_dir,
        )

        return file_storage

    @provide(scope=Scope.REQUEST)
    def get_geo_locator(self) -> interfaces.GeoLocator:
        return OSMGeoLocator()
