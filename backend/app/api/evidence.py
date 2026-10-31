from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List
import uuid
import hashlib
from datetime import datetime

from ..core.database import get_db
from ..models.violation import Violation, EvidenceAsset
from .auth import get_current_user
from ..models.auth import User, Membership
from pydantic import BaseModel, ConfigDict

router = APIRouter()

class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    asset_kind: str
    media_type: str
    byte_size: int
    sha256_hex: str
    status: str
    object_key: str

@router.post("/violations/{violation_id}/evidence", response_model=EvidenceResponse)
async def upload_evidence(
    violation_id: uuid.UUID,
    file: UploadFile = File(...),
    asset_kind: str = Form("image"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id

    violation = db.query(Violation).filter(Violation.id == violation_id, Violation.organisation_id == org_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    content = await file.read()
    file_size = len(content)
    file_hash = hashlib.sha256(content).hexdigest()

    # In a real app we'd upload to S3. For now, generate a mock object key.
    object_key = f"{org_id}/{violation_id}/{uuid.uuid4()}_{file.filename}"

    asset = EvidenceAsset(
        organisation_id=org_id,
        violation_id=violation_id,
        asset_kind=asset_kind,
        media_type=file.content_type or "application/octet-stream",
        byte_size=file_size,
        sha256_hex=file_hash,
        object_key=object_key,
        uploader_user_id=current_user.id,
        original_filename=file.filename
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset
