"""Structured logging configuration."""
import structlog
import logging
from app.config import settings
from datetime import datetime


def configure_logging():
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance."""
    return structlog.get_logger(name)


class EventLogger:
    """Specialized logger for supply chain events."""

    @staticmethod
    def log_event(
        shipment_id: str,
        event_type: str,
        message: str,
        severity: str = "info",
        **context
    ):
        """Log a supply chain event."""
        logger = get_logger("event")
        logger.log(
            logging.getLevelName(severity.upper()),
            "supply_chain_event",
            shipment_id=shipment_id,
            event_type=event_type,
            message=message,
            severity=severity,
            timestamp=datetime.utcnow().isoformat(),
            **context
        )

    @staticmethod
    def log_prediction(
        shipment_id: str,
        disruption_probability: float,
        risk_factors: list,
        **context
    ):
        """Log a disruption prediction."""
        logger = get_logger("prediction")
        logger.info(
            "disruption_prediction",
            shipment_id=shipment_id,
            disruption_probability=disruption_probability,
            risk_factors=risk_factors,
            timestamp=datetime.utcnow().isoformat(),
            **context
        )

    @staticmethod
    def log_reroute(
        shipment_id: str,
        old_route: str,
        new_route: str,
        reason: str,
        **context
    ):
        """Log a rerouting event."""
        logger = get_logger("reroute")
        logger.warning(
            "shipment_rerouted",
            shipment_id=shipment_id,
            old_route=old_route,
            new_route=new_route,
            reason=reason,
            timestamp=datetime.utcnow().isoformat(),
            **context
        )
