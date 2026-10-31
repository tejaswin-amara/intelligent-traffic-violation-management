# DATABASE OPERATIONS (CO2)

## Representative SQL Queries

### 1. Listing Pending Violations for Review Workbench
```sql
SELECT id, status, event_at
FROM violations
WHERE organisation_id = 'org-uuid'
  AND status IN ('draft', 'needs_information')
ORDER BY event_at DESC;
```

### 2. Fine Schedule Temporal Evaluation (Avoiding Ambiguity)
```sql
-- Determines the exact financial schedule snapshot to apply
SELECT id, amount, currency_code
FROM fine_schedules
WHERE organisation_id = 'org-uuid'
  AND offence_id = 'offence-uuid'
  AND effective_from <= '2026-10-30T10:00:00Z'
  AND (effective_until > '2026-10-30T10:00:00Z' OR effective_until IS NULL);
```

### 3. Dashboard Statistics Aggregation
```sql
SELECT
  (SELECT COUNT(*) FROM vehicles WHERE organisation_id = 'org-uuid') as total_vehicles,
  (SELECT COUNT(*) FROM violations WHERE organisation_id = 'org-uuid' AND status IN ('draft', 'submitted')) as active_violations;
```

### 4. Deterministic Identity Hashing Check
```sql
SELECT id, person_id
FROM drivers
WHERE organisation_id = 'org-uuid'
  AND licence_lookup_hmac = 'secure-hash-digest-bytes';
```

## Setup & Migrations
The ITVM relies heavily on `alembic`. Developers trigger standard operations using:
- `alembic upgrade head`: Bring DB up to latest transactional DDL requirements.
