"""
Token-aware chunker with sliding-window overlap.
Operates on the page-dicts produced by loaders.py.
"""
from __future__ import annotations

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def _split_sentences(text: str) -> List[str]:
    """Naive sentence splitter — good enough for chunking purposes."""
    return re.split(r"(?<=[.!?])\s+", text)


def chunk_pages(
    pages: List[Dict[str, Any]],
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> List[Dict[str, Any]]:
    """
    Convert page dicts → smaller overlapping chunks (word-based).
    Each output dict keeps: text, page, source, chunk_index, total_pages.
    """
    chunks: List[Dict[str, Any]] = []
    chunk_index = 0

    for page_dict in pages:
        raw_text = page_dict["text"]
        words = raw_text.split()
        if not words:
            continue

        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = " ".join(words[start:end]).strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "page": page_dict["page"],
                    "source": page_dict["source"],
                    "total_pages": page_dict.get("total_pages"),
                    "chunk_index": chunk_index,
                })
                chunk_index += 1

            if end == len(words):
                break
            start += chunk_size - chunk_overlap

    logger.info(f"Chunking produced {len(chunks)} chunks from {len(pages)} pages")
    return chunks
