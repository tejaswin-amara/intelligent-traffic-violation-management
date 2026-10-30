from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..core.database import get_db
from ..models.domain import Driver, Person
from ..schemas.domain import DriverCreate, DriverResponse
from .auth import get_current_user
from ..models.auth import User, Membership

router = APIRouter()

@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(
    driver: DriverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    memberships = db.query(Membership).filter(Membership.user_id == current_user.id).all()
    if not memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = memberships[0].organisation_id

    licence_last4 = driver.licence_number[-4:] if len(driver.licence_number) >= 4 else driver.licence_number

    db_driver = Driver(
        organisation_id=org_id,
        person_id=driver.person_id,
        licence_last4=licence_last4,
        issuing_authority=driver.issuing_authority,
        licence_class=driver.licence_class,
        licence_number_ciphertext=b"encrypted",
        licence_lookup_hmac=b"hmac"
    )
    db.add(db_driver)
    try:
        db.commit()
        db.refresh(db_driver)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Driver creation failed: {e}")
    return db_driver

@router.get("/", response_model=List[DriverResponse])
def get_drivers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    memberships = db.query(Membership).filter(Membership.user_id == current_user.id).all()
    if not memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = memberships[0].organisation_id
    drivers = db.query(Driver).filter(Driver.organisation_id == org_id).offset(skip).limit(limit).all()
    return drivers
