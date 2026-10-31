# HACKATHON DEMO GUIDE (CO6)

## 1. Project Introduction
Intelligent Traffic Violation Management (ITVM) solves fragmented local state traffic enforcement operations by delivering a holistic, mathematically-secure monolithic registry encapsulating violation tracking, review mechanics, multi-tenant RBAC, temporal fine snapshots, and idempotent payment ledgering.

## 2. Team Contribution Matrix
| Team member | Main responsibility | Files/modules implemented | Technical concepts to explain |
|---|---|---|---|
| To be confirmed | Backend Architecture & Schema | FastAPI, SQLAlchemy Models | Database design, multitenancy, API routing |
| To be confirmed | Frontend Engineering | React, Vite, Tailwind UI | Component state, JWT flow, UI integration |
| To be confirmed | Security & Workflow | Pytest, Payment Ledgering | Cryptography, temporal schedules, idempotency |

## 3. Technology Stack
- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Pydantic, Passlib, Cryptography.
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, TanStack Query.

## 4. Setup & Running the Demo
1. Ensure dependencies are satisfied:
```bash
docker-compose up -d
cd backend && uv sync && uv run alembic upgrade head
```
2. Seed the deterministic demo database:
```bash
uv run python seed_demo.py
```
3. Run the applications (separate shells):
```bash
uv run fastapi dev app/main.py
cd frontend && pnpm run dev
```

## 5. Demonstration Sequence (5-7 Minutes)
1. **Login:** Navigate to `http://localhost:5173/login`, authenticate via `demo@example.com` / `password123`.
2. **Dashboard:** Highlight timezone-aware analytic graphs loading directly from PostgreSQL.
3. **Vehicle & Driver:** Register a vehicle manually. Register a driver, highlighting that license numbers are stored encrypted off-screen.
4. **Violation Pipeline:**
   - Create a violation mapping the vehicle to the driver.
   - Navigate to the Review Workbench.
   - Explain how approval can't proceed without required evidence tracking. Approve the violation.
5. **Fines & Appeals:**
   - Note the resulting Notice and Fine Assessment automatically generated. Explain temporal calculations.
   - Execute an Appeal against the resulting Notice ID highlighting the state-machine.

## 6. QA Preparation
### CO1: Database Design
**Q: How are violations connected to evidence?**
A: Through a 1-to-N relationship ensuring all items trace back to a centralized `violation_id`.

**Q: How would the schema handle multiple organisations?**
A: Every primary entity contains an indexed `organisation_id` FK. App-layer interceptors strictly filter via the `X-Organisation-ID` headers enforcing logical multitenancy.

### CO2: Database Operations
**Q: Where are transactions used?**
A: In `app.core.database`, we rely strictly on SQLAlchemy `Session.commit()` boundaries mapped closely against single API scopes to rollback failures globally (e.g. failing a vehicle write).

### CO3: Backend REST
**Q: How is organisation-level access enforced?**
A: A middleware `get_current_active_organisation` parses the JWT, resolves the user, ensures their status is active, and verifies they hold a valid unexpired membership inside the target organisation prior to attaching it to the request object.

### CO4: Distributed & Integration
**Q: Are there any asynchronous or distributed components?**
A: Yes, our `sandbox` payment webhook endpoints process callbacks independently matching the standard asynchronous paradigm to external financial environments.

### CO5: Problem Solving
**Q: What database optimizations have been implemented?**
A: Aside from normal foreign keys, deterministic queries avoiding decryption overhead via keyed HMAC lookups for identifiers like Driver Licenses.
