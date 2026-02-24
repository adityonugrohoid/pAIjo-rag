from enum import Enum

from pydantic_settings import BaseSettings


class EmbeddingProvider(str, Enum):
    local = "local"
    openai = "openai"


class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "paijo_knowledge"

    embedding_provider: EmbeddingProvider = EmbeddingProvider.local
    local_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    openai_api_key: str = ""

    top_k: int = 3
    score_threshold: float = 0.2

    knowledge_dir: str = "rag-knowledge"
    chunk_size: int = 512
    chunk_overlap: int = 50

    host: str = "0.0.0.0"
    port: int = 8100

    @property
    def vector_size(self) -> int:
        return 384 if self.embedding_provider == EmbeddingProvider.local else 1536

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
