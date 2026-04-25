"""SQLAlchemy ORM models for supply chain data."""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum, ForeignKey, 
    Text, JSON, Boolean, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class ShipmentStatus(str, enum.Enum):
    """Shipment status enumeration."""
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELAYED = "delayed"
    REROUTED = "rerouted"
    DELIVERED = "delivered"
    FAILED = "failed"


class EventType(str, enum.Enum):
    """Event types enumeration."""
    LOCATION_UPDATE = "location_update"
    WEATHER_UPDATE = "weather_update"
    TRAFFIC_UPDATE = "traffic_update"
    DELAY_DETECTED = "delay_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    REROUTE_TRIGGERED = "reroute_triggered"
    PREDICTION = "prediction"


class Shipment(Base):
    """Shipment ORM model."""
    __tablename__ = "shipments"
    __table_args__ = (Index("idx_shipment_status", "status"),)

    id = Column(String(50), primary_key=True, index=True)
    source = Column(String(100), nullable=False, index=True)
    destination = Column(String(100), nullable=False, index=True)
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.PENDING, index=True)
    current_location = Column(String(100))
    current_lat = Column(Float)
    current_lon = Column(Float)
    route_id = Column(String(50), ForeignKey("routes.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    estimated_delivery = Column(DateTime)
    actual_delivery = Column(DateTime, nullable=True)
    metadata = Column(JSON, default={})

    # Relationships
    events = relationship("Event", back_populates="shipment", cascade="all, delete-orphan")
    route = relationship("Route", back_populates="shipments")

    def __repr__(self) -> str:
        return f"<Shipment {self.id} {self.status}>"


class Event(Base):
    """Real-time event ORM model."""
    __tablename__ = "events"
    __table_args__ = (Index("idx_event_shipment_timestamp", "shipment_id", "timestamp"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(String(50), ForeignKey("shipments.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    data = Column(JSON, default={})
    severity = Column(String(20), default="info")  # info, warning, critical

    # Relationships
    shipment = relationship("Shipment", back_populates="events")

    def __repr__(self) -> str:
        return f"<Event {self.id} {self.event_type}>"


class Route(Base):
    """Route ORM model for storing computed routes."""
    __tablename__ = "routes"

    id = Column(String(50), primary_key=True, index=True)
    nodes = Column(JSON, nullable=False)  # List of node IDs
    edges = Column(JSON, nullable=False)  # List of edges with weights
    total_distance = Column(Float)
    estimated_time = Column(Float)  # in hours
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shipments = relationship("Shipment", back_populates="route")

    def __repr__(self) -> str:
        return f"<Route {self.id}>"


class Alert(Base):
    """System alerts ORM model."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(String(50), ForeignKey("shipments.id"), nullable=True, index=True)
    alert_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Alert {self.id} {self.alert_type}>"
