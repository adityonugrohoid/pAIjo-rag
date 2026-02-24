"""FastAPI application with lifespan-managed singletons."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import state as app_state
from app.config import settings
from app.core.embeddings import create_embedding_backend
from app.core.vectorstore import VectorStore


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    print(f"Embedding provider: {settings.embedding_provider.value}")
    app_state.embedding_backend = create_embedding_backend(
        provider=settings.embedding_provider.value,
        model_name=settings.local_model_name,
        api_key=settings.openai_api_key,
    )
    print(f"Embedding backend ready (dim={app_state.embedding_backend.dimension})")

    app_state.vector_store = VectorStore()
    app_state.vector_store.connect(settings.qdrant_url, settings.qdrant_collection)
    app_state.vector_store.ensure_collection(app_state.embedding_backend.dimension)
    print(f"Qdrant connected: {settings.qdrant_url} / {settings.qdrant_collection}")

    yield

    # Shutdown
    app_state.embedding_backend = None
    app_state.vector_store = None


app = FastAPI(title="pAIjo RAG Server", version="1.0.0", lifespan=lifespan)

from app.api.routes import router  # noqa: E402

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port)
