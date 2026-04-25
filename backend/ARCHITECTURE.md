# Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│              FastAPI Application Layer                   │
├─────────────────────────────────────────────────────────┤
│  /shipments  │  /events  │  /routes  │  /predictions    │
│              │           │           │                   │
│ ┌──────────────────────────────────────────────────────┐│
│ │            Services Layer (Business Logic)            ││
│ │  ShipmentService │ EventService │ RouteService       ││
│ │  PredictionService │ AnomalyService                  ││
│ └──────────────────────────────────────────────────────┘│
│                          │                               │
│ ┌──────────────────────────────────────────────────────┐│
│ │              Data Access Layer                       ││
│ │  SQLAlchemy ORM │ Redis Cache │ Neo4j Graph         ││
│ └──────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │PostgreSQL│    │  Redis   │    │  Neo4j   │
   │Database  │    │  Cache   │    │  Graph   │
   └──────────┘    └──────────┘    └──────────┘
```

## Module Structure

### 1. **routers/** - API Endpoints
- `shipments.py` - Shipment CRUD operations
- `events.py` - Event ingestion and retrieval
- `predictions.py` - Disruption prediction and anomaly detection
- `routes.py` - Route optimization and rerouting
- `admin.py` - Dashboard and health checks
- `websocket.py` - WebSocket real-time updates
- `ws_manager.py` - Connection management

### 2. **services/** - Business Logic
- `shipment_service.py` - Shipment and event operations
- `prediction_service.py` - ML predictions and anomaly detection
- `route_service.py` - Route optimization logic

### 3. **models/** - ORM Models
- `models.py` - SQLAlchemy models:
  - Shipment
  - Event
  - Route
  - Alert

### 4. **schemas/** - Validation Schemas
- `schemas.py` - Pydantic models for request/response validation

### 5. **db/** - Database Configuration
- `database.py` - SQLAlchemy setup and session management

### 6. **utils/** - Utilities
- `redis_cache.py` - Redis caching layer
- `graph_db.py` - Neo4j graph operations
- `routing_engine.py` - Graph algorithms (Dijkstra, A*)
- `external_apis.py` - Weather, traffic, anomaly detection
- `logging_config.py` - Structured logging

### 7. **ml/** - Machine Learning
- `predictor.py` - Disruption prediction model

## Data Flow

### Creating a Shipment
```
POST /shipments
    ↓
ShipmentRouter.create_shipment()
    ↓
ShipmentService.create_shipment()
    ↓
SQLAlchemy Shipment.create()
    ↓
RedisCache.set_shipment_state()
    ↓
EventLogger.log_event()
    ↓
201 Response
```

### Processing an Event
```
POST /events
    ↓
EventRouter.ingest_event()
    ↓
EventService.create_event()
    ↓
SQLAlchemy Event.create()
    ↓
RedisCache.add_alert()
    ↓
WebSocket broadcast (if severity > info)
    ↓
200 Response
```

### Making a Prediction
```
POST /predictions/disruption
    ↓
PredictionRouter.predict_disruption()
    ↓
PredictionService.predict_disruption()
    ↓
DisruptionPredictor.predict()
    ↓
Machine Learning Model
    ↓
EventService.create_event() (if high probability)
    ↓
200 Response + Recommendations
```

### Optimizing Routes
```
POST /routes/optimize
    ↓
RouteRouter.optimize_route()
    ↓
RouteService.optimize_route()
    ↓
RoutingEngine.dijkstra()
    ↓
Graph calculations
    ↓
RouteService.calculate_metrics()
    ↓
SQLAlchemy Route.create()
    ↓
200 Response + Route data
```

## Database Design

### Shipments Table
```sql
CREATE TABLE shipments (
    id VARCHAR(50) PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    current_location VARCHAR(100),
    current_lat FLOAT,
    current_lon FLOAT,
    route_id VARCHAR(50),
    created_at TIMESTAMP,
    estimated_delivery TIMESTAMP,
    actual_delivery TIMESTAMP,
    metadata JSON,
    INDEX idx_shipment_status (status)
);
```

### Events Table
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    shipment_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    data JSON NOT NULL,
    severity VARCHAR(20),
    INDEX idx_event_shipment_timestamp (shipment_id, timestamp)
);
```

### Routes Table
```sql
CREATE TABLE routes (
    id VARCHAR(50) PRIMARY KEY,
    nodes JSON NOT NULL,
    edges JSON,
    total_distance FLOAT,
    estimated_time FLOAT,
    risk_score FLOAT
);
```

## Caching Strategy

### Redis Keys
```
shipment:{shipment_id}        - Current shipment state
active_alerts                 - List of active alerts
prediction:{shipment_id}      - Cached prediction
route:{route_id}              - Route details
```

### TTL (Time To Live)
- Shipment state: 1 hour
- Predictions: 30 minutes
- Alerts: 24 hours

## Routing Algorithms

### Dijkstra's Algorithm
- Best for: Shortest path by single metric
- Time: O((V + E) log V)
- Use case: Find fastest route given distance/time

### A* Algorithm
- Best for: Fast pathfinding with heuristics
- Heuristics: Euclidean or Manhattan distance
- Use case: Large graphs with spatial data

### K-Shortest Paths
- Best for: Multiple alternative routes
- Algorithm: Modified Dijkstra
- Use case: Backup route options

## ML Model Architecture

### DisruptionPredictor
```python
Input:
  - weather_condition (string)
  - traffic_level (string)
  - delay_history (list of floats)
  - distance_remaining (float)

Weights:
  - Weather: 30%
  - Traffic: 25%
  - Delay History: 25%
  - Distance: 20%

Output:
  - disruption_probability (0.0-1.0)
  - risk_factors (list)
  - recommended_actions (list)
```

## Security Considerations

1. **Input Validation**: Pydantic schemas validate all inputs
2. **SQL Injection**: SQLAlchemy parameterized queries
3. **Dependency Injection**: FastAPI dependency injection pattern
4. **CORS**: Configure for trusted domains
5. **Error Handling**: No sensitive info in error messages

## Performance Optimization

### Query Optimization
- Indexes on frequently filtered columns
- Composite indexes for multi-column queries
- Connection pooling (disabled for SQLite compatibility)

### Caching
- Redis caching for frequently accessed data
- TTL-based automatic expiration
- Cache invalidation on updates

### Async Operations
- All I/O operations are async
- Non-blocking database queries
- Concurrent request handling

## Monitoring & Logging

### Structured Logging
```json
{
  "event": "supply_chain_event",
  "shipment_id": "SHP-001",
  "event_type": "location_update",
  "severity": "info",
  "timestamp": "2024-12-25T10:30:00"
}
```

### Key Metrics
- Total shipments
- In-transit count
- Delivery rate
- Average delay time
- Disruption probability
- Active alerts

### Health Checks
- Database connectivity
- Redis connectivity
- Neo4j connectivity
- API responsiveness

## Deployment Architecture

### Docker Compose
- PostgreSQL container
- Redis container
- Neo4j container
- FastAPI container
- Volume persistence
- Health checks

### Kubernetes Ready
- Stateless API design
- Configuration via environment variables
- Graceful shutdown
- Resource limits definable

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers
- Shared database (PostgreSQL)
- Shared cache (Redis)
- Load balancer frontend

### Vertical Scaling
- Connection pooling optimization
- Query optimization
- Batch processing
- Caching strategies

## Future Enhancements

1. **Advanced ML**: Implement neural networks for predictions
2. **Real-Time Streaming**: Kafka for event streaming
3. **GraphQL**: GraphQL API alongside REST
4. **Authentication**: JWT-based API security
5. **Monitoring**: Prometheus + Grafana integration
6. **Distributed Tracing**: Jaeger for debugging
7. **Message Queue**: Celery for background tasks
8. **API Versioning**: Support multiple API versions

---

**Architecture designed for production scalability and reliability.**
