"""Route optimization endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.db.database import get_db
from app.schemas.schemas import OptimizeRouteRequest, OptimizeRouteResponse, RerouteRequest, RerouteResponse
from app.services.route_service import RouteService

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post("/optimize", response_model=OptimizeRouteResponse)
def optimize_route(
    request: OptimizeRouteRequest,
    db: Session = Depends(get_db)
):
    """Compute optimal route between source and destination."""
    try:
        result = RouteService.optimize_route(
            db,
            request.source,
            request.destination,
            constraints=request.constraints
        )

        if not result:
            raise HTTPException(
                status_code=400,
                detail="Could not find route between source and destination"
            )

        return OptimizeRouteResponse(
            route=result["route"],
            alternatives=[]  # Can be extended
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reroute", response_model=RerouteResponse)
def trigger_reroute(
    request: RerouteRequest,
    db: Session = Depends(get_db)
):
    """Trigger dynamic rerouting for a shipment."""
    try:
        result = RouteService.reroute_shipment(
            db,
            request.shipment_id,
            request.reason,
            request.avoid_regions
        )

        if not result:
            raise HTTPException(
                status_code=400,
                detail="Could not reroute shipment"
            )

        return RerouteResponse(
            shipment_id=result["shipment_id"],
            old_route=result.get("old_route"),
            new_route=result["new_route"],
            savings=result.get("savings")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{route_id}")
def get_route(route_id: str, db: Session = Depends(get_db)):
    """Get route details by ID."""
    route = RouteService.get_route(db, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route
