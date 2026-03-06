"""FastAPI application entry point for sdwc-api."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from sdwc_api.core.config import settings
from sdwc_api.core.error_handlers import (
    pydantic_validation_error_handler,
    request_validation_error_handler,
    sdwc_error_handler,
    unhandled_error_handler,
)
from sdwc_api.core.logging import setup_logging
from sdwc_api.exceptions import SdwcError
from sdwc_api.middleware.request_logging import RequestLoggingMiddleware
from sdwc_api.routers import health, intake


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    setup_logging()
    logger = structlog.get_logger()
    await logger.ainfo("application_started", service="sdwc-api", version=settings.APP_VERSION)
    yield
    await logger.ainfo("application_stopped", service="sdwc-api")


app = FastAPI(
    title="sdwc-api",
    description="Survey-driven project documentation generator API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Exception handlers (RFC 7807)
app.add_exception_handler(SdwcError, sdwc_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(ValidationError, pydantic_validation_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, request_validation_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_error_handler)

# Middleware (first registered = outermost):
# 1. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 2. Request logging (after CORS, before error handling)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(health.router)
app.include_router(intake.router)
