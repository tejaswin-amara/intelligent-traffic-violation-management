# 11 — Implementation Roadmap

## Delivery strategy
Build a narrow, end-to-end trusted workflow first. Add integrations and AI only after authority, legal basis, data contracts and test environments are available.

## Phase 0 — Discovery and authority sign-off
**Deliver:** first jurisdiction/authority and pilot sites; approved offence catalogue and effective-dated fine schedule; notice/appeal/evidence/retention policies; integration inventory and approvals; threat model/privacy assessment; hosting/data-residency decision; pilot workload, availability, RPO/RTO and support model.

**Exit:** no production ingestion or fine issuance until policy and authority owners sign off.

## Phase 1 — Foundation
**Build:** repository and CI; environments; identity integration; tenancy/RBAC; migrations and audit service; jurisdiction/reference data; vehicle/person/driver/ownership records.

**Exit:** tenant-isolation and privileged-access tests pass.

## Phase 2 — Case management
**Build:** manual violation creation/editing; private evidence storage/hash/scan/access audit; queues/assignment; review workbench and state machine; search and basic dashboard.

**Exit:** draft-to-approved/rejected E2E and evidence-integrity tests pass.

## Phase 3 — Fines, notices, payments and appeals
**Build:** versioned schedules and deterministic calculator; notice rendering/reference/issue/cancel history; payment adapter/sandbox/webhook inbox/idempotency/reconciliation; appeal intake/review/decision; templates and finance dashboard.

**Exit:** authority fine test cases pass; duplicate/replayed webhooks cannot double-credit; appeal policy approved.

## Phase 4 — Pilot hardening
**Build:** security/penetration testing; privacy/legal sign-off; accessibility, load, failure-mode and restore tests; training, runbooks, support and pilot analytics.

**Exit:** acceptance criteria signed; no unresolved critical/high issues without approved risk acceptance.

## Phase 5 — Optional integrations and AI
**Build only when approved:** vehicle/licence registry; camera/VMS ingestion; AI OCR/detection candidate intake, evaluation, review UI, monitoring and rollback.

**Exit:** written data-source approval, model validation, human-review controls and kill switch verified.

## Suggested backlog epics
1. Identity and organisation scope.
2. Vehicle/driver registry and ownership history.
3. Offence catalogue and schedules.
4. Violation lifecycle and queue.
5. Evidence storage/integrity.
6. Review and decision audit.
7. Fine assessment and notice issuance.
8. Payment provider and reconciliation.
9. Appeals and communications.
10. Reporting and exports.
11. Security/privacy/operations hardening.
12. Approved integrations and AI candidate intake.

## Sequencing rules
- Implement domain invariants and access tests before UI polish.
- Deliver one vertical workflow end-to-end before broad CRUD expansion.
- Keep legal schedules out of code and require dual review for updates.
- Do not add AI before manual case/review works.
- Do not add microservices before demonstrated need.
- Each phase needs automated tests and operator-visible failure handling.