from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Google API Configuration
    google_api_key: str = ""

    # Vector Database
    vector_db_type: str = "chroma"
    vector_db_path: str = "./data/chroma_db"

    # Document Storage
    upload_dir: str = "./data/uploads"

    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    use_local_embeddings: bool = True

    # LLM Configuration (Google Gemini)
    llm_model: str = "models/gemma-3-1b-it"
    llm_temperature: float = 0.1
    max_tokens: int = 2000

    # Retrieval Configuration
    top_k_chunks: int = 7
    chunk_size: int = 512
    chunk_overlap: int = 128

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()

# Create necessary directories
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.vector_db_path, exist_ok=True)
os.makedirs("./data/logs", exist_ok=True)
