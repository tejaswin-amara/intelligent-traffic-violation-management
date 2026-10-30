# 07 — AI and Evidence Governance

## 1. Scope and boundary

Optional AI tasks may include ANPR/ALPR, image-quality checks, vehicle-type suggestions, event classification and duplicate-candidate detection.

**AI output is not itself a legal finding.** The default workflow requires an authorised human to inspect original evidence and confirm material facts before approval and notice issuance. Any exception requires explicit legal authority, validation and separate operational approval.

## 2. Suggested pipeline

1. Approved source sends event and original media reference.
2. Ingestion validates source identity, event ID, timestamp, media limits, tenant and jurisdiction.
3. Store original media and compute hash.
4. Run content/malware checks and media normalisation in an isolated worker.
5. Run inference and produce structured candidates.
6. Store model name/version, configuration, confidence, preprocessing metadata and input hash.
7. Route by calibrated policy to reviewer queue or quarantine.
8. Reviewer inspects original evidence and accepts, corrects, rejects or marks unusable.
9. Store human decision separately from raw AI output.

## 3. Detection record fields

Capture source system/event ID, jurisdiction, camera/device, event and ingestion timestamps, original evidence ID/hash, model and immutable model digest/version, inference settings, task type, candidate outputs, per-field confidence/uncertainty, bounding boxes/segments, preprocessing/quality flags, review status, reviewer, correction and rationale.

Never overwrite raw model output with reviewer corrections.

## 4. Review policy

- Human review is required by default for high-impact enforcement decisions.
- Evaluate thresholds on representative camera types, plate formats, lighting, weather and road conditions.
- Low-confidence, unreadable, conflicting, occluded or out-of-distribution inputs go to manual review or are rejected as unusable.
- Reviewers must inspect full-resolution original evidence, not only model crops.
- Plate text must be editable; the reviewer must not be forced to accept an AI suggestion.
- Label scores as model confidence, never probability of legal guilt.
- Model failure must not block manual case entry.

## 5. Model evaluation and monitoring

Before pilot:
- lawfully acquire and access-control a representative labelled evaluation set;
- document annotation rules and adjudicate ambiguous samples;
- measure character-level and full-plate exact-match accuracy for ANPR;
- measure precision, recall, false-positive and false-negative rates for each event class;
- review metrics by operating condition and relevant plate subgroup where lawful/statistically meaningful;
- calibrate confidence and select thresholds against error costs and legal risk;
- test blur, glare, rain, night, occlusion, camera angle and format variation;
- document limitations, rollback and disable procedure.

In production monitor input quality, drift, reviewer correction/override, adjudicated false positives, latency and model version. Re-evaluate after camera/environment/jurisdiction/model changes.

## 6. Harm controls

- No face recognition or sensitive-trait inference.
- No individual driver risk scoring or enforcement-propensity ranking.
- No inference of intent or guilt from unrelated personal characteristics.
- Check for material error-rate differences across plate formats/regions/conditions; document and mitigate.
- Preserve evidence/model version and provide an effective appeal path.
- Provide a kill switch for each model/source without disabling manual workflows.

## 7. Evidence provenance and chain of custody

For each asset preserve source and device, capture/ingestion times, source event ID, original filename, declared and detected media type, size, hash, object version/key, uploader/integration, correlation ID, malware scan, transformations/derivatives, and required access/export/redaction/legal-hold/disposal events.

Hashing proves byte-level consistency only. Source authentication and documented handling are also required.

## 8. Model lifecycle

Maintain an approved model register: owner, purpose, data provenance, licence, version/digest, evaluation report, limitations and approval. Pin artefacts by immutable digest. Regression-test before upgrades. Keep rollback. Restrict training data; do not train on operational enforcement records without explicit authority and privacy approval.

## 9. AI enablement checklist

- Written authority and privacy approval for use case/data source.
- Model card/evaluation report approved.
- Representative metrics and subgroup analysis reviewed.
- Human review and role separation verified.
- Evidence provenance/hash tested end-to-end.
- Model/version/output stored immutably.
- Monitoring, incident route, rollback and kill switch tested.
- Appeal process covers AI-assisted evidence and correction history.