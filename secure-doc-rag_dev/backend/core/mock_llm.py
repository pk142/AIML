"""
Dev-mode AI backend — NO Ollama, NO GPU, NO 8 GB RAM required.

Embeddings : sentence-transformers all-MiniLM-L6-v2  (~80 MB model, ~300 MB RAM)
LLM        : rule-based mock that surfaces the retrieved context with clear labels
             (proves the full RAG pipeline — chunking, embedding, retrieval — works)

Switch to real Ollama by setting DEV_MODE=false in your .env.
"""
from __future__ import annotations

import logging
import textwrap
from typing import List

logger = logging.getLogger(__name__)

# Lazy-loaded so import is fast
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading all-MiniLM-L6-v2 (first call — ~5 seconds)…")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model ready.")
    return _model


# ── Embeddings ─────────────────────────────────────────────────────────────

async def embed(texts: List[str]) -> List[List[float]]:
    """Encode texts with all-MiniLM-L6-v2 → 384-dim float lists."""
    model = _get_model()
    vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


# ── LLM mock ───────────────────────────────────────────────────────────────

async def generate(prompt: str, system: str | None = None) -> str:
    """
    Mock LLM: extract the context excerpts from the prompt and
    present them clearly so you can verify the RAG pipeline works.
    In production swap this for a real Ollama call.
    """
    # Parse context excerpts from prompt
    lines = prompt.splitlines()
    excerpts, in_context = [], False
    question = ""

    for line in lines:
        if line.startswith("[Excerpt"):
            in_context = True
            excerpts.append(line)
        elif line.startswith("---") and in_context:
            pass
        elif line.startswith("Question:"):
            in_context = False
            question = line.replace("Question:", "").strip()
        elif in_context and line.strip():
            excerpts.append("  " + line)

    if not excerpts:
        return (
            "⚙️  [DEV MODE — Mock LLM]\n\n"
            "No context was retrieved for this query. "
            "Try uploading a document first, then asking a question about its content."
        )

    context_block = "\n".join(excerpts[:30])  # cap display length
    return textwrap.dedent(f"""
⚙️  **[DEV MODE — Mock LLM active]**

> _Replace `mock_llm.py` with a real Ollama call (set `DEV_MODE=false`) to get actual AI-generated answers._

---

**Your question:** {question or "(see prompt)"}

**Retrieved context (top chunks from your document):**

```
{context_block}
```

**What this proves:** The full pipeline is working —
file upload ✅ · text extraction ✅ · chunking ✅ · embedding ✅ · vector search ✅ · retrieval ✅

When you connect a real LLM (Phi-3 via Ollama), it will receive exactly this context
and generate a grounded answer with page citations.
    """).strip()


async def summarize_mock(context: str, source: str) -> str:
    lines = [l.strip() for l in context.splitlines() if l.strip()][:20]
    preview = "\n".join(lines)
    return textwrap.dedent(f"""
⚙️  **[DEV MODE — Mock Summarizer]**

> _Set `DEV_MODE=false` and run Ollama to get a real AI summary._

**Document:** {source}

**First extracted content (pipeline verification):**

```
{preview}
```

Pipeline status: upload ✅ · extract ✅ · chunk ✅ · embed ✅ · store ✅ · retrieve ✅
    """).strip()


# ── Stubs matching real ollama_client interface ────────────────────────────

async def check_model_available(model: str) -> bool:
    return True  # always "ready" in dev mode


async def pull_model(model: str) -> None:
    logger.info(f"[DEV MODE] Skipping model pull for {model}")
