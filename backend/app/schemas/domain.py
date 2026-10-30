from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

class VehicleCreate(BaseModel):
    jurisdiction_id: UUID
    registration: str
    vehicle_class: str
    make: Optional[str] = None
    model: Optional[str] = None
    colour: Optional[str] = None

class VehicleUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    colour: Optional[str] = None
    verification_status: Optional[str] = None

class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    jurisdiction_id: UUID
    registration_display: str
    registration_normalised: str
    vehicle_class: str
    make: Optional[str]
    model: Optional[str]
    colour: Optional[str]
    verification_status: str
    created_at: datetime

class PersonCreate(BaseModel):
    full_name: str

class PersonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str

class DriverCreate(BaseModel):
    person_id: UUID
    licence_number: str
    issuing_authority: str
    licence_class: str

class DriverResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    person_id: UUID
    licence_last4: Optional[str] = None
    issuing_authority: str
    licence_class: str
    licence_status: str

class OffenceCreate(BaseModel):
    jurisdiction_id: UUID
    code: str
    category: str
    title: str
    description: str

class OffenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    jurisdiction_id: UUID
    code: str
    category: str
    title: str
    description: str
    status: str

class FineScheduleCreate(BaseModel):
    offence_id: UUID
    version: str
    effective_from: datetime
    base_amount: Decimal
    currency_code: str

class FineScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    offence_id: UUID
    version: str
    effective_from: datetime
    effective_until: Optional[datetime]
    base_amount: Decimal
    currency_code: str
    status: str
