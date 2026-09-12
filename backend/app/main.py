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

import threading
from sqlalchemy import inspect, text

logger = logging.getLogger("jaldrishti")

_db_initialized = False
_init_lock = threading.Lock()

def _migrate_schema_columns():
    """Ensures optional prototype columns exist across tables in both SQLite and PostgreSQL."""
    try:
        with engine.begin() as conn:
            inspector = inspect(conn)
            tables = set(inspector.get_table_names())
            
            column_migrations = [
                ("observations", "intervention_id", "ALTER TABLE observations ADD COLUMN intervention_id INTEGER"),
                ("predictions", "model_version", "ALTER TABLE predictions ADD COLUMN model_version VARCHAR(50) DEFAULT '1.0.0'"),
                ("predictions", "status", "ALTER TABLE predictions ADD COLUMN status VARCHAR(50) DEFAULT 'PROTOTYPE_CALIBRATED'"),
                ("predictions", "feature_importances", "ALTER TABLE predictions ADD COLUMN feature_importances JSON DEFAULT '{}'"),
                ("risk_assessments", "contributing_factors", "ALTER TABLE risk_assessments ADD COLUMN contributing_factors JSON DEFAULT '[]'"),
                ("risk_assessments", "model_version", "ALTER TABLE risk_assessments ADD COLUMN model_version VARCHAR(50) DEFAULT '1.0.0'"),
                ("recommendations", "category", "ALTER TABLE recommendations ADD COLUMN category VARCHAR(100) DEFAULT 'WATER_HARVESTING'"),
                ("field_photos", "provenance", "ALTER TABLE field_photos ADD COLUMN provenance VARCHAR(50) DEFAULT 'DEMO_DATA'"),
                ("interventions", "source_type", "ALTER TABLE interventions ADD COLUMN source_type VARCHAR(50) DEFAULT 'DEMO / SEEDED DATA'"),
            ]
            
            for table_name, col_name, ddl_sql in column_migrations:
                if table_name in tables:
                    try:
                        existing_cols = {c["name"] for c in inspector.get_columns(table_name)}
                        if col_name not in existing_cols:
                            conn.execute(text(ddl_sql))
                            logger.info(f"Added column '{col_name}' to table '{table_name}'.")
                    except Exception as ddl_err:
                        logger.warning(f"Could not verify/add column '{col_name}' on table '{table_name}': {ddl_err}")
    except Exception as e:
        logger.warning(f"Database column verification note: {e}")

def init_db(force: bool = False):
    """
    Initializes database tables, runs safe DDL column additions, and executes seeding stages.
    Thread-safe and guarded against duplicate redundant runs.
    Each seeding stage runs in an isolated session so failure in one stage cannot break others.
    """
    global _db_initialized
    with _init_lock:
        if _db_initialized and not force:
            logger.debug("Database initialization already completed; skipping redundant run.")
            return

        # 1. Create all metadata tables
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            logger.error(f"Error creating database tables: {e}", exc_info=True)

        # 2. Safely apply column additions
        _migrate_schema_columns()

        # 3. Resilient individual seeding stages
        seed_stages = [
            ("Base Database & Layers", seed_database),
            ("Indicators & Yearly Values", seed_indicators_and_values),
            ("Interventions & Observations", seed_interventions),
            ("Dataset Catalog", seed_dataset_catalog),
            ("Institutional Demo Users", seed_users),
        ]

        for stage_name, stage_fn in seed_stages:
            db = SessionLocal()
            try:
                stage_fn(db)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Non-fatal error in seed stage '{stage_name}': {e}", exc_info=True)
            finally:
                db.close()

        _db_initialized = True

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
