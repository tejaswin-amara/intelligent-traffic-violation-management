import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models.auth import User, Organisation, Membership
from app.models.domain import Jurisdiction, Person, Vehicle, Driver, Offence
from app.core.security import get_password_hash
import uuid

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
def token_and_data():
    db = TestingSessionLocal()

    try:
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash text"))
        db.commit()
    except Exception as e:
        db.rollback()

    unique_suffix = str(uuid.uuid4())[:8]
    org_code = f"TEST-{unique_suffix}"

    org = Organisation(name="Test Org", code=org_code)
    db.add(org)
    db.commit()

    user = User(
        identity_provider="local",
        identity_subject=f"test_domain_{unique_suffix}@example.com",
        email=f"test_domain_{unique_suffix}@example.com",
        display_name="Test Domain User",
        password_hash=get_password_hash("password123")
    )
    db.add(user)
    db.commit()

    mem = Membership(organisation_id=org.id, user_id=user.id, role="agency_admin")
    db.add(mem)
    db.commit()

    jur = Jurisdiction(organisation_id=org.id, name="Test Jurisdiction", code=f"JUR-{unique_suffix}")
    db.add(jur)
    db.commit()

    person = Person(organisation_id=org.id, full_name=f"John Doe {unique_suffix}")
    db.add(person)
    db.commit()

    login_resp = client.post(
        "/api/auth/login",
        data={"username": f"test_domain_{unique_suffix}@example.com", "password": "password123"}
    )
    token = login_resp.json()["access_token"]

    yield {"token": token, "org_id": str(org.id), "jurisdiction_id": str(jur.id), "person_id": str(person.id)}

def test_create_vehicle(token_and_data):
    token = token_and_data["token"]
    jur_id = token_and_data["jurisdiction_id"]

    response = client.post(
        "/api/vehicles/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jurisdiction_id": jur_id,
            "registration": "AB12CDE",
            "vehicle_class": "car",
            "make": "Toyota",
            "model": "Corolla",
            "colour": "Blue"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["registration_normalised"] == "AB12CDE"
    assert data["vehicle_class"] == "car"

def test_get_vehicles(token_and_data):
    token = token_and_data["token"]
    response = client.get(
        "/api/vehicles/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_create_driver(token_and_data):
    token = token_and_data["token"]
    person_id = token_and_data["person_id"]

    response = client.post(
        "/api/drivers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "person_id": person_id,
            "licence_number": "LIC-987654321",
            "issuing_authority": "Test Authority",
            "licence_class": "car"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["issuing_authority"] == "Test Authority"

def test_create_offence(token_and_data):
    token = token_and_data["token"]
    jur_id = token_and_data["jurisdiction_id"]

    response = client.post(
        "/api/offences/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jurisdiction_id": jur_id,
            "code": "SPEED-01",
            "category": "Speeding",
            "title": "Exceeding Speed Limit",
            "description": "Driving above the posted speed limit."
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SPEED-01"
