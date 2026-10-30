# ADR-002: Store Evidence in Private Object Storage

- **Status:** Proposed
- **Date:** 2026-10-30

## Context
Evidence can include large images and video clips. File bytes and transactional metadata have different access, retention and delivery requirements.

## Decision
Store evidence bytes in private encrypted object storage. Store metadata, hashes, lifecycle state and object references in PostgreSQL. Keep originals immutable at application level; store redacted/annotated derivatives as separate linked assets.

## Consequences
- Database remains focused on transactional records.
- Evidence delivery can use narrowly scoped, short-lived signed URLs.
- Versioning, retention, legal hold, replication and access logs must be configured and tested.
- A hash verifies byte consistency, not source authenticity.

## Revisit when
Authority mandates a specific evidence vault, on-premises WORM store or evidentiary-system integration.