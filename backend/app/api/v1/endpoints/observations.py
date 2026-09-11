from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import ObservationResponse, ObservationCreate
from app.services.intervention_service import InterventionService

router = APIRouter()

@router.get("/observations", response_model=List[ObservationResponse], tags=["Observations"])
def list_observations(
    watershed_id: Optional[int] = Query(None, description="Filter by Watershed ID"),
    field_photo_id: Optional[int] = Query(None, description="Filter by linked photo ID"),
    intervention_id: Optional[int] = Query(None, description="Filter by linked intervention ID"),
    condition_rating: Optional[str] = Query(None, description="Condition: EXCELLENT, GOOD, MODERATE, CRITICAL"),
    limit: int = Query(100, ge=1, le=500, description="Max records"),
    offset: int = Query(0, ge=0, description="Offset"),
    db: Session = Depends(get_db)
):
    """Lists field observations recorded during ground verifications or social audits."""
    return InterventionService.list_observations(
        db,
        watershed_id=watershed_id,
        field_photo_id=field_photo_id,
        intervention_id=intervention_id,
        condition_rating=condition_rating,
        limit=limit,
        offset=offset
    )

@router.get("/observations/{id}", response_model=ObservationResponse, tags=["Observations"])
def get_observation(
    id: int = Path(..., ge=1, description="Observation ID"),
    db: Session = Depends(get_db)
):
    """Retrieves a single field observation record by ID."""
    obs = InterventionService.get_observation_by_id(db, id)
    if not obs:
        raise HTTPException(status_code=404, detail=f"Observation with ID {id} not found.")
    return obs

@router.post("/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED, tags=["Observations"])
def create_observation(
    obs_in: ObservationCreate,
    db: Session = Depends(get_db)
):
    """Records a new field verification observation with condition rating and recommended actions."""
    try:
        return InterventionService.create_observation(db, obs_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
