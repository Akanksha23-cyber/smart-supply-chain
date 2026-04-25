"""Service layer for shipment management."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, timedelta
from app.models.models import Shipment, Event, ShipmentStatus, EventType
from app.schemas.schemas import ShipmentCreate, ShipmentUpdate, ShipmentResponse
from app.utils.redis_cache import redis_cache
from app.utils.logging_config import EventLogger
import logging
import uuid

logger = logging.getLogger(__name__)


class ShipmentService:
    """Service layer for shipment operations."""

    @staticmethod
    def create_shipment(db: Session, shipment_data: ShipmentCreate) -> Shipment:
        """Create a new shipment."""
        try:
            shipment = Shipment(
                id=shipment_data.id or f"SHP-{uuid.uuid4().hex[:12]}",
                source=shipment_data.source,
                destination=shipment_data.destination,
                status=ShipmentStatus.PENDING,
                estimated_delivery=shipment_data.estimated_delivery,
                metadata=shipment_data.metadata or {},
            )
            db.add(shipment)
            db.commit()
            db.refresh(shipment)

            # Cache shipment state
            redis_cache.set_shipment_state(
                shipment.id,
                {
                    "id": shipment.id,
                    "status": shipment.status.value,
                    "location": shipment.current_location,
                }
            )

            EventLogger.log_event(
                shipment.id,
                "shipment_created",
                f"Shipment created from {shipment.source} to {shipment.destination}",
                severity="info"
            )
            return shipment
        except Exception as e:
            logger.error(f"Error creating shipment: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_shipment(db: Session, shipment_id: str) -> Optional[Shipment]:
        """Get shipment by ID."""
        return db.query(Shipment).filter(Shipment.id == shipment_id).first()

    @staticmethod
    def get_all_shipments(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[ShipmentStatus] = None
    ) -> tuple[List[Shipment], int]:
        """Get all shipments with pagination and filtering."""
        query = db.query(Shipment)
        if status:
            query = query.filter(Shipment.status == status)
        total = query.count()
        shipments = query.order_by(desc(Shipment.created_at)).offset(skip).limit(limit).all()
        return shipments, total

    @staticmethod
    def update_shipment(
        db: Session,
        shipment_id: str,
        update_data: ShipmentUpdate
    ) -> Optional[Shipment]:
        """Update shipment status and location."""
        try:
            shipment = ShipmentService.get_shipment(db, shipment_id)
            if not shipment:
                return None

            old_status = shipment.status

            if update_data.status:
                shipment.status = update_data.status
            if update_data.current_location:
                shipment.current_location = update_data.current_location
            if update_data.current_lat is not None:
                shipment.current_lat = update_data.current_lat
            if update_data.current_lon is not None:
                shipment.current_lon = update_data.current_lon

            shipment.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(shipment)

            # Update cache
            redis_cache.set_shipment_state(
                shipment.id,
                {
                    "id": shipment.id,
                    "status": shipment.status.value,
                    "location": shipment.current_location,
                    "lat": shipment.current_lat,
                    "lon": shipment.current_lon,
                }
            )

            # Log status change
            if update_data.status and update_data.status != old_status:
                EventLogger.log_event(
                    shipment.id,
                    "shipment_status_updated",
                    f"Status changed from {old_status} to {update_data.status}",
                    severity="info"
                )

            return shipment
        except Exception as e:
            logger.error(f"Error updating shipment: {e}")
            db.rollback()
            raise

    @staticmethod
    def mark_delivered(db: Session, shipment_id: str) -> Optional[Shipment]:
        """Mark shipment as delivered."""
        try:
            shipment = ShipmentService.get_shipment(db, shipment_id)
            if not shipment:
                return None

            shipment.status = ShipmentStatus.DELIVERED
            shipment.actual_delivery = datetime.utcnow()
            db.commit()
            db.refresh(shipment)

            EventLogger.log_event(
                shipment.id,
                "shipment_delivered",
                f"Shipment delivered to {shipment.destination}",
                severity="info"
            )
            return shipment
        except Exception as e:
            logger.error(f"Error marking shipment as delivered: {e}")
            db.rollback()
            raise


class EventService:
    """Service layer for event management."""

    @staticmethod
    def create_event(
        db: Session,
        shipment_id: str,
        event_type: EventType,
        data: dict,
        severity: str = "info"
    ) -> Event:
        """Create a new event."""
        try:
            event = Event(
                shipment_id=shipment_id,
                timestamp=datetime.utcnow(),
                event_type=event_type,
                data=data,
                severity=severity,
            )
            db.add(event)
            db.commit()
            db.refresh(event)

            # Add to real-time alerts in Redis
            if severity in ["warning", "critical"]:
                redis_cache.add_alert(
                    f"alert_{event.id}",
                    {
                        "id": event.id,
                        "shipment_id": shipment_id,
                        "type": event_type.value,
                        "severity": severity,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            return event
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_shipment_events(
        db: Session,
        shipment_id: str,
        limit: int = 100
    ) -> List[Event]:
        """Get all events for a shipment."""
        return (
            db.query(Event)
            .filter(Event.shipment_id == shipment_id)
            .order_by(desc(Event.timestamp))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_recent_events(
        db: Session,
        hours: int = 24,
        limit: int = 100
    ) -> List[Event]:
        """Get recent events from the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return (
            db.query(Event)
            .filter(Event.timestamp >= cutoff_time)
            .order_by(desc(Event.timestamp))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_critical_events(db: Session, limit: int = 50) -> List[Event]:
        """Get critical events."""
        return (
            db.query(Event)
            .filter(Event.severity == "critical")
            .order_by(desc(Event.timestamp))
            .limit(limit)
            .all()
        )
