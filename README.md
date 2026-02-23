<div align="center">

# 🕌 pAIjo RAG — Islamic Knowledge Retrieval System

**A Retrieval-Augmented Generation (RAG) pipeline for an Islamic knowledge assistant serving the Nahdlatul Ulama (NU) community**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-red.svg)](https://qdrant.tech)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Built in collaboration with [Ainun Najib](https://github.com/ainunnajib) as part of the pAIjo WhatsApp Muslim Assistant project*

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [API Endpoints](#api-endpoints)
- [Knowledge Base](#knowledge-base)
- [Performance](#performance)
- [Testing & Verification](#testing--verification)
- [Getting Started](#getting-started)
- [Project Context](#project-context)
- [Collaboration](#collaboration)
- [License](#license)

---

## 🔍 Overview

**pAIjo RAG** is the retrieval-augmented generation component of [pAIjo](https://github.com/ainunnajib), a WhatsApp-based Islamic knowledge assistant designed for the Indonesian Muslim community, specifically aligned with the **Nahdlatul Ulama (NU)** tradition — the largest Islamic organization in the world with over 90 million members.

The RAG system enables pAIjo to:
- **Retrieve verified Islamic knowledge** from a curated vector database
- **Ground LLM responses** in authentic NU-tradition sources to prevent hallucination
- **Serve real-time queries** on Islamic jurisprudence (fiqih), worship practices, and religious guidance
- **Scale to concurrent users** with sub-100ms retrieval latency

### Why RAG for Islamic Knowledge?

Fabricating or misattributing Islamic quotes is a **critical failure mode** for any AI system. By implementing RAG, we ensure that every response is grounded in verified, curated content from trusted NU scholars and authenticated Islamic sources — not generated from potentially unreliable training data.

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User Query    │────▶│   FastAPI Server  │────▶│  OpenAI Embeddings│
│  (WhatsApp/     │     │   (Port 8100)     │     │  (text-embedding) │
│   Telegram)     │     └────────┬─────────┘     └────────┬────────┘
└─────────────────┘              │                         │
                                 │    ┌────────────────────┘
                                 ▼    ▼
                        ┌──────────────────┐
                        │     Qdrant       │
                        │   Vector DB      │
                        │  (68 chunks)     │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  Ranked Results  │
                        │  + Source Cites   │
                        └──────────────────┘
```

### Data Flow

1. **Ingestion Pipeline** — Islamic knowledge documents (Markdown) are chunked, embedded via OpenAI, and stored in Qdrant
2. **Query Pipeline** — User questions are embedded and matched against the vector store using cosine similarity
3. **Response Pipeline** — Retrieved chunks are passed as context to the LLM, ensuring grounded, cited responses

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI (Python) | High-performance async REST API |
| **Vector Database** | Qdrant | Similarity search & vector storage |
| **Embeddings** | OpenAI text-embedding | Semantic vectorization of knowledge chunks |
| **Deployment** | Cloud VM (Dalang) | Production hosting with persistent storage |
| **Integration** | WhatsApp & Telegram | End-user messaging platforms |

---

## 🔌 API Endpoints

### `GET /healthz`
Health check endpoint for monitoring and load balancer integration.

```bash
curl http://localhost:8100/healthz
```

**Response:**
```json
{
  "status": "healthy",
  "qdrant": "connected",
  "chunks": 68
}
```

### `POST /ingest`
Ingest new knowledge documents into the vector database.

```bash
curl -X POST http://localhost:8100/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Tahlilan adalah tradisi membaca doa dan surat-surat Al-Quran...",
    "metadata": {
      "topic": "tahlilan",
      "source": "NU Online",
      "category": "fiqih"
    }
  }'
```

### `POST /retrieve`
Retrieve relevant knowledge chunks for a given query.

```bash
curl -X POST http://localhost:8100/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Apa itu tahlilan?",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "results": [
    {
      "text": "Tahlilan adalah tradisi membaca doa...",
      "score": 0.30,
      "metadata": {
        "topic": "tahlilan",
        "source": "NU Online"
      }
    }
  ]
}
```

---

## 📚 Knowledge Base

The RAG system currently contains **68 curated knowledge chunks** across multiple Islamic domains:

| Category | Chunks | Topics |
|----------|--------|--------|
| **NU Fiqih & Traditions** | 24 | Tahlilan, Qunut, Maulid Nabi, Ziarah, Istighotsah, Hizib, Ratib, and more |
| **Ramadan Guidance** | 12 | Prayer times, fiqih puasa, tarawih, sahur/iftar, zakat fitrah |
| **General Islamic Q&A** | 32 | Foundational Islamic knowledge, ibadah, muamalah |

### Knowledge Domains
- **Tahlilan** — NU tradition of collective prayer and Quran recitation
- **Tarawih** — Ramadan night prayers (20 rakaat NU tradition)
- **Puasa (Fasting)** — Rules, invalidators, and spiritual dimensions
- **Zakat** — Obligatory charity calculations and distribution
- **Sholat** — Daily prayer guidance and jurisprudence
- **NU-specific practices** — Qunut, Maulid, Hizib, Ratib Al-Haddad

---

## ⚡ Performance

Benchmarked under realistic production conditions:

| Metric | Result |
|--------|--------|
| **Average query latency** | ~100ms |
| **Concurrent connections** | 25 simultaneous (stable) |
| **Retrieval accuracy** | Verified across all 68 chunks |
| **Uptime** | Continuous operation since Feb 2026 |

### Retrieval Quality Scores (Sample)
| Query | Top Score | Relevant |
|-------|-----------|----------|
| "Apa itu tahlilan?" | 0.30 | ✅ |
| "Sholat tarawih berapa rakaat?" | 0.34 | ✅ |

---

## ✅ Testing & Verification

### The "Undid Iridium" Test

End-to-end verification was performed via Telegram integration, codenamed **"Undid Iridium"**:

1. **Ingestion verification** — All 68 chunks successfully embedded and stored in Qdrant
2. **Retrieval verification** — Queries returned semantically relevant results with correct source attribution
3. **Integration verification** — Full pipeline tested from Telegram message → FastAPI → Qdrant → Response delivery
4. **Stress testing** — 25 concurrent connections maintained stable ~100ms response times
5. **Content accuracy** — Retrieved content verified against original NU scholarly sources

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Qdrant (local or cloud instance)
- OpenAI API key (for embeddings)

### Installation

```bash
# Clone the repository
git clone https://github.com/adityonugrohoid/pAIjo-rag.git
cd pAIjo-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key"
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8100
```

### Quick Test

```bash
# Health check
curl http://localhost:8100/healthz

# Test retrieval
curl -X POST http://localhost:8100/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "apa itu tahlilan?", "top_k": 3}'
```

---

## 🌍 Project Context

### pAIjo — WhatsApp Muslim Assistant

pAIjo is a larger initiative to build an accessible, trustworthy Islamic knowledge assistant for Indonesian Muslims via WhatsApp — the most widely used messaging platform in Indonesia (200M+ users).

**Brand tiers:**
- **pAIjo** — Free community tier (NU-focused Islamic Q&A)
- **santAI** — Premium tier with advanced features
- **pandAI** — Enterprise/institutional tier

The RAG system is the **knowledge backbone** that ensures pAIjo's responses are grounded in verified Islamic scholarship rather than LLM hallucination — a critical requirement for religious content.

### Nahdlatul Ulama (NU)

[Nahdlatul Ulama](https://www.nu.or.id/) is the world's largest Islamic organization (~90 million members), headquartered in Indonesia. NU follows the Sunni tradition with the Shafi'i school of jurisprudence and is known for its moderate, tolerant approach to Islam (*Islam Nusantara*).

---

## 🤝 Collaboration

This project was built in collaboration with **[Ainun Najib](https://github.com/ainunnajib)**, an AI engineer based in Singapore who leads the pAIjo initiative.

**Roles:**
- **Ainun Najib** — Project lead, architecture design, AI/ML strategy, knowledge curation, infrastructure (Dalang cloud VM)
- **Adityo Nugroho** — RAG implementation, FastAPI development, Qdrant integration, API design, stress testing, end-to-end verification

### Key Contributions (Adityo Nugroho)
- Designed and implemented the FastAPI-based RAG service
- Configured and optimized Qdrant vector database for Islamic knowledge retrieval
- Built ingestion pipeline for converting Islamic scholarly content into embeddings
- Conducted stress testing (25 concurrent connections, ~100ms latency)
- Performed end-to-end verification ("Undid Iridium" test) via Telegram integration
- Compiled 60-70 NU topic questions for knowledge base expansion

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for the Muslim community**

*بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ*

</div>
