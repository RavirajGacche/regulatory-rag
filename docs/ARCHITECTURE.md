# Architecture

## 1. Context (C4 L1)

<!-- ```mermaid
graph LR
    CO[Compliance Officer] --> SYS
    AN[Analyst] --> SYS
    AU[Auditor] --> SYS
    SYS[Regulatory RAG Platform]
    SYS --> RBI[RBI Website]
    SYS --> GROQ[Groq LLM API]
``` -->

'''mermaid
graph LR
    CO[Compliance Officer] --> SYS
    AN[Analyst] --> SYS
    AU[Auditor] --> SYS
    SYS[Regulatory RAG Platform]
    SYS --> RBI[RBI website]
    SYS --> GROQ[Groq LLM API]
'''

## 2. Containers (C4 L2)

```mermaid
graph TD
    CLIENT[API Client] --> GW[Nginx Gateway]
    GW --> AUTH[Auth Service]
    GW --> DOC[Document Service]
    GW --> QRY[Query Service]

    DOC --> MONGO[(MongoDB raw_documents)]
    DOC --> PG[(PostgreSQL + pgvector)]
    DOC -- document.ready --> BUS[[Celery / Redis]]
    BUS --> IDX[Indexing Worker]
    IDX --> PG

    AUTH --> PG
    QRY --> PG
    QRY --> REDIS[(Redis cache)]
    QRY --> LLM[Groq API]
```

## 3. Service ownership — one writer per table

| Service | Owns (writes) | Reads |
|---|---|---|
| Auth | users, tenants, roles, refresh_tokens | — |
| Document | Mongo raw_documents, PG documents | — |
| Indexing | chunks (incl. embeddings) | documents |
| Query | conversations, messages, semantic cache | documents, chunks |

## 4. Data boundary

**Mongo = what we received. Postgres = what we know.**

| Mongo `raw_documents` | Postgres |
|---|---|
| Raw HTML / PDF bytes, as received | Typed, validated, constrained |
| Schema drifts freely | Strict schema |
| Immutable audit trail | Transactional, versioned |

A parser bug means a re-parse from Mongo, not a re-scrape of RBI.

## 5. Ingestion flow

```mermaid
sequenceDiagram
    participant S as Scraper
    participant M as MongoDB
    participant P as PostgreSQL
    participant B as Celery
    participant I as Indexing
    S->>S: fetch list page (1 req/sec)
    S->>M: store raw (skip if sha256 seen)
    S->>S: extract text (OCR fallback)
    S->>P: upsert on content_hash
    S->>B: emit document.ready
    B->>I: deliver event
    I->>I: chunk + embed
    I->>P: delete-then-insert chunks
```

## 6. Query flow

```mermaid
sequenceDiagram
    participant U as User
    participant Q as Query Service
    participant R as Redis
    participant P as PostgreSQL
    participant L as Groq
    U->>Q: POST /v1/query
    Q->>R: semantic cache lookup
    alt cache hit
        R-->>U: cached answer
    else miss
        Q->>Q: embed question
        Q->>P: vector search (filtered by tenant_id)
        Q->>Q: rerank to top 5
        Q->>L: prompt + context
        L-->>U: streamed answer + citations
        Q->>R: store in cache
    end
```

## 7. Non-functional targets

| Attribute | Target |
|---|---|
| p95 latency | < 3 s; first token < 1 s |
| Scale | 500 tenants, 10K DAU, ~8 QPS peak |
| Storage | 4M chunks ≈ 19 GB → pgvector sufficient |
| Availability | 99.9% reads |
| Constraint | Cost-bound, not throughput-bound |