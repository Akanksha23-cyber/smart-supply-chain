"""Initialize routers module."""
from . import shipments, events, predictions, routes, admin, websocket

__all__ = [
    "shipments",
    "events",
    "predictions",
    "routes",
    "admin",
    "websocket",
]
