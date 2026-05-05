"""Document routes — upload + list."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from src.api.deps import get_document_repo, get_ingestion_service, get_retrieval_service
from src.api.schemas import DocumentOut, IngestResponse
from src.core.errors import BadRequestError, UnsupportedMediaError
from src.repositories.document import DocumentRepository
from src.services.ingestion import IngestionService
from src.services.retrieval import RetrievalService

router = APIRouter(prefix="/v1/documents", tags=["documents"])

_ALLOWED_SUFFIXES = {".txt", ".md", ".markdown"}
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB per file


@router.post("", response_model=IngestResponse)
async def upload_document(
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    ingestion: IngestionService = Depends(get_ingestion_service),
    retrieval: RetrievalService = Depends(get_retrieval_service),
) -> IngestResponse:
    if not file.filename:
        raise BadRequestError("File missing a filename")
    suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if suffix not in _ALLOWED_SUFFIXES:
        raise UnsupportedMediaError(f"Unsupported file type: {suffix or 'unknown'}")

    raw = await file.read()
    if len(raw) > _MAX_BYTES:
        raise BadRequestError(f"File exceeds {_MAX_BYTES} bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BadRequestError("File is not valid UTF-8") from exc

    document, n = ingestion.ingest(name=(name or file.filename), text=text)
    retrieval.invalidate()
    return IngestResponse(
        document=DocumentOut(**vars(document)),
        chunks=n,
    )


@router.get("", response_model=list[DocumentOut])
def list_documents(repo: DocumentRepository = Depends(get_document_repo)) -> list[DocumentOut]:
    return [DocumentOut(**vars(d)) for d in repo.list_all()]
