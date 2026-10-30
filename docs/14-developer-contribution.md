# 14 — Developer and Contribution Standard

## Working principles
- Treat docs as the project contract; update them when behaviour changes.
- Inspect existing code/architecture before adding dependencies or infrastructure.
- Prefer simple module boundaries over premature distributed services.
- Enforce invariants and access rules in server/domain layers, not only the UI.
- Never silently alter legal schedules, payment logic, retention or enforcement process.

## Suggested repository layout

```text
/
├── apps/
│   ├── web/                 # staff and public experiences
│   └── api/                 # modular API application
├── workers/                 # async job entry points
├── packages/
│   ├── domain/              # rules, entities, state transitions
│   ├── contracts/           # OpenAPI/shared types
│   └── ui/                  # accessible shared components
├── database/
│   ├── migrations/
│   └── seeds/               # synthetic fixtures only
├── docs/adr/
├── infra/                   # reviewed deployment/IaC
└── tests/
    ├── integration/
    ├── e2e/
    ├── security/
    └── fixtures/            # synthetic data only
```

Adapt to the selected framework; do not create empty packages to mimic the template.

## Branches and commits
- Use short-lived feature branches from protected default branch.
- Use conventional commits, e.g. `feat(violations): add review workflow`.
- Link changes to requirement IDs/issues and describe migration/API impact.
- Require PR review; protect production branches and tags.
- Never commit real credentials, enforcement evidence or production exports.

## Pull-request checklist
- [ ] Requirement IDs and scope stated.
- [ ] Domain invariants and server-side permissions enforced.
- [ ] Tests cover success, invalid data, conflicts and security-negative cases.
- [ ] Migrations reviewed and safe for existing data.
- [ ] OpenAPI/API contract updated where applicable.
- [ ] Audit events and sensitive-field redaction considered.
- [ ] UI error states/accessibility covered.
- [ ] Logs/metrics contain no raw sensitive identifiers or secrets.
- [ ] Docs/ADRs updated for changed behaviour or decisions.
- [ ] No silently skipped tests or unrelated temporary files.

## Code rules
- Validate inputs at boundaries; re-check critical rules in domain services.
- Use explicit types for money, IDs, states and timezone-aware timestamps.
- Use UTC internally and retain source timezone context.
- Commit state transition and audit/outbox records in one transaction.
- Make imports, webhooks and retryable commands idempotent.
- Avoid logging request bodies; redact sensitive values.
- Call external services through adapters with timeouts and bounded retries.
- Test denied access, not just permitted access.
- Avoid generic “admin can do anything” shortcuts in production.

## Definition of done
Code, tests, security checks, docs, migration/API compatibility, observability and operator impact are addressed; CI is green; peer review is complete; deployment/rollback implications are recorded.

## ADR policy
Create an ADR for material decisions (identity, tenancy, hosting, storage, payments, queue, AI and registry integration). Include context, decision, alternatives, consequences, security/privacy implications and revisit triggers.