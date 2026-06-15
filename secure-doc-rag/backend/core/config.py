from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "documents"

    # Ollama
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    llm_model: str = "phi3"
    embed_model: str = "nomic-embed-text"

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Storage
    upload_dir: str = "/app/uploads"

    # Embedding dimension for nomic-embed-text
    embed_dim: int = 768

    class Config:
        env_file = ".env"


settings = Settings()
