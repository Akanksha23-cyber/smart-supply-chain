"""Redis cache management."""
import redis
import json
from typing import Optional, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache wrapper for real-time state management."""

    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair in cache."""
        try:
            if self.redis_client is None:
                return False
            ttl = ttl or settings.redis_cache_ttl
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value) if not isinstance(value, str) else value
            )
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            if self.redis_client is None:
                return None
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        try:
            if self.redis_client is None:
                return False
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False

    def get_shipment_state(self, shipment_id: str) -> Optional[dict]:
        """Get cached shipment state."""
        return self.get(f"shipment:{shipment_id}")

    def set_shipment_state(self, shipment_id: str, state: dict) -> bool:
        """Cache shipment state."""
        return self.set(f"shipment:{shipment_id}", state, ttl=settings.redis_cache_ttl)

    def add_alert(self, alert_id: str, alert_data: dict) -> bool:
        """Add an alert to real-time alerts."""
        try:
            if self.redis_client is None:
                return False
            self.redis_client.lpush("active_alerts", json.dumps(alert_data))
            return True
        except Exception as e:
            logger.error(f"Redis alert error: {e}")
            return False

    def get_alerts(self, limit: int = 10) -> list:
        """Get recent alerts."""
        try:
            if self.redis_client is None:
                return []
            alerts = self.redis_client.lrange("active_alerts", 0, limit - 1)
            return [json.loads(alert) for alert in alerts]
        except Exception as e:
            logger.error(f"Redis get alerts error: {e}")
            return []

    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        try:
            if self.redis_client is None:
                return False
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis connection check failed: {e}")
            return False


# Global Redis cache instance
redis_cache = RedisCache()
