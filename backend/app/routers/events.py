"""Event and data ingestion endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.schemas import EventCreate, EventResponse
from app.services.shipment_service import EventService
from app.models.models import EventType

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventResponse)
def ingest_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    """Ingest real-time shipment event (location, weather, traffic, etc)."""
    try:
        # Verify shipment exists
        from app.services.shipment_service import ShipmentService
        shipment = ShipmentService.get_shipment(db, event.shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        event_type = EventType(event.event_type)
        created_event = EventService.create_event(
            db,
            event.shipment_id,
            event_type,
            event.data,
            event.severity
        )
        return EventResponse.from_orm(created_event)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{shipment_id}", response_model=List[EventResponse])
def get_shipment_events(
    shipment_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all events for a shipment."""
    # Verify shipment exists
    from app.services.shipment_service import ShipmentService
    shipment = ShipmentService.get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    events = EventService.get_shipment_events(db, shipment_id, limit)
    return [EventResponse.from_orm(e) for e in events]


@router.get("", response_model=List[EventResponse])
def get_recent_events(
    hours: int = 24,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get recent events from the last N hours."""
    events = EventService.get_recent_events(db, hours, limit)
    return [EventResponse.from_orm(e) for e in events]


@router.get("/critical", response_model=List[EventResponse])
def get_critical_events(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get critical events."""
    events = EventService.get_critical_events(db, limit)
    return [EventResponse.from_orm(e) for e in events]
