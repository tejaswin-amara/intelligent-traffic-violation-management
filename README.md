# Intelligent Traffic Violation Management (ITVM) Platform

A comprehensive enterprise-grade platform for enforcing and managing traffic violations, fine calculations, and appeals.

## Architecture

This project is structured as a **modular monolith** consisting of:
- **Backend**: Python 3.12, FastAPI, SQLAlchemy (PostgreSQL), Alembic, Pydantic, Passlib, python-jose (JWT).
- **Frontend**: React 19, Vite, TypeScript, TailwindCSS v4, React Router, React Query, Lucide-React.
- **Database**: PostgreSQL 15 via Docker Compose.

## Features

- **RBAC & Tenancy**: Multi-tenant architecture with strict organization data isolation and Role-Based Access Control (e.g. `agency_admin`, `enforcement_officer`, `reviewing_officer`, `finance_officer`).
- **Domain Registries**: Management of Jurisdictions, Persons, Vehicles, and Drivers.
- **Violation Lifecycle**: Officers capture violations. Reviewers approve or reject. The state is strictly enforced through a FastAPI API.
- **Evidence Management**: Secure handling of digital evidence assets (mocked object storage via file endpoints).
- **Deterministic Fines & Notices**: Fine amounts are calculated automatically and deterministically via effective-dated schedules.
- **Financial Workflows**: Idempotent payment intent handling, secure mock webhook processing, and ledger entries for reconciliation.
- **Appeals Engine**: Complete support for handling violation appeals.
- **Analytics & Dashboards**: Operational metrics exposed natively.

## Local Setup

### 1. Requirements

- Docker & Docker Compose
- `uv` (Fast Python packaging)
- `pnpm` (Fast Node.js packaging)
- Python 3.12+
- Node.js 18+

### 2. Start PostgreSQL

```bash
docker compose up -d
```

### 3. Backend Setup

```bash
cd backend
# Create env
uv sync
# Run database migrations
uv run alembic upgrade head
# Start local API
uv run uvicorn app.main:app --reload
```

### 4. Frontend Setup

```bash
cd frontend
pnpm install
pnpm run dev
```

### 5. Running Tests

```bash
cd backend
uv run pytest tests/ -s
```
