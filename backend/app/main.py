from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import settings
from app.core.exception_handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import get_logger, setup_logging
from app.core.request_logging import RequestLoggingMiddleware


setup_logging(
    app_name=settings.app_name,
    app_env=settings.app_env,
    app_version=settings.app_version,
    log_level=settings.log_level,
)
settings.validate_runtime_security()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info(
        "Application startup complete",
        extra={
            "event": "app_startup",
            "app_name": settings.app_name,
            "app_version": settings.app_version,
        },
    )
    yield
    logger.info(
        "Application shutdown complete",
        extra={
            "event": "app_shutdown",
        },
    )


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.include_router(api_router, prefix=settings.api_v1_prefix)
