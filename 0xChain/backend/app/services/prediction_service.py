"""Service layer for prediction and anomaly detection."""
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import Shipment, Event, EventType
from app.ml.predictor import disruption_predictor
from app.utils.external_apis import AnomalyDetector, WeatherService, TrafficService
from app.utils.logging_config import EventLogger
from app.services.shipment_service import EventService
import logging

logger = logging.getLogger(__name__)


class PredictionService:
    """Service layer for disruption prediction."""

    @staticmethod
    async def predict_disruption(
        db: Session,
        shipment_id: str,
        weather_condition: Optional[str] = None,
        traffic_level: Optional[str] = None,
        distance_remaining: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Predict disruption probability for a shipment."""
        try:
            shipment = db.query(Shipment).filter(
                Shipment.id == shipment_id
            ).first()
            if not shipment:
                logger.error(f"Shipment not found: {shipment_id}")
                return {}

            # Get delay history
            delay_history = PredictionService._get_delay_history(db, shipment_id)

            # Predict disruption
            prediction = disruption_predictor.predict(
                weather_condition=weather_condition,
                traffic_level=traffic_level,
                delay_history=delay_history,
                distance_remaining=distance_remaining,
            )

            # Log prediction
            EventLogger.log_prediction(
                shipment_id,
                prediction["disruption_probability"],
                prediction["risk_factors"],
                weather=weather_condition,
                traffic=traffic_level,
                distance=distance_remaining
            )

            # Create event for high probability
            if prediction["disruption_probability"] > 0.5:
                EventService.create_event(
                    db,
                    shipment_id,
                    EventType.PREDICTION,
                    {
                        "disruption_probability": prediction["disruption_probability"],
                        "risk_factors": prediction["risk_factors"],
                    },
                    severity="warning" if prediction["disruption_probability"] > 0.7 else "info"
                )

            return prediction
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                "disruption_probability": 0.1,
                "risk_factors": ["Prediction service error"],
                "recommended_actions": ["Monitor shipment"],
            }

    @staticmethod
    def _get_delay_history(db: Session, shipment_id: str, limit: int = 10) -> list:
        """Get historical delays for a shipment source-destination pair."""
        try:
            shipment = db.query(Shipment).filter(
                Shipment.id == shipment_id
            ).first()
            if not shipment:
                return []

            # Get delivered shipments with same route
            similar_shipments = (
                db.query(Shipment)
                .filter(
                    Shipment.source == shipment.source,
                    Shipment.destination == shipment.destination,
                    Shipment.actual_delivery.isnot(None),
                )
                .order_by(desc(Shipment.actual_delivery))
                .limit(limit)
                .all()
            )

            delays = []
            for s in similar_shipments:
                if s.estimated_delivery and s.actual_delivery:
                    delay_hours = (s.actual_delivery - s.estimated_delivery).total_seconds() / 3600
                    if delay_hours > 0:
                        delays.append(delay_hours)

            return delays
        except Exception as e:
            logger.error(f"Error getting delay history: {e}")
            return []


class AnomalyService:
    """Service layer for anomaly detection."""

    @staticmethod
    def detect_anomalies(
        db: Session,
        shipment_id: str,
        current_location: Tuple[float, float],
        current_speed: float,
    ) -> Dict[str, Any]:
        """Detect anomalies in shipment transit data."""
        try:
            shipment = db.query(Shipment).filter(
                Shipment.id == shipment_id
            ).first()
            if not shipment:
                return {}

            anomalies = {
                "detected": False,
                "delay": False,
                "deviation": False,
                "speed": False,
                "details": [],
            }

            # Check for delay
            if shipment.estimated_delivery:
                is_delayed, delay_minutes = AnomalyDetector.detect_delay(
                    datetime.utcnow(),
                    shipment.estimated_delivery,
                    buffer_minutes=30
                )
                if is_delayed:
                    anomalies["detected"] = True
                    anomalies["delay"] = True
                    anomalies["details"].append(
                        f"Shipment is delayed by {delay_minutes:.0f} minutes"
                    )
                    # Create event
                    EventService.create_event(
                        db,
                        shipment_id,
                        EventType.DELAY_DETECTED,
                        {"delay_minutes": delay_minutes},
                        severity="warning"
                    )

            # Check for route deviation
            if shipment.current_lat and shipment.current_lon:
                expected_location = (
                    shipment.current_lat,  # This is simplified
                    shipment.current_lon
                )
                is_deviated, deviation_km = AnomalyDetector.detect_route_deviation(
                    current_location,
                    expected_location,
                    threshold_km=50.0
                )
                if is_deviated:
                    anomalies["detected"] = True
                    anomalies["deviation"] = True
                    anomalies["details"].append(
                        f"Route deviation detected: {deviation_km:.1f}km off expected path"
                    )
                    EventService.create_event(
                        db,
                        shipment_id,
                        EventType.ANOMALY_DETECTED,
                        {"deviation_km": deviation_km},
                        severity="warning"
                    )

            # Check for speed anomaly
            if current_speed > 0:
                avg_speed = 80.0  # km/h - typical truck speed
                is_abnormal_speed = AnomalyDetector.detect_speed_anomaly(
                    current_speed,
                    avg_speed,
                    std_deviation=20.0
                )
                if is_abnormal_speed:
                    anomalies["detected"] = True
                    anomalies["speed"] = True
                    anomalies["details"].append(
                        f"Abnormal speed detected: {current_speed:.1f} km/h"
                    )

            if anomalies["detected"]:
                EventLogger.log_event(
                    shipment_id,
                    "anomalies_detected",
                    f"Anomalies detected: {', '.join(anomalies['details'])}",
                    severity="warning",
                    anomalies=anomalies
                )

            return anomalies
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return {"detected": False, "details": []}

    @staticmethod
    async def get_environmental_factors(
        lat: float,
        lon: float
    ) -> Dict[str, Any]:
        """Get weather and traffic data for a location."""
        try:
            weather_data = await WeatherService.get_weather(lat, lon)
            traffic_data = await TrafficService.get_traffic_conditions(
                f"{lat},{lon}",
                f"{lat + 0.1},{lon + 0.1}"  # Mock destination
            )
            return {
                "weather": weather_data,
                "traffic": traffic_data,
            }
        except Exception as e:
            logger.error(f"Error getting environmental factors: {e}")
            return {"weather": {}, "traffic": {}}
