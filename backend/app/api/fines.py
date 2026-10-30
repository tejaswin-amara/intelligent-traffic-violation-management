from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import hashlib
import os

from ..core.database import get_db
from ..models.domain import FineSchedule
from ..models.finance import FineAssessment, Notice
from ..models.violation import Violation
from .auth import get_current_user
from ..models.auth import User, Membership

router = APIRouter()

class FineAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    violation_id: uuid.UUID
    final_amount: float
    currency_code: str
    status: str = "assessed"

class NoticeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    violation_id: uuid.UUID
    public_reference_last4: str
    status: str

@router.post("/violations/{violation_id}/assess", response_model=FineAssessmentResponse)
def assess_fine(
    violation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id

    # Check permission
    if not any(m.role in ["finance_officer", "super_admin", "agency_admin"] for m in user_with_mems.memberships if m.organisation_id == org_id):
        raise HTTPException(status_code=403, detail="User does not have finance permissions")

    violation = db.query(Violation).filter(Violation.id == violation_id, Violation.organisation_id == org_id).first()
    if not violation or violation.status != "approved":
        raise HTTPException(status_code=400, detail="Violation must exist and be in 'approved' status")

    # Determine Fine Schedule
    schedule = db.query(FineSchedule).filter(
        FineSchedule.organisation_id == org_id,
        FineSchedule.offence_id == violation.offence_id,
        FineSchedule.effective_from <= violation.event_at,
        (FineSchedule.effective_until >= violation.event_at) | (FineSchedule.effective_until.is_(None))
    ).first()

    if not schedule:
        raise HTTPException(status_code=400, detail="No valid fine schedule found for this offence and event time")

    assessment = FineAssessment(
        organisation_id=org_id,
        violation_id=violation.id,
        fine_schedule_id=schedule.id,
        schedule_version=schedule.version,
        base_amount=schedule.amount,
        final_amount=schedule.amount,
        currency_code=schedule.currency_code,
        calculation_snapshot={"base": str(schedule.amount), "modifiers": []},
        assessed_by=current_user.id
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

@router.post("/assessments/{assessment_id}/issue-notice", response_model=NoticeResponse)
def issue_notice(
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id

    if not any(m.role in ["finance_officer", "super_admin", "agency_admin"] for m in user_with_mems.memberships if m.organisation_id == org_id):
        raise HTTPException(status_code=403, detail="User does not have finance permissions")

    assessment = db.query(FineAssessment).filter(FineAssessment.id == assessment_id, FineAssessment.organisation_id == org_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    violation = db.query(Violation).filter(Violation.id == assessment.violation_id).first()

    # Generate secure random public reference
    public_ref = os.urandom(16)
    public_ref_hash = hashlib.sha256(public_ref).digest()
    public_ref_last4 = public_ref.hex()[-4:]

    notice = Notice(
        organisation_id=org_id,
        violation_id=assessment.violation_id,
        fine_assessment_id=assessment.id,
        public_reference_hash=public_ref_hash,
        public_reference_last4=public_ref_last4,
        issued_at=datetime.utcnow(),
        notice_snapshot={"amount": str(assessment.final_amount), "currency": assessment.currency_code},
        issued_by=current_user.id
    )
    db.add(notice)

    violation.status = "notice_issued"

    db.commit()
    db.refresh(notice)
    return notice
