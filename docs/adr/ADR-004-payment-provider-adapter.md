# ADR-004: Use a Payment Provider Adapter and Webhook Inbox

- **Status:** Proposed
- **Date:** 2026-10-30

## Context
Payment providers differ in checkout, webhook, refund and settlement interfaces. Payment state must remain correct under retries, duplicated callbacks, delayed events and outages.

## Decision
Define a provider-neutral payment interface. Persist webhook events before business processing, verify signatures, deduplicate provider event IDs, and reconcile against settlement reports. Do not store raw payment credentials.

## Consequences
- Provider can change without rewriting fine/notice domain logic.
- Webhook processing is auditable and retry-safe.
- Each provider needs adapter tests, signature-key rotation and settlement mapping.
- Provider success remains subject to reconciliation and reversal handling.

## Revisit when
An authority-mandated payment rail offers a materially different contract or settlement model.