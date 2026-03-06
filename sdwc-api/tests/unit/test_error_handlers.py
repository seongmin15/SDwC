"""Tests for global exception handlers (RFC 7807 responses)."""

import json

import pytest
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, ValidationError

from sdwc_api.core.error_handlers import (
    _build_rfc7807,
    pydantic_validation_error_handler,
    request_validation_error_handler,
    sdwc_error_handler,
    unhandled_error_handler,
)
from sdwc_api.exceptions import (
    FrameworkNotFoundError,
    OutputContractError,
    PipelineTimeoutError,
    RenderingError,
    SdwcError,
    YamlParseError,
)

# ---------------------------------------------------------------------------
# _build_rfc7807 helper
# ---------------------------------------------------------------------------


class TestBuildRfc7807:
    def test_produces_correct_structure(self) -> None:
        resp = _build_rfc7807(
            error_type="https://sdwc.dev/errors/test",
            title="Test Error",
            status=418,
            detail="Something went wrong",
            instance="/api/v1/test",
        )
        assert resp.status_code == 418
        body = json.loads(resp.body)
        assert body["type"] == "https://sdwc.dev/errors/test"
        assert body["title"] == "Test Error"
        assert body["status"] == 418
        assert body["detail"] == "Something went wrong"
        assert body["instance"] == "/api/v1/test"

    def test_all_five_rfc7807_fields_present(self) -> None:
        resp = _build_rfc7807("t", "t", 400, "d", "/i")
        body = json.loads(resp.body)
        assert set(body.keys()) == {"type", "title", "status", "detail", "instance"}


# ---------------------------------------------------------------------------
# sdwc_error_handler
# ---------------------------------------------------------------------------


def _make_request(path: str = "/api/v1/test") -> Request:
    """Create a minimal ASGI Request for testing."""
    scope = {
        "type": "http",
        "method": "POST",
        "path": path,
        "query_string": b"",
        "headers": [],
    }
    return Request(scope)


class TestSdwcErrorHandler:
    @pytest.mark.asyncio
    async def test_yaml_parse_error(self) -> None:
        exc = YamlParseError("Invalid YAML: bad syntax")
        resp = await sdwc_error_handler(_make_request("/api/v1/preview"), exc)
        assert resp.status_code == 422
        body = json.loads(resp.body)
        assert body["type"] == "https://sdwc.dev/errors/validation-failed"
        assert body["title"] == "Validation Failed"
        assert body["detail"] == "Invalid YAML: bad syntax"
        assert body["instance"] == "/api/v1/preview"

    @pytest.mark.asyncio
    async def test_pipeline_timeout_error(self) -> None:
        exc = PipelineTimeoutError("Pipeline exceeded 30s timeout")
        resp = await sdwc_error_handler(_make_request("/api/v1/generate"), exc)
        assert resp.status_code == 408
        body = json.loads(resp.body)
        assert body["type"] == "https://sdwc.dev/errors/request-timeout"
        assert body["title"] == "Request Timeout"

    @pytest.mark.asyncio
    async def test_rendering_error(self) -> None:
        exc = RenderingError("Template rendering failed")
        resp = await sdwc_error_handler(_make_request(), exc)
        assert resp.status_code == 500
        body = json.loads(resp.body)
        assert body["type"] == "https://sdwc.dev/errors/rendering-failed"

    @pytest.mark.asyncio
    async def test_framework_not_found_error(self) -> None:
        exc = FrameworkNotFoundError("django", "my-api")
        resp = await sdwc_error_handler(_make_request(), exc)
        assert resp.status_code == 422
        body = json.loads(resp.body)
        assert body["type"] == "https://sdwc.dev/errors/rendering-failed"
        assert "django" in body["detail"]

    @pytest.mark.asyncio
    async def test_output_contract_error(self) -> None:
        exc = OutputContractError(["missing CLAUDE.md", "bad structure"])
        resp = await sdwc_error_handler(_make_request(), exc)
        assert resp.status_code == 422
        body = json.loads(resp.body)
        assert body["type"] == "https://sdwc.dev/errors/output-contract-failed"

    @pytest.mark.asyncio
    async def test_base_sdwc_error_fallback(self) -> None:
        exc = SdwcError("Generic domain error")
        resp = await sdwc_error_handler(_make_request(), exc)
        assert resp.status_code == 500
        body = json.loads(resp.body)
        assert body["type"] == "https://sdwc.dev/errors/internal-error"

    @pytest.mark.asyncio
    async def test_instance_reflects_request_path(self) -> None:
        exc = YamlParseError("bad")
        resp = await sdwc_error_handler(_make_request("/api/v1/generate"), exc)
        body = json.loads(resp.body)
        assert body["instance"] == "/api/v1/generate"


# ---------------------------------------------------------------------------
# pydantic_validation_error_handler
# ---------------------------------------------------------------------------


class TestPydanticValidationErrorHandler:
    @pytest.mark.asyncio
    async def test_field_level_details(self) -> None:
        class _M(BaseModel):
            name: str
            age: int

        try:
            _M.model_validate({"age": "not_int"})
        except ValidationError as exc:
            resp = await pydantic_validation_error_handler(_make_request(), exc)

        assert resp.status_code == 422
        body = json.loads(resp.body)
        assert body["type"] == "https://sdwc.dev/errors/validation-failed"
        assert body["title"] == "Validation Failed"
        assert "name" in body["detail"]


# ---------------------------------------------------------------------------
# request_validation_error_handler
# ---------------------------------------------------------------------------


class TestRequestValidationErrorHandler:
    @pytest.mark.asyncio
    async def test_missing_param(self) -> None:
        exc = RequestValidationError(
            errors=[{"loc": ("body", "file"), "msg": "Field required", "type": "missing"}]
        )
        resp = await request_validation_error_handler(_make_request(), exc)
        assert resp.status_code == 422
        body = json.loads(resp.body)
        assert body["type"] == "https://sdwc.dev/errors/validation-failed"
        assert "file" in body["detail"]


# ---------------------------------------------------------------------------
# unhandled_error_handler
# ---------------------------------------------------------------------------


class TestUnhandledErrorHandler:
    @pytest.mark.asyncio
    async def test_hides_internal_detail(self) -> None:
        exc = RuntimeError("secret DB connection string")
        resp = await unhandled_error_handler(_make_request(), exc)
        assert resp.status_code == 500
        body = json.loads(resp.body)
        assert body["type"] == "https://sdwc.dev/errors/internal-error"
        assert body["title"] == "Internal Error"
        assert body["detail"] == "An unexpected error occurred."
        assert "secret" not in body["detail"]
        assert "DB" not in body["detail"]


# ---------------------------------------------------------------------------
# Integration: handlers registered on app
# ---------------------------------------------------------------------------


class TestHandlersRegisteredOnApp:
    @pytest.mark.asyncio
    async def test_sdwc_error_returns_rfc7807_via_app(self) -> None:
        """Verify that SdwcError exceptions are caught by the global handler."""
        app = FastAPI()

        @app.get("/boom")
        async def boom() -> None:
            raise YamlParseError("test error via app")

        app.add_exception_handler(SdwcError, sdwc_error_handler)  # type: ignore[arg-type]

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/boom")

        assert resp.status_code == 422
        body = resp.json()
        assert body["type"] == "https://sdwc.dev/errors/validation-failed"
        assert body["detail"] == "test error via app"
