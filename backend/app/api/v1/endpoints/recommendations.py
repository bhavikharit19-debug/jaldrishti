from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import RecommendationResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()

@router.get("/recommendations", response_model=RecommendationResponse, tags=["Recommendations"])
def get_recommendations(
    watershed_id: int = Query(..., description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """Retrieves prioritized decision-support watershed intervention recommendations (Frontend compatibility)."""
    try:
        return RecommendationService.get_recommendations_for_watershed(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/watersheds/{watershed_id}/recommendations", response_model=RecommendationResponse, tags=["Recommendations"])
def get_watershed_recommendations(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """RESTful endpoint retrieving prioritized engineering DPR intervention recommendations."""
    try:
        return RecommendationService.get_recommendations_for_watershed(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
