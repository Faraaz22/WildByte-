"""Application settings and configuration."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AI Data Dictionary"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/data_dictionary"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_pre_ping: bool = True
    database_echo: bool = False

    # Redis (Celery broker)
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # AI/LLM
    ai_provider: Literal["openai", "ollama", "auto"] = "openai"
    openai_api_key: str = ""
    openai_model_complex: str = "gpt-4-turbo-preview"
    openai_model_simple: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-3-small"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b"

    # ChromaDB
    chromadb_path: str = "./data/chromadb"
    chromadb_collection_name: str = "table_embeddings"

    # Security
    encryption_key: str = ""  # Fernet encryption key for credentials
    jwt_secret_key: str = "dev-secret-change-in-production"  # JWT signing key
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit_per_minute: int = 60

    # Task Execution
    task_timeout_seconds: int = 300
    max_context_tables: int = 5
    max_query_result_rows: int = 1000
    query_timeout_seconds: int = 30

    # Performance
    max_workers: int = 4
    batch_size: int = 100


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
