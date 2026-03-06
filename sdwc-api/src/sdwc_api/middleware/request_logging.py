"""Request logging middleware with request_id correlation."""

import time
import uuid
from collections.abc import MutableMapping
from typing import Any

import structlog
from starlette.types import ASGIApp, Receive, Scope, Send

logger = structlog.get_logger()

_EXCLUDED_PATHS = frozenset({"/health"})


class RequestLoggingMiddleware:
    """Pure ASGI middleware that logs requests and binds request_id to structlog context."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope["path"]
        if path in _EXCLUDED_PATHS:
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex
        method: str = scope["method"]

        # Store request_id in scope state for access via request.state
        state: MutableMapping[str, Any] = scope.setdefault("state", {})
        state["request_id"] = request_id

        # Bind request_id to structlog context vars for correlation
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            service="sdwc-api",
        )

        await logger.ainfo("request_started", method=method, path=path)

        status_code = 500
        start = time.perf_counter()

        async def send_wrapper(message: MutableMapping[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            await logger.ainfo(
                "request_completed",
                method=method,
                path=path,
                status=status_code,
                duration_ms=duration_ms,
            )
            structlog.contextvars.clear_contextvars()
