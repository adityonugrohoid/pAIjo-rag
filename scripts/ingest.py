#!/usr/bin/env python3
"""CLI ingestion tool for pAIjo RAG knowledge base."""

import argparse
import glob
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.chunker import chunk_text
from app.core.embeddings import create_embedding_backend
from app.core.parser import parse_file
from app.core.vectorstore import VectorStore


def main():
    parser = argparse.ArgumentParser(
        description="Ingest knowledge files into Qdrant"
    )
    parser.add_argument(
        "--path", help="Specific file to ingest (default: all files in knowledge dir)"
    )
    parser.add_argument(
        "--knowledge-dir",
        default=settings.knowledge_dir,
        help="Knowledge directory",
    )
    args = parser.parse_args()

    # Initialize embedding backend
    print(f"Embedding provider: {settings.embedding_provider.value}")
    backend = create_embedding_backend(
        provider=settings.embedding_provider.value,
        model_name=settings.local_model_name,
        api_key=settings.openai_api_key,
    )
    print(f"Embedding backend ready (dim={backend.dimension})")

    # Connect to Qdrant
    store = VectorStore()
    store.connect(settings.qdrant_url, settings.qdrant_collection)
    store.ensure_collection(backend.dimension)
    print(f"Qdrant connected: {settings.qdrant_url} / {settings.qdrant_collection}\n")

    # Collect files
    if args.path:
        files = [args.path]
    else:
        files = glob.glob(
            os.path.join(args.knowledge_dir, "**/*"), recursive=True
        )
        files = [f for f in files if Path(f).suffix in (".json", ".md", ".txt")]

    ingested = 0
    errors = []

    for filepath in sorted(files):
        try:
            docs = parse_file(filepath)
            for doc in docs:
                chunks = chunk_text(doc["text"])
                if not chunks:
                    continue
                embeddings = backend.encode(chunks)
                count = store.upsert_chunks(
                    chunks=chunks,
                    embeddings=embeddings,
                    metadata=doc,
                    filepath=filepath,
                )
                ingested += count
                print(f"  {Path(filepath).name}: {count} chunks ingested")
        except Exception as e:
            errors.append({"file": filepath, "error": str(e)})
            print(f"  ERROR {Path(filepath).name}: {e}")

    print(f"\nDone: {ingested} chunks ingested, {len(errors)} errors")
    if errors:
        for err in errors:
            print(f"  - {err['file']}: {err['error']}")


if __name__ == "__main__":
    main()
