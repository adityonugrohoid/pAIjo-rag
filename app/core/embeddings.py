"""Dual embedding backend: local sentence-transformers and OpenAI."""

from abc import ABC, abstractmethod


class EmbeddingBackend(ABC):
    """Abstract base class for embedding backends."""

    @abstractmethod
    def encode(self, texts: list[str]) -> list[list[float]]:
        """Encode a batch of texts into embedding vectors."""
        ...

    @abstractmethod
    def encode_single(self, text: str) -> list[float]:
        """Encode a single text into an embedding vector."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimensionality of the embedding vectors."""
        ...


class LocalEmbeddingBackend(EmbeddingBackend):
    """Sentence-transformers MiniLM backend (384 dimensions)."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        print(f"Loading local embedding model: {model_name}")
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, show_progress_bar=False).tolist()

    def encode_single(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()

    @property
    def dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()


class OpenAIEmbeddingBackend(EmbeddingBackend):
    """OpenAI text-embedding backend (1536 dimensions)."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        from openai import OpenAI

        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when using openai provider")
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def encode(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.embeddings.create(input=texts, model=self._model)
        return [item.embedding for item in resp.data]

    def encode_single(self, text: str) -> list[float]:
        resp = self._client.embeddings.create(input=[text], model=self._model)
        return resp.data[0].embedding

    @property
    def dimension(self) -> int:
        return 1536


def create_embedding_backend(provider: str, **kwargs) -> EmbeddingBackend:
    """Factory function to create the appropriate embedding backend.

    Args:
        provider: "local" or "openai".
        **kwargs: Backend-specific arguments (model_name, api_key).
    """
    if provider == "local":
        model_name = kwargs.get(
            "model_name", "paraphrase-multilingual-MiniLM-L12-v2"
        )
        return LocalEmbeddingBackend(model_name)
    elif provider == "openai":
        return OpenAIEmbeddingBackend(api_key=kwargs["api_key"])
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")
