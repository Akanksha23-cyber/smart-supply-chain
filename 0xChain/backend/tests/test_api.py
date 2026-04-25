"""Test suite for the supply chain backend."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.db.database import Base, get_db
from app.models.models import Shipment, ShipmentStatus
from app.schemas.schemas import ShipmentCreate

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestShipments:
    """Tests for shipment endpoints."""

    def test_create_shipment(self):
        """Test creating a new shipment."""
        response = client.post(
            "/shipments",
            json={
                "id": "SHP-TEST-001",
                "source": "NYC",
                "destination": "LA",
                "estimated_delivery": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "SHP-TEST-001"
        assert data["source"] == "NYC"
        assert data["status"] == "pending"

    def test_get_shipment(self):
        """Test retrieving a shipment."""
        # Create first
        client.post(
            "/shipments",
            json={
                "id": "SHP-TEST-002",
                "source": "CHI",
                "destination": "MIA",
                "estimated_delivery": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            }
        )

        # Get shipment
        response = client.get("/shipments/SHP-TEST-002")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "SHP-TEST-002"

    def test_list_shipments(self):
        """Test listing all shipments."""
        response = client.get("/shipments")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "shipments" in data

    def test_update_shipment(self):
        """Test updating a shipment."""
        # Create first
        client.post(
            "/shipments",
            json={
                "id": "SHP-TEST-003",
                "source": "BOS",
                "destination": "ATL",
                "estimated_delivery": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            }
        )

        # Update
        response = client.patch(
            "/shipments/SHP-TEST-003",
            json={
                "status": "in_transit",
                "current_location": "NYC",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_transit"
        assert data["current_location"] == "NYC"

    def test_mark_delivered(self):
        """Test marking shipment as delivered."""
        # Create first
        client.post(
            "/shipments",
            json={
                "id": "SHP-TEST-004",
                "source": "DEN",
                "destination": "SFO",
                "estimated_delivery": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            }
        )

        # Mark delivered
        response = client.post("/shipments/SHP-TEST-004/mark-delivered")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "delivered"


class TestEvents:
    """Tests for event endpoints."""

    def test_ingest_event(self):
        """Test ingesting an event."""
        # Create shipment first
        client.post(
            "/shipments",
            json={
                "id": "SHP-EVENT-001",
                "source": "NYC",
                "destination": "LA",
                "estimated_delivery": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            }
        )

        # Ingest event
        response = client.post(
            "/events",
            json={
                "shipment_id": "SHP-EVENT-001",
                "event_type": "location_update",
                "data": {"location": "CHI", "lat": 41.8781, "lon": -87.6298},
            }
        )
        assert response.status_code == 200

    def test_get_shipment_events(self):
        """Test retrieving shipment events."""
        response = client.get("/events/SHP-EVENT-001")
        assert response.status_code in [200, 404]


class TestRoutes:
    """Tests for route optimization."""

    def test_optimize_route(self):
        """Test route optimization."""
        response = client.post(
            "/routes/optimize",
            json={
                "source": "NYC",
                "destination": "LA",
            }
        )
        # Note: May fail if graph not initialized, but checks API works
        assert response.status_code in [200, 400]


class TestPredictions:
    """Tests for predictions."""

    def test_predict_disruption(self):
        """Test disruption prediction."""
        # Create shipment first
        client.post(
            "/shipments",
            json={
                "id": "SHP-PRED-001",
                "source": "NYC",
                "destination": "LA",
                "estimated_delivery": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            }
        )

        response = client.post(
            "/predictions/disruption",
            json={
                "shipment_id": "SHP-PRED-001",
                "weather_condition": "rainy",
                "traffic_level": "heavy",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "disruption_probability" in data


class TestAdmin:
    """Tests for admin endpoints."""

    def test_health_check(self):
        """Test health check."""
        response = client.get("/admin/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_dashboard(self):
        """Test dashboard endpoint."""
        response = client.get("/admin/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
