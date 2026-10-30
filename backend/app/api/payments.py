from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import hmac
import hashlib

from ..core.database import get_db
from ..models.payments import Payment, PaymentLedgerEntry, PaymentWebhookEvent
from ..models.finance import Notice
from .auth import get_current_user
from ..models.auth import User, Membership
from ..core.config import settings

router = APIRouter()

class PaymentIntentCreate(BaseModel):
    notice_id: uuid.UUID
    amount: float
    currency_code: str
    provider: str = "sandbox"
    idempotency_key: str

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    notice_id: uuid.UUID
    amount: float
    currency_code: str
    status: str

@router.post("/intent", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment_intent(
    intent: PaymentIntentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_with_mems = db.query(User).options(joinedload(User.memberships)).filter(User.id == current_user.id).first()
    if not user_with_mems or not user_with_mems.memberships:
        raise HTTPException(status_code=403, detail="User has no active organisation membership")
    org_id = user_with_mems.memberships[0].organisation_id

    notice = db.query(Notice).filter(Notice.id == intent.notice_id, Notice.organisation_id == org_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")

    # Check for idempotency key
    existing_payment = db.query(Payment).filter(
        Payment.organisation_id == org_id,
        Payment.provider == intent.provider,
        Payment.idempotency_key == intent.idempotency_key
    ).first()
    if existing_payment:
        return existing_payment

    payment = Payment(
        organisation_id=org_id,
        notice_id=intent.notice_id,
        provider=intent.provider,
        idempotency_key=intent.idempotency_key,
        amount=intent.amount,
        currency_code=intent.currency_code,
        status="created"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@router.post("/webhook/{provider}")
async def payment_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    payload = await request.body()
    # In a real app, verify signature based on provider. Mocking here.
    sig_header = request.headers.get("X-Signature")

    # Very basic dummy verification for Sandbox
    is_valid = True

    data = await request.json()
    org_id_str = data.get("organisation_id")
    event_id = data.get("event_id")
    payment_id_str = data.get("payment_id")
    new_status = data.get("status")

    if not org_id_str or not event_id or not payment_id_str:
        raise HTTPException(status_code=400, detail="Missing required webhook fields")

    org_id = uuid.UUID(org_id_str)
    payment_id = uuid.UUID(payment_id_str)

    # Store Webhook Event (deduplication)
    existing_event = db.query(PaymentWebhookEvent).filter(
        PaymentWebhookEvent.organisation_id == org_id,
        PaymentWebhookEvent.provider == provider,
        PaymentWebhookEvent.provider_event_id == event_id
    ).first()

    if existing_event:
        return {"status": "already_processed"}

    webhook_event = PaymentWebhookEvent(
        organisation_id=org_id,
        provider=provider,
        provider_event_id=event_id,
        signature_valid=is_valid,
        processing_status="processed",
        payload_redacted={} # Don't store PII
    )
    db.add(webhook_event)

    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.organisation_id == org_id).first()
    if payment and is_valid:
        payment.status = new_status
        if new_status == "succeeded":
            payment.completed_at = datetime.utcnow()

            # Create Ledger Entry
            ledger = PaymentLedgerEntry(
                organisation_id=org_id,
                notice_id=payment.notice_id,
                payment_id=payment.id,
                entry_type="payment_credit",
                amount=payment.amount,
                currency_code=payment.currency_code,
                provider_event_reference=event_id
            )
            db.add(ledger)

    db.commit()
    return {"status": "ok"}
