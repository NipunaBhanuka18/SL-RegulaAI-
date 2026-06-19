from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Groq LLM
    groq_api_key: str
    groq_model: str = "llama3-8b-8192"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # ChromaDB
    chroma_persist_dir: str = "./data/vectorstore"
    chroma_collection_name: str = "sl_compliance_gazettes"

    # Ingestion
    gazette_pdf_dir: str = "./data/gazettes"
    chunk_size: int = 800
    chunk_overlap: int = 150

    # Pipeline
    max_retrieval_retries: int = 3
    retrieval_top_k: int = 5

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings — loaded once at startup."""
    return Settings()
