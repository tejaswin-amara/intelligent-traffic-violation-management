# 12 — MVP Acceptance Criteria

Record test run, evidence, approver and date for every applicable criterion.

## Access and tenancy
- [ ] Authentication uses the approved identity provider.
- [ ] Privileged roles enforce MFA.
- [ ] Organisation/jurisdiction/role scopes are enforced on protected reads and writes.
- [ ] Negative tests prove cross-tenant access is blocked at API and data-access layers.
- [ ] User suspension/role revocation meets approved session-revocation window.

## Vehicle and driver
- [ ] Registration is stored in display and jurisdiction-normalised forms.
- [ ] Duplicate handling follows jurisdiction policy.
- [ ] Owner and driver are separate records.
- [ ] Ownership history resolves owner at event time.
- [ ] Sensitive identifiers are encrypted/masked and absent from logs.
- [ ] Source and verification status are visible to authorised staff.

## Violation and evidence
- [ ] Officer can create, edit, save and submit a case with required fields.
- [ ] Unknown driver remains unknown; owner is not copied into driver.
- [ ] Required evidence blocks approval when absent.
- [ ] Evidence is private, hashed and verifiable on retrieval/export.
- [ ] Original evidence cannot be overwritten by derivative/ordinary action.
- [ ] Evidence access is permission-checked and audited.
- [ ] Invalid transitions fail without partial updates.

## Review
- [ ] Reviewer can inspect case facts, evidence provenance and history.
- [ ] Creator cannot approve own case by default.
- [ ] Approve/reject/return requires rationale and immutable decision event.
- [ ] Review decisions cannot be silently edited/deleted.

## Fine and notice
- [ ] Only approved cases can be assessed.
- [ ] Schedule is valid for jurisdiction, offence, class and event date.
- [ ] Assessment stores schedule version and calculation snapshot.
- [ ] Currency, rounding and boundary tests pass.
- [ ] Manual adjustment requires permission, reason and audit.
- [ ] Notice uses unique non-sequential reference and correct snapshot.
- [ ] Cancellation/reissue preserves history.

## Payment and appeal
- [ ] Payment starts through provider sandbox with idempotency.
- [ ] Browser redirect alone cannot mark payment successful.
- [ ] Invalid webhook signature is rejected.
- [ ] Duplicate/replayed webhooks are processed once.
- [ ] Failed, reversed, refunded and reconciliation-exception states are visible.
- [ ] Appeal window follows approved configuration.
- [ ] Appeal decision preserves original notice and assessment.

## Reporting, operations and governance
- [ ] Dashboard distinguishes assessed, issued, collected, outstanding, refunded and settled.
- [ ] Exports are permission-controlled and audited.
- [ ] Logs/metrics have correlation IDs and sensitive-data redaction.
- [ ] Backup restore meets approved RPO/RTO.
- [ ] CI runs tests, schema checks, security scans and SBOM generation.
- [ ] Runbooks/support contacts are approved.
- [ ] Legal owner approved offence, schedule, notice, appeal, evidence and retention rules.
- [ ] Privacy/security owner approved data flows, access, retention and hosting.
- [ ] Operators completed training.
- [ ] AI is disabled unless separately approved under `docs/07-ai-evidence-governance.md`.
- [ ] Pilot owner signed go-live.