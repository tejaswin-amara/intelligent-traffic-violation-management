# 05 — Database Design

## 1. Design principles

- PostgreSQL-oriented relational design with UUID primary keys.
- Every operational record is organisation-scoped; foreign keys should preserve tenant consistency.
- Keep people, drivers, vehicles, ownership, violations, evidence, assessments, notices, payments and appeals separate.
- Use `timestamptz` for instants and retain source timezone/offset context where relevant.
- Use `numeric` or integer minor units for money, never floating point.
- Encrypt sensitive licence/identity values at application level; use keyed HMAC lookup tokens for exact matching if required.
- Preserve immutable decision and financial event history.
- Store evidence bytes outside the database in private object storage.

## 2. Baseline tables

`database/schema.sql` provides a starter schema for:
- `organisations`, `users`, `memberships`;
- `jurisdictions`, `persons`, `drivers`, `vehicles`, `vehicle_ownerships`;
- `offences`, `fine_schedules`;
- `violations`, `evidence_assets`, `detection_runs`, `review_decisions`;
- `fine_assessments`, `notices`, `payments`, `payment_ledger_entries`, `payment_webhook_events`;
- `appeals`, `notifications`, `audit_events`.

It is a design baseline, not a production migration. Add row-level security policies, overlap constraints, outbox/import/reconciliation/legal-hold tables and indexes after the approved workflow is finalised.

## 3. Sensitive identifiers

Do not store licence/identity numbers as plaintext. Recommended pattern:
- encrypt the original identifier using application-managed envelope encryption;
- store ciphertext and key version;
- store keyed HMAC lookup token only if exact-match search is necessary;
- show only a short masked suffix in ordinary screens;
- never log raw identifier or lookup token.

Audit decryption access and document key rotation/revocation/recovery. Do not collect national identity numbers unless the authority documents necessity and legal authority.

## 4. Indexes

Initial indexes should cover:
- vehicle lookup by organisation, jurisdiction and normalised registration;
- driver lookup by organisation and HMAC lookup token;
- violation queues by organisation, status, event time and assignee;
- vehicle violation history by vehicle and event time;
- evidence by violation;
- notice by public-reference hash;
- payment by provider reference and notice;
- appeal queues by organisation, status and filing date;
- audit history by organisation, entity and time.

Avoid indexes on raw sensitive values. Validate index choice against real query plans and pilot data volume.

## 5. Lifecycle and migrations

Define a retention matrix before production: record class, purpose, legal basis, retention trigger/duration, legal-hold behaviour, disposal method, owner and audit evidence. Evidence, identity fields, payment metadata and logs may have different schedules.

Migrations are append-only and reviewed. Use expand/migrate/contract for populated tables, bounded restartable backfills, and a rollback or forward-fix plan. Never use production personal data in local development/test fixtures. Test migrations against empty and prior-version databases.

## 6. Reconciliation and quality checks

Run scheduled checks for orphaned records, duplicate source event IDs, inconsistent notice/payment balances, missing evidence hashes, invalid schedule references and overlapping ownership/schedule periods. Derive balances from append-only payment-ledger movements, not only the latest payment status. Exceptions enter a review queue; do not auto-correct legal or financial records without authority.