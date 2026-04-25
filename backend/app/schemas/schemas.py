"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ShipmentStatusEnum(str, Enum):
    """Shipment status enumeration."""
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELAYED = "delayed"
    REROUTED = "rerouted"
    DELIVERED = "delivered"
    FAILED = "failed"


class EventTypeEnum(str, Enum):
    """Event types enumeration."""
    LOCATION_UPDATE = "location_update"
    WEATHER_UPDATE = "weather_update"
    TRAFFIC_UPDATE = "traffic_update"
    DELAY_DETECTED = "delay_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    REROUTE_TRIGGERED = "reroute_triggered"
    PREDICTION = "prediction"


# Shipment Schemas
class ShipmentCreate(BaseModel):
    """Create a new shipment."""
    id: str
    source: str
    destination: str
    estimated_delivery: datetime
    metadata: Optional[Dict[str, Any]] = None


class ShipmentUpdate(BaseModel):
    """Update shipment status and location."""
    status: Optional[ShipmentStatusEnum] = None
    current_location: Optional[str] = None
    current_lat: Optional[float] = None
    current_lon: Optional[float] = None


class ShipmentResponse(BaseModel):
    """Response model for shipment details."""
    id: str
    source: str
    destination: str
    status: ShipmentStatusEnum
    current_location: Optional[str]
    current_lat: Optional[float]
    current_lon: Optional[float]
    created_at: datetime
    updated_at: datetime
    estimated_delivery: Optional[datetime]
    actual_delivery: Optional[datetime]
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ShipmentListResponse(BaseModel):
    """Response model for shipment list."""
    total: int
    shipments: List[ShipmentResponse]


# Event Schemas
class EventCreate(BaseModel):
    """Create a new event."""
    shipment_id: str
    event_type: EventTypeEnum
    data: Dict[str, Any]
    severity: str = "info"


class EventResponse(BaseModel):
    """Response model for event details."""
    id: int
    shipment_id: str
    timestamp: datetime
    event_type: EventTypeEnum
    data: Dict[str, Any]
    severity: str

    class Config:
        from_attributes = True


# Route Schemas
class RouteCreate(BaseModel):
    """Create a new route."""
    nodes: List[str]
    edges: List[Dict[str, Any]]
    total_distance: float
    estimated_time: float


class RouteResponse(BaseModel):
    """Response model for route details."""
    id: str
    nodes: List[str]
    edges: List[Dict[str, Any]]
    total_distance: float
    estimated_time: float
    risk_score: float

    class Config:
        from_attributes = True


# Prediction Schemas
class PredictionRequest(BaseModel):
    """Request model for disruption prediction."""
    shipment_id: Optional[str] = None
    weather_condition: Optional[str] = None
    delay_history: List[float] = Field(default_factory=list)
    traffic_level: Optional[str] = None
    distance_remaining: Optional[float] = None


class PredictionResponse(BaseModel):
    """Response model for disruption prediction."""
    disruption_probability: float = Field(ge=0, le=1)
    risk_factors: List[str]
    recommended_actions: List[str]


# Reroute Schemas
class RerouteRequest(BaseModel):
    """Request model for rerouting."""
    shipment_id: str
    reason: str
    avoid_regions: Optional[List[str]] = None


class RerouteResponse(BaseModel):
    """Response model for rerouting."""
    shipment_id: str
    old_route: Optional[RouteResponse]
    new_route: RouteResponse
    savings: Optional[Dict[str, float]]  # time, distance, cost saved


# Optimization Request/Response
class OptimizeRouteRequest(BaseModel):
    """Request model for route optimization."""
    source: str
    destination: str
    constraints: Optional[Dict[str, Any]] = None


class OptimizeRouteResponse(BaseModel):
    """Response model for route optimization."""
    route: RouteResponse
    alternatives: List[RouteResponse] = []


# Dashboard Schemas
class DashboardMetrics(BaseModel):
    """Dashboard metrics aggregation."""
    total_shipments: int
    in_transit: int
    delivered: int
    delayed: int
    failed: int
    average_delay_hours: float
    disruption_probability_avg: float
    alerts_active: int


class DashboardResponse(BaseModel):
    """Response model for dashboard."""
    metrics: DashboardMetrics
    recent_events: List[EventResponse]
    critical_alerts: List[Dict[str, Any]]


# Alert Schemas
class AlertResponse(BaseModel):
    """Response model for alert details."""
    id: int
    shipment_id: Optional[str]
    alert_type: str
    message: str
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Health Check
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    redis: str
    neo4j: str
    timestamp: datetime
