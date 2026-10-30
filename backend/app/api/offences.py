from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..core.database import get_db
from ..models.domain import Offence
from ..schemas.domain import OffenceCreate, OffenceResponse
from .auth import get_current_user
from ..models.auth import User, Membership

router = APIRouter()

@router.post("/", response_model=OffenceResponse, status_code=status.HTTP_201_CREATED)
def create_offence(
    offence: OffenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    memberships = db.query(Membership).filter(Membership.user_id == current_user.id).all()
    if not memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = memberships[0].organisation_id

    db_offence = Offence(
        organisation_id=org_id,
        jurisdiction_id=offence.jurisdiction_id,
        code=offence.code,
        category=offence.category,
        title=offence.title,
        description=offence.description
    )
    db.add(db_offence)
    try:
        db.commit()
        db.refresh(db_offence)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Offence creation failed: {e}")
    return db_offence

@router.get("/", response_model=List[OffenceResponse])
def get_offences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    memberships = db.query(Membership).filter(Membership.user_id == current_user.id).all()
    if not memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = memberships[0].organisation_id
    offences = db.query(Offence).filter(Offence.organisation_id == org_id).offset(skip).limit(limit).all()
    return offences
