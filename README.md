<div align="center">

# pAIjo RAG — Islamic Knowledge Retrieval System

**A Retrieval-Augmented Generation (RAG) pipeline for an Islamic knowledge assistant serving the Indonesian Muslim community**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-red.svg)](https://qdrant.tech)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Built in collaboration with [Ainun Najib](https://github.com/ainunnajib) as part of the pAIjo WhatsApp Muslim Assistant project*

</div>

---

## Overview

**pAIjo RAG** is the retrieval-augmented generation component of [pAIjo](https://github.com/ainunnajib), a WhatsApp-based Islamic knowledge assistant designed for the Indonesian Muslim community.

The RAG system enables pAIjo to:
- **Retrieve verified Islamic knowledge** from a curated vector database
- **Ground LLM responses** in authentic Islamic sources to prevent hallucination
- **Serve real-time queries** on Islamic jurisprudence (fiqih), worship practices, and religious guidance
- **Scale to concurrent users** with sub-100ms retrieval latency

### Why RAG for Islamic Knowledge?

Fabricating or misattributing Islamic quotes is a **critical failure mode** for any AI system. By implementing RAG, we ensure that every response is grounded in verified, curated content from trusted Islamic scholars and authenticated sources — not generated from potentially unreliable training data.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   User Query    │────▶│   FastAPI Server  │────▶│  Embedding Backend  │
│  (WhatsApp/     │     │   (Port 8100)     │     │  (Local MiniLM or   │
│   Telegram)     │     └────────┬─────────┘     │   OpenAI)           │
└─────────────────┘              │                └────────┬────────────┘
                                 │    ┌────────────────────┘
                                 ▼    ▼
                        ┌──────────────────┐
                        │     Qdrant       │
                        │   Vector DB      │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  Ranked Results  │
                        │  + Source Cites   │
                        └──────────────────┘
```

### Data Flow

1. **Ingestion Pipeline** — Islamic knowledge documents (JSON/Markdown) are chunked, embedded, and stored in Qdrant
2. **Query Pipeline** — User questions are embedded and matched against the vector store using cosine similarity
3. **Response Pipeline** — Retrieved chunks with scores and source attribution are returned to the caller

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI (Python) | High-performance async REST API |
| **Vector Database** | Qdrant | Similarity search & vector storage |
| **Embeddings (default)** | sentence-transformers MiniLM | Local multilingual embeddings (384 dims) |
| **Embeddings (optional)** | OpenAI text-embedding-3-small | Cloud embeddings (1536 dims) |
| **Configuration** | Pydantic Settings | Type-safe env var configuration |

---

## API Endpoints

### `GET /healthz`
Health check endpoint for monitoring and load balancer integration.

```bash
curl http://localhost:8100/healthz
```

**Response:**
```json
{
  "status": "ok",
  "collection": "paijo_knowledge",
  "points": 68
}
```

### `POST /ingest`
Ingest knowledge files from the knowledge directory into the vector database.

```bash
# Ingest all files
curl -X POST http://localhost:8100/ingest \
  -H "Content-Type: application/json" \
  -d '{}'

# Ingest a specific file
curl -X POST http://localhost:8100/ingest \
  -H "Content-Type: application/json" \
  -d '{"path": "rag-knowledge/ramadan-01.md"}'
```

### `POST /retrieve`
Retrieve relevant knowledge chunks for a given query.

```bash
curl -X POST http://localhost:8100/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "Apa itu tahlilan?", "top_k": 3}'
```

**Response:**
```json
{
  "query": "Apa itu tahlilan?",
  "count": 3,
  "results": [
    {
      "text": "Tahlilan adalah tradisi membaca doa...",
      "title": "Tahlilan dan Kirim Doa untuk Mayit",
      "source": "Bahtsul Masail NU",
      "category": "fiqih",
      "score": 0.3042
    }
  ]
}
```

---

## Knowledge Base

The RAG system contains curated knowledge chunks across multiple Islamic domains:

| Category | Files | Topics |
|----------|-------|--------|
| **NU Islamic Traditions** | 24 | Tahlilan, Qunut, Maulid Nabi, Tawassul, Istighatsah, Hizib, Sholawat, Yasin |
| **Ramadan Guidance** | 12 | Prayer times, fiqih puasa, tarawih, sahur/iftar, zakat fitrah |
| **Fiqih & Ibadah** | 3 JSON | Wudhu, shalat, puasa, zakat, istilah dasar, fatwa |
| **Other** | 2 | Sample fatwa Muhammadiyah, verification test |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (for Qdrant)

### Installation

```bash
# Clone the repository
git clone https://github.com/adityonugrohoid/pAIjo-rag.git
cd pAIjo-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env if needed (defaults work for local setup)
```

### Start Qdrant

```bash
docker compose up -d
```

### Run the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8100
```

### Quick Test

```bash
# Health check
curl http://localhost:8100/healthz

# Ingest all knowledge files
curl -X POST http://localhost:8100/ingest \
  -H "Content-Type: application/json" -d '{}'

# Test retrieval
curl -X POST http://localhost:8100/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "apa itu tahlilan?", "top_k": 3}'
```

### CLI Ingestion

```bash
# Ingest all knowledge files
python scripts/ingest.py

# Ingest a specific file
python scripts/ingest.py --path rag-knowledge/ramadan-01.md
```

### Embedding Providers

By default, pAIjo RAG uses **local sentence-transformers** (no API key required). To switch to OpenAI:

```bash
# In .env
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

> **Note:** Switching providers changes the vector dimension (384 vs 1536). You must recreate the Qdrant collection when switching.

---

## Project Structure

```
pAIjo-rag/
├── app/
│   ├── main.py           # FastAPI app, lifespan, singletons
│   ├── config.py          # Pydantic Settings configuration
│   ├── models.py          # Request/response Pydantic models
│   ├── state.py           # Module-level singletons
│   ├── api/
│   │   └── routes.py      # /healthz, /retrieve, /ingest handlers
│   └── core/
│       ├── parser.py      # JSON/Markdown file parsing
│       ├── chunker.py     # Word-based text chunking with overlap
│       ├── embeddings.py  # Dual backend: local MiniLM + OpenAI
│       └── vectorstore.py # Qdrant client wrapper
├── scripts/
│   └── ingest.py          # CLI ingestion tool
├── rag-knowledge/         # Curated Islamic knowledge base
├── docker-compose.yml     # Qdrant service
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Project Context

### pAIjo — WhatsApp Muslim Assistant

pAIjo is a larger initiative to build an accessible, trustworthy Islamic knowledge assistant for Indonesian Muslims via WhatsApp — the most widely used messaging platform in Indonesia (200M+ users).

The RAG system is the **knowledge backbone** that ensures pAIjo's responses are grounded in verified Islamic scholarship rather than LLM hallucination — a critical requirement for religious content.

---

## Collaboration

This project was built in collaboration with **[Ainun Najib](https://github.com/ainunnajib)**, an Indonesian data platform & civic tech leader based in Singapore, who leads the pAIjo initiative.

**Roles:**
- **Ainun Najib** — Project lead, architecture design, AI/ML strategy, knowledge curation, infrastructure
- **Adityo Nugroho** — RAG implementation, FastAPI development, Qdrant integration, API design, testing, end-to-end verification

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built for the Muslim community**

</div>
