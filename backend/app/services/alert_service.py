import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.domain import Watershed, Alert
from app.schemas.schemas import AlertItem, AlertCreate

class AlertService:
    @staticmethod
    def get_alerts_for_watershed(
        db: Session,
        watershed_id: int,
        severity: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[AlertItem]:
        """Backward-compatible method: fetches alerts for a given watershed."""
        return AlertService.list_alerts(
            db=db,
            watershed_id=watershed_id,
            severity=severity,
            status=status
        )

    @staticmethod
    def list_alerts(
        db: Session,
        watershed_id: Optional[int] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AlertItem]:
        """Lists active and historical environmental alerts with filtering."""
        query = db.query(Alert)
        if watershed_id:
            query = query.filter(Alert.watershed_id == watershed_id)
        if severity:
            query = query.filter(Alert.severity == severity.upper())
        if status:
            query = query.filter(Alert.status == status.upper())
            
        alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()
        return [AlertItem.model_validate(a) for a in alerts]

    @staticmethod
    def get_alert_by_id(db: Session, alert_id: int) -> Optional[AlertItem]:
        """Retrieves a single alert record."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        return AlertItem.model_validate(alert)

    @staticmethod
    def create_alert(db: Session, alert_in: AlertCreate) -> AlertItem:
        """Triggers and logs a new watershed alert."""
        ws = db.query(Watershed).filter(Watershed.id == alert_in.watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed ID {alert_in.watershed_id} does not exist.")

        alert = Alert(
            watershed_id=alert_in.watershed_id,
            alert_type=alert_in.alert_type,
            severity=alert_in.severity.upper(),
            trigger_reason=alert_in.trigger_reason,
            supporting_indicator=alert_in.supporting_indicator,
            status="ACTIVE",
            created_at=datetime.datetime.utcnow()
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return AlertItem.model_validate(alert)

    @staticmethod
    def update_alert_status(db: Session, alert_id: int, new_status: str) -> Optional[AlertItem]:
        """Acknowledges or resolves an existing environmental alert."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        alert.status = new_status.upper()
        db.commit()
        db.refresh(alert)
        return AlertItem.model_validate(alert)
