from typing import Optional

from pydantic import BaseModel


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 3
    category: Optional[str] = None


class RetrieveResult(BaseModel):
    text: str
    title: str
    source: str
    category: str
    score: float


class RetrieveResponse(BaseModel):
    query: str
    count: int
    results: list[RetrieveResult]


class IngestRequest(BaseModel):
    path: Optional[str] = None


class IngestResponse(BaseModel):
    ingested: int
    errors: list[dict]


class HealthResponse(BaseModel):
    status: str
    collection: str
    points: int
