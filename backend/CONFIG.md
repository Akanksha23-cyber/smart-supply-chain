# Configuration Guide

## Environment Variables

All configuration is managed through environment variables. Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

## Database Configuration

### PostgreSQL
```env
# Format: postgresql://[user]:[password]@[host]:[port]/[database]
DATABASE_URL=postgresql://supply_user:supply_password@localhost:5432/supply_chain

# Connection pooling
SQLALCHEMY_ECHO=False  # Set to True for SQL query logging
```

**Setup:**
```bash
# Create database
createdb supply_chain

# Create user
createuser supply_user
psql -c "ALTER USER supply_user WITH PASSWORD 'supply_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE supply_chain TO supply_user;"
```

### Redis Configuration

```env
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600  # Cache expiration in seconds
```

**Setup:**
```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or locally
redis-server
```

### Neo4j Configuration

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

**Setup:**
```bash
# Using Docker
docker run -d \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

## API Configuration

```env
API_HOST=0.0.0.0         # Listen on all interfaces
API_PORT=8000            # Server port
DEBUG=True               # Development mode (disable in production)
```

## Logging Configuration

```env
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Structured logs output to stdout as JSON:
```json
{
  "event": "event_name",
  "timestamp": "2024-12-25T10:30:00.000000",
  "level": "INFO"
}
```

## External API Configuration

### Weather API

```env
WEATHER_API_URL=https://api.openweathermap.org/data/2.5/weather
WEATHER_API_KEY=your_api_key
```

Currently uses mock implementation. To enable real API:
1. Get API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Update `WEATHER_API_KEY`
3. Modify `WeatherService.get_weather()` to use real requests

### Traffic API

```env
TRAFFIC_API_URL=https://maps.googleapis.com/maps/api/distancematrix/json
TRAFFIC_API_KEY=your_api_key
```

Currently uses mock implementation. To enable real API:
1. Get API key from [Google Maps](https://developers.google.com/)
2. Update `TRAFFIC_API_KEY`
3. Modify `TrafficService.get_traffic_conditions()` to use real requests

## Docker Environment

When using Docker Compose, databases are automatically configured:

```yaml
environment:
  DATABASE_URL: postgresql://supply_user:supply_password@postgres:5432/supply_chain
  REDIS_URL: redis://redis:6379/0
  NEO4J_URI: bolt://neo4j:7687
  NEO4J_USERNAME: neo4j
  NEO4J_PASSWORD: supply_password
  API_HOST: 0.0.0.0
  API_PORT: 8000
```

## Production Settings

For production deployment:

```env
DEBUG=False              # Disable debug mode
LOG_LEVEL=WARNING        # Only log warnings and errors
API_HOST=0.0.0.0        # Production app listens on all IPs
API_PORT=8000           # Standard port

# Database with connection pooling
DATABASE_URL=postgresql://[prod_user]:[strong_password]@[prod_host]:5432/[prod_db]

# Redis cluster
REDIS_URL=redis://[cluster_host]:6379/0

# Neo4j cluster
NEO4J_URI=bolt://[neo4j_host]:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=[strong_password]
```

## Configuration Validation

The application validates all configuration on startup. Check logs for:

```
✓ Database connected
✓ Redis connected
✓ Neo4j connected
```

If any service is not available:
- The application will start but with degraded functionality
- Check `/admin/health` endpoint for status
- Review logs for specific error messages

## Modifying Configuration

### At Runtime

Configuration is read on application startup. To apply changes:

1. Update `.env` file
2. Restart the application
3. Verify changes with health check:

```bash
curl http://localhost:8000/admin/health
```

### In Code

Direct configuration can be modified in `app/config.py`:

```python
class Settings(BaseSettings):
    database_url: str = "postgresql://..."
    redis_cache_ttl: int = 3600
    # ... other settings
```

## Configuration Examples

### Local Development

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/supply_chain
REDIS_URL=redis://localhost:6379/0
NEO4J_URI=bolt://localhost:7687
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
LOG_LEVEL=DEBUG
```

### Docker Compose

```env
DATABASE_URL=postgresql://supply_user:supply_password@postgres:5432/supply_chain
REDIS_URL=redis://redis:6379/0
NEO4J_URI=bolt://neo4j:7687
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
LOG_LEVEL=INFO
```

### Kubernetes

```env
DATABASE_URL=postgresql://supply_user@postgres.default.svc.cluster.local/supply_chain
REDIS_URL=redis://redis.default.svc.cluster.local:6379/0
NEO4J_URI=bolt://neo4j.default.svc.cluster.local:7687
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
LOG_LEVEL=WARNING
```

## Troubleshooting Configuration

### Connection Refused

```bash
# Test database
psql -h localhost -U supply_user -d supply_chain

# Test Redis
redis-cli -h localhost ping

# Test Neo4j
curl http://localhost:7474/
```

### Environment Variables Not Loading

```bash
# Verify .env file exists
ls -la .env

# Check file format
cat .env | head -20

# Ensure no extra spaces
DATABASE_URL=value  # OK
DATABASE_URL = value  # NOT OK
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000
kill -9 <PID>

# Or change API_PORT
API_PORT=8001
```

## Configuration Precedence

Configuration is loaded in this order (later overrides earlier):

1. Default values in `app/config.py`
2. Environment variables from `.env` file
3. System environment variables
4. Docker compose environment
5. Kubernetes ConfigMap/Secrets

## Performance Tuning

### Database Optimization

```env
# Connection pooling size
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=40
```

### Redis Optimization

```env
# Larger TTL for less frequently updated data
REDIS_CACHE_TTL=7200  # 2 hours
```

### API Optimization

```env
# Number of worker processes (docker-compose)
WORKERS=4
THREADS_PER_WORKER=2
```

## Security Configuration

### Credentials

```env
# Use strong passwords
NEO4J_PASSWORD=super_strong_password_123!
POSTGRES_PASSWORD=$(openssl rand -base64 32)
```

### CORS

Modify in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trusted-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### API Keys

For external APIs:

```env
WEATHER_API_KEY=real_api_key_here
TRAFFIC_API_KEY=real_api_key_here
```

---

**Keep configuration secure and environment-specific!**
