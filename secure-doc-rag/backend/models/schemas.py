from __future__ import annotations
from typing import List, Optional, Any
from pydantic import BaseModel


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks_stored: int
    pages: int
    message: str


class QuestionRequest(BaseModel):
    question: str
    doc_id: Optional[str] = None  # None → search across all documents
    top_k: int = 5


class Source(BaseModel):
    source: str
    page: int
    score: float
    excerpt: str


class AnswerResponse(BaseModel):
    answer: str
    sources: List[Source]
    doc_id: Optional[str] = None


class SummaryResponse(BaseModel):
    doc_id: str
    summary: str
    source: str
    total_pages: Optional[int] = None
    chunks_used: int


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    chunks: int
    pages: Optional[int] = None
    uploaded_at: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]


class DeleteResponse(BaseModel):
    doc_id: str
    message: str


class HealthResponse(BaseModel):
    status: str
    qdrant: str
    ollama: str
    llm_model: str
    embed_model: str
