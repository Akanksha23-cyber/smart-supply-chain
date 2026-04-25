"""Sample data initialization script."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.models import Shipment, Event, Route, ShipmentStatus, EventType
from app.utils.routing_engine import routing_engine
import random
import uuid


def init_graph_network():
    """Initialize sample network graph for routing."""
    # Define sample cities/nodes
    cities = {
        "NYC": (40.7128, -74.0060),
        "LA": (34.0522, -118.2437),
        "CHI": (41.8781, -87.6298),
        "HOU": (29.7604, -95.3698),
        "PHX": (33.4484, -112.0742),
        "MIA": (25.7617, -80.1918),
        "SFO": (37.7749, -122.4194),
        "BOS": (42.3601, -71.0589),
        "ATL": (33.7490, -84.3880),
        "DEN": (39.7392, -104.9903),
    }

    # Add nodes
    for city, (lat, lon) in cities.items():
        routing_engine.add_node(city, lat=lat, lon=lon, name=city)

    # Add sample edges (routes between cities)
    routes_data = [
        ("NYC", "BOS", 215, 3.5),
        ("NYC", "CHI", 790, 11.5),
        ("NYC", "MIA", 1280, 18.5),
        ("CHI", "DEN", 920, 13.5),
        ("DEN", "LA", 1020, 15),
        ("DEN", "SFO", 1300, 19),
        ("LA", "SFO", 380, 5.5),
        ("PHX", "LA", 370, 5.5),
        ("HOU", "ATL", 790, 11.5),
        ("ATL", "MIA", 660, 9.5),
        ("SFO", "PHX", 650, 9.5),
        ("CHI", "ATL", 720, 10.5),
    ]

    for from_node, to_node, distance, time in routes_data:
        routing_engine.add_edge(from_node, to_node, distance, time, risk=random.uniform(0.1, 0.3))
        # Add reverse route
        routing_engine.add_edge(to_node, from_node, distance, time, risk=random.uniform(0.1, 0.3))


def seed_sample_shipments(db: Session):
    """Create sample shipments."""
    cities = ["NYC", "LA", "CHI", "HOU", "PHX", "MIA", "SFO", "BOS", "ATL", "DEN"]

    shipments_data = [
        {
            "id": "SHP-001-URGENT",
            "source": "NYC",
            "destination": "LA",
            "status": ShipmentStatus.IN_TRANSIT,
            "current_location": "CHI",
            "current_lat": 41.8781,
            "current_lon": -87.6298,
            "estimated_delivery": datetime.utcnow() + timedelta(days=3),
        },
        {
            "id": "SHP-002-STANDARD",
            "source": "LA",
            "destination": "NYC",
            "status": ShipmentStatus.IN_TRANSIT,
            "current_location": "DEN",
            "current_lat": 39.7392,
            "current_lon": -104.9903,
            "estimated_delivery": datetime.utcnow() + timedelta(days=4),
        },
        {
            "id": "SHP-003-EXPRESS",
            "source": "SFO",
            "destination": "LA",
            "status": ShipmentStatus.PENDING,
            "current_location": "SFO",
            "current_lat": 37.7749,
            "current_lon": -122.4194,
            "estimated_delivery": datetime.utcnow() + timedelta(days=1),
        },
        {
            "id": "SHP-004-DELAYED",
            "source": "CHI",
            "destination": "MIA",
            "status": ShipmentStatus.DELAYED,
            "current_location": "ATL",
            "current_lat": 33.7490,
            "current_lon": -84.3880,
            "estimated_delivery": datetime.utcnow() - timedelta(hours=2),
        },
        {
            "id": "SHP-005-DELIVERED",
            "source": "BOS",
            "destination": "NYC",
            "status": ShipmentStatus.DELIVERED,
            "current_location": "NYC",
            "current_lat": 40.7128,
            "current_lon": -74.0060,
            "estimated_delivery": datetime.utcnow() - timedelta(days=1),
            "actual_delivery": datetime.utcnow() - timedelta(hours=12),
        },
    ]

    for data in shipments_data:
        # Check if shipment already exists
        existing = db.query(Shipment).filter(Shipment.id == data["id"]).first()
        if not existing:
            shipment = Shipment(**data)
            db.add(shipment)
            print(f"✅ Created shipment: {data['id']}")

    db.commit()


def seed_sample_events(db: Session):
    """Create sample events."""
    events_data = [
        {
            "shipment_id": "SHP-001-URGENT",
            "event_type": EventType.LOCATION_UPDATE,
            "data": {"location": "CHI", "lat": 41.8781, "lon": -87.6298},
            "severity": "info",
        },
        {
            "shipment_id": "SHP-001-URGENT",
            "event_type": EventType.WEATHER_UPDATE,
            "data": {"condition": "rainy", "temperature": 15},
            "severity": "warning",
        },
        {
            "shipment_id": "SHP-004-DELAYED",
            "event_type": EventType.DELAY_DETECTED,
            "data": {"delay_minutes": 120},
            "severity": "warning",
        },
        {
            "shipment_id": "SHP-002-STANDARD",
            "event_type": EventType.TRAFFIC_UPDATE,
            "data": {"traffic_level": "heavy"},
            "severity": "info",
        },
    ]

    for data in events_data:
        event = Event(**data)
        db.add(event)
        print(f"✅ Created event: {data['event_type'].value} for {data['shipment_id']}")

    db.commit()


def seed_sample_routes(db: Session):
    """Create sample routes."""
    routes_data = [
        {
            "id": "RT-NYC-LA-001",
            "nodes": ["NYC", "CHI", "DEN", "PHX", "LA"],
            "edges": [],
            "total_distance": 2800,
            "estimated_time": 40,
            "risk_score": 0.2,
        },
        {
            "id": "RT-LA-NYC-001",
            "nodes": ["LA", "PHX", "DEN", "CHI", "NYC"],
            "edges": [],
            "total_distance": 2800,
            "estimated_time": 40,
            "risk_score": 0.25,
        },
        {
            "id": "RT-SFO-LA-001",
            "nodes": ["SFO", "LA"],
            "edges": [],
            "total_distance": 380,
            "estimated_time": 5.5,
            "risk_score": 0.1,
        },
    ]

    for data in routes_data:
        existing = db.query(Route).filter(Route.id == data["id"]).first()
        if not existing:
            route = Route(**data)
            db.add(route)
            print(f"✅ Created route: {data['id']}")

    db.commit()


def main():
    """Initialize sample data."""
    print("\n🌱 Initializing Sample Data...\n")

    # Initialize graph network
    print("📍 Initializing network graph...")
    init_graph_network()
    print("✅ Network graph initialized\n")

    # Create tables
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created\n")

    # Seed data
    db = SessionLocal()
    try:
        print("📦 Seeding sample shipments...")
        seed_sample_shipments(db)

        print("\n📅 Seeding sample events...")
        seed_sample_events(db)

        print("\n🗺️  Seeding sample routes...")
        seed_sample_routes(db)

        print("\n✅ Sample data initialization complete!\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
