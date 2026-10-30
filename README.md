# Intelligent Traffic Violation Management (ITVM)

Development documentation pack for a platform that records, manages, reviews, and tracks traffic violations and associated fines.

## Product lifecycle

Vehicle/driver records → violation capture → evidence verification → officer review → fine assessment → notice/challan issuance → payment or appeal → reconciliation and closure.

A vehicle, registered owner, driver, violation, evidence asset, fine assessment, notice, payment, and appeal are separate records. The registered owner is not automatically the person who drove the vehicle. An AI detection is a candidate for review, not proof of an offence.

## Documentation index

| File | Purpose |
|---|---|
| `docs/00-project-charter.md` | Vision, scope, assumptions, stakeholders |
| `docs/01-product-requirements.md` | Personas, capabilities, priorities, business rules |
| `docs/02-software-requirements.md` | Functional and non-functional requirements |
| `docs/03-domain-model.md` | Entities, relationships, state machine, invariants |
| `docs/04-architecture.md` | Architecture, module boundaries, integrations |
| `docs/05-database-design.md` | Data model, retention, migration strategy |
| `database/schema.sql` | PostgreSQL baseline schema |
| `api/openapi.yaml` | Draft OpenAPI 3.1 API contract |
| `docs/06-security-privacy-compliance.md` | Security, privacy, evidence and audit controls |
| `docs/07-ai-evidence-governance.md` | AI/ANPR governance and evidence provenance |
| `docs/08-ux-workflows.md` | Screens, roles, workflows and accessibility |
| `docs/09-testing-quality.md` | Test strategy and quality gates |
| `docs/10-deployment-operations.md` | Environments, CI/CD, monitoring, backup, incidents |
| `docs/11-implementation-roadmap.md` | Phases, epics and delivery gates |
| `docs/12-acceptance-criteria.md` | MVP release checklist |
| `docs/13-risk-register.md` | Key risks and mitigations |
| `docs/14-developer-contribution.md` | Repository, review, coding and change standards |
| `docs/15-glossary.md` | Shared vocabulary |
| `docs/adr/` | Architecture decision records |

## Recommended baseline

Use a modular monolith with clearly separated domain modules, PostgreSQL for transactional records, private object storage for evidence, a background worker for asynchronous tasks, and a payment-provider adapter. Run API and worker as separate processes/containers from one codebase. Avoid microservices until measured scale, team ownership, or isolation requirements justify them.

The schema is PostgreSQL-oriented; the API contract uses OpenAPI 3.1. Programming language, UI framework, identity provider, hosting environment, queue, and payment provider remain implementation decisions.

## Assumptions requiring sign-off

- The first deployment jurisdiction and enforcement authority have not been specified. Offence codes, fine amounts, due dates, appeal windows, notice formats, evidence retention and access rules must be supplied from current authorised sources. Never hard-code assumed legal values.
- Production use requires an authorised enforcement body, approved users, approved data sources and an approved operating procedure.
- AI is optional and disabled by default. It may assist with plate reading or event classification, but must not issue fines autonomously by default.
- Vehicle/driver registry access requires legal and contractual approval.
- Payment credentials remain with an external payment provider; ITVM stores provider references and payment outcomes, not raw card/bank credentials.
- Government registry, camera/VMS, payment, identity and notification integrations require official interface documentation and test access.

## How to use this pack

1. Confirm jurisdiction, deploying authority, user roles, legal basis and hosting/data-residency requirements.
2. Review the PRD and SRS; mark each requirement in-scope, deferred or excluded.
3. Approve the domain rules, architecture decisions and threat model.
4. Review the SQL and API contract; convert them into versioned migrations and a validated API spec.
5. Map requirement IDs to backlog items and automated tests.
6. Obtain legal, security, privacy and operational sign-off before pilot/go-live.

This pack is a project-development baseline, not legal advice, a government-approved enforcement specification, or a claim that any external integration is available.
