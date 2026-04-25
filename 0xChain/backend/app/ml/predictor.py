"""Machine learning models for disruption prediction."""
import numpy as np
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DisruptionPredictor:
    """Simplified ML model for disruption probability prediction."""

    def __init__(self):
        """Initialize the predictor with rule-based logic."""
        self.weather_risk_map = {
            "clear": 0.05,
            "cloudy": 0.10,
            "rainy": 0.25,
            "stormy": 0.60,
            "snowy": 0.70,
        }
        self.traffic_risk_map = {
            "low": 0.05,
            "moderate": 0.15,
            "heavy": 0.35,
            "severe": 0.70,
        }

    def predict(
        self,
        weather_condition: Optional[str] = None,
        traffic_level: Optional[str] = None,
        delay_history: List[float] = None,
        distance_remaining: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Predict disruption probability using rule-based approach.

        Args:
            weather_condition: Current weather
            traffic_level: Current traffic level
            delay_history: Historical delays in hours
            distance_remaining: Remaining distance in km

        Returns:
            Dict with probability and risk factors
        """
        try:
            risk_score = 0.0
            risk_factors: List[str] = []
            weights = []

            # Weather risk
            if weather_condition:
                weather_risk = self.weather_risk_map.get(weather_condition.lower(), 0.1)
                risk_score += weather_risk * 0.3
                weights.append(0.3)
                if weather_risk > 0.3:
                    risk_factors.append(f"Adverse weather: {weather_condition}")

            # Traffic risk
            if traffic_level:
                traffic_risk = self.traffic_risk_map.get(traffic_level.lower(), 0.1)
                risk_score += traffic_risk * 0.25
                weights.append(0.25)
                if traffic_risk > 0.3:
                    risk_factors.append(f"Heavy traffic: {traffic_level}")

            # Historical delay risk
            if delay_history and len(delay_history) > 0:
                avg_delay = np.mean(delay_history)
                delay_risk = min(avg_delay / 24.0, 1.0)  # Normalize to max 1.0
                risk_score += delay_risk * 0.25
                weights.append(0.25)
                if avg_delay > 6:
                    risk_factors.append(f"History of delays: avg {avg_delay:.1f}h")

            # Distance risk (longer distances = higher risk)
            if distance_remaining:
                distance_risk = min(distance_remaining / 1000.0, 0.5)  # Cap at 0.5
                risk_score += distance_risk * 0.2
                weights.append(0.2)
                if distance_remaining > 500:
                    risk_factors.append(f"Long distance remaining: {distance_remaining:.0f}km")

            # Normalize score if we have weights
            if weights:
                risk_score = risk_score / sum(weights)
            else:
                risk_score = 0.1  # Default baseline risk

            # Ensure probability is between 0 and 1
            disruption_probability = min(max(risk_score, 0.0), 1.0)

            # Generate recommended actions
            recommended_actions = self._get_recommendations(
                disruption_probability,
                risk_factors
            )

            return {
                "disruption_probability": disruption_probability,
                "risk_factors": risk_factors,
                "recommended_actions": recommended_actions,
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                "disruption_probability": 0.1,
                "risk_factors": ["Prediction model error"],
                "recommended_actions": ["Monitor shipment closely"],
            }

    @staticmethod
    def _get_recommendations(
        probability: float,
        risk_factors: List[str]
    ) -> List[str]:
        """Generate recommendations based on disruption probability."""
        recommendations = []

        if probability > 0.7:
            recommendations.append("URGENT: Consider immediate rerouting")
            recommendations.append("Alert customer of potential delays")
            recommendations.append("Prepare alternative carriers")
        elif probability > 0.5:
            recommendations.append("Monitor shipment closely")
            recommendations.append("Identify backup routes")
            recommendations.append("Notify stakeholders of elevated risk")
        elif probability > 0.3:
            recommendations.append("Standard monitoring active")
            recommendations.append("Keep alternative routes ready")
        else:
            recommendations.append("Proceed with normal handling")

        # Add specific recommendations based on risk factors
        if any("weather" in rf.lower() for rf in risk_factors):
            recommendations.append("Track weather updates closely")
        if any("traffic" in rf.lower() for rf in risk_factors):
            recommendations.append("Monitor traffic and consider flexible routing")
        if any("delay" in rf.lower() for rf in risk_factors):
            recommendations.append("Add buffer time to next stop")

        return recommendations[:5]  # Return top 5 recommendations


# Global predictor instance
disruption_predictor = DisruptionPredictor()
