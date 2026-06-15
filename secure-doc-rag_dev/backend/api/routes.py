"""
API routes:
  POST /upload          — ingest a document
  POST /ask             — Q&A over document(s)
  GET  /summary/{id}    — summarize a document
  GET  /documents       — list all documents
  DELETE /documents/{id} — delete a document
  GET  /health          — service health
"""
from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from core.config import settings
from core.loaders import load_document
from core.chunker import chunk_pages
from core import ollama_client, vector_store, rag
from models.schemas import (
    UploadResponse, QuestionRequest, AnswerResponse,
    SummaryResponse, DocumentListResponse, DocumentInfo,
    DeleteResponse, HealthResponse,
)
from utils import registry

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_FILE_SIZE_MB = 50


# ── Health ─────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
async def health():
    qdrant_ok = "ok"
    ollama_ok = "ok"

    try:
        client = vector_store.get_client()
        client.get_collections()
    except Exception as e:
        qdrant_ok = f"error: {e}"

    try:
        phi3_ready = await ollama_client.check_model_available(settings.llm_model)
        embed_ready = await ollama_client.check_model_available(settings.embed_model)
        if not phi3_ready or not embed_ready:
            ollama_ok = "models not pulled yet"
    except Exception as e:
        ollama_ok = f"error: {e}"

    return HealthResponse(
        status="ok" if qdrant_ok == "ok" and ollama_ok == "ok" else "degraded",
        qdrant=qdrant_ok,
        ollama=ollama_ok,
        llm_model=settings.llm_model,
        embed_model=settings.embed_model,
    )


# ── Upload ─────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    # Validate extension
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    # Read file
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {MAX_FILE_SIZE_MB} MB limit")
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    doc_id = str(uuid.uuid4())
    filename = file.filename or f"document{suffix}"

    try:
        # 1. Extract text with page metadata
        pages = load_document(file_bytes, filename)
        if not pages:
            raise HTTPException(status_code=422, detail="Could not extract text from file")

        # 2. Chunk
        chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)

        # 3. Embed (batch for efficiency)
        texts = [c["text"] for c in chunks]
        vectors = await ollama_client.embed(texts)

        # 4. Upsert to Qdrant
        client = vector_store.get_client()
        vector_store.ensure_collection(client)
        n = vector_store.upsert_chunks(client, chunks, vectors, doc_id)

        # 5. Register metadata
        total_pages = pages[-1].get("page") if pages else None
        registry.register(doc_id, filename, n, total_pages)

        return UploadResponse(
            doc_id=doc_id,
            filename=filename,
            chunks_stored=n,
            pages=total_pages or 0,
            message="Document ingested successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Upload failed for {filename}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Q&A ────────────────────────────────────────────────────────────────────

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(req: QuestionRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if req.doc_id and not registry.get(req.doc_id):
        raise HTTPException(status_code=404, detail=f"Document {req.doc_id} not found")

    try:
        result = await rag.ask(req.question, doc_id=req.doc_id, top_k=req.top_k)
        return AnswerResponse(
            answer=result["answer"],
            sources=result["sources"],
            doc_id=req.doc_id,
        )
    except Exception as e:
        logger.exception("Q&A failed")
        raise HTTPException(status_code=500, detail=str(e))


# ── Summary ────────────────────────────────────────────────────────────────

@router.get("/summary/{doc_id}", response_model=SummaryResponse)
async def get_summary(doc_id: str):
    if not registry.get(doc_id):
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    try:
        result = await rag.summarize(doc_id)
        return SummaryResponse(
            doc_id=doc_id,
            summary=result["summary"],
            source=result.get("source", ""),
            total_pages=result.get("total_pages"),
            chunks_used=result.get("chunks_used", 0),
        )
    except Exception as e:
        logger.exception("Summary failed")
        raise HTTPException(status_code=500, detail=str(e))


# ── Document Management ────────────────────────────────────────────────────

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    docs = registry.list_all()
    return DocumentListResponse(
        documents=[DocumentInfo(**d) for d in docs]
    )


@router.delete("/documents/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str):
    if not registry.get(doc_id):
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    try:
        client = vector_store.get_client()
        vector_store.delete_document(client, doc_id)
        registry.remove(doc_id)
        return DeleteResponse(doc_id=doc_id, message="Document deleted successfully")
    except Exception as e:
        logger.exception("Delete failed")
        raise HTTPException(status_code=500, detail=str(e))
