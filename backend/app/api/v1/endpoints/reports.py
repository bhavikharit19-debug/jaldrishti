from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import WatershedReportResponse, ReportSummaryItem
from app.services.report_service import ReportService

router = APIRouter()

@router.get("/reports", response_model=List[ReportSummaryItem], tags=["Reports"])
def list_reports(
    limit: int = Query(100, ge=1, le=500, description="Max report summaries to return"),
    offset: int = Query(0, ge=0, description="Offset"),
    db: Session = Depends(get_db)
):
    """Lists executive diagnostic report summaries across all catalogued watersheds."""
    return ReportService.list_reports_summary(db, limit=limit, offset=offset)

@router.get("/reports/{watershed_id}", response_model=WatershedReportResponse, tags=["Reports"])
def get_watershed_report(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """Compiles a complete watershed assessment report with health indicators, interventions, and risks (Frontend compatibility)."""
    try:
        return ReportService.generate_watershed_report(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/watersheds/{watershed_id}/report", response_model=WatershedReportResponse, tags=["Reports"])
def get_watershed_report_restful(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """RESTful endpoint compiling comprehensive diagnostic report for official review."""
    try:
        return ReportService.generate_watershed_report(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
