"""
Simple document registry backed by a JSON file.
Tracks doc_id → metadata so we can list and manage documents.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("/app/uploads/registry.json")


def _load() -> Dict[str, Any]:
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_text())
        except Exception:
            return {}
    return {}


def _save(data: Dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2))


def register(
    doc_id: str,
    filename: str,
    chunks: int,
    pages: int | None,
) -> None:
    registry = _load()
    registry[doc_id] = {
        "doc_id": doc_id,
        "filename": filename,
        "chunks": chunks,
        "pages": pages,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    _save(registry)
    logger.info(f"Registered doc: {doc_id} ({filename})")


def get(doc_id: str) -> Dict[str, Any] | None:
    return _load().get(doc_id)


def list_all() -> List[Dict[str, Any]]:
    return list(_load().values())


def remove(doc_id: str) -> None:
    registry = _load()
    registry.pop(doc_id, None)
    _save(registry)
