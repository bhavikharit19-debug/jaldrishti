from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import RiskAssessmentResponse
from app.services.risk_service import RiskService

router = APIRouter()

@router.get("/risks", response_model=RiskAssessmentResponse, tags=["Risks"])
def get_risk_assessment(
    watershed_id: int = Query(..., description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """Retrieves synthesized multi-criteria risk matrix and spatial hotspots (Frontend compatibility)."""
    try:
        return RiskService.get_risk_assessment_for_watershed(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/watersheds/{watershed_id}/risks", response_model=RiskAssessmentResponse, tags=["Risks"])
def get_watershed_risks(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """RESTful endpoint retrieving synthesized multi-hazard risk assessment and scientific evidence."""
    try:
        return RiskService.get_risk_assessment_for_watershed(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
