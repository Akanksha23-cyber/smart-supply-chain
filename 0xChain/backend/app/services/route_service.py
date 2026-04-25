"""Service layer for route optimization and management."""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from app.models.models import Route, Shipment, Event, EventType
from app.schemas.schemas import RouteResponse
from app.utils.routing_engine import routing_engine
from app.utils.graph_db import graph_db
from app.services.shipment_service import EventService
import logging
import uuid

logger = logging.getLogger(__name__)


class RouteService:
    """Service layer for route operations."""

    @staticmethod
    def optimize_route(
        db: Session,
        source: str,
        destination: str,
        constraints: Optional[Dict] = None,
    ) -> Dict:
        """Optimize route using graph algorithms."""
        try:
            constraints = constraints or {}

            # Try multiple algorithms and return best
            dijkstra_path, dijkstra_cost = routing_engine.dijkstra(
                source,
                destination,
                weight="distance"
            )

            if not dijkstra_path:
                logger.warning(f"No route found from {source} to {destination}")
                return {}

            # Calculate metrics
            metrics = routing_engine.calculate_route_metrics(dijkstra_path)

            # Create route in database
            route = Route(
                id=f"RT-{uuid.uuid4().hex[:12]}",
                nodes=dijkstra_path,
                edges=[],  # Simplified for demo
                total_distance=metrics.get("distance", 0),
                estimated_time=metrics.get("time_hours", 0),
                risk_score=metrics.get("risk_score", 0),
            )

            db.add(route)
            db.commit()
            db.refresh(route)

            return {
                "route": RouteService._route_to_response(route),
                "metrics": metrics,
            }
        except Exception as e:
            logger.error(f"Route optimization error: {e}")
            return {}

    @staticmethod
    def reroute_shipment(
        db: Session,
        shipment_id: str,
        reason: str,
        avoid_regions: Optional[List[str]] = None,
    ) -> Dict:
        """Trigger rerouting for a shipment."""
        try:
            shipment = db.query(Shipment).filter(
                Shipment.id == shipment_id
            ).first()

            if not shipment:
                logger.error(f"Shipment not found: {shipment_id}")
                return {}

            old_route_id = shipment.route_id

            # Get new route
            new_route_result = RouteService.optimize_route(
                db,
                shipment.source,
                shipment.destination,
                constraints={"avoid": avoid_regions or []}
            )

            if not new_route_result:
                logger.error(f"Could not find new route for {shipment_id}")
                return {}

            new_route = new_route_result["route"]

            # Update shipment
            shipment.route_id = new_route["id"]
            shipment.status = "rerouted"
            db.commit()

            # Create reroute event
            EventService.create_event(
                db,
                shipment_id,
                EventType.REROUTE_TRIGGERED,
                {
                    "old_route": old_route_id,
                    "new_route": new_route["id"],
                    "reason": reason,
                },
                severity="warning"
            )

            logger.info(f"Shipment {shipment_id} rerouted: {reason}")

            # Calculate savings
            old_route = (
                db.query(Route).filter(Route.id == old_route_id).first()
                if old_route_id else None
            )
            savings = None
            if old_route:
                savings = {
                    "distance_saved_km": old_route.total_distance - new_route["total_distance"],
                    "time_saved_hours": old_route.estimated_time - new_route["estimated_time"],
                }

            return {
                "shipment_id": shipment_id,
                "old_route": RouteService._route_to_response(old_route) if old_route else None,
                "new_route": new_route,
                "savings": savings,
            }
        except Exception as e:
            logger.error(f"Reroute error: {e}")
            db.rollback()
            return {}

    @staticmethod
    def get_route(db: Session, route_id: str) -> Optional[Dict]:
        """Get route by ID."""
        try:
            route = db.query(Route).filter(Route.id == route_id).first()
            return RouteService._route_to_response(route) if route else None
        except Exception as e:
            logger.error(f"Error getting route: {e}")
            return None

    @staticmethod
    def _route_to_response(route: Route) -> RouteResponse:
        """Convert Route model to response schema."""
        return RouteResponse(
            id=route.id,
            nodes=route.nodes,
            edges=route.edges or [],
            total_distance=route.total_distance,
            estimated_time=route.estimated_time,
            risk_score=route.risk_score,
        )
