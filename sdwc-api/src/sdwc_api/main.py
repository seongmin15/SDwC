"""FastAPI application entry point for sdwc-api."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sdwc_api.core.config import settings
from sdwc_api.routers import health, intake


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    import structlog

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
    )
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

# Middleware: CORS (outermost). Logging and error handling added in later tasks.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(intake.router)
