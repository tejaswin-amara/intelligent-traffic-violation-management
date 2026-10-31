from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Organisation(Base):
    __tablename__ = 'organisations'

    name = Column(String(120), nullable=False)
    code = Column(String(40), unique=True, nullable=False)
    status = Column(String, default='active', nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class User(Base):
    __tablename__ = 'users'

    identity_provider = Column(String, nullable=False)
    identity_subject = Column(String, nullable=False)
    email = Column(String(255), unique=True, nullable=False) # Make email unique
    display_name = Column(String(160), nullable=False)
    status = Column(String, default='active', nullable=False)

    password_hash = Column(String(255))

    memberships = relationship("Membership", back_populates="user")

    __table_args__ = (
        UniqueConstraint('identity_provider', 'identity_subject'),
    )

class Membership(Base):
    __tablename__ = 'memberships'

    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, default='active', nullable=False)

    user = relationship("User", back_populates="memberships", lazy="joined")
    organisation = relationship("Organisation")

    __table_args__ = (
        UniqueConstraint('organisation_id', 'user_id', 'role'),
    )
