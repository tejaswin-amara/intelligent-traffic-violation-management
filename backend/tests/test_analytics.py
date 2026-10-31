import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.auth import User, Organisation, Membership
from app.models.domain import Jurisdiction, Person, Vehicle, Driver, Offence, FineSchedule
from app.models.violation import Violation, EvidenceAsset, ReviewDecision
from app.core.security import get_password_hash
import uuid
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
def setup_analytics_data():
    db = TestingSessionLocal()

    unique_suffix = str(uuid.uuid4())[:8]
    org_code = f"ANALYTICS-ORG-{unique_suffix}"

    org = Organisation(name="Analytics Org", code=org_code)
    db.add(org)
    db.commit()

    officer = User(identity_provider="local", identity_subject=f"officer_{unique_suffix}@example.com", email=f"officer_{unique_suffix}@example.com", display_name="Officer", password_hash=get_password_hash("pass"))
    db.add(officer)
    db.commit()
    db.add(Membership(organisation_id=org.id, user_id=officer.id, role="enforcement_officer"))
    db.commit()

    jur = Jurisdiction(organisation_id=org.id, name="Ana Jur", code=f"ANA-JUR-{unique_suffix}")
    db.add(jur)
    db.commit()

    offence = Offence(organisation_id=org.id, jurisdiction_id=jur.id, code=f"ANA-OFF-{unique_suffix}", category="Speeding", title="Speeding", description="Speeding", valid_from=datetime(2020, 1, 1, tzinfo=timezone.utc))
    person = Person(organisation_id=org.id, full_name="John Ana")
    db.add_all([offence, person])
    db.commit()

    vehicle = Vehicle(organisation_id=org.id, jurisdiction_id=jur.id, registration_display=f"ANA{unique_suffix}", registration_normalised=f"ANA{unique_suffix}", vehicle_class="car")
    db.add(vehicle)
    db.commit()

    violation = Violation(
        organisation_id=org.id,
        jurisdiction_id=jur.id,
        vehicle_id=vehicle.id,
        offence_id=offence.id,
        event_at=datetime(2023, 10, 26, 12, 0, tzinfo=timezone.utc), # Thursday
        event_timezone="UTC",
        source_type="camera",
        status="draft",
        created_by=officer.id
    )
    db.add(violation)
    db.commit()

    officer_token = client.post("/api/auth/login", data={"username": f"officer_{unique_suffix}@example.com", "password": "pass"}).json()["access_token"]

    yield {"officer_token": officer_token, "org_id": org.id}


def test_get_dashboard_stats(setup_analytics_data):
    token = setup_analytics_data["officer_token"]

    response = client.get(
        "/api/analytics/dashboard-stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_vehicles"] == 1
    assert data["active_violations"] == 1

def test_get_violation_patterns(setup_analytics_data):
    token = setup_analytics_data["officer_token"]

    response = client.get(
        "/api/analytics/violation-patterns",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_analyzed"] == 1
    assert data["by_day_of_week"]["Thursday"] == 1
    assert data["by_source_type"]["camera"] == 1
