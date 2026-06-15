"""
RAG pipeline:
  ask(question, doc_id?) → {answer, sources}
  summarize(doc_id)      → {summary}
"""
from __future__ import annotations

import logging
from typing import List, Dict, Any

from core import ollama_client, vector_store
from core.config import settings

logger = logging.getLogger(__name__)

# ── Prompts ────────────────────────────────────────────────────────────────

QA_SYSTEM = (
     "You are a precise document analyst. "
    "Answer the user's question using ONLY the provided context excerpts. "
    "Be direct and concise. Start with the answer immediately. "
    "Always mention the page number at the end like: (Source: Page X). "
    "If the answer is not in the context, say exactly: "
    "'This information is not found in the uploaded document.' "
    "Do NOT make up information."
)

SUMMARY_SYSTEM = (
    "You are a concise document summarizer. "
    "Write a clear, structured summary of the provided document excerpts. "
    "Cover: main topic, key points, conclusions. "
    "Be factual and professional."
)


def _build_context(chunks: List[Dict[str, Any]]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(
            f"[Excerpt {i} — Page {c['page']} of {c.get('source', 'document')}]\n"
            f"{c['text']}"
        )
    return "\n\n---\n\n".join(parts)


# ── Q&A ────────────────────────────────────────────────────────────────────

async def ask(
    question: str,
    doc_id: str | None = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    client = vector_store.get_client()

    # 1. Embed the question
    [q_vector] = await ollama_client.embed([question])

    # 2. Retrieve top-k relevant chunks
    chunks = vector_store.search(client, q_vector, doc_id=doc_id, top_k=top_k)

    if not chunks:
        return {
            "answer": "No relevant content found in the document(s).",
            "sources": [],
        }

    # 3. Build prompt
    context = _build_context(chunks)
    prompt = (
        f"Context from the document:\n\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer (cite pages):"
    )

    # 4. Generate answer
    answer = await ollama_client.generate(prompt, system=QA_SYSTEM)

    # 5. Deduplicate sources
    seen = set()
    sources = []
    for c in chunks:
        key = (c["source"], c["page"])
        if key not in seen:
            seen.add(key)
            sources.append({
                "source": c["source"],
                "page": c["page"],
                "score": c["score"],
                "excerpt": c["text"][:200] + ("…" if len(c["text"]) > 200 else ""),
            })

    return {"answer": answer, "sources": sources}


# ── Summarisation ──────────────────────────────────────────────────────────

async def summarize(doc_id: str, max_chunks: int = 12) -> Dict[str, Any]:
    """
    Retrieve a broad sample of chunks from the document and summarize.
    Uses a scroll-based approach to get representative coverage.
    """
    from qdrant_client.http import models as qmodels

    client = vector_store.get_client()

    # Fetch a representative spread of chunks (not semantic search)
    records, _ = client.scroll(
        collection_name=settings.collection_name,
        scroll_filter=qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="doc_id",
                    match=qmodels.MatchValue(value=doc_id),
                )
            ]
        ),
        limit=max_chunks,
        with_payload=True,
    )

    if not records:
        return {"summary": "No content found for this document."}

    chunks = [r.payload for r in records if r.payload]
    # Sort by chunk_index for coherent order
    chunks.sort(key=lambda x: x.get("chunk_index", 0))

    context = _build_context(chunks)
    prompt = (
        f"Document excerpts:\n\n{context}\n\n"
        f"Provide a comprehensive summary of this document:"
    )

    summary = await ollama_client.generate(prompt, system=SUMMARY_SYSTEM)

    source_name = chunks[0].get("source", "Unknown") if chunks else "Unknown"
    total_pages = chunks[0].get("total_pages") if chunks else None

    return {
        "summary": summary,
        "source": source_name,
        "total_pages": total_pages,
        "chunks_used": len(chunks),
    }
