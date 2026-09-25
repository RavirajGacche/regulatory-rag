# ADR 0001: MongoDB as the raw landing zone

- **Status:** Accepted
- **Date:** 2026-09-22

## Context
Scraped RBI pages have inconsistent structure that changes without notice. Parsing
errors are discovered late, and re-scraping is slow, rate-limited and may be impossible
if the source page has since changed.

## Decision
Store every fetched artefact verbatim in MongoDB `raw_documents` before parsing.
Postgres holds only the cleaned, typed, validated result.

## Consequences
- A parser bug is fixed by re-parsing from Mongo, with no network access to RBI.
- Full audit trail of exactly what the regulator published, which matters in a regulated domain.
- Cost: two datastores to operate and back up.

## Alternatives considered
- **Postgres JSONB only:** one datastore, but mixes immutable raw data with the
  transactional model and loses the separation of concerns.
- **Files on disk / S3:** cheap, but no queryable metadata and no unique index for deduplication.