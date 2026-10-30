# 10 — Deployment and Operations

## Environments and deployables
Maintain separate dev, test, staging/UAT and production environments, credentials, keys, buckets and databases. Do not copy production data into lower environments without approved de-identification.

Deploy:
- web/API application;
- background workers for evidence, notifications, imports, payments and reports;
- PostgreSQL;
- durable queue or DB-backed job store;
- private evidence and notice object storage;
- reverse proxy/WAF and OIDC integration;
- observability backend and alerting.

API and worker may share one image/codebase but run as different processes with different permissions.

## Configuration and secrets
- Non-secret configuration belongs in environment-specific configuration management.
- Store secrets in an approved secret manager; inject at runtime.
- Never commit real `.env` secrets.
- Fail closed if security-critical configuration is missing.
- Rotate payment webhook secrets, DB credentials, signing keys and encryption keys under an approved process.
- Use distinct keys per environment.

## Database and evidence operations
- Apply schema only through reviewed versioned migrations.
- Use encrypted backups and point-in-time recovery where supported.
- Restrict restore permissions; test restores regularly.
- Monitor replication lag, storage growth, slow queries, locks, pool saturation and job failures.
- Disable public object access; enable encryption, versioning and access logs.
- Apply object lifecycle/deletion only after retention policy approval.
- Respect legal holds and produce disposal audit records.

## CI/CD release process
1. Pull request links requirements/issues and describes migration/API impact.
2. CI runs format, lint, type checks, tests, contract checks, security scans and SBOM.
3. Peer review; security/architecture review for sensitive changes.
4. Build immutable artefact and record digest.
5. Deploy staging, run migrations and smoke/E2E checks.
6. Product/authority UAT sign-off for workflow or policy changes.
7. Production deploy via controlled rolling/blue-green process where supported.
8. Verify health, queues, webhooks, storage and core flows.
9. Monitor and retain rollback/forward-fix plan.

Fine schedule changes are approved policy-data changes, not ordinary unreviewed code updates.

## Observability
Use structured logs, metrics and traces with correlation IDs across API, worker and external calls. Never log raw personal identifiers, full evidence URLs, credentials, payment tokens or unredacted webhook payloads.

Track API rate/latency/errors; authentication failures and denied access; cases by status and queue age; evidence upload/scan/hash failures; detection queue/model latency/override rates; payment outcomes/webhook lag/duplicates/reconciliation exceptions; notification backlog; DB health; backup freshness; object-store availability and lifecycle failures.

## Alerts and runbooks
Alert on API degradation, anomalous access, evidence integrity/storage failure, stuck queues, invalid/unprocessed webhooks, reconciliation mismatches, DB issues, backup failures and unexpected fine-schedule/privilege changes. Runbooks specify severity, containment, diagnostics, safe retry, escalation, communications and recovery verification.

## Backup and disaster recovery
Initial targets: RPO ≤ 15 minutes and RTO ≤ 4 hours, subject to infrastructure/cost approval. Back up DB, configuration, secrets-recovery material and evidence per policy. A backup is not proven until restored. Complete a full restore exercise before pilot and repeat on a defined schedule.

## Incident response and support
Name an incident owner and contacts for authority, hosting, identity, payments, notifications and registry providers. Cover triage, evidence preservation, containment, key revocation, recovery, communication, regulatory-notification assessment and post-incident review. Define support hours, severity, escalation, maintenance windows and operator training before launch.