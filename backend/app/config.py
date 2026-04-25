"""
Configuration management for the supply chain backend.
Supports environment-based settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/supply_chain"
    sqlalchemy_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # External APIs
    weather_api_url: str = "https://api.openweathermap.org/data/2.5/weather"
    weather_api_key: str = "demo_key"
    traffic_api_url: str = "https://maps.googleapis.com/maps/api/distancematrix/json"
    traffic_api_key: str = "demo_key"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    class Settings:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
