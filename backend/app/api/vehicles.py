from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..core.database import get_db
from ..models.domain import Vehicle, Jurisdiction
from ..schemas.domain import VehicleCreate, VehicleUpdate, VehicleResponse
from .auth import get_current_user, get_current_active_organisation
from ..models.auth import User, Membership

router = APIRouter()

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    request: Request,
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_current_active_organisation)
):
    org_id = membership.organisation_id

    normalised_reg = "".join(filter(str.isalnum, vehicle.registration)).upper()

    db_vehicle = Vehicle(
        organisation_id=org_id,
        jurisdiction_id=vehicle.jurisdiction_id,
        registration_display=vehicle.registration,
        registration_normalised=normalised_reg,
        vehicle_class=vehicle.vehicle_class,
        make=vehicle.make,
        model=vehicle.model,
        colour=vehicle.colour
    )
    db.add(db_vehicle)
    try:
        db.commit()
        db.refresh(db_vehicle)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Vehicle creation failed due to database constraint.")
    return db_vehicle

@router.get("/", response_model=List[VehicleResponse])
def get_vehicles(
    request: Request,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_current_active_organisation),
    skip: int = 0,
    limit: int = 100
):
    org_id = membership.organisation_id
    vehicles = db.query(Vehicle).filter(Vehicle.organisation_id == org_id).offset(skip).limit(limit).all()
    return vehicles

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    request: Request,
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_current_active_organisation)
):
    org_id = membership.organisation_id

    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.organisation_id == org_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle
