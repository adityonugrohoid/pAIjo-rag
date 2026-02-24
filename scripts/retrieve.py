#!/usr/bin/env python3
"""CLI retrieval tool for pAIjo RAG knowledge base."""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.embeddings import create_embedding_backend
from app.core.vectorstore import VectorStore


def main():
    parser = argparse.ArgumentParser(
        description="Query the pAIjo RAG knowledge base"
    )
    parser.add_argument("query", help="Search query text")
    parser.add_argument(
        "--top-k", type=int, default=settings.top_k, help="Number of results"
    )
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument(
        "--threshold",
        type=float,
        default=settings.score_threshold,
        help="Minimum score threshold",
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    # Initialize embedding backend
    backend = create_embedding_backend(
        provider=settings.embedding_provider.value,
        model_name=settings.local_model_name,
        api_key=settings.openai_api_key,
    )

    # Connect to Qdrant
    store = VectorStore()
    store.connect(settings.qdrant_url, settings.qdrant_collection)

    # Search
    query_vector = backend.encode_single(args.query)
    results = store.search(
        query_vector=query_vector,
        limit=args.top_k,
        category=args.category,
        score_threshold=args.threshold,
    )

    if args.json:
        print(json.dumps({"query": args.query, "count": len(results), "results": results}, ensure_ascii=False, indent=2))
        return

    print(f'\nQuery: "{args.query}"')
    print(f"Results: {len(results)}\n")

    for i, r in enumerate(results, 1):
        print(f"--- [{i}] score: {r['score']} ---")
        print(f"Title:    {r['title']}")
        print(f"Source:   {r['source']}")
        print(f"Category: {r['category']}")
        print(f"Text:     {r['text'][:300]}{'...' if len(r['text']) > 300 else ''}")
        print()


if __name__ == "__main__":
    main()
