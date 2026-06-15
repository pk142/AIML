# 🔒 Secure Document Intelligence & RAG

**100% local — no OpenAI, no Gemini, no Claude API, no data egress.**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM | Phi-3 (via Ollama) | Answer generation |
| Embeddings | nomic-embed-text (via Ollama) | Semantic search vectors |
| Vector DB | Qdrant | Fast chunk retrieval |
| Backend | FastAPI | REST API layer |
| Frontend | Streamlit | User interface |

---

## Architecture

```
User (Browser)
    │
    ▼
Streamlit UI (port 8501)
    │  HTTP
    ▼
FastAPI Backend (port 8000)
    ├── Loaders (PDF/DOCX/TXT)
    ├── Chunker (sliding window, 512w/64 overlap)
    ├── Ollama Client ──► nomic-embed-text  ──► embed text
    │                 └─► Phi-3              ──► generate answer
    └── Qdrant Client  ──► store / search vectors
```

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- ~8 GB free RAM (for Phi-3)
- ~5 GB disk (models + Qdrant data)

### One-command setup

```bash
git clone <this-repo>
cd secure-doc-rag
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
1. Start Qdrant and Ollama
2. Pull `phi3` and `nomic-embed-text` models
3. Start the backend and frontend

### Manual start (after first setup)

```bash
docker compose up -d
```

### Stop

```bash
docker compose down
```

---

## URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8501 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Qdrant Dashboard | http://localhost:6333/dashboard |

---

## API Reference

### Upload a document
```
POST /api/v1/upload
Content-Type: multipart/form-data
Body: file=<PDF|DOCX|TXT>
```

### Ask a question
```
POST /api/v1/ask
{
  "question": "What is the company's revenue?",
  "doc_id": "optional-uuid",    // omit to search all docs
  "top_k": 5
}
```

Response:
```json
{
  "answer": "Revenue was $120M (Page 14).",
  "sources": [
    { "source": "annual_report.pdf", "page": 14, "score": 0.92, "excerpt": "..." }
  ]
}
```

### Get summary
```
GET /api/v1/summary/{doc_id}
```

### List documents
```
GET /api/v1/documents
```

### Delete document
```
DELETE /api/v1/documents/{doc_id}
```

---

## Configuration

Edit `docker-compose.yml` environment section to tune:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | `phi3` | Ollama LLM model name |
| `EMBED_MODEL` | `nomic-embed-text` | Embedding model |
| `CHUNK_SIZE` | `512` | Words per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between chunks |
| `MAX_FILE_SIZE_MB` | `50` | Upload size limit |

### GPU acceleration (NVIDIA)

Uncomment the `deploy.resources` block in `docker-compose.yml` under the `ollama` service.

---

## File Structure

```
secure-doc-rag/
├── docker-compose.yml
├── scripts/
│   └── setup.sh              # First-run setup
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py               # FastAPI app + lifespan
│   ├── core/
│   │   ├── config.py         # Settings from env
│   │   ├── loaders.py        # PDF/DOCX/TXT extraction
│   │   ├── chunker.py        # Sliding-window chunker
│   │   ├── ollama_client.py  # Embed + generate
│   │   ├── vector_store.py   # Qdrant operations
│   │   └── rag.py            # RAG pipeline
│   ├── api/
│   │   └── routes.py         # All HTTP endpoints
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   └── utils/
│       └── registry.py       # Document metadata store
└── frontend/
    ├── Dockerfile
    ├── requirements.txt
    └── app.py                # Streamlit UI
```

---

## Security Notes

- All model inference runs inside Docker containers on your machine
- Uploaded files are stored in a Docker volume (`uploads_data`)
- No telemetry, no external API calls, no data leaves your infrastructure
- For production: add authentication middleware to FastAPI, restrict CORS, and use HTTPS
