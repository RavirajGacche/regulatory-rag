# ADR 0005: Shared tables with tenant_id for multi-tenancy

- **Status:** Accepted
- **Date:** 2026-09-22

## Context
500 tenants must be isolated from each other. Schema migrations must stay manageable.

## Decision
Shared tables with a `NOT NULL tenant_id` column. Every index is composite and leads
with `tenant_id`. Filtering is applied in the repository layer, never by callers.

## Consequences
- One schema, one migration run, efficient connection pooling.
- A missing filter is a data breach, so the repository layer is the only place that
  queries tenant-owned tables, and tests assert cross-tenant isolation.
- Postgres Row-Level Security remains available as a database-enforced backstop.

## Alternatives considered
- **Database per tenant:** strongest isolation, unmanageable at 500 tenants.
- **Schema per tenant:** middle ground, but migrations run 500 times.