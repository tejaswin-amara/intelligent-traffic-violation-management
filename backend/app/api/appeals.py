from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from ..core.database import get_db
from ..models.appeals import Appeal
from ..models.finance import Notice
from .auth import get_current_user
from ..models.auth import User, Membership

router = APIRouter()

class AppealCreate(BaseModel):
    notice_id: uuid.UUID
    reason_code: Optional[str] = None
    reason_text: str

class AppealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    notice_id: uuid.UUID
    status: str
    filed_at: datetime
    decision: Optional[str]

class AppealReview(BaseModel):
    decision: str # upheld, rejected, reduced, remanded
    decision_reason: str

@router.post("/", response_model=AppealResponse, status_code=status.HTTP_201_CREATED)
def submit_appeal(
    appeal: AppealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id

    # Verify notice exists
    notice = db.query(Notice).filter(Notice.id == appeal.notice_id, Notice.organisation_id == org_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")

    db_appeal = Appeal(
        organisation_id=org_id,
        notice_id=appeal.notice_id,
        reason_code=appeal.reason_code,
        reason_text=appeal.reason_text
    )
    db.add(db_appeal)
    db.commit()
    db.refresh(db_appeal)
    return db_appeal

@router.post("/{appeal_id}/review", response_model=AppealResponse)
def review_appeal(
    appeal_id: uuid.UUID,
    review: AppealReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id

    # Must be reviewer
    if not any(m.role in ["reviewing_officer", "reviewer", "super_admin", "agency_admin"] for m in user_with_mems.memberships if m.organisation_id == org_id):
        raise HTTPException(status_code=403, detail="User does not have permission to review appeals")

    appeal = db.query(Appeal).filter(Appeal.id == appeal_id, Appeal.organisation_id == org_id).first()
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    appeal.status = "closed"
    appeal.decision = review.decision
    appeal.decision_reason = review.decision_reason
    appeal.decided_by = current_user.id
    appeal.decided_at = datetime.utcnow()

    db.commit()
    db.refresh(appeal)
    return appeal
