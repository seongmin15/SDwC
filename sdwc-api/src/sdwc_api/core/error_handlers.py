"""Global exception handlers producing RFC 7807 responses."""

import structlog
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from sdwc_api.exceptions import SdwcError

logger = structlog.get_logger()


def _build_rfc7807(
    error_type: str,
    title: str,
    status: int,
    detail: str,
    instance: str,
) -> JSONResponse:
    """Build a single RFC 7807 Problem Details response."""
    return JSONResponse(
        status_code=status,
        content={
            "type": error_type,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": instance,
        },
    )


async def sdwc_error_handler(request: Request, exc: SdwcError) -> JSONResponse:
    """Handle all SdwcError subclasses using their class-level RFC 7807 attrs."""
    return _build_rfc7807(
        error_type=exc.error_type,
        title=exc.title,
        status=exc.http_status,
        detail=str(exc),
        instance=request.url.path,
    )


async def pydantic_validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic ValidationError with field-level details."""
    details = [
        f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
        for e in exc.errors()
    ]
    return _build_rfc7807(
        error_type="https://sdwc.dev/errors/validation-failed",
        title="Validation Failed",
        status=422,
        detail="; ".join(details),
        instance=request.url.path,
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI's RequestValidationError (missing params, wrong types)."""
    details = [
        f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
        for e in exc.errors()
    ]
    return _build_rfc7807(
        error_type="https://sdwc.dev/errors/validation-failed",
        title="Validation Failed",
        status=422,
        detail="; ".join(details),
        instance=request.url.path,
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exception. Never expose internals."""
    request_id = getattr(request.state, "request_id", None)
    await logger.aerror(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_detail=str(exc),
        path=request.url.path,
        request_id=request_id,
    )
    return _build_rfc7807(
        error_type="https://sdwc.dev/errors/internal-error",
        title="Internal Error",
        status=500,
        detail="An unexpected error occurred.",
        instance=request.url.path,
    )
