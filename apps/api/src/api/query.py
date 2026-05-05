"""Query route — runs the question through every requested retriever."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.deps import get_answer_service, get_retrieval_service
from src.api.schemas import (
    MethodResultOut,
    QueryRequest,
    QueryResponse,
    RetrievedChunkOut,
)
from src.services.answer import AnswerService
from src.services.retrieval import MethodResult, RetrievalService

router = APIRouter(prefix="/v1/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def run_query(
    payload: QueryRequest,
    retrieval: RetrievalService = Depends(get_retrieval_service),
    answer: AnswerService = Depends(get_answer_service),
) -> QueryResponse:
    results = retrieval.query(
        question=payload.question,
        top_k=payload.top_k,
        methods=payload.methods,
    )
    return QueryResponse(
        question=payload.question,
        top_k=payload.top_k,
        results=[_to_out(r, payload.synthesize_answer, answer, payload.question) for r in results],
    )


def _to_out(
    result: MethodResult,
    synthesize: bool,
    answer: AnswerService,
    question: str,
) -> MethodResultOut:
    answer_text: str | None = None
    if synthesize:
        answer_text = answer.synthesize(question=question, chunks=result.chunks)
    return MethodResultOut(
        method=result.method,
        latency_ms=result.latency_ms,
        build_ms=result.build_ms,
        index_size_bytes=result.index_size_bytes,
        n_items=result.n_items,
        chunks=[RetrievedChunkOut(**vars(c)) for c in result.chunks],
        answer=answer_text,
    )
