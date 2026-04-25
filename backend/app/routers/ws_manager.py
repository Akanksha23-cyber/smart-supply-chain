"""WebSocket connection manager for real-time updates."""
from fastapi import WebSocket
from typing import List, Dict, Set
from app.utils.logging_config import get_logger
import json
import asyncio

logger = get_logger("websocket")


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.shipment_subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket, shipment_id: str):
        """Accept a WebSocket connection."""
        await websocket.accept()

        # Add to subscriptions
        if shipment_id not in self.active_connections:
            self.active_connections[shipment_id] = set()
        self.active_connections[shipment_id].add(websocket)

        if websocket not in self.shipment_subscriptions:
            self.shipment_subscriptions[websocket] = set()
        self.shipment_subscriptions[websocket].add(shipment_id)

        logger.info(
            "websocket_connected",
            shipment_id=shipment_id,
            connections=len(self.active_connections[shipment_id])
        )

    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket connection."""
        if websocket in self.shipment_subscriptions:
            for shipment_id in self.shipment_subscriptions[websocket]:
                if shipment_id in self.active_connections:
                    self.active_connections[shipment_id].discard(websocket)
                    if not self.active_connections[shipment_id]:
                        del self.active_connections[shipment_id]

            del self.shipment_subscriptions[websocket]

        logger.info("websocket_disconnected")

    async def broadcast_to_shipment(
        self,
        shipment_id: str,
        message: Dict
    ):
        """Broadcast message to all subscribers of a shipment."""
        if shipment_id not in self.active_connections:
            return

        disconnected = []
        for websocket in self.active_connections[shipment_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error("websocket_send_error", shipment_id=shipment_id, error=str(e))
                disconnected.append(websocket)

        # Clean up disconnected connections
        for websocket in disconnected:
            self.disconnect(websocket)

    async def broadcast_alert(self, message: Dict):
        """Broadcast alert to all connected clients."""
        all_websockets = list(
            ws for connections in self.active_connections.values()
            for ws in connections
        )

        disconnected = []
        for websocket in all_websockets:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)


# Global connection manager
manager = ConnectionManager()
