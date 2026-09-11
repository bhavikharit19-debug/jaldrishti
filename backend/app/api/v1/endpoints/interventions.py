from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import (
    InterventionItem, InterventionCreate, InterventionUpdate,
    ObservationResponse, ObservationCreate
)
from app.services.intervention_service import InterventionService

router = APIRouter()

@router.get("/interventions", response_model=List[InterventionItem], tags=["Interventions"])
def list_interventions(
    watershed_id: Optional[int] = Query(None, description="Watershed ID filter"),
    status: Optional[str] = Query(None, description="Status filter: PROPOSED, SANCTIONED, WORK_IN_PROGRESS, COMPLETED"),
    intervention_type: Optional[str] = Query(None, description="Intervention type filter (e.g. Check Dam, Percolation Tank)"),
    limit: int = Query(100, ge=1, le=500, description="Max records"),
    offset: int = Query(0, ge=0, description="Offset"),
    db: Session = Depends(get_db)
):
    """Lists catalogued watershed interventions, capacities, and before/after impact metrics."""
    return InterventionService.list_interventions(
        db,
        watershed_id=watershed_id,
        status=status,
        intervention_type=intervention_type,
        limit=limit,
        offset=offset
    )

@router.get("/interventions/{id}", response_model=InterventionItem, tags=["Interventions"])
def get_intervention(
    id: int = Path(..., ge=1, description="Intervention ID"),
    db: Session = Depends(get_db)
):
    """Retrieves full details of an individual intervention including before/after metrics."""
    intervention = InterventionService.get_intervention_by_id(db, id)
    if not intervention:
        raise HTTPException(status_code=404, detail=f"Intervention with ID {id} not found.")
    return intervention

@router.post("/interventions", response_model=InterventionItem, status_code=status.HTTP_201_CREATED, tags=["Interventions"])
def create_intervention(
    intervention_in: InterventionCreate,
    db: Session = Depends(get_db)
):
    """Creates a new intervention record with geographic coordinate validation."""
    try:
        return InterventionService.create_intervention(db, intervention_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/interventions/{id}", response_model=InterventionItem, tags=["Interventions"])
def update_intervention(
    id: int = Path(..., ge=1, description="Intervention ID"),
    update_in: InterventionUpdate = ...,
    db: Session = Depends(get_db)
):
    """Updates implementation status, capacity, or observed impact for an intervention."""
    updated = InterventionService.update_intervention(db, id, update_in)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Intervention with ID {id} not found.")
    return updated

@router.get("/interventions/{id}/observations", response_model=List[ObservationResponse], tags=["Interventions"])
def list_intervention_observations(
    id: int = Path(..., ge=1, description="Intervention ID"),
    db: Session = Depends(get_db)
):
    """Retrieves all qualitative and quantitative field observations logged for this intervention."""
    intervention = InterventionService.get_intervention_by_id(db, id)
    if not intervention:
        raise HTTPException(status_code=404, detail=f"Intervention with ID {id} not found.")
    return InterventionService.list_observations_for_intervention(db, id)

@router.post("/interventions/{id}/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED, tags=["Interventions"])
def create_intervention_observation(
    id: int = Path(..., ge=1, description="Intervention ID"),
    obs_in: ObservationCreate = ...,
    db: Session = Depends(get_db)
):
    """Logs a new field inspection observation directly against this intervention."""
    intervention = InterventionService.get_intervention_by_id(db, id)
    if not intervention:
        raise HTTPException(status_code=404, detail=f"Intervention with ID {id} not found.")
    
    obs_in.intervention_id = id
    obs_in.watershed_id = intervention.watershed_id
    try:
        return InterventionService.create_observation(db, obs_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
