from __future__ import annotations
from typing import List
from core.config import settings


def _b():
    if settings.use_ollama:
        import core._ollama_real as backend
    else:
        raise ImportError("USE_OLLAMA=false but mock_llm not available in prod")
    return backend


async def embed(texts: List[str]) -> List[List[float]]:
    return await _b().embed(texts)


async def generate(prompt: str, system: str | None = None) -> str:
    return await _b().generate(prompt, system)


async def check_model_available(model: str) -> bool:
    return await _b().check_model_available(model)


async def pull_model(model: str) -> None:
    return await _b().pull_model(model)