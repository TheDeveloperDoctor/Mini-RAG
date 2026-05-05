"""Retrieval service — owns the in-memory index cache and per-method query.

The index cache is keyed on chunk count + max chunk id, which is cheap to
compute and reliably invalidates when ingestion happens. Rebuilds run lazily
on the next query rather than blocking the upload path.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from src.core.errors import BadRequestError, ServiceUnavailableError
from src.core.logger import get_logger
from src.embeddings import get_embedder
from src.repositories.chunk import Chunk, ChunkRepository
from src.retrievers import RETRIEVER_NAMES, build_all
from src.retrievers.base import Retriever

logger = get_logger(__name__)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    document_id: int
    ord: int
    text: str
    score: float


@dataclass(frozen=True)
class MethodResult:
    method: str
    latency_ms: float
    build_ms: float
    index_size_bytes: int
    n_items: int
    chunks: list[RetrievedChunk]


class RetrievalService:
    def __init__(self, chunks: ChunkRepository | None = None) -> None:
        self._chunks_repo = chunks or ChunkRepository()
        self._lock = threading.Lock()
        self._cache_key: tuple[int, int] | None = None
        self._retrievers: dict[str, Retriever] = {}
        self._chunk_lookup: dict[int, Chunk] = {}

    def query(
        self,
        *,
        question: str,
        top_k: int,
        methods: list[str] | None = None,
    ) -> list[MethodResult]:
        if not question.strip():
            raise BadRequestError("Question is empty")
        if top_k <= 0 or top_k > 50:
            raise BadRequestError("top_k must be in [1, 50]")

        selected = methods or list(RETRIEVER_NAMES)
        unknown = [m for m in selected if m not in RETRIEVER_NAMES]
        if unknown:
            raise BadRequestError(f"Unknown retriever(s): {unknown}")

        retrievers, lookup = self._ensure_built(selected)
        if not lookup:
            raise ServiceUnavailableError("No chunks indexed yet")

        embedder = get_embedder()
        query_vec = embedder.encode_one(question)

        results: list[MethodResult] = []
        for name in selected:
            retriever = retrievers[name]
            start = time.perf_counter()
            hits = retriever.search(question, query_vec, top_k)
            latency_ms = (time.perf_counter() - start) * 1000.0

            retrieved = [
                RetrievedChunk(
                    chunk_id=h.chunk_id,
                    document_id=lookup[h.chunk_id].document_id,
                    ord=lookup[h.chunk_id].ord,
                    text=lookup[h.chunk_id].text,
                    score=h.score,
                )
                for h in hits
                if h.chunk_id in lookup
            ]
            results.append(
                MethodResult(
                    method=name,
                    latency_ms=latency_ms,
                    build_ms=retriever.build_ms,
                    index_size_bytes=retriever.size_bytes,
                    n_items=retriever.n_items,
                    chunks=retrieved,
                )
            )
        return results

    def invalidate(self) -> None:
        with self._lock:
            self._cache_key = None
            self._retrievers = {}
            self._chunk_lookup = {}

    def _ensure_built(
        self, selected: list[str]
    ) -> tuple[dict[str, Retriever], dict[int, Chunk]]:
        chunks = self._chunks_repo.all_chunks()
        if not chunks:
            return {}, {}

        key = (len(chunks), chunks[-1].id)
        with self._lock:
            missing = [m for m in selected if m not in self._retrievers]
            stale = self._cache_key != key
            if not stale and not missing:
                return self._retrievers, self._chunk_lookup

            if stale:
                logger.info("rebuilding_indices", extra={"key": key, "n": len(chunks)})
                self._retrievers = build_all(chunks, list(selected))
                self._cache_key = key
            elif missing:
                self._retrievers.update(build_all(chunks, missing))

            self._chunk_lookup = {c.id: c for c in chunks}
            return self._retrievers, self._chunk_lookup
