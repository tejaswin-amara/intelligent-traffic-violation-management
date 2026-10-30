# ADR-001: Start with a Modular Monolith

- **Status:** Proposed
- **Date:** 2026-10-30

## Context
The first release has tight transactional relationships across violation cases, reviews, fine assessments, notices and audit events. Early microservices would add deployment, consistency, observability and permission complexity before scale is known.

## Decision
Build one modular application with explicit domain modules and separate process entry points for API and background workers. Prevent undocumented cross-module table manipulation.

## Consequences
- Easier transactional workflows and end-to-end tests.
- Lower operational complexity for a small team.
- Modules can be extracted later when scale/team ownership justifies it.
- Requires discipline to prevent a tightly coupled monolith.

## Revisit when
Measured load, independent release needs, regulatory isolation or team structure demonstrates a concrete benefit from service extraction.