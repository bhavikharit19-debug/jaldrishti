from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Indicator, IndicatorValue, Watershed
from app.schemas.schemas import (
    HealthScoreResponse, ChangeDetectionResponse,
    IndicatorItem, WatershedIndicatorValue
)
from app.services.health_score_service import HealthScoreService
from app.services.change_service import ChangeDetectionService

router = APIRouter()

# ----------------- Biophysical Indicator Catalog -----------------

@router.get("/indicators", response_model=List[IndicatorItem], tags=["Analytics"])
def list_indicators(db: Session = Depends(get_db)):
    """Lists all registered biophysical, hydrological, and land-condition indicators with formula weights."""
    indicators = db.query(Indicator).order_by(Indicator.id).all()
    return [IndicatorItem.model_validate(i) for i in indicators]

@router.get("/watersheds/{watershed_id}/indicators", response_model=List[WatershedIndicatorValue], tags=["Analytics"])
def get_watershed_indicators(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    year: Optional[int] = Query(None, description="Optional year filter"),
    db: Session = Depends(get_db)
):
    """Retrieves recorded historical indicator values for a specific watershed."""
    ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail=f"Watershed with ID {watershed_id} not found.")

    query = db.query(IndicatorValue).filter(IndicatorValue.watershed_id == watershed_id)
    if year:
        query = query.filter(IndicatorValue.recorded_year == year)
        
    values = query.order_by(IndicatorValue.recorded_year.desc(), IndicatorValue.indicator_id.asc()).all()
    result = []
    for v in values:
        result.append(WatershedIndicatorValue(
            id=v.id,
            indicator_code=v.indicator.code if v.indicator else "UNKNOWN",
            indicator_name=v.indicator.name if v.indicator else "Unknown",
            category=v.indicator.category if v.indicator else "GENERAL",
            unit=v.indicator.unit if v.indicator else None,
            recorded_year=v.recorded_year,
            recorded_month=v.recorded_month,
            value=v.value,
            normalized_score=v.normalized_score,
            source_type=v.source_type
        ))
    return result

# ----------------- Health Score Endpoints -----------------

@router.get("/health-score", response_model=HealthScoreResponse, tags=["Analytics"])
def get_watershed_health_score(
    watershed_id: int = Query(..., description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """Calculates and returns the multi-criteria transparent Watershed Health Score (Frontend compatibility)."""
    try:
        return HealthScoreService.calculate_watershed_health(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/watersheds/{watershed_id}/health-score", response_model=HealthScoreResponse, tags=["Analytics"])
def get_watershed_health_score_restful(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """RESTful endpoint calculating transparent Watershed Health Score and category rating."""
    try:
        return HealthScoreService.calculate_watershed_health(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ----------------- Change Detection Endpoints -----------------

@router.get("/changes", response_model=ChangeDetectionResponse, tags=["Analytics"])
def get_change_detection(
    watershed_id: int = Query(..., description="Watershed ID"),
    from_year: int = Query(2018, description="Baseline year"),
    to_year: int = Query(2024, description="Target comparison year"),
    db: Session = Depends(get_db)
):
    """Computes multi-temporal delta analysis and historical trajectory (Frontend compatibility)."""
    try:
        return ChangeDetectionService.compare_periods(db, watershed_id, from_year, to_year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/watersheds/{watershed_id}/changes", response_model=ChangeDetectionResponse, tags=["Analytics"])
def get_watershed_changes_restful(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    from_year: int = Query(2018, description="Baseline year"),
    to_year: int = Query(2024, description="Target comparison year"),
    db: Session = Depends(get_db)
):
    """RESTful endpoint computing multi-temporal delta analysis and indicator trajectory."""
    try:
        return ChangeDetectionService.compare_periods(db, watershed_id, from_year, to_year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
