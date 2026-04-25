"""Prediction and anomaly detection endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService, AnomalyService
from app.services.shipment_service import ShipmentService

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/disruption", response_model=PredictionResponse)
async def predict_disruption(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """Predict disruption probability for a shipment."""
    try:
        if not request.shipment_id:
            raise HTTPException(status_code=400, detail="shipment_id is required")

        # Verify shipment exists
        shipment = ShipmentService.get_shipment(db, request.shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        prediction = await PredictionService.predict_disruption(
            db,
            request.shipment_id,
            weather_condition=request.weather_condition,
            traffic_level=request.traffic_level,
            distance_remaining=request.distance_remaining,
        )

        return PredictionResponse(
            disruption_probability=prediction.get("disruption_probability", 0.1),
            risk_factors=prediction.get("risk_factors", []),
            recommended_actions=prediction.get("recommended_actions", []),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anomalies")
async def detect_anomalies(
    shipment_id: str,
    current_location: tuple[float, float],
    current_speed: float,
    db: Session = Depends(get_db)
):
    """Detect anomalies in shipment transit data."""
    try:
        # Verify shipment exists
        shipment = ShipmentService.get_shipment(db, shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        anomalies = AnomalyService.detect_anomalies(
            db,
            shipment_id,
            current_location,
            current_speed
        )

        return anomalies
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
