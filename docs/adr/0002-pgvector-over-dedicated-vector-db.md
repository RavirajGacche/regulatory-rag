# ADR 0002: pgvector instead of a dedicated vector database

- **Status:** Accepted
- **Date:** 2026-09-22

## Context
4M chunks x 384 dims x 4 bytes is roughly 6 GB of vectors, about 19 GB with text and
metadata. Every query must be filtered by `tenant_id`.

## Decision
Use pgvector inside the existing PostgreSQL instance with an HNSW index.

## Consequences
- Metadata filtering and vector search happen in one query, with no cross-system join.
- One datastore to operate, back up and transact against.
- Revisit around ~20M vectors, where a dedicated engine starts to win.

## Alternatives considered
- **Qdrant / Weaviate:** better at very large scale, but adds a service, a second
  consistency boundary and a sync problem for tenant metadata.