"""End-to-end route tests via FastAPI TestClient."""
from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from src.api.deps import (
    get_chunk_repo,
    get_document_repo,
    get_eval_repo,
    get_ingestion_service,
    get_retrieval_service,
)
from src.main import create_app


@pytest.fixture
def client() -> TestClient:
    # Reset cached deps so each test gets fresh repos backed by the per-test sqlite.
    for fn in (
        get_document_repo,
        get_chunk_repo,
        get_eval_repo,
        get_ingestion_service,
        get_retrieval_service,
    ):
        fn.cache_clear()
    return TestClient(create_app())


class TestHealth:
    def test_healthz_ok(self, client: TestClient) -> None:
        r = client.get("/healthz")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestDocuments:
    def test_upload_then_list(self, client: TestClient) -> None:
        text = b"alpha beta gamma " * 50
        r = client.post(
            "/v1/documents",
            files={"file": ("hello.txt", BytesIO(text), "text/plain")},
        )
        assert r.status_code == 200, r.text
        assert r.json()["chunks"] >= 1

        r2 = client.get("/v1/documents")
        assert r2.status_code == 200
        assert len(r2.json()) == 1
        assert r2.json()[0]["name"] == "hello.txt"

    def test_unsupported_extension_rejected(self, client: TestClient) -> None:
        r = client.post(
            "/v1/documents",
            files={"file": ("hello.pdf", BytesIO(b"not text"), "application/pdf")},
        )
        assert r.status_code == 415

    def test_invalid_utf8_rejected(self, client: TestClient) -> None:
        r = client.post(
            "/v1/documents",
            files={"file": ("hello.txt", BytesIO(b"\xff\xfe\x00\x00"), "text/plain")},
        )
        assert r.status_code == 400


class TestQuery:
    def test_query_runs_every_method(self, client: TestClient) -> None:
        client.post(
            "/v1/documents",
            files={"file": ("x.txt", BytesIO(b"alpha beta gamma delta " * 30), "text/plain")},
        )
        r = client.post(
            "/v1/query",
            json={"question": "alpha", "top_k": 3, "synthesize_answer": False},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        methods = {row["method"] for row in body["results"]}
        assert {"naive", "faiss_flat", "faiss_ivf", "bm25", "hybrid"} <= methods

    def test_query_empty_question_rejected(self, client: TestClient) -> None:
        r = client.post(
            "/v1/query",
            json={"question": "", "top_k": 3, "synthesize_answer": False},
        )
        assert r.status_code == 422
