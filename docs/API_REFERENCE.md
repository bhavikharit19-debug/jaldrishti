# JalDrishti AI — Version 1 API Specification

Base URL: `http://localhost:8000/api/v1`
Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 1. System Health
- **`GET /health`**
  - Verifies database and backend service connectivity.
  - Returns: `{ "status": "healthy", "database": "connected", "version": "1.0.0" }`

---

## 2. Watershed Catalog & Hierarchy
- **`GET /states-hierarchy`**
  - Returns cascading state and district tree for territory selection.
- **`GET /watersheds`**
  - Query parameters: `state_id`, `district_id`, `search`.
  - Returns a list of watersheds matching criteria.
- **`GET /watersheds/{id}`**
  - Returns full metadata and boundary GeoJSON with bounding box.

---

## 3. Geospatial Layers
- **`GET /layers?watershed_id={id}&layer_type={type}`**
  - Supported layer types: `DRAINAGE`, `WATER_BODIES`, `LULC`, `RISK_ZONES`, `INTERVENTIONS`.
  - Returns GeoJSON FeatureCollection payload ready for MapLibre GL rendering.

---

## 4. Geo-Tagged Field Photographs
- **`GET /photos?watershed_id={id}&category={cat}&verification_status={status}`**
  - Returns geo-tagged photographs with coordinates, categories, and observation notes.
- **`POST /photos`**
  - Ingests a new photograph with EXIF coordinate extraction and verification workflow.

---

## 5. Analytics & Change Detection
- **`GET /health-score?watershed_id={id}`**
  - Returns transparent multi-criteria composite score (0–100) and weighted breakdown.
- **`GET /changes?watershed_id={id}&from_year=2018&to_year=2024`**
  - Calculates multi-temporal deltas for vegetation, water spread, soil moisture, and time-series points.

---

## 6. Predictive Intelligence & Risk Matrix
- **`GET /predictions?watershed_id={id}`**
  - Returns Ridge regression and ensemble projections with 95% confidence intervals.
- **`GET /risks?watershed_id={id}`**
  - Returns synthesized multi-criteria risk matrix (LOW / MEDIUM / HIGH) and evidence.

---

## 7. Interventions & Recommendations
- **`GET /recommendations?watershed_id={id}`**
  - Returns prioritized engineering and bio-physical intervention recommendations with DPR disclaimers.
- **`GET /interventions?watershed_id={id}`**
  - Returns catalog of physical structures with before vs monitored change metrics.

---

## 8. Environmental Alerts & Reporting
- **`GET /alerts?watershed_id={id}`**
  - Returns active environmental warnings and field inspection reminders.
- **`PATCH /alerts/{id}/status?status={ACTIVE|ACKNOWLEDGED|RESOLVED}`**
  - Updates alert workflow status.
- **`GET /reports/{id}`**
  - Compiles comprehensive printable diagnostic report.
