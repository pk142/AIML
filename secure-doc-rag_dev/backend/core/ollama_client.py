"""
ollama_client.py — auto-selects backend based on settings.dev_mode.

DEV_MODE=true  → mock_llm.py   (sentence-transformers, ~300 MB RAM, no GPU)
DEV_MODE=false → _ollama_real  (phi3 + nomic-embed-text via Ollama, ~8 GB RAM)
"""
from __future__ import annotations
from typing import List
from core.config import settings


def _b():
    if settings.dev_mode:
        import core.mock_llm as backend
    else:
        import core._ollama_real as backend  # type: ignore
    return backend


async def embed(texts: List[str]) -> List[List[float]]:
    return await _b().embed(texts)


async def generate(prompt: str, system: str | None = None) -> str:
    return await _b().generate(prompt, system)


async def check_model_available(model: str) -> bool:
    return await _b().check_model_available(model)


async def pull_model(model: str) -> None:
    return await _b().pull_model(model)
