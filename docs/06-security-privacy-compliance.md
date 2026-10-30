# 06 — Security, Privacy and Compliance

## 1. Security objective

Protect confidentiality, integrity, availability and evidentiary reliability. A compromise may expose personal data, alter legal/financial outcomes or undermine evidence. Security is a release gate.

## 2. Threats and baseline controls

| Threat | Example | Controls |
|---|---|---|
| Unauthorised case access | IDOR across agencies | Tenant scoping in service and DB; negative authorisation tests |
| Privilege escalation | Officer grants self reviewer role | Server-side RBAC, admin-only grants, MFA, audit |
| Evidence tampering | Original image replaced | Hash verification, versioned/private storage, immutable audit |
| Payment spoofing | Forged success webhook | Signature verification, raw-body validation, deduplication, reconciliation |
| Public reference enumeration | Guessing notice references | High-entropy references, rate limits, recipient verification, minimal disclosure |
| Personal-data leakage | Licence number in logs | Encryption, masking, structured log redaction, export controls |
| Malicious upload | Executable/malformed evidence | Allowlisted formats, size limits, scanning, isolated processing |
| Insider misuse | Staff browses unrelated cases | Least privilege, access history, reviews and alerts |
| Supply-chain risk | Compromised dependency | Lockfiles, dependency scanning, SBOM, controlled artefacts |
| Model error/bias | False-positive detections | Representative evaluation, human review, appeals, monitoring, kill switch |
| Denial of service | Flooded public lookup/webhooks | WAF, rate limits, request limits, backpressure |

## 3. Access control and separation of duties

- Use role-based permissions with organisation and, where required, jurisdiction/location scope.
- Authorise every request on the server; UI hiding is not security.
- Separate case creation, review approval, fine adjustment, payment reconciliation, appeal decisions and security administration.
- By default, a case creator cannot approve the same case. Fine adjustments/refunds require separate permission and reason.
- Support time-bounded support/break-glass access with purpose, expiry and audit.
- Review privileged memberships regularly.

## 4. Authentication and sessions

- Prefer an approved OIDC provider over custom password storage.
- Require MFA for privileged roles.
- Use short-lived access tokens, refresh-token rotation and session revocation on suspension/role changes.
- Use Secure/HttpOnly/SameSite cookies where applicable; protect state-changing requests against CSRF.
- Rate-limit login, reset, public lookup and appeal endpoints.

## 5. Data protection

- Classify public reference data, case data, personal data, restricted identifiers, evidence, financial metadata and audit/security data.
- Encrypt in transit and at rest; apply application-layer envelope encryption to high-risk identifiers.
- Store keys in a managed KMS/HSM or equivalent; audit key use and rotation.
- Mask identifiers/contact details by default.
- Never place sensitive values in URLs, analytics, logs, traces, crash reports or support tickets.
- Use synthetic/de-identified data in development.
- Define retention, legal hold, disclosure, deletion and data-subject request procedures where applicable.
- Do not assume technical access equals legal authority to collect/share data.

## 6. Evidence controls

- Keep originals immutable at application level.
- Calculate SHA-256 at ingestion and verify before export.
- Use private encrypted object storage and short-lived signed URLs.
- Log views, downloads, redactions and exports where required.
- Preserve source metadata but do not treat client-supplied metadata as authoritative.
- Record acquisition, transfer, processing, review, redaction, disclosure, legal hold and disposal events.
- Keep derivatives separate and linked to originals.

A hash verifies byte-level consistency against a recorded digest; it does not by itself prove who captured the media, where it was captured or whether the source was trustworthy.

## 7. Application and infrastructure controls

- Use parameterised queries and boundary validation.
- Apply security headers, CSP, CORS allowlists, request limits and safe error responses.
- Scan dependencies, containers, infrastructure-as-code and secrets in CI.
- Produce an SBOM for release artefacts.
- Use protected branches and peer review.
- Separate dev/test/staging/prod identities, keys, accounts and data.
- Restrict production DB access and audit break-glass use.
- Conduct vulnerability assessment and independent penetration testing before public launch and after major changes.

## 8. Audit

Capture actor/type, organisation, timestamp, action, entity, correlation ID, reason and relevant before/after values with sensitive fields redacted. Ordinary application roles cannot alter/delete audit events. High-assurance deployments should replicate audit records to separately protected/tamper-evident storage. Synchronise system clocks.

## 9. Jurisdictional compliance workstream

Before production, legal/privacy advisers and the deploying authority must confirm:
- lawful authority for collection, processing, sharing and enforcement;
- permitted vehicle/driver data sources and access conditions;
- offence codes, fine amounts, effective dates and payment rules;
- notice service, appeal, review, refund and deadline requirements;
- evidence authenticity, admissibility, disclosure, redaction and retention;
- privacy notices, applicable individual rights and deletion obligations;
- cross-border/data-residency and records-management rules;
- payment-provider/financial reconciliation requirements;
- public-sector security, accessibility and language obligations.

This document is not legal advice and does not interpret any jurisdiction's law. Requirements must be checked against current official sources and approved in writing by the relevant authority.

## 10. Security release gates

- No unresolved critical/high exploitable issue without signed, time-bounded risk acceptance.
- No secrets in repository or artefacts.
- Tenant-isolation and role-negative tests pass.
- Webhook forgery/replay/duplicate tests pass.
- Backup restore and privileged-access review completed.
- Evidence hash and access-audit tests pass.
- Incident response and escalation contacts documented.