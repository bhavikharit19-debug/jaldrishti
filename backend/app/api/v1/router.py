from fastapi import APIRouter, Depends
from app.core.security import require_authenticated_user
from app.api.v1.endpoints import (
    health, watersheds, gis_layers, field_photos,
    observations, interventions, analytics, predictions,
    risks, recommendations, alerts, reports, data_integration,
    auth, admin_users
)

api_router = APIRouter()

# Health & Diagnostics (Public)
api_router.include_router(health.router, tags=["Health"])

# Geographic Hierarchy & Administrative Units (Protected: requires valid JWT)
api_router.include_router(watersheds.router, dependencies=[Depends(require_authenticated_user)])

# Geospatial Layers & Thematic Map Statistics (Protected: requires valid JWT)
api_router.include_router(gis_layers.router, dependencies=[Depends(require_authenticated_user)])

# Geo-Tagged Verification Photos & EXIF Metadata (Protected: requires valid JWT)
api_router.include_router(field_photos.router, dependencies=[Depends(require_authenticated_user)])

# Ground-Truth Field Inspection Observations (Protected: requires valid JWT)
api_router.include_router(observations.router, dependencies=[Depends(require_authenticated_user)])

# Interventions & Structural Monitoring (Protected: requires valid JWT)
api_router.include_router(interventions.router, dependencies=[Depends(require_authenticated_user)])

# Biophysical Analytics & Health Score (Protected: requires valid JWT)
api_router.include_router(analytics.router, dependencies=[Depends(require_authenticated_user)])

# Machine Learning Predictive Forecasting (Protected: requires valid JWT)
api_router.include_router(predictions.router, dependencies=[Depends(require_authenticated_user)])

# Multi-Hazard Risk Assessments (Protected: requires valid JWT)
api_router.include_router(risks.router, dependencies=[Depends(require_authenticated_user)])

# Decision-Support Intervention Recommendations (Protected: requires valid JWT)
api_router.include_router(recommendations.router, dependencies=[Depends(require_authenticated_user)])

# Environmental Alerts & Monitoring (Protected: requires valid JWT)
api_router.include_router(alerts.router, dependencies=[Depends(require_authenticated_user)])

# Comprehensive Diagnostic Reports (Protected: requires valid JWT)
api_router.include_router(reports.router, dependencies=[Depends(require_authenticated_user)])

# Real Data Ingestion & Dataset Catalog (Protected: requires valid JWT)
api_router.include_router(data_integration.router, prefix="/data", tags=["Data Integration"], dependencies=[Depends(require_authenticated_user)])

# Officer Authentication & Access Requests (Public login/register, protected /me)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Administrative User Management & Audit (Protected: requires ADMIN role)
api_router.include_router(admin_users.router, prefix="/admin", tags=["User Management & Audit"])


