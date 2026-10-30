# 00 — Project Charter

## Project summary

**Name:** Intelligent Traffic Violation Management (ITVM)  
**Type:** Traffic-enforcement case-management platform with optional AI-assisted evidence intake.  
**Outcome:** A reliable, auditable process for creating, validating, reviewing, issuing, collecting, disputing and closing traffic-violation cases and associated fines.

ITVM is not a traffic-signal-control system. Its responsibility begins when a possible violation is reported or detected and ends when the case is resolved and retained or disposed of under the applicable policy.

## Problem statement

Enforcement work may be fragmented across paper forms, spreadsheets, cameras, payment portals and disconnected vehicle/driver records. This can cause duplicate cases, weak evidence provenance, unclear review responsibility, incorrect fine amounts, poor payment reconciliation and limited reporting. ITVM centralises the lifecycle without removing human accountability or due-process controls.

## Objectives and outcomes

| Objective | Outcome measure |
|---|---|
| Complete traceability | Every issued notice links to its violation, evidence, review decision, fine assessment and status history. |
| Reliable records | Required vehicle, offence, event, jurisdiction and evidence fields are validated. |
| Financial correctness | Assessment is calculated from a versioned fine schedule; adjustments are attributable and explained. |
| Payment traceability | Every payment has a provider reference, idempotency key and reconciliation state. |
| Appeal support | Eligible notices can be challenged and the decision is retained. |
| Evidence integrity | Evidence assets have hashes, provenance and access history. |
| Operational visibility | Dashboards show backlog, ageing, financial states and exceptions. |
| Least privilege | Users can access only the organisations, jurisdictions and functions assigned to them. |

## Stakeholders

- Deploying authority — owns policy, jurisdiction configuration and legal approval.
- Enforcement officer — creates cases and captures evidence.
- Reviewer/supervisor — validates cases and approves, rejects or returns them.
- Finance/reconciliation officer — monitors assessments, payments, refunds and settlements.
- Agency administrator — manages users, roles, offence catalogues and configuration.
- Vehicle owner/driver — views a notice, pays or appeals through an authorised channel.
- Auditor/compliance officer — inspects access, decisions, changes and reconciliation.
- Integration operator — maintains approved registry, camera, payment and messaging connections.

## Scope

### In scope

- Organisation/tenant setup, authentication, role and access management.
- Vehicle, registered-owner and driver records with history and source provenance.
- Jurisdiction-specific offence catalogue and effective-dated fine schedules.
- Manual and authorised imported violation creation.
- Optional AI-assisted detection candidate intake.
- Evidence upload, secure storage, integrity hash and chain-of-custody events.
- Review, approval, rejection and correction workflow.
- Fine assessment, notice/challan generation and tracking.
- Payment initiation, webhook handling and reconciliation.
- Appeal/dispute intake, review and decision.
- Notifications, dashboards, reporting, audit trail and exports.

### Excluded from MVP

- Live traffic-signal or road-network control.
- Autonomous fines based only on AI output.
- Face recognition or biometric identification.
- Unauthorised vehicle/licence database access.
- Storage of raw payment credentials.
- Replacing courts, tribunals or statutory appeal bodies.
- Predictive policing, driver risk scoring or behavioural profiling.
- Full video-surveillance/VMS functionality; ITVM consumes approved events/evidence from source systems.

## Product principles

1. Evidence before enforcement.
2. Human accountability for final approval in the default workflow.
3. Jurisdictional rules are versioned configuration, not constants in code.
4. Registered owner and actual driver are distinct.
5. Material decisions and changes are attributable and timestamped.
6. Collect only data necessary for an approved purpose.
7. External operations are retry-safe and idempotent.
8. Interfaces are accessible and usable on mobile.

## Assumptions and constraints

- One pilot jurisdiction and one authorised enforcement organisation will be selected before production.
- MVP is a responsive web application; native mobile apps and offline capture are later decisions.
- PostgreSQL (or equivalent relational DB) is the source of truth.
- Evidence binaries are kept outside the database in private object storage.
- Integrations require approved credentials, contracts, interface documentation and test environments.
- Legal retention, appeal, notice, evidence and payment rules must be approved before launch.

## Open decisions

| Decision | Owner | Needed before |
|---|---|---|
| First jurisdiction and enforcement authority | Sponsor / legal | Policy configuration |
| Approved offence catalogue and fine schedule | Authority / legal | Fine UAT |
| Evidence admissibility, retention and disclosure | Authority / legal | Evidence pilot |
| Public portal verification method | Authority / privacy | Public launch |
| Payment provider, settlement and refund model | Finance / procurement | Payment integration |
| Vehicle/driver registry interfaces | Authority / integration owner | Registry integration |
| Hosting, data residency and recovery targets | Security / infrastructure | Environment provisioning |

## Success / go-live conditions

All MVP acceptance criteria pass; offence and fine configuration is authority-approved; security and privacy reviews are complete; operators are trained; backup restoration is demonstrated; support and incident-response processes are staffed; and the pilot owner signs the release.