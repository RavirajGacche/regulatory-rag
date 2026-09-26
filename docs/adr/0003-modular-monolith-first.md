# ADR 0003: Modular monolith before microservices

- **Status:** Accepted
- **Date:** 2026-09-22

## Context
The design has four clear service boundaries, but the team is one engineer and the
load is ~8 QPS.

## Decision
Ship one deployable application with strict module boundaries: services never import
each other, only `shared/`. Split into separate deployments later if load or team
size justifies it.

## Consequences
- No service discovery, distributed tracing or distributed transactions on day one.
- The boundary rule must be enforced in CI, or it will erode.
- The later split becomes a deployment change rather than a redesign.

## Alternatives considered
- **Microservices immediately:** correct end state, heavy accidental complexity now.
- **Unstructured monolith:** fastest to write, but the boundaries never appear later.