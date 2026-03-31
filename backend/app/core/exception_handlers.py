from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger


logger = get_logger(__name__)


def _request_id_from(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def build_error_response(
    *,
    error: str,
    message: str,
    status_code: int,
    details: list[dict[str, object]] | dict[str, object] | None = None,
) -> JSONResponse:
    payload = {
        "error": error,
        "message": message,
        "status_code": status_code,
    }
    if details is not None:
        payload["details"] = details

    return JSONResponse(status_code=status_code, content=payload)


async def http_exception_handler(
    request: Request,
    exc: HTTPException | StarletteHTTPException,
) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."
    details = exc.detail if not isinstance(exc.detail, str) else None

    log_method = logger.warning if exc.status_code < 500 else logger.error
    log_method(
        "HTTP exception handled",
        extra={
            "event": "http_exception",
            "request_id": _request_id_from(request),
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "error_type": "http_error",
        },
    )

    return build_error_response(
        error="http_error",
        message=message,
        status_code=exc.status_code,
        details=details,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.warning(
        "Request validation error handled",
        extra={
            "event": "validation_exception",
            "request_id": _request_id_from(request),
            "path": request.url.path,
            "method": request.method,
            "status_code": 422,
            "error_type": "validation_error",
        },
    )
    return build_error_response(
        error="validation_error",
        message="Request validation failed.",
        status_code=422,
        details=exc.errors(),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled exception",
        extra={
            "event": "unhandled_exception",
            "request_id": _request_id_from(request),
            "path": request.url.path,
            "method": request.method,
            "status_code": 500,
            "error_type": "internal_server_error",
        },
    )
    return build_error_response(
        error="internal_server_error",
        message="Internal server error.",
        status_code=500,
    )
