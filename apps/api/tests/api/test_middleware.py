"""Tests for production-hardening middleware: request id, security headers,
rate limiting, and the /readyz probe."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.deps import (
    get_chunk_repo,
    get_document_repo,
    get_eval_repo,
    get_ingestion_service,
    get_retrieval_service,
)
from src.core.config import get_settings


@pytest.fixture
def client() -> TestClient:
    for fn in (
        get_document_repo,
        get_chunk_repo,
        get_eval_repo,
        get_ingestion_service,
        get_retrieval_service,
    ):
        fn.cache_clear()
    # Re-import inside the fixture so a fresh app is created with current settings.
    from src.main import create_app

    return TestClient(create_app())


class TestRequestId:
    def test_generates_id_when_missing(self, client: TestClient) -> None:
        r = client.get("/healthz")
        assert r.status_code == 200
        rid = r.headers.get("X-Request-ID")
        assert rid and len(rid) == 32  # uuid4 hex

    def test_honours_inbound_id(self, client: TestClient) -> None:
        r = client.get("/healthz", headers={"X-Request-ID": "trace-abc-123"})
        assert r.headers["X-Request-ID"] == "trace-abc-123"

    def test_truncates_overlong_id(self, client: TestClient) -> None:
        long_id = "x" * 200
        r = client.get("/healthz", headers={"X-Request-ID": long_id})
        assert len(r.headers["X-Request-ID"]) <= 64


class TestSecurityHeaders:
    def test_sets_baseline_headers(self, client: TestClient) -> None:
        r = client.get("/healthz")
        assert r.headers["X-Content-Type-Options"] == "nosniff"
        assert r.headers["X-Frame-Options"] == "DENY"
        assert r.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert "Permissions-Policy" in r.headers

    def test_no_hsts_in_dev(self, client: TestClient) -> None:
        # NODE_ENV=development in test conftest -> no HSTS
        r = client.get("/healthz")
        assert "Strict-Transport-Security" not in r.headers


class TestReadyz:
    def test_ready_when_db_works(self, client: TestClient) -> None:
        r = client.get("/readyz")
        assert r.status_code == 200
        assert r.json()["status"] == "ready"


class TestRateLimit:
    @pytest.fixture(autouse=True)
    def _tight_limits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RATE_LIMIT_CAPACITY", "3")
        monkeypatch.setenv("RATE_LIMIT_REFILL_PER_SEC", "0.1")
        get_settings.cache_clear()

    def test_429_after_capacity_exhausted(self, client: TestClient) -> None:
        # /v1/query is the rate-limit protected path. Capacity is 3 in this
        # fixture so we expect the 4th+ request to come back 429.
        responses = [
            client.post("/v1/query", json={"question": "hi", "top_k": 1})
            for _ in range(6)
        ]
        statuses = [r.status_code for r in responses]
        assert 429 in statuses[3:], f"expected 429 after capacity, got {statuses}"

        first_429 = next(r for r in responses if r.status_code == 429)
        assert "Retry-After" in first_429.headers
        body = first_429.json()
        assert body["error"]["code"] == "rate_limited"
