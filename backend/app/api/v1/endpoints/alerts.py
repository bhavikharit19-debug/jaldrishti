from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import AlertItem, AlertCreate
from app.services.alert_service import AlertService

router = APIRouter()

@router.get("/alerts", response_model=List[AlertItem], tags=["Alerts"])
def list_alerts(
    watershed_id: Optional[int] = Query(None, description="Optional Watershed ID filter"),
    severity: Optional[str] = Query(None, description="Severity filter: CRITICAL, HIGH, MEDIUM, LOW"),
    status: Optional[str] = Query(None, description="Status filter: ACTIVE, ACKNOWLEDGED, RESOLVED"),
    limit: int = Query(100, ge=1, le=500, description="Max records"),
    offset: int = Query(0, ge=0, description="Offset"),
    db: Session = Depends(get_db)
):
    """Retrieves active and historical environmental alerts with filtering and pagination."""
    return AlertService.list_alerts(
        db,
        watershed_id=watershed_id,
        severity=severity,
        status=status,
        limit=limit,
        offset=offset
    )

@router.get("/watersheds/{watershed_id}/alerts", response_model=List[AlertItem], tags=["Alerts"])
def get_watershed_alerts(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    severity: Optional[str] = Query(None, description="Severity filter: CRITICAL, HIGH, MEDIUM, LOW"),
    status: Optional[str] = Query(None, description="Status filter: ACTIVE, ACKNOWLEDGED, RESOLVED"),
    db: Session = Depends(get_db)
):
    """RESTful endpoint retrieving all alerts configured for a specific watershed catchment."""
    return AlertService.list_alerts(
        db,
        watershed_id=watershed_id,
        severity=severity,
        status=status
    )

@router.post("/alerts", response_model=AlertItem, status_code=status.HTTP_201_CREATED, tags=["Alerts"])
def create_alert(
    alert_in: AlertCreate,
    db: Session = Depends(get_db)
):
    """Triggers and logs a new biophysical threshold or monitoring alert."""
    try:
        return AlertService.create_alert(db, alert_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/alerts/{alert_id}/status", response_model=AlertItem, tags=["Alerts"])
def update_alert_status(
    alert_id: int = Path(..., ge=1, description="Alert ID"),
    status: str = Query(..., description="New status: ACTIVE, ACKNOWLEDGED, RESOLVED"),
    db: Session = Depends(get_db)
):
    """Updates the acknowledgement or resolution status of an alert (Officer action)."""
    updated = AlertService.update_alert_status(db, alert_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found.")
    return updated
