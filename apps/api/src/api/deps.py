"""FastAPI dependency factories — keep services as singletons per process."""
from __future__ import annotations

from functools import lru_cache

from src.repositories.chunk import ChunkRepository
from src.repositories.document import DocumentRepository
from src.repositories.eval_run import EvalRunRepository
from src.services.answer import AnswerService
from src.services.ingestion import IngestionService
from src.services.retrieval import RetrievalService


@lru_cache(maxsize=1)
def get_document_repo() -> DocumentRepository:
    return DocumentRepository()


@lru_cache(maxsize=1)
def get_chunk_repo() -> ChunkRepository:
    return ChunkRepository()


@lru_cache(maxsize=1)
def get_eval_repo() -> EvalRunRepository:
    return EvalRunRepository()


@lru_cache(maxsize=1)
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(chunks=get_chunk_repo())


@lru_cache(maxsize=1)
def get_ingestion_service() -> IngestionService:
    return IngestionService(documents=get_document_repo(), chunks=get_chunk_repo())


@lru_cache(maxsize=1)
def get_answer_service() -> AnswerService:
    return AnswerService()
