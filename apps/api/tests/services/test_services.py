from __future__ import annotations

import pytest

from src.core.errors import BadRequestError, ServiceUnavailableError
from src.services.ingestion import IngestionService
from src.services.retrieval import RetrievalService


class TestIngestionService:
    def test_rejects_empty_text(self) -> None:
        with pytest.raises(BadRequestError):
            IngestionService().ingest(name="x", text="   ")

    def test_rejects_empty_name(self) -> None:
        with pytest.raises(BadRequestError):
            IngestionService().ingest(name="  ", text="hello world")

    def test_creates_document_and_chunks(self) -> None:
        service = IngestionService()
        text = "Photosynthesis turns sunlight into food.\n\n" * 5
        document, n = service.ingest(name="bio.txt", text=text)
        assert document.id > 0
        assert n >= 1


class TestRetrievalService:
    def test_query_without_chunks_raises_unavailable(self) -> None:
        with pytest.raises(ServiceUnavailableError):
            RetrievalService().query(question="hello", top_k=3)

    def test_query_returns_results_per_method(self) -> None:
        IngestionService().ingest(name="x.txt", text="alpha beta gamma " * 50)
        service = RetrievalService()
        results = service.query(question="alpha", top_k=3, methods=["naive", "bm25"])
        assert {r.method for r in results} == {"naive", "bm25"}
        for r in results:
            assert r.latency_ms >= 0
            assert len(r.chunks) <= 3

    def test_query_unknown_method_raises(self) -> None:
        IngestionService().ingest(name="x.txt", text="content " * 10)
        with pytest.raises(BadRequestError):
            RetrievalService().query(question="q", top_k=3, methods=["nope"])

    def test_query_top_k_bounds(self) -> None:
        IngestionService().ingest(name="x.txt", text="content " * 10)
        with pytest.raises(BadRequestError):
            RetrievalService().query(question="q", top_k=0)
        with pytest.raises(BadRequestError):
            RetrievalService().query(question="q", top_k=999)
