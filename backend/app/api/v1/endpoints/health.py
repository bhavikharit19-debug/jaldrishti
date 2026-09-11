import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.schemas.schemas import HealthCheckResponse

router = APIRouter()

@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return HealthCheckResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        version="1.0.0",
        timestamp=datetime.datetime.utcnow()
    )
