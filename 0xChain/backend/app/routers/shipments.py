"""Shipment management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.schemas import (
    ShipmentCreate, ShipmentUpdate, ShipmentResponse,
    ShipmentListResponse, ShipmentStatusEnum
)
from app.services.shipment_service import ShipmentService, EventService
from app.models.models import ShipmentStatus

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.post("", response_model=ShipmentResponse)
def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new shipment."""
    try:
        created_shipment = ShipmentService.create_shipment(db, shipment)
        return created_shipment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=ShipmentListResponse)
def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[ShipmentStatusEnum] = None,
    db: Session = Depends(get_db)
):
    """Get all shipments with pagination and filtering."""
    try:
        shipment_status = ShipmentStatus(status) if status else None
        shipments, total = ShipmentService.get_all_shipments(
            db,
            skip=skip,
            limit=limit,
            status=shipment_status
        )
        return ShipmentListResponse(
            total=total,
            shipments=[ShipmentResponse.from_orm(s) for s in shipments]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(shipment_id: str, db: Session = Depends(get_db)):
    """Get shipment details by ID."""
    shipment = ShipmentService.get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return ShipmentResponse.from_orm(shipment)


@router.patch("/{shipment_id}", response_model=ShipmentResponse)
def update_shipment(
    shipment_id: str,
    update_data: ShipmentUpdate,
    db: Session = Depends(get_db)
):
    """Update shipment status and location."""
    try:
        updated_shipment = ShipmentService.update_shipment(db, shipment_id, update_data)
        if not updated_shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return ShipmentResponse.from_orm(updated_shipment)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{shipment_id}/mark-delivered", response_model=ShipmentResponse)
def mark_delivered(shipment_id: str, db: Session = Depends(get_db)):
    """Mark shipment as delivered."""
    try:
        shipment = ShipmentService.mark_delivered(db, shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return ShipmentResponse.from_orm(shipment)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
