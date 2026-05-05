"""Retriever-level tests using a tiny synthetic corpus.

Vectors are deterministic and disjoint per chunk so the "right" answer is
unambiguous. Tests assert: build is non-zero, search returns up to k, top hit
is the matching chunk.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.repositories.chunk import Chunk
from src.retrievers import (
    BM25Retriever,
    FAISSFlatRetriever,
    FAISSIVFRetriever,
    HybridRetriever,
    NaiveRetriever,
    RETRIEVER_NAMES,
    build_all,
)
from src.retrievers.base import Retriever


_DIM = 8


def _vec(idx: int) -> np.ndarray:
    v = np.zeros(_DIM, dtype=np.float32)
    v[idx % _DIM] = 1.0
    return v


def _chunk(idx: int, text: str) -> Chunk:
    return Chunk(id=idx, document_id=1, ord=idx, text=text, embedding=_vec(idx), dim=_DIM)


@pytest.fixture
def chunks() -> list[Chunk]:
    return [
        _chunk(1, "the cat sat on the mat"),
        _chunk(2, "dogs bark at strangers loudly"),
        _chunk(3, "fish swim in the ocean depths"),
        _chunk(4, "birds fly above the tall trees"),
        _chunk(5, "horses run across the open fields"),
    ]


@pytest.mark.parametrize(
    "factory",
    [NaiveRetriever, FAISSFlatRetriever, FAISSIVFRetriever, BM25Retriever, HybridRetriever],
)
class TestRetrieverContract:
    def test_empty_corpus_returns_no_hits(self, factory: type[Retriever]) -> None:
        retriever = factory()
        retriever.build([])
        hits = retriever.search("anything", _vec(0), k=5)
        assert hits == []

    def test_search_returns_at_most_k(self, factory: type[Retriever], chunks: list[Chunk]) -> None:
        retriever = factory()
        retriever.build(chunks)
        hits = retriever.search("the cat sat on the mat", _vec(1), k=3)
        assert len(hits) <= 3
        assert all(h.chunk_id in {c.id for c in chunks} for h in hits)

    def test_build_metadata_set(self, factory: type[Retriever], chunks: list[Chunk]) -> None:
        retriever = factory()
        retriever.build(chunks)
        assert retriever.n_items == len(chunks)
        assert retriever.build_ms >= 0.0
        assert retriever.size_bytes >= 0


class TestNaiveExactness:
    def test_naive_top1_matches_query_vector(self, chunks: list[Chunk]) -> None:
        retriever = NaiveRetriever()
        retriever.build(chunks)
        hits = retriever.search("query", _vec(3), k=1)
        assert hits[0].chunk_id == 3


class TestRegistry:
    def test_build_all_returns_every_retriever(self, chunks: list[Chunk]) -> None:
        retrievers = build_all(chunks)
        assert set(retrievers.keys()) == set(RETRIEVER_NAMES)

    def test_build_all_unknown_raises(self, chunks: list[Chunk]) -> None:
        with pytest.raises(KeyError):
            build_all(chunks, ["does-not-exist"])

    def test_build_all_subset(self, chunks: list[Chunk]) -> None:
        retrievers = build_all(chunks, ["naive", "bm25"])
        assert set(retrievers.keys()) == {"naive", "bm25"}
