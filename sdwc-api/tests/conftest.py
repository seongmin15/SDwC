"""Shared test fixtures for sdwc-api."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from sdwc_api.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
