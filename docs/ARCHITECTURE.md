# JalDrishti AI — Technical Architecture & Geospatial Foundation

## 1. System Philosophy & Workflow
JalDrishti AI is designed as a scalable, cloud-ready decision-support layer for national, state, and district watershed monitoring:

```
MONITOR → ANALYSE → DETECT CHANGE → PREDICT → ASSESS RISK → RECOMMEND → MONITOR IMPACT
```

Unlike static dashboards, the platform is **watershed-agnostic**; it models catchments through standardized GeoJSON boundaries, multi-criteria biophysical indicators, and spatial layers, allowing government agencies to ingest official records without rewriting the application.

---

## 2. Monorepo Organization

```
jaldrishti-ai/
├── frontend/               # Next.js 15, TypeScript, Tailwind CSS, MapLibre GL JS
│   ├── src/
│   │   ├── app/            # App router pages (dashboard & diagnostic reports)
│   │   ├── components/     # GIS map, layer controls, and modular decision panels
│   │   ├── services/       # Type-safe API client for backend v1 endpoints
│   │   └── types/          # Domain schemas and GeoJSON typings
│   └── package.json
├── backend/                # Python 3.11+, FastAPI, SQLAlchemy 2.0, Scikit-Learn
│   ├── app/
│   │   ├── api/v1/         # Versioned REST endpoints (watersheds, layers, ML)
│   │   ├── core/           # Configuration, security, database session
│   │   ├── models/         # SQLAlchemy 2.0 ORM data models
│   │   ├── schemas/        # Pydantic v2 validation models
│   │   └── services/       # Modular business logic (Health, GIS, ML, Risks, Recs)
│   ├── data/               # Calibrated baseline multi-watershed seed generator
│   └── tests/              # Pytest automated API verification suite
├── infrastructure/         # Docker Compose (PostGIS, Redis, Backend, Frontend)
└── docs/                   # Architecture, Ingestion Guide, API Reference
```

---

## 3. Database Layer & Geospatial Abstraction
- **Primary Production Engine**: PostgreSQL 15 + PostGIS 3.3. Spatial queries utilize R-tree spatial indexing (`GIST`), topological operators (`ST_Contains`, `ST_Intersects`), and binary formats.
- **Portable Local Fallback**: Automatically defaults to SQLite with JSON-based GeoJSON serialization and Shapely geometry computations when a PostGIS instance is not running locally.
- **Key Entities**:
  - `states` & `districts`: Administrative hierarchy.
  - `watersheds`: Core catchment entity (area, agro-climatic zone, river basin, health score).
  - `watershed_boundaries`: MultiPolygon/Polygon boundary GeoJSON, centroid, and bounding box.
  - `gis_layers`: Thematic vector/raster layers (Drainage streams, Water bodies, LULC, Interventions).
  - `field_photos`: Geo-tagged field records with EXIF coordinate extraction and verification workflow.
  - `indicator_values`: Multi-temporal time series (2018–2024) across NDVI, NDWI, SMI, and water spread.
  - `predictions`: Ridge regression and ensemble projections with 95% confidence intervals.
  - `risk_assessments`: Categorized hazard matrices (Water stress, Soil erosion, Vegetation decline).
  - `recommendations`: Decision-support engineering suggestions with mandatory DPR disclaimers.
  - `interventions`: Physical structure tracking with "Before vs Observed Change" telemetry.
  - `alerts`: Dynamic threshold evaluation and field verification warnings.

---

## 4. Frontend Geospatial Cartography
- **Map Engine**: MapLibre GL JS (`maplibre-gl`), open-source and free without proprietary API keys.
- **Dynamic Bounding Box Fit**: Calls `map.fitBounds(bbox)` when a watershed is selected.
- **Layer Switcher**: Toggle between Vector Base and High-Resolution Satellite Cartography, with individual layer toggles for drainage networks, water bodies, LULC zones, intervention pins, and field photo markers.
- **Interactive Photo Popups**: Custom HTML markers with photo previews, coordinates, category, and verification badges.
