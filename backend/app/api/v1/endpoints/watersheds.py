from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import (
    WatershedListItem, WatershedDetail, StateResponse, DistrictResponse,
    StateListItem, DistrictListItem, WatershedLocateResult
)
from app.services.watershed_service import WatershedService

router = APIRouter()

# ----------------- Geographic Hierarchy Endpoints -----------------

@router.get("/states-hierarchy", response_model=List[StateResponse], tags=["Geography"])
def get_states_hierarchy(db: Session = Depends(get_db)):
    """Returns the State -> District hierarchical tree for cascading dropdowns (Frontend compatibility)."""
    return WatershedService.get_states_hierarchy(db)

@router.get("/states", response_model=List[StateListItem], tags=["Geography"])
def list_states(
    search: Optional[str] = Query(None, description="Search state name or code"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Records offset"),
    db: Session = Depends(get_db)
):
    """Lists all administrative states with district and watershed aggregate counts."""
    return WatershedService.list_states(db, search=search, limit=limit, offset=offset)

@router.get("/states/{state_id}", response_model=StateResponse, tags=["Geography"])
def get_state(
    state_id: int = Path(..., ge=1, description="State ID"),
    db: Session = Depends(get_db)
):
    """Retrieves a single state with all its child districts."""
    state = WatershedService.get_state_by_id(db, state_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"State with ID {state_id} not found.")
    return state

@router.get("/states/{state_id}/districts", response_model=List[DistrictResponse], tags=["Geography"])
def list_state_districts(
    state_id: int = Path(..., ge=1, description="State ID"),
    db: Session = Depends(get_db)
):
    """Lists all districts belonging to the specified state."""
    state = WatershedService.get_state_by_id(db, state_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"State with ID {state_id} not found.")
    return WatershedService.list_districts_for_state(db, state_id)

@router.get("/districts", response_model=List[DistrictListItem], tags=["Geography"])
def list_districts(
    state_id: Optional[int] = Query(None, description="Filter by parent State ID"),
    search: Optional[str] = Query(None, description="Search district name or code"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Records offset"),
    db: Session = Depends(get_db)
):
    """Lists districts with optional state filter and text search."""
    return WatershedService.list_districts(db, state_id=state_id, search=search, limit=limit, offset=offset)

@router.get("/districts/{district_id}", response_model=DistrictListItem, tags=["Geography"])
def get_district(
    district_id: int = Path(..., ge=1, description="District ID"),
    db: Session = Depends(get_db)
):
    """Retrieves single district detail and watershed count."""
    dist = WatershedService.get_district_by_id(db, district_id)
    if not dist:
        raise HTTPException(status_code=404, detail=f"District with ID {district_id} not found.")
    return dist

@router.get("/districts/{district_id}/watersheds", response_model=List[WatershedListItem], tags=["Watersheds"])
def list_district_watersheds(
    district_id: int = Path(..., ge=1, description="District ID"),
    db: Session = Depends(get_db)
):
    """Lists all watersheds belonging to a specific district."""
    dist = WatershedService.get_district_by_id(db, district_id)
    if not dist:
        raise HTTPException(status_code=404, detail=f"District with ID {district_id} not found.")
    return WatershedService.list_watersheds_for_district(db, district_id)

# ----------------- Spatial Point Lookup -----------------

@router.get("/watersheds/spatial/locate", response_model=WatershedLocateResult, tags=["Watersheds"])
def locate_watershed(
    lat: float = Query(..., ge=-90.0, le=90.0, description="GPS Latitude in decimal degrees"),
    lng: float = Query(..., ge=-180.0, le=180.0, description="GPS Longitude in decimal degrees"),
    db: Session = Depends(get_db)
):
    """
    Spatial containment query: locates which watershed polygon contains the given coordinates.
    If outside, identifies the closest watershed by Haversine centroid distance.
    """
    try:
        res = WatershedService.locate_watershed_by_coordinates(db, latitude=lat, longitude=lng)
        if not res:
            raise HTTPException(status_code=404, detail="No watersheds available in the database.")
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----------------- Watershed CRUD & Query Endpoints -----------------

@router.get("/watersheds", response_model=List[WatershedListItem], tags=["Watersheds"])
def list_watersheds(
    state_id: Optional[int] = Query(None, description="Filter by State ID"),
    district_id: Optional[int] = Query(None, description="Filter by District ID"),
    risk_level: Optional[str] = Query(None, description="Filter by risk rating: LOW, MEDIUM, HIGH, CRITICAL"),
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, UNDER_TREATMENT, MONITORED"),
    search: Optional[str] = Query(None, description="Search watershed name or code"),
    min_lng: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Spatial Bounding Box: Min Longitude"),
    min_lat: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Spatial Bounding Box: Min Latitude"),
    max_lng: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Spatial Bounding Box: Max Longitude"),
    max_lat: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Spatial Bounding Box: Max Latitude"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    Lists all watersheds with multi-criteria administrative, risk rating, text search,
    and spatial bounding box filtering.
    """
    return WatershedService.list_watersheds(
        db,
        state_id=state_id,
        district_id=district_id,
        risk_level=risk_level,
        status=status,
        search=search,
        min_lng=min_lng,
        min_lat=min_lat,
        max_lng=max_lng,
        max_lat=max_lat,
        limit=limit,
        offset=offset
    )

@router.get("/watersheds/{watershed_id}", response_model=WatershedDetail, tags=["Watersheds"])
def get_watershed(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """Retrieves full details of a specific watershed including boundary geometry, agro-climatic zone, and health rating."""
    ws = WatershedService.get_watershed_by_id(db, watershed_id)
    if not ws:
        raise HTTPException(status_code=404, detail=f"Watershed with ID {watershed_id} not found.")
    return ws

@router.get("/watersheds/{watershed_id}/boundary", response_model=Dict[str, Any], tags=["Watersheds"])
def get_watershed_boundary(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """Retrieves the clean GeoJSON Feature representation of the watershed catchment boundary."""
    boundary = WatershedService.get_watershed_boundary(db, watershed_id)
    if not boundary:
        raise HTTPException(status_code=404, detail=f"Boundary for watershed {watershed_id} not found.")
    return boundary
