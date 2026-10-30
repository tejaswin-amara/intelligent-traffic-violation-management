# ADR-005: Keep Enforcement Policy Jurisdiction-Configurable

- **Status:** Proposed
- **Date:** 2026-10-30

## Context
Offence definitions, fine amounts, due dates, notice content, appeal windows, retention and evidence rules vary across jurisdictions and change over time.

## Decision
Represent enforcement rules as approved, effective-dated configuration with official source references, version IDs and approver. Snapshot applied policy on assessments/notices. Do not hard-code a jurisdiction's fine amounts or procedures.

## Consequences
- Supports policy changes without code releases for each schedule update.
- Requires controlled administration and approval for reference data.
- Requires regression tests for effective-date boundaries.
- Legal owners remain accountable for configured rules.

## Revisit when
A deployment is restricted to one jurisdiction with an approved fixed ruleset and the authority prefers another controlled release process.