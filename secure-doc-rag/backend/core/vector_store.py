"""
Qdrant vector store wrapper.
Handles collection init, upsert, search, and document deletion.
"""
from __future__ import annotations

import logging
import uuid
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from core.config import settings

logger = logging.getLogger(__name__)


def get_client() -> QdrantClient:
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def ensure_collection(client: QdrantClient) -> None:
    """Create the collection if it doesn't exist yet."""
    existing = [c.name for c in client.get_collections().collections]
    if settings.collection_name not in existing:
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=qmodels.VectorParams(
                size=settings.embed_dim,
                distance=qmodels.Distance.COSINE,
            ),
        )
        logger.info(f"Created Qdrant collection: {settings.collection_name}")
    else:
        logger.info(f"Qdrant collection already exists: {settings.collection_name}")


def upsert_chunks(
    client: QdrantClient,
    chunks: List[Dict[str, Any]],
    vectors: List[List[float]],
    doc_id: str,
) -> int:
    """Upsert chunk embeddings with metadata into Qdrant."""
    points = []
    for chunk, vector in zip(chunks, vectors):
        points.append(
            qmodels.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "doc_id": doc_id,
                    "text": chunk["text"],
                    "page": chunk["page"],
                    "source": chunk["source"],
                    "total_pages": chunk.get("total_pages"),
                    "chunk_index": chunk.get("chunk_index", 0),
                },
            )
        )
    client.upsert(collection_name=settings.collection_name, points=points)
    logger.info(f"Upserted {len(points)} chunks for doc_id={doc_id}")
    return len(points)


def search(
    client: QdrantClient,
    query_vector: List[float],
    doc_id: str | None = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Semantic search. Optionally filter to a specific document by doc_id.
    Returns list of payload dicts with an added 'score' key.
    """
    query_filter = None
    if doc_id:
        query_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="doc_id",
                    match=qmodels.MatchValue(value=doc_id),
                )
            ]
        )

    results = client.search(
        collection_name=settings.collection_name,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    )

    return [
        {**r.payload, "score": round(r.score, 4)}
        for r in results
    ]


def delete_document(client: QdrantClient, doc_id: str) -> int:
    """Delete all vectors belonging to a document."""
    result = client.delete(
        collection_name=settings.collection_name,
        points_selector=qmodels.FilterSelector(
            filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="doc_id",
                        match=qmodels.MatchValue(value=doc_id),
                    )
                ]
            )
        ),
    )
    logger.info(f"Deleted vectors for doc_id={doc_id}")
    return result.operation_id


def list_doc_ids(client: QdrantClient) -> List[str]:
    """Scroll through all points and collect unique doc_ids."""
    doc_ids = set()
    offset = None
    while True:
        records, offset = client.scroll(
            collection_name=settings.collection_name,
            scroll_filter=None,
            limit=100,
            offset=offset,
            with_payload=["doc_id"],
        )
        for r in records:
            if r.payload and "doc_id" in r.payload:
                doc_ids.add(r.payload["doc_id"])
        if offset is None:
            break
    return list(doc_ids)
