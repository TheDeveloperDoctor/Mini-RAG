"""Hybrid retriever — Reciprocal Rank Fusion of dense (FAISS Flat) + BM25.

RRF is score-free: it fuses ranks instead of raw scores, which sidesteps the
need to normalise across very different score scales. Standard k=60.
"""
from __future__ import annotations

import time

import numpy as np

from src.repositories.chunk import Chunk
from src.retrievers.base import RetrievalHit, Retriever
from src.retrievers.bm25 import BM25Retriever
from src.retrievers.faiss_flat import FAISSFlatRetriever

_RRF_K = 60


class HybridRetriever(Retriever):
    name = "hybrid"

    def __init__(self, fetch_k: int = 50) -> None:
        super().__init__()
        self._dense = FAISSFlatRetriever()
        self._sparse = BM25Retriever()
        self._fetch_k = fetch_k

    def build(self, chunks: list[Chunk]) -> None:
        start = time.perf_counter()
        self._dense.build(chunks)
        self._sparse.build(chunks)
        self._n = len(chunks)
        self._size_bytes = self._dense.size_bytes + self._sparse.size_bytes
        self._build_ms = (time.perf_counter() - start) * 1000.0

    def search(self, query_text: str, query_vec: np.ndarray, k: int) -> list[RetrievalHit]:
        if self._n == 0:
            return []
        fetch = max(self._fetch_k, k)
        dense_hits = self._dense.search(query_text, query_vec, fetch)
        sparse_hits = self._sparse.search(query_text, query_vec, fetch)

        rrf: dict[int, float] = {}
        for rank, hit in enumerate(dense_hits):
            rrf[hit.chunk_id] = rrf.get(hit.chunk_id, 0.0) + 1.0 / (_RRF_K + rank + 1)
        for rank, hit in enumerate(sparse_hits):
            rrf[hit.chunk_id] = rrf.get(hit.chunk_id, 0.0) + 1.0 / (_RRF_K + rank + 1)

        ordered = sorted(rrf.items(), key=lambda kv: kv[1], reverse=True)[:k]
        return [RetrievalHit(chunk_id=cid, score=score) for cid, score in ordered]
