from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from ..core.database import get_db
from ..models.violation import Violation, EvidenceAsset, ReviewDecision
from .auth import get_current_user
from ..models.auth import User, Membership

router = APIRouter()

class ViolationCreate(BaseModel):
    jurisdiction_id: uuid.UUID
    vehicle_id: uuid.UUID
    driver_id: Optional[uuid.UUID] = None
    offence_id: uuid.UUID
    event_at: datetime
    event_timezone: str
    location_text: Optional[str] = None
    source_type: str = "manual"
    source_system: Optional[str] = None
    source_event_id: Optional[str] = None
    summary: Optional[str] = None

class ViolationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    jurisdiction_id: uuid.UUID
    vehicle_id: uuid.UUID
    offence_id: uuid.UUID
    status: str
    created_at: datetime
    event_at: datetime

class ReviewDecisionCreate(BaseModel):
    decision: str # approved, rejected, needs_information, reopened, cancelled
    rationale: str

@router.post("/", response_model=ViolationResponse, status_code=status.HTTP_201_CREATED)
def create_violation(
    violation: ViolationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id

    db_violation = Violation(
        organisation_id=org_id,
        jurisdiction_id=violation.jurisdiction_id,
        vehicle_id=violation.vehicle_id,
        driver_id=violation.driver_id,
        offence_id=violation.offence_id,
        event_at=violation.event_at,
        event_timezone=violation.event_timezone,
        location_text=violation.location_text,
        source_type=violation.source_type,
        source_system=violation.source_system,
        source_event_id=violation.source_event_id,
        summary=violation.summary,
        status="draft",
        created_by=current_user.id
    )
    db.add(db_violation)
    db.commit()
    db.refresh(db_violation)
    return db_violation

@router.get("/", response_model=List[ViolationResponse])
def get_violations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id
    violations = db.query(Violation).filter(Violation.organisation_id == org_id).offset(skip).limit(limit).all()
    return violations

@router.post("/{violation_id}/review", response_model=ViolationResponse)
def review_violation(
    violation_id: uuid.UUID,
    decision: ReviewDecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id

    is_reviewer = any(m.role in ["reviewer", "super_admin", "agency_admin"] for m in user_with_mems.memberships if m.organisation_id == org_id)
    if not is_reviewer:
        roles = [m.role for m in user_with_mems.memberships]
        raise HTTPException(status_code=403, detail=f"User does not have review permissions. Roles: {roles}")

    violation = db.query(Violation).filter(Violation.id == violation_id, Violation.organisation_id == org_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    if violation.created_by == current_user.id:
        raise HTTPException(status_code=403, detail="Creator cannot review their own violation")

    db_decision = ReviewDecision(
        organisation_id=org_id,
        violation_id=violation.id,
        decision=decision.decision,
        rationale=decision.rationale,
        actor_user_id=current_user.id
    )
    db.add(db_decision)

    # Simple state transition
    if decision.decision == "approved":
        violation.status = "approved"
    elif decision.decision == "rejected":
        violation.status = "rejected"
    elif decision.decision == "needs_information":
        violation.status = "needs_information"

    db.commit()
    db.refresh(violation)
    return violation
