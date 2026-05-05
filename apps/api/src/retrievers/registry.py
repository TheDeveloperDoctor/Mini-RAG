"""Retriever registry — single source of truth for available strategies.

Adding a new retriever means adding one entry here and one import. Endpoints,
benchmark, and eval all read from this map (Open/Closed).
"""
from __future__ import annotations

from collections.abc import Callable

from src.repositories.chunk import Chunk
from src.retrievers.base import Retriever
from src.retrievers.bm25 import BM25Retriever
from src.retrievers.faiss_flat import FAISSFlatRetriever
from src.retrievers.faiss_ivf import FAISSIVFRetriever
from src.retrievers.hybrid import HybridRetriever
from src.retrievers.naive import NaiveRetriever

_RETRIEVERS: dict[str, Callable[[], Retriever]] = {
    "naive": NaiveRetriever,
    "faiss_flat": FAISSFlatRetriever,
    "faiss_ivf": FAISSIVFRetriever,
    "bm25": BM25Retriever,
    "hybrid": HybridRetriever,
}

RETRIEVER_NAMES: tuple[str, ...] = tuple(_RETRIEVERS.keys())


def build_all(chunks: list[Chunk], names: list[str] | None = None) -> dict[str, Retriever]:
    selected = names or list(RETRIEVER_NAMES)
    out: dict[str, Retriever] = {}
    for name in selected:
        factory = _RETRIEVERS.get(name)
        if factory is None:
            raise KeyError(f"Unknown retriever: {name}")
        instance = factory()
        instance.build(chunks)
        out[name] = instance
    return out
