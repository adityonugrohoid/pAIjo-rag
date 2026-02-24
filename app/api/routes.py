"""API route handlers: /healthz, /retrieve, /ingest."""

import glob
import os
from pathlib import Path

from fastapi import APIRouter

import app.state
from app.config import settings
from app.core.chunker import chunk_text
from app.core.parser import parse_file
from app.models import (
    HealthResponse,
    IngestRequest,
    IngestResponse,
    RetrieveRequest,
    RetrieveResponse,
    RetrieveResult,
)

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
async def healthz():
    info = app.state.vector_store.get_collection_info()
    return HealthResponse(status="ok", **info)


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(req: RetrieveRequest):
    query_vector = app.state.embedding_backend.encode_single(req.query)
    results = app.state.vector_store.search(
        query_vector=query_vector,
        limit=req.top_k,
        category=req.category,
        score_threshold=settings.score_threshold,
    )
    return RetrieveResponse(
        query=req.query,
        count=len(results),
        results=[RetrieveResult(**r) for r in results],
    )


@router.post("/ingest", response_model=IngestResponse)
async def ingest(req: IngestRequest):
    ingested = 0
    errors = []

    if req.path:
        files = [req.path]
    else:
        files = glob.glob(
            os.path.join(settings.knowledge_dir, "**/*"), recursive=True
        )
        files = [f for f in files if Path(f).suffix in (".json", ".md", ".txt")]

    for filepath in files:
        try:
            docs = parse_file(filepath)
            for doc in docs:
                chunks = chunk_text(doc["text"])
                if not chunks:
                    continue
                embeddings = app.state.embedding_backend.encode(chunks)
                count = app.state.vector_store.upsert_chunks(
                    chunks=chunks,
                    embeddings=embeddings,
                    metadata=doc,
                    filepath=filepath,
                )
                ingested += count
        except Exception as e:
            errors.append({"file": filepath, "error": str(e)})

    return IngestResponse(ingested=ingested, errors=errors)
