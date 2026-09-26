# ADR 0004: Celery for background work, not Airflow

- **Status:** Accepted
- **Date:** 2026-09-22

## Context
Ingestion is triggered by user uploads and must start immediately. One job (the daily
RBI scrape) is genuinely scheduled.

## Decision
Celery with a Redis broker for event-driven tasks, Celery Beat for the nightly scrape.

## Consequences
- Sub-second task dispatch; no scheduler polling delay on the user-facing path.
- Small footprint (~200 MB) versus an Airflow deployment (scheduler, webserver, its own database).
- No DAG UI or backfill tooling; acceptable for a single linear pipeline.

## Alternatives considered
- **Apache Airflow:** excellent for scheduled DAG pipelines, wrong fit for
  event-driven low-latency work, and heavy for one cron job.