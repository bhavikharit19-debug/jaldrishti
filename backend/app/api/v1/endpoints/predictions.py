from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter()

@router.get("/predictions", response_model=PredictionResponse, tags=["Predictions"])
def get_predictions(
    watershed_id: int = Query(..., description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """Retrieves ML predictive projections and uncertainty bounds (Frontend compatibility)."""
    try:
        return PredictionService.get_predictions_for_watershed(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/watersheds/{watershed_id}/predictions", response_model=PredictionResponse, tags=["Predictions"])
def get_watershed_predictions(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """RESTful endpoint retrieving ML trend forecasts, confidence bands, and feature importance."""
    try:
        return PredictionService.get_predictions_for_watershed(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
