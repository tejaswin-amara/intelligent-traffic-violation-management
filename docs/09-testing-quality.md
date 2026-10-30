# 09 — Testing and Quality Strategy

## Quality objectives
Validate workflow correctness, tenant isolation, evidence integrity, payment correctness, auditability, accessibility and operational recovery. A happy-path-only test suite is insufficient for an enforcement/financial system.

## Test layers

| Layer | Focus | Examples |
|---|---|---|
| Unit | Domain rules/calculation | State transitions, effective schedule, rounding, appeal deadline |
| Integration | DB constraints/transactions | Tenant filters, RLS, concurrent review, outbox write |
| API contract | Compatibility | OpenAPI validation, schema, error codes, pagination |
| E2E | Full journeys | Create → review → assess → issue → pay; appeal → decision |
| Security | Abuse cases | IDOR, role escalation, webhook forgery/replay, enumeration, malicious upload |
| Evidence | Provenance/integrity | Hash mismatch, derivative link, overwrite prevention, access audit |
| Performance | Pilot workload | Search latency, queue throughput, reviewer concurrency |
| Accessibility | WCAG 2.2 AA | Keyboard, screen reader, contrast, focus, validation |
| Resilience | Failure/recovery | Queue/storage/provider outage, backup restore |
| AI (if enabled) | Model risk | Precision/recall, false positives, calibration, drift |

## Mandatory business test cases

### Registry
- Same plate in different jurisdictions follows configured uniqueness policy.
- Normalisation preserves display string and rejects malformed values.
- Owner history resolves correctly at event timestamp, including transfer boundaries.
- Unknown driver stays unknown; registered owner is not copied into driver.
- Stale/unverified external data is visibly marked.

### Violation/review
- Missing mandatory facts/evidence blocks submit/approval according to policy.
- Invalid state transition returns conflict without partial mutation.
- Creator cannot approve own case by default.
- Reject/return requires reason.
- Concurrent reviews cannot create conflicting final decisions.
- Replayed imported event does not create a duplicate case.

### Fine/notice
- Schedule selection uses event timestamp and correct jurisdiction/offence/class.
- Schedule update does not mutate earlier assessments.
- Rounding/currency/boundary cases are deterministic.
- Manual adjustment requires permission, rationale and audit.
- Public reference is unique, non-sequential and non-enumerable.
- Cancel/reissue preserves prior notice history.

### Payment/appeal
- Duplicate webhook credits once; invalid signature is rejected.
- Out-of-order webhook does not incorrectly regress terminal state.
- Browser return without provider confirmation cannot mark paid.
- Reversal/refund updates balance and remains auditable.
- Settlement mismatch enters exception queue.
- Appeal deadline boundary uses configured timezone/rule.
- Appeal decision preserves original notice and assessment.

### Security/evidence
- Cross-tenant reads/writes fail at API and data-access layers.
- Public notice reveals no unnecessary personal data and resists enumeration.
- Disallowed uploads are rejected; suspicious files are quarantined.
- Hash mismatch blocks evidence finalisation/export.
- Derivative cannot replace original.
- Sensitive fields are redacted from logs/traces.

## Test data
Use synthetic names, registrations, licence numbers, evidence and payment fixtures. Cover invalid, missing, conflicting, expired and edge-date values. Include timezone boundaries and daylight-saving transitions where relevant. Use payment sandbox and signed test webhooks. AI evaluation material must be lawfully sourced and access-controlled; do not copy production evidence to developer devices.

## CI quality gates
1. Format/lint/type checks.
2. Unit and integration tests.
3. OpenAPI validation/compatibility.
4. Migration tests against empty and prior-version databases.
5. SAST, dependency, secret, container and IaC scans.
6. Tenant-isolation/authorisation regression tests.
7. E2E smoke tests for case lifecycle and payment webhook.
8. Immutable artefact and SBOM generation.
9. Deployment smoke tests and rollback verification.

No tests may be silently skipped. Environment-dependent skips require an explicit reason and visible CI status.

## Exit criteria
- All M requirements map to passing tests or approved exceptions.
- No unresolved critical/high finding without signed, time-bounded risk acceptance.
- No known data-loss, cross-tenant, evidence-integrity, double-payment or fine-calculation defect.
- Critical E2E workflows pass in release candidate environment.
- Load targets meet agreed pilot profile.
- Backup restore is demonstrated.
- Accessibility findings are resolved or formally accepted with a remediation plan.