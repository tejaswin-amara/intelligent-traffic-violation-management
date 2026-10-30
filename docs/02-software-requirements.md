# 02 — Software Requirements Specification (SRS)

Requirement priority: **M** = mandatory for MVP; **S** = should follow; **C** = could follow. Requirements with legal dependencies require written authority/legal approval.

## 1. Functional requirements

| ID | Priority | Requirement |
|---|---:|---|
| AUTH-001 | M | Authenticate staff using an approved identity mechanism. |
| AUTH-002 | M | Enforce role permissions and organisation/jurisdiction scope on every protected request. |
| AUTH-003 | M | Require MFA or an approved equivalent for privileged users. |
| AUTH-004 | M | Support user suspension and session revocation. |
| AUTH-005 | M | Record security-relevant login, access-denial and administration events. |
| REG-001 | M | Create, view, update, archive and search vehicle records. |
| REG-002 | M | Preserve registration display value and jurisdiction-normalised value. |
| REG-003 | M | Create, view, update and archive driver records. |
| REG-004 | M | Represent registered owner separately from driver. |
| REG-005 | M | Maintain effective-dated vehicle ownership history. |
| REG-006 | M | Preserve source and verification metadata for registry data. |
| REG-007 | S | Integrate with authorised vehicle/licence registries with provenance and conflict handling. |
| OFF-001 | M | Manage jurisdiction-scoped offences and evidence requirements. |
| OFF-002 | M | Support effective-dated, versioned fine schedules. |
| OFF-003 | M | Reject assessment if schedule is not applicable to jurisdiction, offence, class or event date. |
| OFF-004 | M | Store calculation inputs, schedule version, currency and final amount. |
| OFF-005 | M | Restrict fine adjustments and require a reason. |
| VIO-001 | M | Create a violation with event time, jurisdiction, location, vehicle, offence and source. |
| VIO-002 | M | Allow driver to remain unknown; never auto-copy vehicle owner as driver. |
| VIO-003 | M | Assign a unique internal case identifier. |
| VIO-004 | M | Deduplicate imports by source event ID/idempotency key. |
| VIO-005 | M | Associate one or more evidence assets with a violation. |
| VIO-006 | M | Preserve immutable original evidence and SHA-256 digest. |
| VIO-007 | M | Authorise and audit evidence access/export. |
| VIO-008 | M | Enforce the violation state machine and reject invalid transitions. |
| VIO-009 | M | Record actor, time and reason for review, rejection, return and cancellation. |
| VIO-010 | S | Support bulk import with validation preview and error report. |
| VIO-011 | S | Ingest AI candidates without automatically issuing notices. |
| REV-001 | M | Reviewer can inspect case facts, evidence, provenance and history before decision. |
| REV-002 | M | Prevent creator from approving own case by default. |
| REV-003 | M | Require rationale for approve/reject/return decision. |
| FIN-001 | M | Permit fine assessment only after approval and valid schedule selection. |
| FIN-002 | M | Generate non-sequential, high-entropy public notice reference. |
| FIN-003 | M | Snapshot schedule, amount, currency and due date on notice. |
| FIN-004 | M | Support controlled cancellation/reissue with preserved history. |
| PAY-001 | M | Create payment attempt through configured provider adapter. |
| PAY-002 | M | Verify webhook signatures and process events idempotently. |
| PAY-003 | M | Distinguish created, pending, succeeded, failed, reversed and refunded states. |
| PAY-004 | M | Reconcile provider references/settlement and record exceptions. |
| PAY-005 | M | Never store raw payment credentials. |
| APP-001 | M | Accept eligible appeals within configured time window. |
| APP-002 | M | Preserve appeal reason, material, filing time, decision, rationale and reviewer. |
| APP-003 | M | Preserve original notice and assessment after appeal outcome. |
| APP-004 | S | Implement payment holds/deadline extensions according to policy. |
| COM-001 | M | Send approved notices and receipts through configured providers. |
| COM-002 | M | Retry notification jobs without creating duplicate notices. |
| REP-001 | M | Report case counts by status, offence, period and agency. |
| REP-002 | M | Distinguish assessed, issued, paid, outstanding, refunded and settled amounts. |
| REP-003 | M | Permission-control and audit exports. |
| AUD-001 | M | Record material business/security actions in append-only audit history. |
| AUD-002 | M | Include actor, organisation, action, entity, time, correlation ID and reason/change metadata. |
| AUD-003 | M | Deny ordinary application roles update/delete access to audit history. |

## 2. Non-functional requirements

| ID | Area | Initial requirement / target |
|---|---|---|
| NFR-AV-001 | Availability | 99.5% monthly MVP target, excluding approved maintenance; validate against support and hosting model. |
| NFR-PERF-001 | API latency | Standard list/detail API P95 < 500 ms at agreed pilot load, excluding external integrations/media processing. |
| NFR-PERF-002 | Search | Common indexed searches P95 < 1 s at agreed pilot data volume. |
| NFR-SCALE-001 | Scaling | API and worker processes can scale independently. |
| NFR-SEC-001 | Security | TLS, encryption at rest, least privilege, tenant isolation, secret management and vulnerability scanning. |
| NFR-SEC-002 | Identity | Privileged MFA and session revocation. |
| NFR-PRIV-001 | Privacy | Minimum necessary data; retention and disclosure configurable by jurisdiction. |
| NFR-REL-001 | Reliability | Critical writes transactional; jobs retry-safe and idempotent. |
| NFR-BCP-001 | Recovery | Initial RPO ≤ 15 min and RTO ≤ 4 hours, subject to approval and restore tests. |
| NFR-OBS-001 | Observability | Structured logs, metrics, traces, correlation IDs and alerts; no secrets/full identifiers in telemetry. |
| NFR-ACC-001 | Accessibility | Target WCAG 2.2 AA for staff and public interfaces. |
| NFR-I18N-001 | Localisation | Store instants in UTC; render using configured time zone, locale and currency. |
| NFR-MAINT-001 | Maintainability | Reviewed migrations, automated tests, API contract checks, module boundaries and ADRs. |
| NFR-PORT-001 | Portability | Containerisable for approved cloud or on-premises deployment. |

## 3. Validation rules

- Event timestamp must include an offset or known jurisdiction time zone; store UTC plus source-zone context.
- Preserve original plate string; normalisation is jurisdiction-aware.
- Offence and schedule must be valid at the event time.
- Fine values use fixed precision or integer minor units, never binary floating point.
- Mandatory evidence and review must be complete before notice issuance.
- Imported events include source identity and idempotency reference.
- Public notice references are high-entropy and rate-limited.
- Any time-dependent policy (due date, appeal deadline, retention) is versioned/configured.

## 4. External interfaces

OIDC identity provider; authorised vehicle/licence registry; camera/VMS/ANPR source; payment gateway and settlement reports; SMS/email provider; optional notice rendering/signing service; optional government challan/case system.

Every integration requires an interface-control document describing authentication, ownership, data mapping, rate limits, retries, error semantics, SLA, sandbox, monitoring and incident contacts.

## 5. Traceability

Every M requirement maps to one or more acceptance criteria and tests. Legal dependencies also map to written approval from the designated authority/legal owner.