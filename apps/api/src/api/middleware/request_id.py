"""Request-ID middleware + contextvar plumbing.

Every request gets a UUID (or honors an inbound X-Request-ID), exposes it on
`request.state.request_id`, and stamps a `request_id` field on every log line
emitted while the request is in flight. Returned in the response header so
clients (and tests) can correlate.
"""
from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.core.logger import get_logger, request_id_ctx

_HEADER = "X-Request-ID"
_MAX_LEN = 64

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        incoming = request.headers.get(_HEADER, "").strip()
        rid = incoming[:_MAX_LEN] if incoming else uuid.uuid4().hex
        token = request_id_ctx.set(rid)
        request.state.request_id = rid

        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed",
                extra={"method": request.method, "path": request.url.path},
            )
            raise
        finally:
            request_id_ctx.reset(token)

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        response.headers[_HEADER] = rid
        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "latency_ms": round(elapsed_ms, 2),
            },
        )
        return response
