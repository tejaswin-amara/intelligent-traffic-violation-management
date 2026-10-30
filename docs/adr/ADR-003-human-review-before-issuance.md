# ADR-003: Require Human Review Before Notice Issuance

- **Status:** Proposed
- **Date:** 2026-10-30

## Context
Camera and AI outputs can contain recognition/classification errors. Fine issuance is a high-impact action governed by jurisdiction-specific legal authority and evidentiary requirements.

## Decision
Treat all imported or AI-generated detections as candidates. In the default workflow, an authorised reviewer inspects original evidence and approves the case before fine assessment and notice issuance.

## Consequences
- Reduces risk of automated false-positive enforcement.
- Creates an accountable review event and an appeal trail.
- Adds reviewer workload and requires queue-quality metrics.
- Any automated mode needs explicit legal/operational approval, separate validation and a dedicated ADR.

## Revisit when
The authority provides an explicit legal/operational basis and the system passes required certification and independent validation.