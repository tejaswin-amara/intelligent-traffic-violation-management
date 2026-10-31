# Intelligent Traffic Violation Management (ITVM)

An intelligent, multitenant traffic violation enforcement platform demonstrating robust modular-monolith backend design, secure cryptography, timezone-aware analytics, temporal data resolution, and idempotent financial webhook flows.

## Core Features
1. **Multitenancy & RBAC:** Organization-isolated enforcement with granular roles.
2. **Cryptographic Identity Protection:** Authenticated AES encryption with deterministic HMAC lookups for sensitive PII (Licenses).
3. **Temporal Fine Engine:** Resilient chronological evaluation linking exact historical fine parameters to localized violation timestamps.
4. **Idempotent Ledgers:** Signed webhook evaluation ensuring duplicate payment integrations safely bounce.

## Technology Stack
- **Backend:** Python 3.12+, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Passlib, Cryptography
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, TanStack Query

## Prerequisites
- Docker & Docker Compose
- `uv` (Python 3.12+)
- `pnpm` (Node.js 20.19+ or 22.12+)

## Setup Instructions

### 1. Database
```bash
docker-compose up -d
```
Creates PostgreSQL bound locally (`127.0.0.1:5432`) mapped to credentials: `itvm_user:itvm_password`.

### 2. Backend
```bash
cd backend
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run python seed_demo.py
uv run fastapi dev app/main.py
```
*Note: Generating a `.env` dynamically populates the secure sandbox configurations necessary to execute the server.*

### 3. Frontend
```bash
cd frontend
cp .env.example .env
pnpm install
pnpm run dev
```
Navigate to `http://localhost:5173`.

## Demo
Use `demo@example.com` / `password123` to enter the application as an authorized local admin to interact with the seeded models securely.

## Limitations
- OCR/ANPR models remain local structural placeholders.
- Real Payment Gateways require active ingress URLs outside of the local sandbox environment.
