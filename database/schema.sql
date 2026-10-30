-- ITVM starter schema for PostgreSQL 15+
-- Review and apply through versioned migrations. Not production-ready as-is.
-- Add RLS, range-overlap constraints, retention and outbox tables before launch.

CREATE TABLE organisations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  code text NOT NULL UNIQUE,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended','archived')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  identity_provider text NOT NULL,
  identity_subject text NOT NULL,
  email text,
  display_name text NOT NULL,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended','disabled')),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (identity_provider, identity_subject)
);

CREATE TABLE memberships (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  user_id uuid NOT NULL REFERENCES users(id),
  role text NOT NULL CHECK (role IN ('agency_admin','enforcement_officer','reviewer','finance_officer','auditor','support_readonly')),
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended','expired')),
  valid_from timestamptz NOT NULL DEFAULT now(),
  valid_until timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organisation_id, user_id, role),
  UNIQUE (id, organisation_id),
  CHECK (valid_until IS NULL OR valid_until > valid_from)
);
CREATE INDEX memberships_user_idx ON memberships(user_id, status);

CREATE TABLE jurisdictions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  code text NOT NULL,
  name text NOT NULL,
  country_code char(2),
  timezone text NOT NULL,
  currency_code char(3) NOT NULL,
  policy_version text,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organisation_id, code),
  UNIQUE (id, organisation_id)
);

CREATE TABLE persons (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  full_name text NOT NULL,
  contact_email_ciphertext bytea,
  contact_phone_ciphertext bytea,
  source_system text,
  source_reference text,
  verification_status text NOT NULL DEFAULT 'unverified' CHECK (verification_status IN ('unverified','verified','conflicted','stale')),
  verified_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (id, organisation_id)
);

CREATE TABLE drivers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  person_id uuid NOT NULL,
  licence_number_ciphertext bytea,
  licence_lookup_hmac bytea,
  licence_last4 text,
  issuing_authority text,
  licence_class text,
  licence_status text NOT NULL DEFAULT 'unknown' CHECK (licence_status IN ('valid','suspended','revoked','expired','unknown','unverified')),
  source_system text,
  verified_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (person_id, organisation_id) REFERENCES persons(id, organisation_id),
  UNIQUE (id, organisation_id)
);
CREATE INDEX drivers_licence_lookup_idx ON drivers(organisation_id, licence_lookup_hmac) WHERE licence_lookup_hmac IS NOT NULL;

CREATE TABLE vehicles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  jurisdiction_id uuid NOT NULL,
  registration_display text NOT NULL,
  registration_normalised text NOT NULL,
  vehicle_class text,
  make text,
  model text,
  colour text,
  model_year integer CHECK (model_year IS NULL OR model_year BETWEEN 1886 AND 2200),
  registry_reference text,
  verification_status text NOT NULL DEFAULT 'unverified' CHECK (verification_status IN ('unverified','verified','conflicted','stale')),
  source_system text,
  verified_at timestamptz,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive','impounded','scrapped','unknown')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (jurisdiction_id, organisation_id) REFERENCES jurisdictions(id, organisation_id),
  UNIQUE (id, organisation_id),
  UNIQUE (organisation_id, jurisdiction_id, registration_normalised)
);
CREATE INDEX vehicles_registration_idx ON vehicles(organisation_id, jurisdiction_id, registration_normalised);

CREATE TABLE vehicle_ownerships (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  vehicle_id uuid NOT NULL,
  person_id uuid NOT NULL,
  valid_from timestamptz NOT NULL,
  valid_until timestamptz,
  source_system text,
  source_reference text,
  verified_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (vehicle_id, organisation_id) REFERENCES vehicles(id, organisation_id),
  FOREIGN KEY (person_id, organisation_id) REFERENCES persons(id, organisation_id),
  CHECK (valid_until IS NULL OR valid_until > valid_from)
);
CREATE INDEX vehicle_ownership_lookup_idx ON vehicle_ownerships(organisation_id, vehicle_id, valid_from DESC);

CREATE TABLE offences (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  jurisdiction_id uuid NOT NULL,
  code text NOT NULL,
  title text NOT NULL,
  description text NOT NULL,
  category text NOT NULL,
  required_evidence jsonb NOT NULL DEFAULT '[]'::jsonb,
  applicable_vehicle_classes text[] NOT NULL DEFAULT '{}',
  valid_from timestamptz NOT NULL,
  valid_until timestamptz,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive','retired')),
  official_source_reference text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (jurisdiction_id, organisation_id) REFERENCES jurisdictions(id, organisation_id),
  UNIQUE (id, organisation_id),
  UNIQUE (organisation_id, jurisdiction_id, code, valid_from),
  CHECK (valid_until IS NULL OR valid_until > valid_from)
);
CREATE INDEX offences_active_idx ON offences(organisation_id, jurisdiction_id, code, valid_from DESC);

CREATE TABLE fine_schedules (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  offence_id uuid NOT NULL,
  version text NOT NULL,
  vehicle_class text NOT NULL DEFAULT '*',
  amount numeric(14,2) NOT NULL CHECK (amount >= 0),
  currency_code char(3) NOT NULL,
  modifiers jsonb NOT NULL DEFAULT '{}'::jsonb,
  effective_from timestamptz NOT NULL,
  effective_until timestamptz,
  official_source_reference text NOT NULL,
  approved_by uuid REFERENCES users(id),
  approved_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (offence_id, organisation_id) REFERENCES offences(id, organisation_id),
  UNIQUE (id, organisation_id),
  UNIQUE (organisation_id, offence_id, version, vehicle_class),
  CHECK (effective_until IS NULL OR effective_until > effective_from)
);
CREATE INDEX fine_schedule_effective_idx ON fine_schedules(organisation_id, offence_id, effective_from DESC);

CREATE TABLE violations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  jurisdiction_id uuid NOT NULL,
  vehicle_id uuid NOT NULL,
  driver_id uuid,
  offence_id uuid NOT NULL,
  event_at timestamptz NOT NULL,
  event_timezone text NOT NULL,
  location_text text,
  latitude numeric(9,6) CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
  longitude numeric(9,6) CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
  source_type text NOT NULL CHECK (source_type IN ('manual','camera','registry_import','partner_api','other')),
  source_system text,
  source_event_id text,
  status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','submitted','under_review','needs_information','approved','rejected','notice_issued','payment_pending','paid','appealed','appeal_upheld','appeal_rejected','cancelled','closed')),
  assigned_to uuid REFERENCES users(id),
  created_by uuid NOT NULL REFERENCES users(id),
  submitted_at timestamptz,
  closed_at timestamptz,
  summary text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (jurisdiction_id, organisation_id) REFERENCES jurisdictions(id, organisation_id),
  FOREIGN KEY (vehicle_id, organisation_id) REFERENCES vehicles(id, organisation_id),
  FOREIGN KEY (driver_id, organisation_id) REFERENCES drivers(id, organisation_id),
  FOREIGN KEY (offence_id, organisation_id) REFERENCES offences(id, organisation_id),
  UNIQUE (id, organisation_id)
);
CREATE UNIQUE INDEX violations_source_event_unique ON violations(organisation_id, source_system, source_event_id)
  WHERE source_system IS NOT NULL AND source_event_id IS NOT NULL;
CREATE INDEX violations_queue_idx ON violations(organisation_id, status, event_at DESC);
CREATE INDEX violations_vehicle_event_idx ON violations(organisation_id, vehicle_id, event_at DESC);

CREATE TABLE evidence_assets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  violation_id uuid NOT NULL,
  original_asset_id uuid,
  asset_kind text NOT NULL CHECK (asset_kind IN ('image','video','document','metadata','redacted_derivative')),
  object_key text NOT NULL UNIQUE,
  original_filename text,
  media_type text NOT NULL,
  byte_size bigint NOT NULL CHECK (byte_size >= 0),
  sha256_hex char(64) NOT NULL,
  captured_at timestamptz,
  ingested_at timestamptz NOT NULL DEFAULT now(),
  source_device text,
  uploader_user_id uuid REFERENCES users(id),
  uploader_source text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  scan_status text NOT NULL DEFAULT 'pending' CHECK (scan_status IN ('pending','clean','quarantined','failed','not_applicable')),
  retention_until timestamptz,
  legal_hold boolean NOT NULL DEFAULT false,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','quarantined','expired','disposed')),
  FOREIGN KEY (violation_id, organisation_id) REFERENCES violations(id, organisation_id),
  UNIQUE (id, organisation_id),
  FOREIGN KEY (original_asset_id, organisation_id) REFERENCES evidence_assets(id, organisation_id)
);
CREATE INDEX evidence_violation_idx ON evidence_assets(organisation_id, violation_id, ingested_at);

CREATE TABLE detection_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  violation_id uuid,
  input_evidence_id uuid NOT NULL,
  model_name text NOT NULL,
  model_version text NOT NULL,
  model_digest text,
  task_type text NOT NULL,
  confidence numeric(7,6) CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
  output jsonb NOT NULL,
  processing_status text NOT NULL CHECK (processing_status IN ('queued','running','succeeded','failed','review_required')),
  reviewed_by uuid REFERENCES users(id),
  reviewed_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (violation_id, organisation_id) REFERENCES violations(id, organisation_id),
  FOREIGN KEY (input_evidence_id, organisation_id) REFERENCES evidence_assets(id, organisation_id)
);
CREATE INDEX detection_violation_idx ON detection_runs(organisation_id, violation_id, created_at DESC);

CREATE TABLE review_decisions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  violation_id uuid NOT NULL,
  decision text NOT NULL CHECK (decision IN ('approved','rejected','needs_information','reopened','cancelled')),
  rationale text NOT NULL,
  actor_user_id uuid NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (violation_id, organisation_id) REFERENCES violations(id, organisation_id)
);
CREATE INDEX review_decisions_violation_idx ON review_decisions(organisation_id, violation_id, created_at);

CREATE TABLE fine_assessments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  violation_id uuid NOT NULL,
  fine_schedule_id uuid NOT NULL,
  schedule_version text NOT NULL,
  base_amount numeric(14,2) NOT NULL CHECK (base_amount >= 0),
  adjustments jsonb NOT NULL DEFAULT '[]'::jsonb,
  final_amount numeric(14,2) NOT NULL CHECK (final_amount >= 0),
  currency_code char(3) NOT NULL,
  calculation_snapshot jsonb NOT NULL,
  assessed_by uuid NOT NULL REFERENCES users(id),
  assessed_at timestamptz NOT NULL DEFAULT now(),
  supersedes_assessment_id uuid,
  FOREIGN KEY (violation_id, organisation_id) REFERENCES violations(id, organisation_id),
  FOREIGN KEY (fine_schedule_id, organisation_id) REFERENCES fine_schedules(id, organisation_id),
  FOREIGN KEY (supersedes_assessment_id, organisation_id) REFERENCES fine_assessments(id, organisation_id),
  UNIQUE (id, organisation_id)
);

CREATE TABLE notices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  violation_id uuid NOT NULL,
  fine_assessment_id uuid NOT NULL,
  public_reference_hash bytea NOT NULL UNIQUE,
  public_reference_last4 text NOT NULL,
  recipient_person_id uuid,
  issued_at timestamptz NOT NULL,
  due_at timestamptz,
  status text NOT NULL CHECK (status IN ('issued','cancelled','superseded','closed')),
  rendered_document_key text,
  notice_snapshot jsonb NOT NULL,
  issued_by uuid NOT NULL REFERENCES users(id),
  cancellation_reason text,
  cancelled_at timestamptz,
  FOREIGN KEY (violation_id, organisation_id) REFERENCES violations(id, organisation_id),
  FOREIGN KEY (fine_assessment_id, organisation_id) REFERENCES fine_assessments(id, organisation_id),
  FOREIGN KEY (recipient_person_id, organisation_id) REFERENCES persons(id, organisation_id),
  UNIQUE (id, organisation_id)
);
CREATE INDEX notices_violation_idx ON notices(organisation_id, violation_id, issued_at DESC);

CREATE TABLE payments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  notice_id uuid NOT NULL,
  provider text NOT NULL,
  provider_payment_reference text,
  idempotency_key text NOT NULL,
  amount numeric(14,2) NOT NULL CHECK (amount > 0),
  currency_code char(3) NOT NULL,
  status text NOT NULL CHECK (status IN ('created','pending','succeeded','failed','reversed','refunded','partially_refunded','reconciliation_exception')),
  initiated_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz,
  provider_payload_redacted jsonb NOT NULL DEFAULT '{}'::jsonb,
  FOREIGN KEY (notice_id, organisation_id) REFERENCES notices(id, organisation_id),
  UNIQUE (organisation_id, provider, idempotency_key),
  UNIQUE (id, organisation_id)
);
CREATE UNIQUE INDEX payments_provider_reference_unique ON payments(provider, provider_payment_reference)
  WHERE provider_payment_reference IS NOT NULL;
CREATE INDEX payments_notice_idx ON payments(organisation_id, notice_id, initiated_at DESC);

-- Append-only financial movements provide an auditable basis for balance calculations.
CREATE TABLE payment_ledger_entries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  notice_id uuid NOT NULL,
  payment_id uuid,
  entry_type text NOT NULL CHECK (entry_type IN (
    'payment_credit','refund_debit','reversal_debit','authorised_adjustment','writeoff'
  )),
  amount numeric(14,2) NOT NULL CHECK (amount > 0),
  currency_code char(3) NOT NULL,
  provider_event_reference text,
  reason text,
  actor_user_id uuid REFERENCES users(id),
  occurred_at timestamptz NOT NULL DEFAULT now(),
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (notice_id, organisation_id) REFERENCES notices(id, organisation_id),
  FOREIGN KEY (payment_id, organisation_id) REFERENCES payments(id, organisation_id)
);
CREATE INDEX payment_ledger_notice_idx
  ON payment_ledger_entries(organisation_id, notice_id, occurred_at);

CREATE TABLE payment_webhook_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  provider text NOT NULL,
  provider_event_id text NOT NULL,
  received_at timestamptz NOT NULL DEFAULT now(),
  signature_valid boolean NOT NULL,
  processing_status text NOT NULL CHECK (processing_status IN ('received','processed','duplicate','rejected','failed')),
  payload_redacted jsonb NOT NULL DEFAULT '{}'::jsonb,
  processed_at timestamptz,
  UNIQUE (organisation_id, provider, provider_event_id)
);

CREATE TABLE appeals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  notice_id uuid NOT NULL,
  appellant_person_id uuid,
  reason_code text,
  reason_text text NOT NULL,
  status text NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted','under_review','needs_information','upheld','rejected','withdrawn','closed')),
  filed_at timestamptz NOT NULL DEFAULT now(),
  assigned_to uuid REFERENCES users(id),
  decision text CHECK (decision IS NULL OR decision IN ('upheld','rejected','reduced','remanded')),
  decision_reason text,
  decided_by uuid REFERENCES users(id),
  decided_at timestamptz,
  FOREIGN KEY (notice_id, organisation_id) REFERENCES notices(id, organisation_id),
  FOREIGN KEY (appellant_person_id, organisation_id) REFERENCES persons(id, organisation_id),
  UNIQUE (id, organisation_id)
);
CREATE INDEX appeals_queue_idx ON appeals(organisation_id, status, filed_at);

CREATE TABLE notifications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  notice_id uuid,
  appeal_id uuid,
  channel text NOT NULL CHECK (channel IN ('email','sms','push','letter','other')),
  template_key text NOT NULL,
  destination_masked text,
  provider_reference text,
  status text NOT NULL CHECK (status IN ('queued','sent','delivered','failed','cancelled')),
  attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
  last_error_code text,
  created_at timestamptz NOT NULL DEFAULT now(),
  sent_at timestamptz,
  FOREIGN KEY (notice_id, organisation_id) REFERENCES notices(id, organisation_id),
  FOREIGN KEY (appeal_id, organisation_id) REFERENCES appeals(id, organisation_id)
);

CREATE TABLE audit_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid NOT NULL REFERENCES organisations(id),
  actor_user_id uuid REFERENCES users(id),
  actor_type text NOT NULL CHECK (actor_type IN ('user','system','integration')),
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id uuid,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  correlation_id text,
  reason text,
  before_snapshot jsonb,
  after_snapshot jsonb,
  source_ip inet,
  user_agent text
);
CREATE INDEX audit_entity_idx ON audit_events(organisation_id, entity_type, entity_id, occurred_at DESC);
CREATE INDEX audit_time_idx ON audit_events(organisation_id, occurred_at DESC);

-- Production hardening still required:
-- 1. Enable/test row-level security for every tenant-owned table.
-- 2. Add exclusion constraints for overlapping ownership/schedule validity periods.
-- 3. Restrict UPDATE/DELETE on audit_events and review_decisions to a separately controlled role.
-- 4. Add updated_at triggers or set updated_at consistently in application services.
-- 5. Add transactional outbox, import-batch, reconciliation-batch and legal-hold event tables.
-- 6. Enforce same-organisation constraints on every future cross-reference.
-- 7. Configure encryption, backup, retention and object-store lifecycle policies.
-- 8. Keep payment-ledger rows append-only; grant mutation only to controlled migration/maintenance roles.
