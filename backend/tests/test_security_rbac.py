import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.auth import User, Organisation, Membership
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

@pytest.fixture(scope="module", autouse=True)
def setup_rbac_data():
    db = TestingSessionLocal()

    unique_suffix = str(uuid.uuid4())[:8]
    org_code1 = f"RBAC-ORG1-{unique_suffix}"
    org_code2 = f"RBAC-ORG2-{unique_suffix}"

    org1 = Organisation(name="RBAC Org 1", code=org_code1)
    org2 = Organisation(name="RBAC Org 2", code=org_code2)
    db.add_all([org1, org2])
    db.commit()

    # Active User with Role
    active_user = User(
        identity_provider="local",
        identity_subject=f"active_{unique_suffix}@example.com",
        email=f"active_{unique_suffix}@example.com",
        display_name="Active User",
        password_hash=get_password_hash("password123")
    )
    db.add(active_user)
    db.commit()
    db.add(Membership(organisation_id=org1.id, user_id=active_user.id, role="agency_admin"))
    db.commit()

    # Suspended User
    suspended_user = User(
        identity_provider="local",
        identity_subject=f"suspended_{unique_suffix}@example.com",
        email=f"suspended_{unique_suffix}@example.com",
        display_name="Suspended User",
        status="suspended",
        password_hash=get_password_hash("password123")
    )
    db.add(suspended_user)
    db.commit()
    db.add(Membership(organisation_id=org1.id, user_id=suspended_user.id, role="agency_admin"))
    db.commit()

    # User with no memberships
    no_mem_user = User(
        identity_provider="local",
        identity_subject=f"nomem_{unique_suffix}@example.com",
        email=f"nomem_{unique_suffix}@example.com",
        display_name="No Membership User",
        password_hash=get_password_hash("password123")
    )
    db.add(no_mem_user)
    db.commit()

    yield {"suffix": unique_suffix, "org1_id": org1.id}

def test_active_user_login(setup_rbac_data):
    suffix = setup_rbac_data["suffix"]
    response = client.post(
        "/api/auth/login",
        data={"username": f"active_{suffix}@example.com", "password": "password123"}
    )
    assert response.status_code == 200

def test_suspended_user_login(setup_rbac_data):
    suffix = setup_rbac_data["suffix"]
    response = client.post(
        "/api/auth/login",
        data={"username": f"suspended_{suffix}@example.com", "password": "password123"}
    )
    assert response.status_code == 403
    assert "Account is disabled or suspended" in response.json()["detail"]

def test_no_membership_user_login(setup_rbac_data):
    suffix = setup_rbac_data["suffix"]
    # Login should succeed but accessing protected domain API should fail
    response = client.post(
        "/api/auth/login",
        data={"username": f"nomem_{suffix}@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Try creating a vehicle which requires org membership
    resp = client.post(
        "/api/vehicles/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jurisdiction_id": str(uuid.uuid4()),
            "registration": "TEST999",
            "vehicle_class": "car"
        }
    )
    assert resp.status_code == 403
    assert "User has no active organisation membership" in resp.json()["detail"]

def test_invalid_token():
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401

def test_missing_token():
    response = client.get("/api/auth/me")
    assert response.status_code == 401
