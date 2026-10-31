# INNOVATION & OPTIMIZATION (CO5)

## 1. Temporal Fine Scheduling
**Problem:** Legislative fines change over time. If a fine algorithm updates globally, recalculating an older notice historically overwrites reality.
**Solution:** The system traverses a temporal table mapping (`effective_from`, `effective_until`) strictly against the violation's `event_at`. The snapshot is stored directly inside the generated `FineAssessment`.

## 2. Strong Cryptographic Licensing
**Problem:** PII leakage via Database dumps (specifically driver licence numbers).
**Solution:** Implementation avoids storing the raw driver license. Instead, the backend leverages authenticated encryption (AES via `cryptography.fernet`) for full recovery by authorised personnel, alongside a strict keyed HMAC (`hashlib.sha256`) index utilized explicitly for deterministic equality matching searches without decryption overhead.

## 3. Strict Webhook Idempotency & Signatures
**Problem:** Double-charging or duplicate network transmission.
**Solution:** Webhooks are required to provide a cryptographic symmetric signature header to authorize external integration callbacks. The backend then records `PaymentWebhookEvent` hashes mapped back to single-ledger insertions preventing duplicate data.

## 4. Timezone-Aware Analytic Distributions
**Problem:** Aggregating data purely at UTC corrupts analytic understanding of localized traffic violations.
**Solution:** The analytics engine explicitly converts UTC rows to local `event_timezone` objects dynamically utilizing `pytz` prior to sorting them into localized weekday matrices natively on the server layer.
