from fastapi import APIRouter
from app.api.v1.endpoints import (
    health, watersheds, gis_layers, field_photos,
    observations, interventions, analytics, predictions,
    risks, recommendations, alerts, reports, data_integration,
    auth, admin_users
)

api_router = APIRouter()

# Health & Diagnostics
api_router.include_router(health.router, tags=["Health"])

# Geographic Hierarchy & Administrative Units
# (tags configured on endpoint level: Geography & Watersheds)
api_router.include_router(watersheds.router)

# Geospatial Layers & Thematic Map Statistics
api_router.include_router(gis_layers.router)

# Geo-Tagged Verification Photos & EXIF Metadata
api_router.include_router(field_photos.router)

# Ground-Truth Field Inspection Observations
api_router.include_router(observations.router)

# Interventions & Structural Monitoring
api_router.include_router(interventions.router)

# Biophysical Analytics & Health Score
api_router.include_router(analytics.router)

# Machine Learning Predictive Forecasting
api_router.include_router(predictions.router)

# Multi-Hazard Risk Assessments
api_router.include_router(risks.router)

# Decision-Support Intervention Recommendations
api_router.include_router(recommendations.router)

# Environmental Alerts & Monitoring
api_router.include_router(alerts.router)

# Comprehensive Diagnostic Reports
api_router.include_router(reports.router)

# Real Data Ingestion & Dataset Catalog
api_router.include_router(data_integration.router, prefix="/data", tags=["Data Integration"])

# Officer Authentication & Access Requests
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Administrative User Management & Audit
api_router.include_router(admin_users.router, prefix="/admin", tags=["User Management & Audit"])


