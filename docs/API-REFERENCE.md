# REST API REFERENCE (CO3)

## Base Path: `/api`

### Auth (`/api/auth`)
- **`POST /login-json`**: Authenticate via JSON payload (`email`, `password`) generating a short-lived Bearer JWT.
- **`GET /me`**: Returns authorized session metadata, including `Organisation` membership mappings.

### Domain (`/api/vehicles`, `/api/drivers`, `/api/offences`)
- **`GET /`**: List records associated directly with the caller's active organisation.
- **`POST /`**: Create a new record (RBAC checks implemented on Write paths).

### Operations (`/api/violations`)
- **`POST /`**: Stage a violation draft.
- **`GET /`**: Enumerate violations for reviewer workbenches.
- **`POST /{violation_id}/review`**: Submits a `decision` (e.g. `approved`, `rejected`, `needs_information`) altering the state machine safely. Approval demands a strict `EvidenceAsset` check if the underlying offence commands one.

### Finance (`/api/fines`, `/api/payments`)
- **`POST /violations/{violation_id}/assess`**: Traverses the temporal `FineSchedule` resolving the exact fee required for the event based on timestamp, avoiding overlaps. Spawns `FineAssessment`.
- **`POST /webhook/sandbox`**: Idempotent ledger entry orchestration mock handling external payment callbacks. Strictly secured utilizing symmetric signature validation.

### Appeals (`/api/appeals`)
- **`POST /`**: Creates an `Appeal` referencing a `notice_id`.

### Analytics (`/api/analytics`)
- **`GET /dashboard-stats`**: Read-only KPI aggregates.
- **`GET /violation-patterns`**: Analytical python pipeline resolving weekday occurrence ratios mapped securely to the localized timezone embedded inside the violation record.
