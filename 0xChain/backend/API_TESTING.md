"""Comprehensive API testing guide and examples."""

# ============================================================================
# API TESTING GUIDE - Supply Chain Backend
# ============================================================================

# Test Scenario 1: Create and Track a New Shipment
# ============================================================================

# 1.1 Create a shipment
curl -X POST http://localhost:8000/shipments \
  -H "Content-Type: application/json" \
  -d '{
    "id": "SHP-NYC-LA-001",
    "source": "NYC",
    "destination": "LA",
    "estimated_delivery": "2024-12-28T14:00:00"
  }'

# Expected response:
# {
#   "id": "SHP-NYC-LA-001",
#   "source": "NYC",
#   "destination": "LA",
#   "status": "pending",
#   "current_location": null,
#   "created_at": "2024-12-25T10:30:00",
#   "updated_at": "2024-12-25T10:30:00",
#   "estimated_delivery": "2024-12-28T14:00:00",
#   "actual_delivery": null,
#   "metadata": null
# }

# 1.2 Update shipment to in-transit
curl -X PATCH http://localhost:8000/shipments/SHP-NYC-LA-001 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_transit",
    "current_location": "New York Distribution Center",
    "current_lat": 40.7128,
    "current_lon": -74.0060
  }'

# 1.3 Get shipment details
curl http://localhost:8000/shipments/SHP-NYC-LA-001

# 1.4 List all shipments with pagination
curl "http://localhost:8000/shipments?skip=0&limit=10"

# 1.5 Filter shipments by status
curl "http://localhost:8000/shipments?status=in_transit"


# Test Scenario 2: Real-Time Event Ingestion
# ============================================================================

# 2.1 Ingest location update event
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHP-NYC-LA-001",
    "event_type": "location_update",
    "data": {
      "location": "Chicago Hub",
      "lat": 41.8781,
      "lon": -87.6298,
      "speed": 65.5,
      "timestamp": "2024-12-25T12:30:00"
    },
    "severity": "info"
  }'

# 2.2 Ingest weather update
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHP-NYC-LA-001",
    "event_type": "weather_update",
    "data": {
      "condition": "stormy",
      "temperature": 5,
      "wind_speed": 45,
      "visibility": 2.5
    },
    "severity": "warning"
  }'

# 2.3 Ingest traffic update
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHP-NYC-LA-001",
    "event_type": "traffic_update",
    "data": {
      "traffic_level": "heavy",
      "incidents": 3,
      "estimated_delay_minutes": 45
    },
    "severity": "warning"
  }'

# 2.4 Get all events for a shipment
curl http://localhost:8000/events/SHP-NYC-LA-001

# 2.5 Get recent events (last 24 hours)
curl "http://localhost:8000/events?hours=24&limit=50"

# 2.6 Get only critical events
curl http://localhost:8000/events/critical


# Test Scenario 3: Disruption Prediction
# ============================================================================

# 3.1 Predict disruption with current conditions
curl -X POST http://localhost:8000/predictions/disruption \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHP-NYC-LA-001",
    "weather_condition": "stormy",
    "traffic_level": "heavy",
    "delay_history": [2.5, 3.0, 1.5],
    "distance_remaining": 1800
  }'

# Expected response:
# {
#   "disruption_probability": 0.68,
#   "risk_factors": [
#     "Adverse weather: stormy",
#     "Heavy traffic: heavy",
#     "Long distance remaining: 1800km"
#   ],
#   "recommended_actions": [
#     "URGENT: Consider immediate rerouting",
#     "Alert customer of potential delays",
#     "Prepare alternative carriers",
#     "Track weather updates closely",
#     "Monitor traffic and consider flexible routing"
#   ]
# }

# 3.2 Get predictions for multiple shipments
for shipment in "SHP-001" "SHP-002" "SHP-003"; do
  curl -X POST http://localhost:8000/predictions/disruption \
    -H "Content-Type: application/json" \
    -d "{\"shipment_id\": \"$shipment\", \"weather_condition\": \"rainy\"}"
done


# Test Scenario 4: Route Optimization
# ============================================================================

# 4.1 Optimize route (Dijkstra algorithm)
curl -X POST http://localhost:8000/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "source": "NYC",
    "destination": "LA",
    "constraints": {
      "avoid": ["desert_regions"]
    }
  }'

# Expected response:
# {
#   "route": {
#     "id": "RT-xxx",
#     "nodes": ["NYC", "CHI", "DEN", "PHX", "LA"],
#     "total_distance": 2800,
#     "estimated_time": 40,
#     "risk_score": 0.22
#   },
#   "alternatives": []
# }

# 4.2 Trigger rerouting due to disruption
curl -X POST http://localhost:8000/routes/reroute \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHP-NYC-LA-001",
    "reason": "Severe weather in Phoenix region",
    "avoid_regions": ["PHX"]
  }'

# Expected response:
# {
#   "shipment_id": "SHP-NYC-LA-001",
#   "old_route": {...},
#   "new_route": {...},
#   "savings": {
#     "distance_saved_km": -150,
#     "time_saved_hours": -2.5
#   }
# }

# 4.3 Get route details
curl http://localhost:8000/routes/RT-xxx


# Test Scenario 5: Anomaly Detection
# ============================================================================

# 5.1 Detect anomalies in transit data
curl -X POST "http://localhost:8000/predictions/anomalies?shipment_id=SHP-NYC-LA-001&current_location=41.8781,-87.6298&current_speed=15" \
  -H "Content-Type: application/json"

# Expected response:
# {
#   "detected": true,
#   "delay": true,
#   "deviation": false,
#   "speed": true,
#   "details": [
#     "Shipment is delayed by 120 minutes",
#     "Abnormal speed detected: 15 km/h"
#   ]
# }


# Test Scenario 6: Dashboard & Monitoring
# ============================================================================

# 6.1 Get system dashboard
curl http://localhost:8000/admin/dashboard

# Expected response:
# {
#   "metrics": {
#     "total_shipments": 5,
#     "in_transit": 2,
#     "delivered": 1,
#     "delayed": 1,
#     "failed": 0,
#     "average_delay_hours": 2.5,
#     "disruption_probability_avg": 0.35,
#     "alerts_active": 3
#   },
#   "recent_events": [...],
#   "critical_alerts": [...]
# }

# 6.2 Check system health
curl http://localhost:8000/admin/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "redis": "connected",
#   "neo4j": "connected",
#   "timestamp": "2024-12-25T10:30:00"
# }


# Test Scenario 7: Mark Delivery
# ============================================================================

# 7.1 Mark shipment as delivered
curl -X POST http://localhost:8000/shipments/SHP-NYC-LA-001/mark-delivered

# Verify delivery status
curl http://localhost:8000/shipments/SHP-NYC-LA-001


# Test Scenario 8: WebSocket Real-Time Updates (Advanced)
# ============================================================================

# Using websocat (install: cargo install websocat)

# 8.1 Connect to shipment updates
websocat ws://localhost:8000/ws/shipments/SHP-NYC-LA-001

# 8.2 In another terminal, send events
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHP-NYC-LA-001",
    "event_type": "location_update",
    "data": {"location": "Denver", "lat": 39.7392, "lon": -104.9903}
  }'

# 8.3 Connect to system alerts
websocat ws://localhost:8000/ws/alerts


# Performance Testing
# ============================================================================

# Load test: Create multiple shipments
for i in {1..100}; do
  curl -X POST http://localhost:8000/shipments \
    -H "Content-Type: application/json" \
    -d "{
      \"id\": \"SHP-LOAD-$i\",
      \"source\": \"NYC\",
      \"destination\": \"LA\",
      \"estimated_delivery\": \"2024-12-28T14:00:00\"
    }" &
done
wait

# Stress test: Rapid event ingestion
for i in {1..50}; do
  curl -X POST http://localhost:8000/events \
    -H "Content-Type: application/json" \
    -d "{
      \"shipment_id\": \"SHP-NYC-LA-001\",
      \"event_type\": \"location_update\",
      \"data\": {\"location\": \"Stop $i\", \"speed\": $((RANDOM % 100))}
    }" &
done
wait


# Batch Operations
# ============================================================================

# Process multiple shipment updates
cat > batch_updates.json << 'EOF'
[
  {
    "id": "SHP-001",
    "status": "in_transit",
    "current_location": "CHI"
  },
  {
    "id": "SHP-002",
    "status": "delayed",
    "current_location": "DEN"
  },
  {
    "id": "SHP-003",
    "status": "delivered",
    "current_location": "LA"
  }
]
EOF

# Process batch
while IFS= read -r line; do
  shipment_id=$(echo "$line" | grep -o '"id": "[^"]*' | cut -d'"' -f4)
  curl -X PATCH "http://localhost:8000/shipments/$shipment_id" \
    -H "Content-Type: application/json" \
    -d "$line"
done < batch_updates.json
