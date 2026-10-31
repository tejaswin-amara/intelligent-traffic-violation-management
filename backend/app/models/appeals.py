from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
from sqlalchemy.schema import ForeignKeyConstraint
import uuid

class Appeal(Base):
    __tablename__ = 'appeals'

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    notice_id = Column(UUID(as_uuid=True), nullable=False)
    appellant_person_id = Column(UUID(as_uuid=True), nullable=True)
    reason_code = Column(String(80))
    reason_text = Column(String, nullable=False)
    status = Column(String, default='submitted', nullable=False)
    filed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    decision = Column(String)
    decision_reason = Column(String)
    decided_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    decided_at = Column(DateTime(timezone=True))

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # the created_at is omitted as it doesn't exist in original schema
    created_at = None

    __table_args__ = (
        UniqueConstraint('id', 'organisation_id'),
        ForeignKeyConstraint(
            ['notice_id', 'organisation_id'],
            ['notices.id', 'notices.organisation_id']
        ),
        ForeignKeyConstraint(
            ['appellant_person_id', 'organisation_id'],
            ['persons.id', 'persons.organisation_id']
        )
    )
