"""Ingestion service — text -> chunks -> embeddings -> SQLite."""
from __future__ import annotations

from src.chunking import chunk_text
from src.core.config import get_settings
from src.core.errors import BadRequestError
from src.core.logger import get_logger
from src.embeddings import get_embedder
from src.repositories.chunk import ChunkRepository
from src.repositories.document import Document, DocumentRepository

logger = get_logger(__name__)


class IngestionService:
    def __init__(
        self,
        documents: DocumentRepository | None = None,
        chunks: ChunkRepository | None = None,
    ) -> None:
        self._documents = documents or DocumentRepository()
        self._chunks = chunks or ChunkRepository()

    def ingest(self, *, name: str, text: str) -> tuple[Document, int]:
        if not name.strip():
            raise BadRequestError("Document name is required")
        if not text.strip():
            raise BadRequestError("Document text is empty")

        settings = get_settings()
        pieces = chunk_text(
            text,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        if not pieces:
            raise BadRequestError("Document produced no chunks")

        embedder = get_embedder()
        vectors = embedder.encode([p.text for p in pieces])

        document = self._documents.create(name=name, byte_size=len(text.encode("utf-8")))
        items = [(p.ord, p.text, vectors[i]) for i, p in enumerate(pieces)]
        n = self._chunks.bulk_insert(document_id=document.id, items=items)

        logger.info(
            "ingested",
            extra={"document_id": document.id, "chunks": n, "bytes": document.byte_size},
        )
        return document, n
