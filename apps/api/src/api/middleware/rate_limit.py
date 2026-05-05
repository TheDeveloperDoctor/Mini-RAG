"""Per-IP token-bucket rate limiter.

In-process, lock-protected, no external dep. Suitable for single-process /
single-host deployments which is the realistic shape of this project. Swap
for Redis-backed limiting if the API ever fans out to multiple workers.

Strategy:
    - Apply only to selected paths (default: /v1/query).
    - Each client (resolved IP) has a bucket of `capacity` tokens that refills
      at `refill_per_sec` tokens per second. Each request costs one token.
    - When the bucket is empty: respond 429 with Retry-After.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


@dataclass
class _Bucket:
    tokens: float
    updated_at: float


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        *,
        capacity: int = 30,
        refill_per_sec: float = 1.0,
        protected_prefixes: tuple[str, ...] = ("/v1/query",),
    ) -> None:
        super().__init__(app)
        self._capacity = float(capacity)
        self._refill = float(refill_per_sec)
        self._prefixes = protected_prefixes
        self._buckets: dict[str, _Bucket] = {}
        self._lock = threading.Lock()

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if not self._is_protected(request.url.path):
            return await call_next(request)

        client = self._client_key(request)
        retry_after = self._take_token(client)
        if retry_after is not None:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "rate_limited",
                        "message": "Too many requests. Slow down and try again.",
                    }
                },
                headers={"Retry-After": str(retry_after)},
            )

        response: Response = await call_next(request)
        return response

    def _is_protected(self, path: str) -> bool:
        return any(path.startswith(p) for p in self._prefixes)

    @staticmethod
    def _client_key(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "anonymous"

    def _take_token(self, client: str) -> int | None:
        now = time.monotonic()
        with self._lock:
            bucket = self._buckets.get(client)
            if bucket is None:
                bucket = _Bucket(tokens=self._capacity, updated_at=now)
                self._buckets[client] = bucket
            else:
                elapsed = now - bucket.updated_at
                bucket.tokens = min(self._capacity, bucket.tokens + elapsed * self._refill)
                bucket.updated_at = now

            if bucket.tokens < 1.0:
                deficit = 1.0 - bucket.tokens
                retry_in = max(1, int(deficit / max(self._refill, 1e-6)) + 1)
                return retry_in

            bucket.tokens -= 1.0
            return None
