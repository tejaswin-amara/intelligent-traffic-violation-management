from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, DateTime, Numeric, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
from sqlalchemy.schema import ForeignKeyConstraint
import uuid

class Violation(Base):
    __tablename__ = 'violations'

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    jurisdiction_id = Column(UUID(as_uuid=True), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), nullable=False)
    driver_id = Column(UUID(as_uuid=True), nullable=True)
    offence_id = Column(UUID(as_uuid=True), nullable=False)

    event_at = Column(DateTime(timezone=True), nullable=False)
    event_timezone = Column(String, nullable=False)
    location_text = Column(String)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))

    source_type = Column(String, nullable=False)
    source_system = Column(String)
    source_event_id = Column(String)
    summary = Column(String)

    status = Column(String, default='draft', nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint('id', 'organisation_id'),
        ForeignKeyConstraint(
            ['jurisdiction_id', 'organisation_id'],
            ['jurisdictions.id', 'jurisdictions.organisation_id']
        ),
        ForeignKeyConstraint(
            ['vehicle_id', 'organisation_id'],
            ['vehicles.id', 'vehicles.organisation_id']
        ),
        ForeignKeyConstraint(
            ['driver_id', 'organisation_id'],
            ['drivers.id', 'drivers.organisation_id']
        ),
        ForeignKeyConstraint(
            ['offence_id', 'organisation_id'],
            ['offences.id', 'offences.organisation_id']
        ),
    )

class EvidenceAsset(Base):
    __tablename__ = 'evidence_assets'
    __mapper_args__ = {"eager_defaults": True} # needed for server defaults like ingested_at if not populated

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    violation_id = Column(UUID(as_uuid=True), nullable=False)
    asset_kind = Column(String, nullable=False)
    original_asset_id = Column(UUID(as_uuid=True), nullable=True)
    original_filename = Column(String)

    media_type = Column(String, nullable=False)
    byte_size = Column(BigInteger, nullable=False)
    sha256_hex = Column(String(64), nullable=False)
    object_key = Column(String, nullable=False, unique=True)
    captured_at = Column(DateTime(timezone=True), nullable=True)
    ingested_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    uploader_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    uploader_source = Column(String)
    scan_status = Column(String, default='pending', nullable=False)
    legal_hold = Column(Boolean, default=False, nullable=False)
    status = Column(String, default='active', nullable=False)
    source_device = Column(String)
    metadata_ = Column("metadata", JSONB, nullable=False, default={})
    retention_until = Column(DateTime(timezone=True))

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = None

    __table_args__ = (
        UniqueConstraint('id', 'organisation_id'),
        ForeignKeyConstraint(
            ['violation_id', 'organisation_id'],
            ['violations.id', 'violations.organisation_id']
        ),
        ForeignKeyConstraint(
            ['original_asset_id', 'organisation_id'],
            ['evidence_assets.id', 'evidence_assets.organisation_id']
        ),
    )

class ReviewDecision(Base):
    __tablename__ = 'review_decisions'

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    violation_id = Column(UUID(as_uuid=True), nullable=False)
    decision = Column(String, nullable=False)
    rationale = Column(String, nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['violation_id', 'organisation_id'],
            ['violations.id', 'violations.organisation_id']
        ),
    )
