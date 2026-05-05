"""Test fixtures — fake embedder + isolated SQLite per test session."""
from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Isolate state — fresh sqlite + faiss dir + cache_clear before every test.
# Set up env BEFORE importing src.* so config picks up the right paths.
# ---------------------------------------------------------------------------

_TMP = Path(tempfile.mkdtemp(prefix="mini_rag_test_"))
os.environ["SQLITE_PATH"] = str(_TMP / "test.sqlite")
os.environ["FAISS_INDEX_DIR"] = str(_TMP / "faiss")
os.environ["HF_HOME"] = str(_TMP / "hf")
os.environ["NODE_ENV"] = "development"
os.environ["LOG_LEVEL"] = "warn"
os.environ["ANTHROPIC_API_KEY"] = ""

from src.core.config import get_settings  # noqa: E402
from src.embeddings import local as embeddings_local  # noqa: E402


_DIM = 32


class _FakeEmbedder:
    """Deterministic hash-based embedder. No network, no model load.

    Encodes text to a 32-d normalised vector using a SHA-256-derived seed, so
    the same text always maps to the same vector but different texts diverge.
    """

    @property
    def dim(self) -> int:
        return _DIM

    def encode(self, texts: list[str], *, batch_size: int = 32) -> np.ndarray:
        if not texts:
            return np.zeros((0, _DIM), dtype=np.float32)
        out = np.vstack([self.encode_one(t) for t in texts]).astype(np.float32, copy=False)
        return out

    def encode_one(self, text: str) -> np.ndarray:
        seed = int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(_DIM).astype(np.float32)
        norm = float(np.linalg.norm(vec))
        return vec / norm if norm > 0 else vec


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch: pytest.MonkeyPatch) -> Any:
    # Each test gets its own sqlite file so writes don't bleed across tests.
    db_path = _TMP / f"test_{os.urandom(4).hex()}.sqlite"
    monkeypatch.setenv("SQLITE_PATH", str(db_path))
    get_settings.cache_clear()

    # db module caches an _initialised flag — reset it.
    from src.core import db as db_module

    db_module._initialised = False  # type: ignore[attr-defined]

    # Force fake embedder.
    monkeypatch.setattr(embeddings_local, "_instance", _FakeEmbedder())
    monkeypatch.setattr("src.embeddings.local.get_embedder", lambda: _FakeEmbedder())

    yield
    db_path.unlink(missing_ok=True)


@pytest.fixture
def fake_embedder() -> _FakeEmbedder:
    return _FakeEmbedder()
