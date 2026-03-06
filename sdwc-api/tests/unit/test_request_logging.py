"""Tests for request logging middleware."""

import json

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient

from sdwc_api.core.logging import setup_logging
from sdwc_api.middleware.request_logging import RequestLoggingMiddleware


@pytest.fixture(autouse=True)
def _init_structlog() -> None:
    setup_logging()


def _create_app() -> FastAPI:
    """Create a minimal FastAPI app with the middleware."""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/api/v1/test")
    async def test_endpoint(request: Request) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse({"request_id": request_id})

    @app.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    @app.get("/api/v1/error")
    async def error_endpoint() -> JSONResponse:
        raise RuntimeError("boom")

    return app


class TestRequestLoggingMiddleware:
    @pytest.mark.asyncio
    async def test_sets_request_id_on_state(self) -> None:
        app = _create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/test")

        assert resp.status_code == 200
        data = resp.json()
        assert data["request_id"] is not None
        assert len(data["request_id"]) == 32  # hex UUID4

    @pytest.mark.asyncio
    async def test_request_id_differs_per_request(self) -> None:
        app = _create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r1 = await client.get("/api/v1/test")
            r2 = await client.get("/api/v1/test")

        assert r1.json()["request_id"] != r2.json()["request_id"]

    @pytest.mark.asyncio
    async def test_health_excluded_from_logging(self, capsys: pytest.CaptureFixture[str]) -> None:
        app = _create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.get("/health")

        captured = capsys.readouterr().out
        # Health endpoint should not produce request_started/request_completed logs
        for line in captured.strip().splitlines():
            if not line.strip():
                continue
            log_entry = json.loads(line)
            assert log_entry.get("event") not in ("request_started", "request_completed")

    @pytest.mark.asyncio
    async def test_logs_request_started_and_completed(self, capsys: pytest.CaptureFixture[str]) -> None:
        app = _create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.get("/api/v1/test")

        captured = capsys.readouterr().out
        events = []
        for line in captured.strip().splitlines():
            if line.strip():
                events.append(json.loads(line))

        event_names = [e["event"] for e in events]
        assert "request_started" in event_names
        assert "request_completed" in event_names

    @pytest.mark.asyncio
    async def test_completed_log_contains_required_fields(self, capsys: pytest.CaptureFixture[str]) -> None:
        app = _create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.get("/api/v1/test")

        captured = capsys.readouterr().out
        for line in captured.strip().splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry["event"] == "request_completed":
                assert entry["method"] == "GET"
                assert entry["path"] == "/api/v1/test"
                assert entry["status"] == 200
                assert "duration_ms" in entry
                assert "request_id" in entry
                assert "timestamp" in entry
                break
        else:
            pytest.fail("request_completed log entry not found")

    @pytest.mark.asyncio
    async def test_request_id_correlates_across_logs(self, capsys: pytest.CaptureFixture[str]) -> None:
        app = _create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.get("/api/v1/test")

        captured = capsys.readouterr().out
        request_ids = set()
        for line in captured.strip().splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry["event"] in ("request_started", "request_completed"):
                request_ids.add(entry.get("request_id"))

        # Both logs should share the same request_id
        assert len(request_ids) == 1
        assert None not in request_ids

    @pytest.mark.asyncio
    async def test_started_log_contains_method_and_path(self, capsys: pytest.CaptureFixture[str]) -> None:
        app = _create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.get("/api/v1/test")

        captured = capsys.readouterr().out
        for line in captured.strip().splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry["event"] == "request_started":
                assert entry["method"] == "GET"
                assert entry["path"] == "/api/v1/test"
                assert "request_id" in entry
                break
        else:
            pytest.fail("request_started log entry not found")

    @pytest.mark.asyncio
    async def test_non_http_scope_passes_through(self) -> None:
        """WebSocket or lifespan scopes should pass through without logging."""
        # Simulate a lifespan scope — should not raise
        called = False

        async def mock_app(scope: dict, receive: object, send: object) -> None:  # type: ignore[type-arg]
            nonlocal called
            called = True

        mw = RequestLoggingMiddleware(mock_app)  # type: ignore[arg-type]
        await mw({"type": "lifespan"}, None, None)  # type: ignore[arg-type]
        assert called
