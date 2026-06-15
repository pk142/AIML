"""
Secure Document Intelligence — FastAPI entry point.
All processing is fully local; no data leaves the server.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from core import ollama_client, vector_store
from core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: ensure Qdrant collection exists and models are pulled."""
    logger.info("🚀 Starting Secure Document Intelligence API")

    # Ensure Qdrant collection
    try:
        client = vector_store.get_client()
        vector_store.ensure_collection(client)
        logger.info("✅ Qdrant collection ready")
    except Exception as e:
        logger.warning(f"⚠️  Qdrant not ready at startup (will retry on first request): {e}")

    # Pull models if missing
    for model in [settings.llm_model, settings.embed_model]:
        try:
            if not await ollama_client.check_model_available(model):
                logger.info(f"📥 Pulling model: {model}")
                await ollama_client.pull_model(model)
            else:
                logger.info(f"✅ Model already available: {model}")
        except Exception as e:
            logger.warning(f"⚠️  Could not verify/pull model {model}: {e}")

    logger.info("✅ Startup complete")
    yield
    logger.info("👋 Shutdown complete")


app = FastAPI(
    title="Secure Document Intelligence API",
    description=(
        "Fully local RAG system — PDF/DOCX/TXT ingestion, "
        "semantic Q&A, and summarization. No data leaves the server."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "service": "Secure Document Intelligence API",
        "status": "running",
        "docs": "/docs",
        "security": "fully local — no external API calls",
    }
