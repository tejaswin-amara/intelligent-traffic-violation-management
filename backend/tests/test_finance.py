import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.auth import User, Organisation, Membership
from app.models.domain import Jurisdiction, Person, Vehicle, Driver, Offence, FineSchedule
from app.models.violation import Violation, EvidenceAsset, ReviewDecision
from app.models.finance import FineAssessment, Notice
from app.models.appeals import Appeal
from app.models.payments import Payment, PaymentLedgerEntry, PaymentWebhookEvent
from app.core.security import get_password_hash
import uuid
import json
from datetime import datetime, timezone

SQLALCHEMY_DATABASE_URL = "postgresql://itvm_user:itvm_password@localhost/itvm"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_finance_data():
    db = TestingSessionLocal()

    unique_suffix = str(uuid.uuid4())[:8]
    org_code = f"FIN-ORG-{unique_suffix}"

    org = Organisation(name="Finance Org", code=org_code)
    db.add(org)
    db.commit()

    finance_officer = User(identity_provider="local", identity_subject=f"finance_{unique_suffix}@example.com", email=f"finance_{unique_suffix}@example.com", display_name="Finance Officer", password_hash=get_password_hash("pass"))
    db.add(finance_officer)
    db.commit()
    db.add(Membership(organisation_id=org.id, user_id=finance_officer.id, role="finance_officer"))

    reviewer = User(identity_provider="local", identity_subject=f"reviewer_{unique_suffix}@example.com", email=f"reviewer_{unique_suffix}@example.com", display_name="Reviewer", password_hash=get_password_hash("pass"))
    db.add(reviewer)
    db.commit()
    db.add(Membership(organisation_id=org.id, user_id=reviewer.id, role="reviewer"))
    db.commit()

    jur = Jurisdiction(organisation_id=org.id, name="Fin Jur", code=f"FIN-JUR-{unique_suffix}")
    db.add(jur)
    db.commit()

    offence = Offence(organisation_id=org.id, jurisdiction_id=jur.id, code=f"FIN-OFF-{unique_suffix}", category="Speeding", title="Speeding", description="Speeding", valid_from=datetime(2020, 1, 1, tzinfo=timezone.utc))
    db.add(offence)
    db.commit()

    schedule = FineSchedule(organisation_id=org.id, offence_id=offence.id, version="v1", effective_from=datetime(2020, 1, 1, tzinfo=timezone.utc), amount=100.00, currency_code="USD")
    db.add(schedule)
    db.commit()

    vehicle = Vehicle(organisation_id=org.id, jurisdiction_id=jur.id, registration_display=f"FIN{unique_suffix}", registration_normalised=f"FIN{unique_suffix}", vehicle_class="car")
    db.add(vehicle)
    db.commit()

    violation = Violation(
        organisation_id=org.id,
        jurisdiction_id=jur.id,
        vehicle_id=vehicle.id,
        offence_id=offence.id,
        event_at=datetime(2023, 10, 26, 12, 0, tzinfo=timezone.utc),
        event_timezone="UTC",
        source_type="manual",
        status="approved",
        created_by=finance_officer.id
    )
    db.add(violation)
    db.commit()

    finance_token = client.post("/api/auth/login", data={"username": f"finance_{unique_suffix}@example.com", "password": "pass"}).json()["access_token"]
    reviewer_token = client.post("/api/auth/login", data={"username": f"reviewer_{unique_suffix}@example.com", "password": "pass"}).json()["access_token"]

    yield {"finance_token": finance_token, "reviewer_token": reviewer_token, "org_id": org.id, "vio_id": violation.id}

def test_assess_fine(setup_finance_data):
    token = setup_finance_data["finance_token"]
    vio_id = setup_finance_data["vio_id"]

    response = client.post(
        f"/api/violations/{vio_id}/assess",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["final_amount"] == 100.0
    assert "id" in data

    setup_finance_data["assess_id"] = data["id"]

def test_issue_notice(setup_finance_data):
    token = setup_finance_data["finance_token"]
    assess_id = setup_finance_data["assess_id"]

    response = client.post(
        f"/api/assessments/{assess_id}/issue-notice",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "issued"

    setup_finance_data["notice_id"] = data["id"]

def test_payment_intent_and_webhook(setup_finance_data):
    token = setup_finance_data["finance_token"]
    notice_id = setup_finance_data["notice_id"]
    org_id = setup_finance_data["org_id"]

    idempotency_key = str(uuid.uuid4())

    intent_resp = client.post(
        "/api/payments/intent",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "notice_id": notice_id,
            "amount": 100.0,
            "currency_code": "USD",
            "provider": "sandbox",
            "idempotency_key": idempotency_key
        }
    )
    assert intent_resp.status_code == 201
    payment_id = intent_resp.json()["id"]

    # Webhook
    event_id = str(uuid.uuid4())
    webhook_resp = client.post(
        "/api/payments/webhook/sandbox",
        json={
            "organisation_id": str(org_id),
            "payment_id": payment_id,
            "event_id": event_id,
            "status": "succeeded"
        }
    )
    assert webhook_resp.status_code == 200

    # Duplicate webhook should return 200 but not process
    webhook_resp2 = client.post(
        "/api/payments/webhook/sandbox",
        json={
            "organisation_id": str(org_id),
            "payment_id": payment_id,
            "event_id": event_id,
            "status": "succeeded"
        }
    )
    assert webhook_resp2.status_code == 200
    assert webhook_resp2.json()["status"] == "already_processed"

def test_appeals(setup_finance_data):
    token = setup_finance_data["finance_token"]
    reviewer_token = setup_finance_data["reviewer_token"]
    notice_id = setup_finance_data["notice_id"]

    # Submit
    appeal_resp = client.post(
        "/api/appeals/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "notice_id": notice_id,
            "reason_text": "I was not driving."
        }
    )
    assert appeal_resp.status_code == 201
    appeal_id = appeal_resp.json()["id"]

    # Review
    review_resp = client.post(
        f"/api/appeals/{appeal_id}/review",
        headers={"Authorization": f"Bearer {reviewer_token}"},
        json={
            "decision": "upheld",
            "decision_reason": "Verified driver claim."
        }
    )
    assert review_resp.status_code == 200
    assert review_resp.json()["status"] == "closed"
    assert review_resp.json()["decision"] == "upheld"
