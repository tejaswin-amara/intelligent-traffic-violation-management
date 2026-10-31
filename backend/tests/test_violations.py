import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.auth import User, Organisation, Membership
from app.models.domain import Jurisdiction, Person, Vehicle, Driver, Offence
from app.models.violation import Violation, EvidenceAsset, ReviewDecision
from app.core.security import get_password_hash
import uuid
import json

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
def setup_violation_data():
    db = TestingSessionLocal()

    unique_suffix = str(uuid.uuid4())[:8]
    org_code = f"VIO-ORG-{unique_suffix}"

    org = Organisation(name="Vio Org", code=org_code)
    db.add(org)
    db.commit()

    # Users
    officer = User(identity_provider="local", identity_subject=f"officer_{unique_suffix}@example.com", email=f"officer_{unique_suffix}@example.com", display_name="Officer", password_hash=get_password_hash("pass"))
    db.add(officer)
    db.commit()
    db.add(Membership(organisation_id=org.id, user_id=officer.id, role="enforcement_officer"))
    db.commit()

    reviewer = User(identity_provider="local", identity_subject=f"reviewer_{unique_suffix}@example.com", email=f"reviewer_{unique_suffix}@example.com", display_name="Reviewer", password_hash=get_password_hash("pass"))
    db.add(reviewer)
    db.commit()
    # Fixed the role to exactly match the CHECK constraint in database
    db.add(Membership(organisation_id=org.id, user_id=reviewer.id, role="reviewer"))
    db.commit()

    # Reference data
    jur = Jurisdiction(organisation_id=org.id, name="Vio Jur", code=f"VIO-JUR-{unique_suffix}")
    db.add(jur)
    db.commit()

    offence = Offence(organisation_id=org.id, jurisdiction_id=jur.id, code=f"VIO-OFF-{unique_suffix}", category="Speeding", title="Speeding", description="Speeding")
    db.add(offence)
    db.commit()

    person = Person(organisation_id=org.id, full_name="John Vio")
    db.add(person)
    db.commit()

    vehicle = Vehicle(organisation_id=org.id, jurisdiction_id=jur.id, registration_display=f"VIO{unique_suffix}", registration_normalised=f"VIO{unique_suffix}", vehicle_class="car")
    db.add(vehicle)
    db.commit()

    officer_token = client.post("/api/auth/login", data={"username": f"officer_{unique_suffix}@example.com", "password": "pass"}).json()["access_token"]
    reviewer_token = client.post("/api/auth/login", data={"username": f"reviewer_{unique_suffix}@example.com", "password": "pass"}).json()["access_token"]

    yield {"officer_token": officer_token, "reviewer_token": reviewer_token, "org_id": org.id, "jur_id": jur.id, "veh_id": vehicle.id, "off_id": offence.id}

def test_create_violation(setup_violation_data):
    token = setup_violation_data["officer_token"]
    response = client.post(
        "/api/violations/",
        headers={"Authorization": f"Bearer {token}", "X-Organisation-ID": str(setup_violation_data["org_id"])},
        json={
            "jurisdiction_id": str(setup_violation_data["jur_id"]),
            "vehicle_id": str(setup_violation_data["veh_id"]),
            "offence_id": str(setup_violation_data["off_id"]),
            "event_at": "2023-10-26T12:00:00Z",
            "event_timezone": "UTC"
        }
    )
    assert response.status_code == 201
    assert response.json()["status"] == "draft"

def test_upload_evidence(setup_violation_data):
    token = setup_violation_data["officer_token"]
    # Get the violation we just created
    resp = client.get("/api/violations/", headers={"Authorization": f"Bearer {token}", "X-Organisation-ID": str(setup_violation_data["org_id"])})
    vio_id = resp.json()[0]["id"]

    response = client.post(
        f"/api/violations/{vio_id}/evidence",
        headers={"Authorization": f"Bearer {token}", "X-Organisation-ID": str(setup_violation_data["org_id"])},
        data={"asset_kind": "image"},
        files={"file": ("test.jpg", b"fake_image_content", "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["asset_kind"] == "image"
    assert data["sha256_hex"] is not None

def test_reviewer_approve_violation(setup_violation_data):
    officer_token = setup_violation_data["officer_token"]
    reviewer_token = setup_violation_data["reviewer_token"]

    # Needs to be a reviewer reviewing a case THEY didn't create
    # Let's create a NEW violation specifically for testing approval,
    # to avoid state issues from other tests
    response = client.post(
        "/api/violations/",
        headers={"Authorization": f"Bearer {officer_token}", "X-Organisation-ID": str(setup_violation_data["org_id"])},
        json={
            "jurisdiction_id": str(setup_violation_data["jur_id"]),
            "vehicle_id": str(setup_violation_data["veh_id"]),
            "offence_id": str(setup_violation_data["off_id"]),
            "event_at": "2023-10-26T12:00:00Z",
            "event_timezone": "UTC"
        }
    )
    vio_id = response.json()["id"]

    # Creator cannot approve
    bad_resp = client.post(
        f"/api/violations/{vio_id}/review",
        headers={"Authorization": f"Bearer {officer_token}", "X-Organisation-ID": str(setup_violation_data["org_id"])},
        json={"decision": "approved", "rationale": "Looks good"}
    )
    assert bad_resp.status_code == 403

    # Reviewer can approve
    good_resp = client.post(
        f"/api/violations/{vio_id}/review",
        headers={"Authorization": f"Bearer {reviewer_token}", "X-Organisation-ID": str(setup_violation_data["org_id"])},
        json={"decision": "approved", "rationale": "Looks good"}
    )
    if good_resp.status_code != 200:
        print("ERROR:", good_resp.json())
    assert good_resp.status_code == 200
    assert good_resp.json()["status"] == "approved"
