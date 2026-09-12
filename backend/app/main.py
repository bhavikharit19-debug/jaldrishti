import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1.router import api_router
from data.seed_data import (
    seed_database, seed_indicators_and_values,
    seed_interventions, seed_dataset_catalog, seed_users
)

from sqlalchemy import inspect, text

logger = logging.getLogger("jaldrishti")

def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            inspector = inspect(conn)
            tables = inspector.get_table_names()
            if "observations" in tables:
                cols = [c["name"] for c in inspector.get_columns("observations")]
                if "intervention_id" not in cols:
                    conn.execute(text("ALTER TABLE observations ADD COLUMN intervention_id INTEGER"))
                    conn.commit()
            if "predictions" in tables:
                cols = [c["name"] for c in inspector.get_columns("predictions")]
                if "model_version" not in cols:
                    conn.execute(text("ALTER TABLE predictions ADD COLUMN model_version VARCHAR(50) DEFAULT '1.0.0'"))
                if "status" not in cols:
                    conn.execute(text("ALTER TABLE predictions ADD COLUMN status VARCHAR(50) DEFAULT 'PROTOTYPE_CALIBRATED'"))
                if "feature_importances" not in cols:
                    conn.execute(text("ALTER TABLE predictions ADD COLUMN feature_importances JSON DEFAULT '{}'"))
                conn.commit()
            if "risk_assessments" in tables:
                cols = [c["name"] for c in inspector.get_columns("risk_assessments")]
                if "contributing_factors" not in cols:
                    conn.execute(text("ALTER TABLE risk_assessments ADD COLUMN contributing_factors JSON DEFAULT '[]'"))
                if "model_version" not in cols:
                    conn.execute(text("ALTER TABLE risk_assessments ADD COLUMN model_version VARCHAR(50) DEFAULT '1.0.0'"))
                conn.commit()
            if "recommendations" in tables:
                cols = [c["name"] for c in inspector.get_columns("recommendations")]
                if "category" not in cols:
                    conn.execute(text("ALTER TABLE recommendations ADD COLUMN category VARCHAR(100) DEFAULT 'WATER_HARVESTING'"))
                conn.commit()
            if "field_photos" in tables:
                cols = [c["name"] for c in inspector.get_columns("field_photos")]
                if "provenance" not in cols:
                    conn.execute(text("ALTER TABLE field_photos ADD COLUMN provenance VARCHAR(50) DEFAULT 'DEMO_DATA'"))
                conn.commit()
            if "interventions" in tables:
                cols = [c["name"] for c in inspector.get_columns("interventions")]
                if "source_type" not in cols:
                    conn.execute(text("ALTER TABLE interventions ADD COLUMN source_type VARCHAR(50) DEFAULT 'DEMO / SEEDED DATA'"))
                conn.commit()
    except Exception as e:
        logger.warning(f"Database column verification note: {e}")
    db = SessionLocal()
    try:
        seed_database(db)
        seed_indicators_and_values(db)
        seed_interventions(db)
        seed_dataset_catalog(db)
        seed_users(db)
    finally:
        db.close()

# Ensure tables and baseline seed exist immediately
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

tags_metadata = [
    {"name": "Authentication", "description": "Government officer login, JWT issuance, profile resolution, and access requests."},
    {"name": "User Management & Audit", "description": "Administrative user provisioning, access request approval/rejection, and compliance audit logs."},
    {"name": "Geography", "description": "National administrative hierarchy (States, Districts) and spatial jurisdiction."},
    {"name": "Watersheds", "description": "Micro-watershed boundaries, spatial locate, and multi-criteria catchment filtering."},
    {"name": "GIS Layers", "description": "8-layer vector cartography: Boundary, LULC, Drainage, Water Bodies, NDVI, Elevation, Interventions, Field Photos."},
    {"name": "Photos", "description": "Geo-tagged ground-truth field verification photographs with EXIF metadata."},
    {"name": "Observations", "description": "Field inspections, condition ratings, and participatory social audit records."},
    {"name": "Interventions", "description": "Structural soil and water conservation catalog (Check dams, percolation tanks) and before/after monitoring."},
    {"name": "Analytics", "description": "Transparent biophysical indicator calculation, health score, and multi-temporal change detection (2018–2024)."},
    {"name": "Predictions", "description": "Machine learning trend projections (12–24 month) with uncertainty confidence bands."},
    {"name": "Risks", "description": "Synthesized multi-hazard risk engine combining soil erosion, vegetative loss, and water stress."},
    {"name": "Recommendations", "description": "Prioritized DPR intervention suggestions and engineering estimates."},
    {"name": "Alerts", "description": "Dynamic environmental alerts, rapid decline detection, and officer status acknowledgment."},
    {"name": "Reports", "description": "Official diagnostic catchment assessment summaries and printable reports."},
    {"name": "Data Integration", "description": "Ingestion pipelines for GeoJSON, CSV, Sentinel-2/Bhuvan satellite adapters, and dataset catalog."},
    {"name": "Health", "description": "System health, database connection, and deployment diagnostics."},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="JalDrishti AI: Scalable Geospatial & Watershed Decision Support System (SIH 26015)",
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

# Exception handlers for safe, standardized error formatting
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Translates domain value errors into structured 400 Bad Request responses."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "error_type": "VALIDATION_ERROR"}
    )

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files mount for uploaded field verification photographs
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": "JalDrishti AI",
        "status": "Operational",
        "api_docs": "/docs",
        "api_v1": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
