import re

with open('backend/tests/test_finance.py', 'r') as f:
    content = f.read()

# I need to properly write the test with the signature header.
content = re.sub(
r'''    # Webhook
    event_id = str\(uuid.uuid4\(\)\)
    import hmac, hashlib, json; payload = json.dumps\(\{"organisation_id": str\(org_id\), "payment_id": payment_id, "event_id": event_id, "status": "succeeded"\}\).encode\("utf-8"\); sig = hmac.new\(b"super_secret_key_for_local_dev_only", payload, hashlib.sha256\).hexdigest\(\); webhook_resp = client.post\(
        "/api/payments/webhook/sandbox",
        json=\{
            "organisation_id": str\(org_id\),
            "payment_id": payment_id,
            "event_id": event_id,
            "status": "succeeded"
        \}
    \)
    assert webhook_resp.status_code == 200

    # Duplicate webhook should return 200 but not process
    webhook_resp2 = client.post\(
        "/api/payments/webhook/sandbox",
        json=\{
            "organisation_id": str\(org_id\),
            "payment_id": payment_id,
            "event_id": event_id,
            "status": "succeeded"
        \}
    \)''',
r'''    # Webhook
    import hmac, hashlib, json
    event_id = str(uuid.uuid4())
    payload_dict = {
        "organisation_id": str(org_id),
        "payment_id": payment_id,
        "event_id": event_id,
        "status": "succeeded"
    }
    payload_bytes = json.dumps(payload_dict).encode("utf-8")
    sig = hmac.new(b"super_secret_key_for_local_dev_only", payload_bytes, hashlib.sha256).hexdigest()

    webhook_resp = client.post(
        "/api/payments/webhook/sandbox",
        content=payload_bytes,
        headers={"X-Signature": sig, "Content-Type": "application/json"}
    )
    assert webhook_resp.status_code == 200

    # Duplicate webhook should return 200 but not process
    webhook_resp2 = client.post(
        "/api/payments/webhook/sandbox",
        content=payload_bytes,
        headers={"X-Signature": sig, "Content-Type": "application/json"}
    )''', content)

with open('backend/tests/test_finance.py', 'w') as f:
    f.write(content)
