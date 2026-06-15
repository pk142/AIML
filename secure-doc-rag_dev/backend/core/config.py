from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "documents"

    # Ollama (used only when dev_mode=False)
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    llm_model: str = "phi3"
    embed_model: str = "nomic-embed-text"

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Storage
    upload_dir: str = "./uploads"

    # nomic-embed-text  → 768 dims
    # all-MiniLM-L6-v2  → 384 dims  (dev mode)
    embed_dim: int = 384

    # ── Dev / Mock mode ────────────────────────────────────────────────────
    # DEV_MODE=true  → sentence-transformers + in-memory Qdrant (< 500 MB RAM)
    # DEV_MODE=false → real Ollama + Docker Qdrant (needs 8 GB)
    dev_mode: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
