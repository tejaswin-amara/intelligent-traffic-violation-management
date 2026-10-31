from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, DateTime, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID, BYTEA, JSONB, ARRAY
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
from sqlalchemy.schema import ForeignKeyConstraint
import uuid

class Jurisdiction(Base):
    __tablename__ = 'jurisdictions'

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String(40), nullable=False)
    timezone = Column(String, nullable=False, default="UTC")
    currency_code = Column(String(3), nullable=False, default="USD")
    status = Column(String, default='active', nullable=False)

    __table_args__ = (
        UniqueConstraint('organisation_id', 'code'),
        UniqueConstraint('id', 'organisation_id'),
    )

class Person(Base):
    __tablename__ = 'persons'

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    full_name = Column(String(160), nullable=False)
    verification_status = Column(String, default='unverified', nullable=False)

    __table_args__ = (
        UniqueConstraint('id', 'organisation_id'),
    )

class Driver(Base):
    __tablename__ = 'drivers'

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    person_id = Column(UUID(as_uuid=True), nullable=False)
    licence_number_ciphertext = Column(BYTEA, nullable=True)
    licence_lookup_hmac = Column(BYTEA, nullable=True)
    licence_last4 = Column(String(4))
    issuing_authority = Column(String(120), nullable=False)
    licence_class = Column(String(80), nullable=False)
    licence_status = Column(String, default='valid', nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['person_id', 'organisation_id'],
            ['persons.id', 'persons.organisation_id']
        ),
        UniqueConstraint('id', 'organisation_id'),
    )

class Vehicle(Base):
    __tablename__ = 'vehicles'

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    jurisdiction_id = Column(UUID(as_uuid=True), nullable=False)
    registration_display = Column(String(32), nullable=False)
    registration_normalised = Column(String(32), nullable=False)
    vehicle_class = Column(String(50), nullable=False)
    make = Column(String(80))
    model = Column(String(80))
    colour = Column(String(40))
    verification_status = Column(String, default='unverified', nullable=False)
    status = Column(String, default='active', nullable=False)

    __table_args__ = (
        UniqueConstraint('organisation_id', 'jurisdiction_id', 'registration_normalised'),
        UniqueConstraint('id', 'organisation_id'),
        ForeignKeyConstraint(
            ['jurisdiction_id', 'organisation_id'],
            ['jurisdictions.id', 'jurisdictions.organisation_id']
        ),
    )

class VehicleOwnership(Base):
    __tablename__ = 'vehicle_ownerships'

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), nullable=False)
    person_id = Column(UUID(as_uuid=True), nullable=False)
    owned_from = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    owned_until = Column(DateTime(timezone=True))

    __table_args__ = (
        ForeignKeyConstraint(
            ['vehicle_id', 'organisation_id'],
            ['vehicles.id', 'vehicles.organisation_id']
        ),
        ForeignKeyConstraint(
            ['person_id', 'organisation_id'],
            ['persons.id', 'persons.organisation_id']
        ),
    )

class Offence(Base):
    __tablename__ = 'offences'

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    jurisdiction_id = Column(UUID(as_uuid=True), nullable=False)
    code = Column(String(40), nullable=False)
    category = Column(String(80), nullable=False)
    title = Column(String(160), nullable=False)
    description = Column(String, nullable=False)
    required_evidence = Column(JSONB, nullable=False, default=[])
    applicable_vehicle_classes = Column(ARRAY(String), nullable=False, default=[])
    valid_from = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    status = Column(String, default='active', nullable=False)
    official_source_reference = Column(String, nullable=False, default='unknown')

    __table_args__ = (
        UniqueConstraint('organisation_id', 'jurisdiction_id', 'code', 'valid_from'),
        UniqueConstraint('id', 'organisation_id'),
        ForeignKeyConstraint(
            ['jurisdiction_id', 'organisation_id'],
            ['jurisdictions.id', 'jurisdictions.organisation_id']
        ),
    )

class FineSchedule(Base):
    __tablename__ = 'fine_schedules'
    __mapper_args__ = {"eager_defaults": True}

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    offence_id = Column(UUID(as_uuid=True), nullable=False)
    version = Column(String, nullable=False)
    vehicle_class = Column(String, nullable=False, default="*")
    effective_from = Column(DateTime(timezone=True), nullable=False)
    effective_until = Column(DateTime(timezone=True))
    amount = Column(Numeric(14, 2), nullable=False)
    currency_code = Column(String(3), nullable=False)

    # We suppress these mapped fields completely to resolve the UndefinedColumn issues
    # if they do not match the database exactly
    modifiers = Column(JSONB, nullable=False, default={})
    official_source_reference = Column(String, nullable=False, default='unknown')
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_at = Column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint('organisation_id', 'offence_id', 'version', 'vehicle_class'),
        UniqueConstraint('id', 'organisation_id'),
        ForeignKeyConstraint(
            ['offence_id', 'organisation_id'],
            ['offences.id', 'offences.organisation_id']
        ),
    )
