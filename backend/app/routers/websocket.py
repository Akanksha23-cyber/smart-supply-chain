"""WebSocket endpoints for real-time updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.routers.ws_manager import manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/shipments/{shipment_id}")
async def websocket_shipment_updates(websocket: WebSocket, shipment_id: str):
    """
    WebSocket endpoint for real-time shipment updates.

    Usage:
        ws://localhost:8000/ws/shipments/{shipment_id}

    Messages sent by server:
        - location_update: Current location and status
        - event_alert: Real-time events
        - prediction_update: Disruption predictions
        - reroute_notification: Rerouting triggered
    """
    await manager.connect(websocket, shipment_id)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for shipment {shipment_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for system-wide alerts.

    Usage:
        ws://localhost:8000/ws/alerts

    Messages sent by server:
        - alert: System alerts
        - prediction: Disruption predictions
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        logger.info("Alert WebSocket disconnected")
    except Exception as e:
        logger.error(f"Alert WebSocket error: {e}")
