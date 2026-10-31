import sys
import os
import uuid
import datetime
import pytz
from cryptography.fernet import Fernet

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.auth import Organisation, User, Membership
from app.models.domain import Jurisdiction, Person, Driver, Vehicle, Offence, FineSchedule
from app.core.security import get_password_hash
from app.api.drivers import encrypt_licence, get_licence_hmac

db = SessionLocal()

def seed():
    print("Seeding demo data...")

    # 1. Organization
    org = db.query(Organisation).filter_by(code="DEMO-ORG").first()
    if not org:
        org = Organisation(name="Demonstration Agency", code="DEMO-ORG")
        db.add(org)
        db.commit()
        db.refresh(org)

    # 2. Users
    user = db.query(User).filter_by(email="demo@example.com").first()
    if not user:
        user = User(
            identity_provider="local",
            identity_subject="demo",
            email="demo@example.com",
            display_name="Demo Reviewer",
            password_hash=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        mem = Membership(
            organisation_id=org.id,
            user_id=user.id,
            role="agency_admin",
            status="active"
        )
        db.add(mem)
        db.commit()

    # 3. Jurisdiction
    jurisdiction = db.query(Jurisdiction).filter_by(code="DEMO-JUR").first()
    if not jurisdiction:
        jurisdiction = Jurisdiction(
            organisation_id=org.id,
            name="Demo City",
            code="DEMO-JUR",
            timezone="UTC"
        )
        db.add(jurisdiction)
        db.commit()
        db.refresh(jurisdiction)

    # 4. Offence & Fine Schedule
    offence = db.query(Offence).filter_by(code="SPEED-1").first()
    if not offence:
        offence = Offence(
            organisation_id=org.id,
            jurisdiction_id=jurisdiction.id,
            code="SPEED-1",
            category="Speeding",
            title="Exceeding Speed Limit by 1-10km/h",
            description="Driving slightly above the limit.",
            evidence_required=True
        )
        db.add(offence)
        db.commit()
        db.refresh(offence)

        schedule = FineSchedule(
            organisation_id=org.id,
            offence_id=offence.id,
            version="1.0",
            effective_from=datetime.datetime(2020, 1, 1, tzinfo=pytz.UTC),
            amount=50.00,
            currency_code="USD",
            approved_by=user.id,
            approved_at=datetime.datetime.now(pytz.UTC)
        )
        db.add(schedule)
        db.commit()

    # 5. Person & Driver
    person = db.query(Person).filter_by(full_name="John Doe").first()
    if not person:
        person = Person(
            organisation_id=org.id,
            full_name="John Doe"
        )
        db.add(person)
        db.commit()
        db.refresh(person)

        licence = "DL-12345"
        driver = Driver(
            organisation_id=org.id,
            person_id=person.id,
            licence_last4=licence[-4:],
            issuing_authority="Demo Authority",
            licence_class="C",
            licence_number_ciphertext=encrypt_licence(licence),
            licence_lookup_hmac=get_licence_hmac(licence)
        )
        db.add(driver)
        db.commit()

    # 6. Vehicle
    vehicle = db.query(Vehicle).filter_by(registration_normalised="XYZ987").first()
    if not vehicle:
        vehicle = Vehicle(
            organisation_id=org.id,
            jurisdiction_id=jurisdiction.id,
            registration_display="XYZ 987",
            registration_normalised="XYZ987",
            vehicle_class="Car",
            make="Toyota",
            model="Corolla",
            colour="Silver"
        )
        db.add(vehicle)
        db.commit()

    print("Demo data seeded successfully.")

if __name__ == "__main__":
    seed()
