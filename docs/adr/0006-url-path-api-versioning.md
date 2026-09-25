# ADR 0006: URL path versioning and a single error envelope

- **Status:** Accepted
- **Date:** 2026-09-22

## Context
Clients need a stable contract and a predictable way to handle failures.

## Decision
Version in the URL path (`/v1/...`), bumped only for breaking changes. Every error
returns `{error: {code, message, details, request_id}}`.

## Consequences
- Versions are obvious in logs, routing and caching.
- Clients branch on a stable `code`, never on message text.
- `request_id` ties a user-visible failure to a trace in the logs.

## Alternatives considered
- **Header versioning:** cleaner URLs, harder to test and debug.
- **Per-endpoint error shapes:** every client writes bespoke handling.