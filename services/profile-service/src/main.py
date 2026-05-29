import logging
from contextlib import asynccontextmanager

import dishka_faststream
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from faststream import FastStream
from src.api.handlers import register_exception_handlers, register_presentation_handlers
from src.api.http.routes import main_router
from src.config import Config, config
from src.infrastructure.logging import setup_logging
from src.infrastructure.resources.broker import broker
from src.infrastructure.resources.exchanges import NOTIFICATION_EXCHANGE
from src.ioc import InfrastructureProvider, RepositoryProvider, UseCaseProvider

setup_logging(config.logging.level)

container = make_async_container(
    InfrastructureProvider(),
    RepositoryProvider(),
    UseCaseProvider(),
    context={Config: config},
)

logger = logging.getLogger(__name__)

faststream_app = FastStream(broker)
dishka_faststream.setup_dishka(container, faststream_app, auto_inject=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await broker.connect()
    await broker.declare_exchange(NOTIFICATION_EXCHANGE)

    await faststream_app.start()
    yield
    await faststream_app.stop()

    # Shutdown
    await broker.close()
    await container.close()


def get_fastapi_app() -> FastAPI:
    logger.info("Creating FastAPI app")
    fastapi_app = FastAPI(
        lifespan=lifespan,
        title="Example Project",
        debug=config.app.debug,
        docs_url="/api/profile/docs" if config.app.debug else None,
        redoc_url="/api/profile/redoc" if config.app.debug else None,
        openapi_url="/api/profile/openapi.json" if config.app.debug else None,
    )

    fastapi_app.include_router(main_router)
    setup_dishka(container, fastapi_app)
    return fastapi_app


def get_app():
    # import for consumer registration
    import src.infrastructure.consumers  # noqa

    logger.info("Initializing application")
    fastapi_app = get_fastapi_app()
    register_exception_handlers(fastapi_app)
    register_presentation_handlers(fastapi_app)
    fastapi_app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=config.app.allowed_hosts
    )
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return fastapi_app
