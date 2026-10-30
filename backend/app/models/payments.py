from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, DateTime, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
from sqlalchemy.schema import ForeignKeyConstraint
import uuid

class Payment(Base):
    __tablename__ = 'payments'
    __mapper_args__ = {"eager_defaults": True}

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    notice_id = Column(UUID(as_uuid=True), nullable=False)
    provider = Column(String, nullable=False)
    provider_payment_reference = Column(String)
    idempotency_key = Column(String, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency_code = Column(String(3), nullable=False)
    status = Column(String, default='created', nullable=False)
    initiated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True))
    provider_payload_redacted = Column(JSONB, nullable=False, default={})

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = None

    __table_args__ = (
        UniqueConstraint('organisation_id', 'provider', 'idempotency_key'),
        UniqueConstraint('id', 'organisation_id'),
        ForeignKeyConstraint(
            ['notice_id', 'organisation_id'],
            ['notices.id', 'notices.organisation_id']
        )
    )

class PaymentLedgerEntry(Base):
    __tablename__ = 'payment_ledger_entries'
    __mapper_args__ = {"eager_defaults": True}

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    notice_id = Column(UUID(as_uuid=True), nullable=False)
    payment_id = Column(UUID(as_uuid=True), nullable=True)
    entry_type = Column(String, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency_code = Column(String(3), nullable=False)
    provider_event_reference = Column(String)
    reason = Column(String)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    occurred_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['notice_id', 'organisation_id'],
            ['notices.id', 'notices.organisation_id']
        ),
        ForeignKeyConstraint(
            ['payment_id', 'organisation_id'],
            ['payments.id', 'payments.organisation_id']
        )
    )

class PaymentWebhookEvent(Base):
    __tablename__ = 'payment_webhook_events'
    __mapper_args__ = {"eager_defaults": True}

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    provider = Column(String, nullable=False)
    provider_event_id = Column(String, nullable=False)
    received_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    signature_valid = Column(Boolean, nullable=False)
    processing_status = Column(String, nullable=False, default='received')
    payload_redacted = Column(JSONB, nullable=False, default={})
    processed_at = Column(DateTime(timezone=True))

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = None

    __table_args__ = (
        UniqueConstraint('organisation_id', 'provider', 'provider_event_id'),
    )
