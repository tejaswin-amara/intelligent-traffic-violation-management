from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import uuid
import hmac
import hashlib
import base64
from cryptography.fernet import Fernet

from ..core.database import get_db
from ..core.config import settings
from ..models.domain import Driver, Person
from ..schemas.domain import DriverCreate, DriverResponse
from .auth import get_current_user, get_current_active_organisation
from ..models.auth import User, Membership

router = APIRouter()

def get_crypto_key():
    # Use the 32-byte url-safe base64-encoded key from settings
    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY must be set in environment")
    return settings.ENCRYPTION_KEY.encode('utf-8')

def encrypt_licence(licence_number: str) -> bytes:
    key = get_crypto_key()
    f = Fernet(key)
    return f.encrypt(licence_number.encode('utf-8'))

def decrypt_licence(ciphertext: bytes) -> str:
    key = get_crypto_key()
    f = Fernet(key)
    return f.decrypt(ciphertext).decode('utf-8')

def get_licence_hmac(licence_number: str) -> bytes:
    # Use SECRET_KEY for HMAC for deterministic lookup
    secret = settings.SECRET_KEY.encode('utf-8')
    h = hmac.new(secret, licence_number.encode('utf-8'), hashlib.sha256)
    return h.digest()

@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(
    request: Request,
    driver: DriverCreate,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_current_active_organisation)
):
    org_id = membership.organisation_id

    licence_last4 = driver.licence_number[-4:] if len(driver.licence_number) >= 4 else driver.licence_number

    # Generate cryptographic representations
    licence_number_ciphertext = encrypt_licence(driver.licence_number)
    licence_lookup_hmac = get_licence_hmac(driver.licence_number)

    db_driver = Driver(
        organisation_id=org_id,
        person_id=driver.person_id,
        licence_last4=licence_last4,
        issuing_authority=driver.issuing_authority,
        licence_class=driver.licence_class,
        licence_number_ciphertext=licence_number_ciphertext,
        licence_lookup_hmac=licence_lookup_hmac
    )
    db.add(db_driver)
    try:
        db.commit()
        db.refresh(db_driver)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Driver creation failed due to database constraint.")
    return db_driver

@router.get("/", response_model=List[DriverResponse])
def get_drivers(
    request: Request,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_current_active_organisation),
    skip: int = 0,
    limit: int = 100
):
    org_id = membership.organisation_id
    drivers = db.query(Driver).filter(Driver.organisation_id == org_id).offset(skip).limit(limit).all()
    return drivers
