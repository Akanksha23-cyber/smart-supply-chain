# Real-Time Resilient Logistics & Dynamic Supply Chain Optimization System

A production-grade backend system for real-time shipment tracking, anomaly detection, ML-based disruption prediction, and dynamic route optimization.

## 🎯 Features

### Core Functionalities
- **Real-Time Shipment Ingestion**: Track location, speed, and route of shipments in real-time
- **External API Integration**: Mock integrations for weather and traffic APIs
- **Anomaly Detection**: Detect delays, route deviations, and speed anomalies
- **ML Disruption Prediction**: Rule-based model predicting disruption probability (0-1)
- **Dynamic Route Optimization**: Dijkstra & A* algorithms for optimal routing
- **Automatic Rerouting**: Trigger rerouting based on disruptions
- **Real-Time Notifications**: WebSocket support for live updates
- **Comprehensive Caching**: Redis for real-time state management
- **Graph-Based Routing**: Neo4j for network topology and route analysis

### Architecture Highlights
- **FastAPI**: Modern async Python framework
- **PostgreSQL**: Structured data storage
- **Redis**: Caching and real-time alerts
- **Neo4j**: Graph-based routing network
- **Modular Design**: Clear separation of concerns (routers, services, models)
- **Production-Ready**: Structured logging, error handling, health checks

## 📁 Project Structure

```
backend/
├── app/
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic layer
│   ├── db/               # Database configuration
│   ├── utils/            # Utilities (caching, graphs, APIs, routing)
│   ├── ml/               # Machine learning models
│   └── config.py         # Configuration management
├── tests/                # Test suite
├── main.py               # FastAPI entry point
├── init_data.py          # Sample data initialization
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Neo4j 4.4+ (optional for routing features)

### Installation

1. **Clone and setup environment:**
```bash
cd backend
cp .env.example .env
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup databases:**

   **PostgreSQL:**
   ```bash
   createdb supply_chain
   # Update DATABASE_URL in .env
   ```

   **Redis (Docker):**
   ```bash
   docker run -d -p 6379:6379 redis:latest
   ```

   **Neo4j (Docker):**
   ```bash
   docker run -d -p 7687:7687 -p 7474:7474 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:latest
   ```

4. **Initialize sample data:**
```bash
python init_data.py
```

5. **Run the server:**
```bash
python main.py
# Or use uvicorn directly:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

### Auto-Generated Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### Shipments
- `POST /shipments` - Create new shipment
- `GET /shipments` - List all shipments (paginated)
- `GET /shipments/{id}` - Get shipment details
- `PATCH /shipments/{id}` - Update shipment status/location
- `POST /shipments/{id}/mark-delivered` - Mark as delivered

#### Events (Real-Time Data)
- `POST /events` - Ingest location, weather, traffic events
- `GET /events/{shipment_id}` - Get shipment events
- `GET /events` - Get recent events (last 24h)
- `GET /events/critical` - Get critical events

#### Route Optimization
- `POST /routes/optimize` - Find optimal route (Dijkstra)
- `POST /routes/reroute` - Trigger dynamic rerouting
- `GET /routes/{id}` - Get route details

#### Predictions
- `POST /predictions/disruption` - Predict disruption probability
- `POST /predictions/anomalies` - Detect transit anomalies

#### Admin
- `GET /admin/dashboard` - System metrics and status
- `GET /admin/health` - Health check (DB, Redis, Neo4j)

#### WebSocket (Real-Time)
- `WS /ws/shipments/{shipment_id}` - Live shipment updates
- `WS /ws/alerts` - System-wide alert stream

## 🧪 API Testing Examples

### Using cURL

**1. Create a Shipment:**
```bash
curl -X POST http://localhost:8000/shipments \
  -H "Content-Type: application/json" \
  -d '{
    "id": "SHP-001",
    "source": "NYC",
    "destination": "LA",
    "estimated_delivery": "2024-12-28T10:00:00"
  }'
```

**2. List Shipments:**
```bash
curl http://localhost:8000/shipments?skip=0&limit=10
```

**3. Update Shipment:**
```bash
curl -X PATCH http://localhost:8000/shipments/SHP-001 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_transit",
    "current_location": "CHI",
    "current_lat": 41.8781,
    "current_lon": -87.6298
  }'
```

**4. Ingest Event:**
```bash
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHP-001",
    "event_type": "location_update",
    "data": {
      "location": "CHI",
      "lat": 41.8781,
      "lon": -87.6298
    },
    "severity": "info"
  }'
```

**5. Optimize Route:**
```bash
curl -X POST http://localhost:8000/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "source": "NYC",
    "destination": "LA"
  }'
```

**6. Predict Disruption:**
```bash
curl -X POST http://localhost:8000/predictions/disruption \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHP-001",
    "weather_condition": "rainy",
    "traffic_level": "heavy",
    "distance_remaining": 500
  }'
```

**7. Check Health:**
```bash
curl http://localhost:8000/admin/health
```

**8. Get Dashboard:**
```bash
curl http://localhost:8000/admin/dashboard
```

### Using Postman

1. Import the API from `http://localhost:8000/openapi.json`
2. Use the generated collection to test all endpoints
3. Set variables for `shipment_id`, `route_id`, etc.

### WebSocket Testing

**Using websocat:**
```bash
# Install: cargo install websocat
# Connect to shipment updates
websocat ws://localhost:8000/ws/shipments/SHP-001

# In another terminal, send an event:
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## 🤖 Machine Learning Models

### Disruption Predictor
**Input Factors:**
- Weather condition (clear, cloudy, rainy, stormy, snowy)
- Traffic level (low, moderate, heavy, severe)
- Historical delay patterns
- Distance remaining

**Output:**
- Disruption probability (0.0 - 1.0)
- Risk factors list
- Recommended actions

**Example:**
```python
from app.ml.predictor import disruption_predictor

result = disruption_predictor.predict(
    weather_condition="stormy",
    traffic_level="heavy",
    delay_history=[2.5, 3.0, 1.5],
    distance_remaining=500
)
# Result: {
#   "disruption_probability": 0.62,
#   "risk_factors": ["Adverse weather: stormy", "Heavy traffic: heavy"],
#   "recommended_actions": [...]
# }
```

## 🗺️ Routing Engine

### Available Algorithms

**Dijkstra's Algorithm:**
- Find shortest path by distance, time, or risk
- Best for standard route optimization
```python
path, cost = routing_engine.dijkstra("NYC", "LA", weight="distance")
```

**A* Algorithm:**
- Optimized pathfinding with heuristics
- Faster for large graphs
```python
path, cost = routing_engine.a_star("NYC", "LA", heuristic="euclidean")
```

**K-Shortest Paths:**
- Find multiple alternative routes
```python
paths = routing_engine.find_k_shortest_paths("NYC", "LA", k=3)
```

## 🔄 Real-Time Simulation

Simulate real-time data ingestion:

```bash
# Terminal 1: Start server
python main.py

# Terminal 2: Connect to WebSocket
websocat ws://localhost:8000/ws/shipments/SHP-001

# Terminal 3: Send simulated updates
python -c "
import requests
import time
import random

locations = ['NYC', 'CHI', 'DEN', 'LA']
for loc in locations:
    requests.post(
        'http://localhost:8000/events',
        json={
            'shipment_id': 'SHP-001',
            'event_type': 'location_update',
            'data': {'location': loc},
            'severity': 'info'
        }
    )
    time.sleep(2)
"
```

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## 📊 Database Schema

### Shipments Table
- `id` (PRIMARY KEY): Unique shipment identifier
- `source`: Starting location
- `destination`: Final destination
- `status`: Current status (pending, in_transit, delayed, rerouted, delivered, failed)
- `current_location`: Current location
- `current_lat/lon`: GPS coordinates
- `route_id`: Assigned route ID
- `created_at`: Creation timestamp
- `estimated_delivery`: Expected delivery time
- `actual_delivery`: Actual delivery time (if delivered)

### Events Table
- `id` (PRIMARY KEY): Event identifier
- `shipment_id` (FOREIGN KEY): Associated shipment
- `timestamp`: Event occurrence time
- `event_type`: Type of event
- `data`: JSON event details
- `severity`: Critical level

### Routes Table
- `id` (PRIMARY KEY): Route identifier
- `nodes`: List of waypoints
- `edges`: Route segments with weights
- `total_distance`: Total route distance (km)
- `estimated_time`: Estimated travel time (hours)
- `risk_score`: Overall risk rating

## 🔧 Configuration

### Environment Variables
See `.env.example` for all options:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/supply_chain

# Redis
REDIS_URL=redis://localhost:6379/0

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Logging
LOG_LEVEL=INFO
```

## 📈 Performance Optimization

### Caching Strategy
- Shipment state cached in Redis (TTL: 1 hour)
- Real-time alerts stored in Redis lists
- Graph database indexes for fast path queries

### Database Optimization
- Indexes on `shipment_id`, `status`, `timestamp`
- Composite indexes for common queries
- Connection pooling disabled for SQLite compatibility

### API Optimization
- Async endpoints for I/O operations
- Pagination for list endpoints
- Query result limiting

## 🐛 Troubleshooting

### Database Connection Error
```
Check DATABASE_URL in .env
Ensure PostgreSQL is running: psql --version
```

### Redis Connection Error
```
Verify Redis is running: redis-cli ping
Check REDIS_URL in .env
```

### Neo4j Connection Error
```
Verify Neo4j is running on correct port
Check credentials in .env
Enable apoc library for path algorithms
```

### WebSocket Issues
```
Check firewall rules
Verify client is using correct WS URL (ws:// not http://)
Check browser console for errors
```

## 📝 Logging

Structured logging to stdout. Examples:

```json
{
  "event": "supply_chain_event",
  "shipment_id": "SHP-001",
  "event_type": "location_update",
  "timestamp": "2024-12-25T10:30:45.123456"
}
```

## 🚀 Deployment

### Using Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Docker Compose

```yaml
version: "3.8"
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/supply_chain
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: supply_chain
      POSTGRES_PASSWORD: password

  redis:
    image: redis:6
```

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Redis](https://redis.io/)
- [Neo4j](https://neo4j.com/)
- [Pydantic](https://pydantic-settings.readthedocs.io/)

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions welcome! Please follow:
1. PEP 8 code style
2. Add tests for new features
3. Update documentation

## 📞 Support

For issues or questions:
- Check documentation at `/docs`
- Review logs in structured JSON format
- Check health endpoint: `/admin/health`

---

**Built with ❤️ for resilient supply chain optimization**
