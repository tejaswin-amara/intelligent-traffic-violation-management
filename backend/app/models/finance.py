from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, DateTime, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, BYTEA, ARRAY
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
from sqlalchemy.schema import ForeignKeyConstraint
import uuid

# FineSchedule is already defined in app.models.domain. We will import it in fines.py

class FineAssessment(Base):
    __tablename__ = 'fine_assessments'
    __mapper_args__ = {"eager_defaults": True}

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    violation_id = Column(UUID(as_uuid=True), nullable=False)
    fine_schedule_id = Column(UUID(as_uuid=True), nullable=False)
    schedule_version = Column(String, nullable=False)
    base_amount = Column(Numeric(14, 2), nullable=False)
    adjustments = Column(JSONB, nullable=False, default=[])
    final_amount = Column(Numeric(14, 2), nullable=False)
    currency_code = Column(String(3), nullable=False)
    calculation_snapshot = Column(JSONB, nullable=False)
    assessed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    assessed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    supersedes_assessment_id = Column(UUID(as_uuid=True), nullable=True)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = None

    __table_args__ = (
        UniqueConstraint('id', 'organisation_id'),
        ForeignKeyConstraint(
            ['violation_id', 'organisation_id'],
            ['violations.id', 'violations.organisation_id']
        ),
        ForeignKeyConstraint(
            ['fine_schedule_id', 'organisation_id'],
            ['fine_schedules.id', 'fine_schedules.organisation_id']
        ),
        ForeignKeyConstraint(
            ['supersedes_assessment_id', 'organisation_id'],
            ['fine_assessments.id', 'fine_assessments.organisation_id']
        )
    )

class Notice(Base):
    __tablename__ = 'notices'
    __mapper_args__ = {"eager_defaults": True}

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    violation_id = Column(UUID(as_uuid=True), nullable=False)
    fine_assessment_id = Column(UUID(as_uuid=True), nullable=False)
    public_reference_hash = Column(BYTEA, nullable=False, unique=True)
    public_reference_last4 = Column(String, nullable=False)
    recipient_person_id = Column(UUID(as_uuid=True), nullable=True)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    due_at = Column(DateTime(timezone=True))
    status = Column(String, default='issued', nullable=False)
    rendered_document_key = Column(String)
    notice_snapshot = Column(JSONB, nullable=False)
    issued_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    cancellation_reason = Column(String)
    cancelled_at = Column(DateTime(timezone=True))

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = None

    __table_args__ = (
        UniqueConstraint('id', 'organisation_id'),
        ForeignKeyConstraint(
            ['violation_id', 'organisation_id'],
            ['violations.id', 'violations.organisation_id']
        ),
        ForeignKeyConstraint(
            ['fine_assessment_id', 'organisation_id'],
            ['fine_assessments.id', 'fine_assessments.organisation_id']
        ),
        ForeignKeyConstraint(
            ['recipient_person_id', 'organisation_id'],
            ['persons.id', 'persons.organisation_id']
        )
    )
