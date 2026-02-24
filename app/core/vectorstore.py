"""Qdrant vector database client wrapper."""

import hashlib

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)


class VectorStore:
    """Wrapper around the Qdrant client for pAIjo RAG operations."""

    def __init__(self):
        self._client: QdrantClient | None = None
        self._collection: str = ""

    def connect(self, url: str, collection: str):
        """Connect to Qdrant and set the target collection."""
        self._client = QdrantClient(url=url, timeout=60)
        self._collection = collection

    def ensure_collection(self, vector_size: int):
        """Create collection if missing, or validate dimension if it exists."""
        collections = [c.name for c in self._client.get_collections().collections]
        if self._collection not in collections:
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(
                    size=vector_size, distance=Distance.COSINE
                ),
            )
            print(f"Created collection: {self._collection} (dim={vector_size})")
        else:
            info = self._client.get_collection(self._collection)
            existing_size = info.config.params.vectors.size
            if existing_size != vector_size:
                raise ValueError(
                    f"Collection '{self._collection}' has vector size {existing_size}, "
                    f"but embedding backend produces {vector_size}. "
                    f"Delete the collection or switch embedding providers."
                )
            print(f"Collection exists: {self._collection} (dim={existing_size})")

    def search(
        self,
        query_vector: list[float],
        limit: int,
        category: str | None = None,
        score_threshold: float = 0.0,
    ) -> list[dict]:
        """Search for similar vectors, optionally filtered by category."""
        query_filter = None
        if category:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="category", match=MatchValue(value=category)
                    )
                ]
            )

        resp = self._client.query_points(
            collection_name=self._collection,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )

        results = []
        for point in resp.points:
            if point.score >= score_threshold:
                results.append(
                    {
                        "text": point.payload.get("text", ""),
                        "title": point.payload.get("title", ""),
                        "source": point.payload.get("source", ""),
                        "category": point.payload.get("category", ""),
                        "score": round(point.score, 4),
                    }
                )
        return results

    def upsert_chunks(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict,
        filepath: str,
    ) -> int:
        """Batch upsert chunks with MD5-based deterministic IDs."""
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc_id = hashlib.md5(
                f"{filepath}:{i}:{chunk[:100]}".encode()
            ).hexdigest()
            point_id = int(doc_id[:16], 16) % (2**63)
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "title": metadata.get("title", ""),
                        "source": metadata.get("source", ""),
                        "category": metadata.get("category", ""),
                        "chunk_index": i,
                        "file": filepath,
                    },
                )
            )
        if points:
            self._client.upsert(collection_name=self._collection, points=points)
        return len(points)

    def get_collection_info(self) -> dict:
        """Get collection stats for health check."""
        info = self._client.get_collection(self._collection)
        return {"points": info.points_count, "collection": self._collection}
