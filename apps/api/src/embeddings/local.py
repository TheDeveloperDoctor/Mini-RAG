"""Local sentence-transformers embedder.

Lazy-loaded singleton — the model is heavy and we want to pay the cost once.
Vectors are L2-normalised so cosine similarity == inner product everywhere.
"""
from __future__ import annotations

import os
import threading

import numpy as np

from src.core.config import get_settings
from src.core.logger import get_logger

logger = get_logger(__name__)

_lock = threading.Lock()
_instance: LocalEmbedder | None = None


class LocalEmbedder:
    def __init__(self, model_name: str, device: str, cache_dir: str) -> None:
        os.environ.setdefault("HF_HOME", cache_dir)
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", cache_dir)
        from sentence_transformers import SentenceTransformer  # heavy import deferred

        logger.info("loading_embedder", extra={"model": model_name, "device": device})
        self._model = SentenceTransformer(model_name, device=device, cache_folder=cache_dir)
        self._dim = int(self._model.get_sentence_embedding_dimension() or 0)
        if self._dim <= 0:
            raise RuntimeError("Embedder reported zero dimension")

    @property
    def dim(self) -> int:
        return self._dim

    def encode(self, texts: list[str], *, batch_size: int = 32) -> np.ndarray:
        if not texts:
            return np.zeros((0, self._dim), dtype=np.float32)
        vectors = self._model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.astype(np.float32, copy=False)

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]


def get_embedder() -> LocalEmbedder:
    global _instance
    if _instance is not None:
        return _instance
    with _lock:
        if _instance is None:
            settings = get_settings()
            _instance = LocalEmbedder(
                model_name=settings.embedding_model,
                device=settings.embedding_device,
                cache_dir=settings.hf_home,
            )
    return _instance
