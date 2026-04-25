"""Dashboard and system health endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.schemas.schemas import DashboardResponse, DashboardMetrics, HealthResponse, EventResponse
from app.models.models import Shipment, ShipmentStatus, Event
from app.utils.redis_cache import redis_cache
from app.utils.graph_db import graph_db
from sqlalchemy import func

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    """Get aggregated system dashboard data."""
    try:
        # Get shipment counts
        total_shipments = db.query(func.count(Shipment.id)).scalar()
        in_transit = db.query(func.count(Shipment.id)).filter(
            Shipment.status == ShipmentStatus.IN_TRANSIT
        ).scalar()
        delivered = db.query(func.count(Shipment.id)).filter(
            Shipment.status == ShipmentStatus.DELIVERED
        ).scalar()
        delayed = db.query(func.count(Shipment.id)).filter(
            Shipment.status == ShipmentStatus.DELAYED
        ).scalar()
        failed = db.query(func.count(Shipment.id)).filter(
            Shipment.status == ShipmentStatus.FAILED
        ).scalar()

        # Calculate average delay
        delivered_shipments = db.query(Shipment).filter(
            Shipment.status == ShipmentStatus.DELIVERED,
            Shipment.actual_delivery.isnot(None),
            Shipment.estimated_delivery.isnot(None)
        ).all()

        avg_delay = 0.0
        if delivered_shipments:
            total_delay = sum(
                (s.actual_delivery - s.estimated_delivery).total_seconds() / 3600
                for s in delivered_shipments
                if s.actual_delivery > s.estimated_delivery
            )
            avg_delay = total_delay / len(delivered_shipments)

        # Get recent events
        recent_events = db.query(Event).order_by(Event.timestamp.desc()).limit(10).all()

        # Get critical alerts from Redis
        alerts = redis_cache.get_alerts(limit=5)

        metrics = DashboardMetrics(
            total_shipments=total_shipments or 0,
            in_transit=in_transit or 0,
            delivered=delivered or 0,
            delayed=delayed or 0,
            failed=failed or 0,
            average_delay_hours=max(0, avg_delay),
            disruption_probability_avg=0.15,  # Placeholder
            alerts_active=len(alerts)
        )

        return DashboardResponse(
            metrics=metrics,
            recent_events=[EventResponse.from_orm(e) for e in recent_events],
            critical_alerts=alerts
        )
    except Exception as e:
        return DashboardResponse(
            metrics=DashboardMetrics(
                total_shipments=0,
                in_transit=0,
                delivered=0,
                delayed=0,
                failed=0,
                average_delay_hours=0,
                disruption_probability_avg=0,
                alerts_active=0
            ),
            recent_events=[],
            critical_alerts=[]
        )


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Check system health and connectivity."""
    # Check database
    db_status = "connected"
    try:
        db.execute("SELECT 1")
    except Exception:
        db_status = "disconnected"

    # Check Redis
    redis_status = "connected" if redis_cache.is_connected() else "disconnected"

    # Check Neo4j
    neo4j_status = "connected" if graph_db.is_connected() else "disconnected"

    return HealthResponse(
        status="healthy" if all([
            db_status == "connected",
            redis_status == "connected",
            neo4j_status == "connected"
        ]) else "degraded",
        database=db_status,
        redis=redis_status,
        neo4j=neo4j_status,
        timestamp=datetime.utcnow()
    )
