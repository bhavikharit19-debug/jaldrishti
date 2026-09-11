# JalDrishti AI — Data Ingestion & Government Integration Guide

## 1. Data Provenance & Distinctions
JalDrishti AI strictly maintains data provenance across all ingestion layers:
- **`DEMO DATA`**: Pre-calibrated spatial boundaries and historical series used for initial validation and testing.
- **`OFFICIAL DATA`**: Official government feeds (e.g. ISRO Bhuvan, PMKSY, Central Ground Water Board).
- **`FIELD UPLOADED DATA`**: Geo-tagged photographs and observational telemetry recorded by district or field officers.

---

## 2. Integrating Official Government Datasets

### A. ISRO Bhuvan Watershed API Adapter
To connect ISRO Bhuvan WMS/WFS vector feeds:
1. Register a data source record via `DataSource(code="ISRO-BHUVAN", source_type="OFFICIAL")`.
2. Configure the layer endpoint in `backend/app/services/gis_service.py` with the official WFS/GeoJSON endpoint URL.
3. GeoJSON geometries will automatically render onto the MapLibre GL layer stack.

### B. Ingesting Shapefiles / GeoJSON Boundaries
Use the backend ingestion service to import watershed boundaries from standard Shapefiles or GeoJSON:
```python
from app.services.ingestion_service import import_watershed_geojson

# Ingest boundary geometry with automatic bounding box and centroid computation
import_watershed_geojson(
    filepath="path/to/official_boundary.geojson",
    state_code="MH",
    district_name="Ahmednagar",
    watershed_name="New Model Catchment"
)
```

---

## 3. Geo-Tagged Field Photograph Ingestion
Field officers can submit geo-tagged photographs via the mobile-friendly web interface or POST to `/api/v1/photos`:
```bash
curl -X POST "http://localhost:8000/api/v1/photos" \
  -H "Content-Type: application/json" \
  -d '{
    "watershed_id": 1,
    "latitude": 19.0465,
    "longitude": 74.6062,
    "photo_url": "https://storage.gov.in/photos/hb_checkdam_01.jpg",
    "category": "CHECK_DAM",
    "description": "Weir crest intact with post-monsoon storage.",
    "exif_metadata": {"camera": "Survey Device", "altitude_m": 612.4}
  }'
```
Coordinates are validated against the watershed bounding box to ensure spatial consistency.
