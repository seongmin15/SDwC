"""Integration tests for health endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_health_returns_200_with_ok_status(client: AsyncClient) -> None:
    """GET /health returns 200 with status ok."""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
