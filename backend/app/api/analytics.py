from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case, text
from typing import List, Dict, Any
import uuid

from ..core.database import get_db
from ..models.violation import Violation
from ..models.finance import Notice, FineAssessment
from ..models.payments import Payment
from ..models.domain import Vehicle, Driver
from .auth import get_current_user
from ..models.auth import User, Membership

router = APIRouter()

@router.get("/dashboard-stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id

    total_vehicles = db.query(Vehicle).filter(Vehicle.organisation_id == org_id).count()
    total_drivers = db.query(Driver).filter(Driver.organisation_id == org_id).count()

    active_violations = db.query(Violation).filter(
        Violation.organisation_id == org_id,
        Violation.status.in_(["draft", "submitted", "under_review", "needs_information"])
    ).count()

    notices_issued = db.query(Notice).filter(
        Notice.organisation_id == org_id,
        Notice.status == "issued"
    ).count()

    return {
        "total_vehicles": total_vehicles,
        "total_drivers": total_drivers,
        "active_violations": active_violations,
        "notices_issued": notices_issued
    }

@router.get("/violation-patterns")
def get_violation_patterns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Python-based violation-pattern and trend analysis module.
    Analyses frequency of violations by day of week based on the DB records.
    """
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id

    # We use python to analyze the patterns from DB records
    # Fetch all violations for the org
    violations = db.query(Violation).filter(Violation.organisation_id == org_id).all()

    # Analysis: Day of Week distribution
    dow_counts = {"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0}
    days = list(dow_counts.keys())

    # Analysis: Source System distributions
    source_counts = {}

    for v in violations:
        # Day of week
        dow = v.event_at.weekday()
        dow_counts[days[dow]] += 1

        # Source type
        source = v.source_type or "unknown"
        source_counts[source] = source_counts.get(source, 0) + 1

    return {
        "total_analyzed": len(violations),
        "by_day_of_week": dow_counts,
        "by_source_type": source_counts
    }
