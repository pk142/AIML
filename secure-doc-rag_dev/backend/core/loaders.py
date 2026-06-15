"""
Document loaders — extract (text, page_number) tuples from uploaded files.
Each loader returns List[dict] with keys: text, page, metadata.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import List, Dict, Any

import chardet
import fitz  # PyMuPDF
from docx import Document

logger = logging.getLogger(__name__)


# ── PDF ────────────────────────────────────────────────────────────────────

def load_pdf(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """Extract text page-by-page from a PDF using PyMuPDF."""
    pages = []
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                pages.append({
                    "text": text,
                    "page": page_num + 1,
                    "source": filename,
                    "total_pages": len(doc),
                })
        doc.close()
    except Exception as e:
        logger.error(f"PDF load error for {filename}: {e}")
        raise
    logger.info(f"PDF '{filename}': extracted {len(pages)} pages with text")
    return pages


# ── DOCX ───────────────────────────────────────────────────────────────────

def load_docx(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Extract text from a DOCX. DOCX has no real 'pages', so we group
    paragraphs into ~500-word logical chunks and track paragraph index.
    """
    chunks = []
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        # Group paragraphs into pseudo-pages of ~400 words
        page, word_count = [], 0
        pseudo_page_num = 1
        for para in paragraphs:
            page.append(para)
            word_count += len(para.split())
            if word_count >= 400:
                chunks.append({
                    "text": "\n".join(page),
                    "page": pseudo_page_num,
                    "source": filename,
                    "total_pages": None,  # filled below
                })
                page, word_count = [], 0
                pseudo_page_num += 1

        if page:  # remainder
            chunks.append({
                "text": "\n".join(page),
                "page": pseudo_page_num,
                "source": filename,
                "total_pages": None,
            })

        # Back-fill total pseudo pages
        for c in chunks:
            c["total_pages"] = pseudo_page_num

    except Exception as e:
        logger.error(f"DOCX load error for {filename}: {e}")
        raise

    logger.info(f"DOCX '{filename}': extracted {len(chunks)} sections")
    return chunks


# ── TXT ────────────────────────────────────────────────────────────────────

def load_txt(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """Split plain text into ~400-word pseudo-pages."""
    detected = chardet.detect(file_bytes)
    encoding = detected.get("encoding") or "utf-8"
    text = file_bytes.decode(encoding, errors="replace")

    words = text.split()
    page_size = 400
    chunks = []
    for i in range(0, len(words), page_size):
        chunk_text = " ".join(words[i : i + page_size])
        chunks.append({
            "text": chunk_text,
            "page": (i // page_size) + 1,
            "source": filename,
            "total_pages": (len(words) // page_size) + 1,
        })

    logger.info(f"TXT '{filename}': split into {len(chunks)} sections")
    return chunks


# ── Dispatcher ─────────────────────────────────────────────────────────────

def load_document(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return load_pdf(file_bytes, filename)
    elif ext in (".docx", ".doc"):
        return load_docx(file_bytes, filename)
    elif ext == ".txt":
        return load_txt(file_bytes, filename)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
