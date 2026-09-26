# Regulatory RAG

Multi-tenant compliance intelligence platform. Ingests RBI circulars, extracts
structured obligations, and answers questions with citations back to the source
document.

## Why it exists
Compliance teams at NBFCs track hundreds of circulars. Finding "what does the current
rule say, and what did it say last June" is manual and error-prone.

## Personas
| Persona | Need | Design consequence |
|---|---|---|
| Compliance officer | Conversational Q&A across documents | Streamed RAG over multiple documents |
| Analyst | Extract obligations from one document | Static prompt, JSON output |
| Auditor | Point-in-time answers | Document versioning and validity ranges |

## Architecture
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for C4 and sequence diagrams.

FastAPI · PostgreSQL 16 + pgvector · MongoDB 7 · Redis 7 · Celery · Groq
(openai/gpt-oss-120b) · sentence-transformers all-MiniLM-L6-v2 · LangGraph

## Documentation
| Doc | Contents |
|---|---|
| [PRD](docs/PRD.md) | Requirements, personas, capacity estimation |
| [Architecture](docs/ARCHITECTURE.md) | C4 diagrams, service ownership, flows |
| [Data model](docs/DATA_MODEL.md) | ERD, tables, indexes, versioning |
| [API contract](docs/API_CONTRACT.md) | Endpoints, schemas, errors |
| [ADRs](docs/adr/) | Decision records |

## Running it
```bash
cp .env.example .env
docker compose up -d
uv sync
uv run python scripts/verify_setup.py
uv run uvicorn services.query.main:app --reload
```
Swagger: http://localhost:8000/docs

## Engineering notes
- **Cost-bound, not throughput-bound:** at ~8 QPS the constraint is token spend, so
  the design prioritises semantic caching, model routing and reranking to 5 chunks.
- **Idempotent ingestion:** skip by source_url, skip by sha256, upsert on
  content_hash, delete-then-insert chunks. A retried job creates no duplicates.
- **Tenant isolation** is enforced in the repository layer, never by callers.