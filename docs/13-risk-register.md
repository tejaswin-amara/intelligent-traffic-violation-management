# 13 — Risk Register

| ID | Risk | Likelihood / impact | Mitigation | Owner |
|---|---|---|---|---|
| R-01 | Outdated/incorrect fine schedule causes invalid assessment | Medium / Critical | Authoritative source, effective dating, dual approval, regression tests, immutable snapshot | Legal/Product |
| R-02 | Unauthorised access to enforcement/personal data | Medium / Critical | Tenant isolation, RBAC, MFA, encryption, audit, penetration tests | Security |
| R-03 | AI false positive causes wrongful notice | Medium / Critical | Candidate-only workflow, human review, evaluation, appeals, kill switch | Product/AI |
| R-04 | Evidence authenticity/chain of custody cannot be shown | Medium / High | Source authentication, hash, immutable original, provenance/access logs | Evidence owner |
| R-05 | Registered owner mistaken for driver | Medium / High | Separate entities, nullable driver, event-time ownership, UI safeguards | Product |
| R-06 | Duplicate/forged payment event changes balance | Medium / Critical | Signature check, idempotency, webhook inbox, reconciliation | Payments |
| R-07 | Public lookup leaks data or permits enumeration | Medium / High | High-entropy reference, verification, rate limits, minimum disclosure | Security/UX |
| R-08 | Registry integration lacks legal/contractual authority | Medium / High | Written approval and interface-control document | Authority |
| R-09 | Deletion conflicts with legal hold/retention | Medium / High | Approved retention matrix, legal hold, dual control, disposal audit | Legal/Records |
| R-10 | Provider outage delays payment/notification | Medium / Medium | Queue/retry, provider health, approved fallback | Operations |
| R-11 | Scope creeps into biometrics or unrelated surveillance | Medium / High | Explicit exclusions, change control and privacy/legal review | Sponsor |
| R-12 | Pilot volume causes latency/queue backlog | Medium / Medium | Workload model, load tests, queue monitoring, independent workers | Engineering |
| R-13 | Migration imports stale/conflicting owner/driver data | Medium / High | Provenance, reconciliation, quarantine conflicts, manual review | Data owner |
| R-14 | Insider misuse/collusion alters case outcomes | Low–Medium / Critical | Separation of duties, immutable events, access analytics, periodic audits | Authority |
| R-15 | Backup cannot be restored | Low–Medium / Critical | Point-in-time backups, isolated restore tests, runbooks, named owner | Operations |

## Risk acceptance
Critical risks cannot be accepted informally. Record rationale, compensating controls, expiry, accountable approver and review date. Risks affecting legality, evidence, individual rights, financial integrity or tenant isolation require explicit authority/security/legal approval.