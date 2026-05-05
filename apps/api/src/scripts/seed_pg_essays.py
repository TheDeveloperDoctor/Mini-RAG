"""Seed the runtime DB with a starter corpus.

Loads `src/eval/corpus.md` so the comparison lab has something to query right
after `make seed`. No network calls, fully reproducible.
"""
from __future__ import annotations

import sys
from pathlib import Path

from src.core.db import init_db
from src.core.logger import Logger, get_logger
from src.services.ingestion import IngestionService

logger = get_logger(__name__)

_CORPUS_PATH = Path(__file__).resolve().parent.parent / "eval" / "corpus.md"


def main() -> int:
    Logger.initialize()
    init_db()

    if not _CORPUS_PATH.exists():
        logger.error("corpus_missing", extra={"path": str(_CORPUS_PATH)})
        return 1

    text = _CORPUS_PATH.read_text(encoding="utf-8")
    service = IngestionService()
    document, n = service.ingest(name="Mini RAG Sample Corpus", text=text)
    print(f"Seeded document #{document.id} with {n} chunks ({document.byte_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
