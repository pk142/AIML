"""
Async Ollama client.
- embed(texts)  → List[List[float]]
- generate(prompt) → str
- summarize(text) → str
"""
from __future__ import annotations

import logging
from typing import List

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

OLLAMA_BASE = f"http://{settings.ollama_host}:{settings.ollama_port}"
TIMEOUT = httpx.Timeout(120.0, connect=10.0)


async def embed(texts: List[str]) -> List[List[float]]:
    """Return embeddings for a batch of texts via nomic-embed-text."""
    vectors = []
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for text in texts:
            resp = await client.post(
                f"{OLLAMA_BASE}/api/embeddings",
                json={"model": settings.embed_model, "prompt": text},
            )
            resp.raise_for_status()
            vectors.append(resp.json()["embedding"])
    return vectors


async def generate(prompt: str, system: str | None = None) -> str:
    """Call Phi-3 via Ollama /api/generate (non-streaming)."""
    payload: dict = {
        "model": settings.llm_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 512,
        },
    }
    if system:
        payload["system"] = system

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(f"{OLLAMA_BASE}/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json()["response"].strip()


async def check_model_available(model: str) -> bool:
    """Return True if the model is already pulled in Ollama."""
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        try:
            resp = await client.get(f"{OLLAMA_BASE}/api/tags")
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            return any(model in m for m in models)
        except Exception:
            return False


async def pull_model(model: str) -> None:
    """Pull a model if not present (blocking until done)."""
    logger.info(f"Pulling model: {model}")
    async with httpx.AsyncClient(timeout=httpx.Timeout(600.0)) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_BASE}/api/pull",
            json={"name": model, "stream": True},
        ) as resp:
            async for line in resp.aiter_lines():
                if line:
                    logger.debug(f"pull [{model}]: {line}")
    logger.info(f"Model ready: {model}")
