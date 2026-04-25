# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Option 1: Using Docker Compose (Recommended)

```bash
# Start all services (PostgreSQL, Redis, Neo4j, FastAPI)
docker-compose up --build

# In another terminal, initialize data
docker exec supply_chain_backend python init_data.py

# Check health
curl http://localhost:8000/admin/health
```

### Option 2: Manual Setup

#### Prerequisites
- Python 3.10+, PostgreSQL 12+, Redis 6+

#### Installation
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start databases
# PostgreSQL
psql -c "CREATE DATABASE supply_chain;"

# Redis
redis-server

# Neo4j (optional, for advanced routing)
docker run -d -p 7687:7687 neo4j:latest

# 4. Initialize database tables
python db_init.py init

# 5. Load sample data
python init_data.py

# 6. Run server
python main.py
```

## 📊 First API Calls

### 1. Create a Shipment
```bash
curl -X POST http://localhost:8000/shipments \
  -H "Content-Type: application/json" \
  -d '{
    "id": "TEST-001",
    "source": "NYC",
    "destination": "LA",
    "estimated_delivery": "2024-12-28T10:00:00"
  }'
```

### 2. Update Location
```bash
curl -X PATCH http://localhost:8000/shipments/TEST-001 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_transit",
    "current_location": "Chicago",
    "current_lat": 41.8781,
    "current_lon": -87.6298
  }'
```

### 3. Send Location Event
```bash
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "TEST-001",
    "event_type": "location_update",
    "data": {"location": "Chicago"},
    "severity": "info"
  }'
```

### 4. Predict Disruption
```bash
curl -X POST http://localhost:8000/predictions/disruption \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "TEST-001",
    "weather_condition": "rainy",
    "traffic_level": "heavy"
  }'
```

### 5. Optimize Route
```bash
curl -X POST http://localhost:8000/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "source": "NYC",
    "destination": "LA"
  }'
```

### 6. Check System Health
```bash
curl http://localhost:8000/admin/health
```

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| API | http://localhost:8000 | Main API |
| Swagger Docs | http://localhost:8000/docs | Interactive API docs |
| ReDoc | http://localhost:8000/redoc | API documentation |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Caching |
| Neo4j | localhost:7687 | Graph DB |

## 🧪 Test Everything

```bash
# Run pytest
pytest tests/ -v

# Health check script
python health_check.py

# Simulate real-time data (5 minutes)
python simulate_data.py 5
```

## 📝 Environment Variables

Edit `.env` for configuration:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/supply_chain

# Redis
REDIS_URL=redis://localhost:6379/0

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Server
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

## 🆘 Troubleshooting

### API not responding
```bash
# Check if server is running
curl http://localhost:8000/health

# View logs
tail -f app.log

# Restart
python main.py
```

### Database connection error
```bash
# Test PostgreSQL
psql -U postgres -h localhost -d supply_chain -c "SELECT 1"

# Reset database
python db_init.py init
python init_data.py
```

### Redis connection error
```bash
# Test Redis
redis-cli ping

# Restart Redis
redis-server
```

### Neo4j issues
```bash
# Test Neo4j connection
docker logs supply_chain_neo4j

# Verify credentials
neo4j-admin set-initial-password [your-password]
```

## 📚 Next Steps

1. **Read Full Documentation**: See [README.md](README.md)
2. **API Testing**: See [API_TESTING.md](API_TESTING.md)
3. **System Design**: Review modular architecture in `/app`
4. **Deployment**: Deploy with Docker Compose or Kubernetes

## 🎯 Key Features to Try

✅ Real-time shipment tracking
✅ Automatic anomaly detection
✅ ML-based disruption prediction
✅ Dynamic route optimization
✅ Live WebSocket updates
✅ System dashboard
✅ Health monitoring

## 💡 Pro Tips

- Use `/docs` for interactive API testing
- WebSocket: `ws://localhost:8000/ws/shipments/{shipment_id}`
- Enable DEBUG=True for detailed logs
- Use `python simulate_data.py` to generate test data
- Monitor with `python health_check.py`

---

**Ready to go! 🚀**
