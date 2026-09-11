# JalDrishti AI — Scalable Geospatial & Watershed Decision Platform

> **JalDrishti AI** is a production-oriented, scalable full-stack web platform for watershed monitoring, geospatial analysis, change detection, predictive intelligence, risk assessment, and intervention decision support.

---

## 🌊 Core Philosophy & Decision Flow

```
USER SELECTS WATERSHED / AREA
→ Identify Geographic Boundary & Spatial Extent
→ Ingest Satellite, Telemetry & Field Photography
→ Compute Transparent Health Score & Biophysical Indicators
→ Execute Multi-Temporal Change Detection (2018–2024)
→ Generate Predictive Outlooks & Confidence Bounds
→ Synthesize Multi-Hazard Risk Assessment
→ Prioritize Recommendations & Decision-Support Interventions
→ Monitor Interventions & Observed Changes
→ Export Official Comprehensive Diagnostic Reports
```

---

## 🚀 Key Architectural Features

1. **Watershed-Agnostic Core**:
   - Seeded with 3 realistic catchments with authentic coordinates and boundaries:
     - **Hiware Bazar Watershed** (Ahmednagar, Maharashtra — ~976 ha)
     - **Ralegan Siddhi Watershed** (Ahmednagar, Maharashtra — ~1,250 ha)
     - **Arvari River Catchment** (Alwar, Rajasthan — ~4,500 ha)
   - Readily extensible to any national catchment via GeoJSON/Shapefile imports.

2. **Interactive MapLibre GL JS Cartography**:
   - Seamless vector boundary rendering and auto-zoom bounds (`fitBounds`).
   - Dynamic basemap toggle: Vector Base vs High-Resolution Satellite Tiles.
   - Vector overlays: Stream Drainage Networks (Order 1–3), Surface Water Bodies, LULC Classification, Proposed/Existing Interventions.
   - Geo-tagged field photo markers with interactive observation cards.

3. **Transparent Scientific Analytics**:
   - **Health Score Service**: Multi-criteria weighted index (Vegetation: 25%, Hydrology: 40%, Soil Condition: 15%, Structure Coverage: 10%) with explicit formula breakdown.
   - **Change Detection**: Dynamic comparison from 2018 to 2024 with delta percentages and multi-year time-series charts.
   - **ML Prediction Engine**: Ridge regression forecasting 12–24 month water stress index with 95% confidence intervals.
   - **Risk Assessment**: Multi-hazard risk categorizations (Water Stress, Degradation, Soil Erosion) with scientific evidence explanations.
   - **Decision-Support Recommendations**: Ground-level DPR recommendations with statutory disclaimer notices.

4. **Multi-Stage Production Readiness**:
   - **Backend**: Python 3.11+ / 3.14, FastAPI, SQLAlchemy 2.0, Pydantic v2, Scikit-Learn.
   - **Database**: PostgreSQL 15 + PostGIS 3.3 (with automatic local SQLite GeoJSON fallback).
   - **Frontend**: Next.js 15, TypeScript, Tailwind CSS, MapLibre GL JS, Recharts, Lucide React.
   - **Deployment**: Full Docker Compose (`postgis/postgis`, `redis`, backend, frontend).

---

## 🛠️ Quick Start Guide

### Option 1: Docker Compose (Full Production Stack)

```bash
cd infrastructure
docker-compose up -d --build
```
- Frontend Dashboard: `http://localhost:3000`
- FastAPI Documentation: `http://localhost:8000/docs`
- PostGIS Database: `localhost:5432`

---

### Option 2: Local Development

#### 1. Start the Backend:
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```
*The database and multi-watershed seed data will initialize automatically on launch.*

#### 2. Start the Frontend:
```bash
cd frontend
npm install
npm run dev
```
*Access the GIS dashboard at `http://localhost:3000`.*

#### 3. Run Backend Automated Tests:
```bash
cd backend
python -m pytest tests/test_api.py -v
```

---

## 📂 Project Structure

```
jaldrishti-ai/
├── frontend/               # Next.js 15, MapLibre GL JS, Tailwind, TypeScript
├── backend/                # FastAPI, SQLAlchemy 2.0, Scikit-learn
├── infrastructure/         # Docker Compose, PostGIS, Redis configs
└── docs/                   # System Architecture & Ingestion Guide
```
