# 01 — Product Requirements Document (PRD)

## 1. Product vision

Provide a dependable platform for enforcement teams to manage the full violation lifecycle and for affected owners/drivers to understand and resolve notices through authorised channels.

## 2. Personas and jobs

| Persona | Primary jobs | Constraints |
|---|---|---|
| Enforcement officer | Find vehicle/driver, capture event, attach evidence, submit case | Fast field workflow; cannot approve own case by default |
| Reviewer/supervisor | Inspect evidence and facts; approve, reject or return | Must see provenance and AI uncertainty; reason required |
| Agency administrator | Manage users, locations, offences, schedules and integrations | Changes are versioned and audited |
| Finance officer | Track fines, payments, refunds, settlements and exceptions | Separate permissions for fine adjustment/refund |
| Owner/driver | Verify notice, view permitted evidence, pay or appeal | Access only to own notice after approved verification |
| Auditor | Inspect decisions, record history and financial trail | Read-only access with controlled exports |

## 3. Functional scope

### 3.1 Identity and organisation
- Support multiple agencies/tenants with strict data isolation.
- Map users to agencies and explicit role grants.
- Prefer OIDC identity integration; require MFA for privileged roles.
- Support account suspension, session revocation and periodic access review.
- Audit security-relevant login and administration actions.

### 3.2 Vehicle and driver records
- Create, view, update, archive and search vehicle records.
- Store registration/plate in original display and jurisdiction-normalised forms.
- Store vehicle class/type and optional make, model and colour.
- Maintain effective-dated ownership history.
- Maintain driver and licence records separately from vehicle owners.
- Permit unknown driver where the driver is not yet established.
- Store data source, verification status and last-verified time.
- Encrypt and mask sensitive identifiers.

### 3.3 Offence catalogue and fine schedule
- Manage jurisdiction-scoped offence codes, descriptions, categories and evidence requirements.
- Store effective-dated fine schedules by offence, jurisdiction and applicable vehicle class.
- Record official source, version, approver and approval timestamp.
- Snapshot the selected schedule and calculation inputs on assessment.
- Require permission and rationale for adjustments, waivers or overrides.
- Never derive a fine amount from AI confidence or an unapproved source.

### 3.4 Violation case management
- Create cases manually or through approved imports/integrations.
- Capture event time/time zone, capture source, jurisdiction, location, offence, vehicle, optional driver and reporting officer.
- Generate stable internal case IDs and deduplicate imports using source event IDs/idempotency keys.
- Support Draft, Submitted, Under Review, Needs Information, Approved, Rejected, Notice Issued, Payment Pending, Paid, Appealed, Appeal Upheld, Appeal Rejected, Cancelled and Closed states.
- Enforce transitions and require reasons for return, rejection, cancellation and override.
- Support assignment, comments, queue filters and controlled attachments.

### 3.5 Evidence
- Accept configured image, video clip, document and metadata evidence.
- Store binaries in private object storage; metadata remains in the database.
- Calculate SHA-256 at ingestion and verify on retrieval/export.
- Record capture source/device, capture time, ingestion time, uploader/integration identity, media type, size and processing history.
- Never overwrite originals; store redacted/annotated derivatives separately and link them to originals.
- Support retention expiry, legal hold and documented disposal.

### 3.6 Optional AI-assisted detection
- Ingest a detection candidate with model/version, confidence, input evidence, event time and candidate fields.
- Display AI suggestions separately from verified facts.
- Allow reviewers to correct output without changing raw model output.
- Keep detection status separate from official violation status.
- Route low-confidence/conflicting candidates to manual review or quarantine.
- Measure precision, recall and false positives on representative labelled data before operational use.

### 3.7 Fine assessment and notice/challan
- Assess only after approval and using a schedule valid for the event date.
- Generate a unique, non-guessable public reference and human-readable notice.
- Snapshot offence code, schedule version, amount, modifiers, currency, due date and calculation explanation.
- Restrict issue, reissue, correction and cancellation to authorised transitions.
- Support late fees, partial payments, instalments, waivers and refunds only where policy permits.

### 3.8 Payments and reconciliation
- Use a server-side payment-provider adapter.
- Use idempotency keys and verify webhook signatures.
- Model payment attempts separately from the outstanding obligation.
- Handle duplicate, delayed, out-of-order, failed, reversed and refunded events.
- Reconcile provider references and settlement reports against notices.
- Never store full card numbers, CVV, bank passwords or wallet credentials.

### 3.9 Appeals/disputes
- Accept an appeal within the configured jurisdictional window.
- Capture reason, documents, filing time and acknowledgement.
- Support assignment, review, decision, rationale and reviewer identity.
- Preserve the original notice and assessment; record changes as new decisions/actions.
- Apply payment holds or deadline extensions only when policy requires them.

### 3.10 Notifications and public portal
- Support templates for notice, reminder, receipt, appeal acknowledgement and outcome.
- Log delivery outcomes without exposing unnecessary personal data.
- Protect public notice lookup with high-entropy reference, additional verification and rate limiting.
- Reveal only information authorised for that recipient.

### 3.11 Dashboards and reporting
- Operational: unassigned cases, review backlog, ageing, returned/rejected cases, evidence exceptions.
- Financial: assessed, issued, paid, outstanding, overdue, refunded/reversed and settlement mismatches.
- Enforcement: trends by offence/date/location, subject to access controls and privacy policy.
- Permission-control and audit CSV/PDF exports.
- Keep assessed, issued, collected and settled amounts distinct.

## 4. Priorities

**MVP must-have:** authentication/RBAC/tenant isolation; vehicle, driver and offence records; manual violation entry; evidence upload; review workflow; fine schedule and assessment; notice/challan; payment sandbox/provider adapter; basic appeals; search, dashboard and audit; backups, monitoring and security tests.

**Should-have after MVP:** camera/VMS event import; ANPR/OCR candidate workbench; settlement import; multilingual notices; bulk operations with preview/audit.

**Could-have later:** offline-first officer capture; advanced map analytics; additional payment/government integrations; model-assisted evidence quality and duplicate clustering.

## 5. Business rules

- Registered owner is not automatically the driver.
- AI/camera detection is a candidate, not an issued violation.
- Fine assessment requires an approved case and valid offence schedule.
- Notice issuance requires completed review and mandatory evidence.
- Browser redirect alone never marks a payment successful.
- Every adjustment, cancellation, appeal decision and override has actor, timestamp, reason and history.
- Tenant users cannot access another tenant's data by changing an identifier.

## 6. MVP definition

A controlled pilot for one approved jurisdiction and authority. Manual capture/review is the baseline. Payment goes live only after provider and finance approval. AI is feature-flagged off and introduced only after separate validation and authority approval.