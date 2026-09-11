"""
JalDrishti AI — Step 5 Test Suite: Real Data Integration & Field Image Intelligence
Tests dataset catalog, GeoJSON/CSV import validation, EXIF extraction,
spatial watershed linking, satellite provider adapters, and Step 4 compatibility.
"""

import io
import json
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.core.database import SessionLocal
from app.models.domain import Watershed, GeospatialDataset, GISLayer, FieldPhoto
from app.core.spatial import validate_geojson_geometry, check_point_in_watershed
from app.core.exif import ExifExtractor
from app.data_pipeline.importer import DataImporter
from app.data_pipeline.normalizer import DataNormalizer
from app.integrations.registry import ProviderRegistry
from app.ml.feature_pipeline import FeatureExtractor
from app.ml.ridge_predictor import RidgePredictor

client = TestClient(app)

def test_dataset_catalog_api():
    """Verifies the dataset catalog endpoint and provenance summary."""
    res = client.get("/api/v1/data/catalog")
    assert res.status_code == 200
    data = res.json()
    assert "total_datasets" in data
    assert "datasets" in data
    assert "provenance_summary" in data
    assert data["total_datasets"] >= 1
    
    first_ds = data["datasets"][0]
    assert "dataset_code" in first_ds
    assert "provider" in first_ds
    assert "crs" in first_ds
    assert first_ds["provenance"] in ["DEMO_DATA", "IMPORTED_DATA", "OFFICIAL_SOURCE"]

def test_provider_adapters_api():
    """Verifies satellite & GIS provider adapters reporting."""
    res = client.get("/api/v1/data/adapters")
    assert res.status_code == 200
    adapters = res.json()
    assert len(adapters) >= 3
    codes = [a["provider_code"] for a in adapters]
    assert "COPERNICUS_SENTINEL2" in codes
    assert "NRSC_BHUVAN" in codes
    assert "USGS_LANDSAT" in codes
    for a in adapters:
        assert "status" in a
        assert "endpoint" in a
        assert "has_credentials" in a

def test_geojson_import_validation_valid():
    """Tests importing a topologically valid GeoJSON vector layer."""
    db = SessionLocal()
    try:
        valid_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "North Slope Bund", "class": "Agriculture", "area_ha": 35.0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[74.590, 19.040], [74.600, 19.040], [74.600, 19.050], [74.590, 19.050], [74.590, 19.040]]
                        ]
                    }
                }
            ]
        }
        result = DataImporter.import_geojson(
            db=db,
            geojson_data=valid_geojson,
            watershed_id=1,
            layer_type="LULC",
            dataset_name="Test Ingested Agricultural Plot",
            provider="District Soil Survey"
        )
        assert result["status"] == "SUCCESS"
        assert result["records_processed"] == 1
        assert result["provenance"] == "IMPORTED_DATA"
        assert "dataset_code" in result

        # Cleanup test artifacts
        db.query(GISLayer).filter(GISLayer.id == result["layer_id"]).delete()
        db.query(GeospatialDataset).filter(GeospatialDataset.id == result["dataset_id"]).delete()
        db.commit()
    finally:
        db.close()

def test_geojson_import_validation_invalid_geometry():
    """Tests rejection of invalid GeoJSON geometry (unclosed polygon coordinates)."""
    db = SessionLocal()
    try:
        invalid_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Bad Polygon"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[74.590, 19.040], [74.600, 19.040]] # Invalid: polygon must have >= 3 points + closed ring
                        ]
                    }
                }
            ]
        }
        with pytest.raises(ValueError) as exc_info:
            DataImporter.import_geojson(
                db=db,
                geojson_data=invalid_geojson,
                watershed_id=1,
                layer_type="LULC"
            )
        assert "geometric topology validation" in str(exc_info.value).lower()
    finally:
        db.close()

def test_csv_import_validation_valid():
    """Tests importing a valid coordinate CSV dataset."""
    db = SessionLocal()
    try:
        csv_data = """latitude,longitude,category,description
19.042,74.605,WATER_BODY,Percolation pond field survey
19.045,74.610,CHECK_DAM,Masonry weir visual inspection
"""
        result = DataImporter.import_csv(
            db=db,
            csv_content=csv_data,
            watershed_id=1,
            dataset_type="FIELD_PHOTOS",
            dataset_name="Ground Survey Nov 2024",
            provider="Ground Monitoring NGO"
        )
        assert result["status"] == "SUCCESS"
        assert result["records_processed"] == 2
        assert result["provenance"] == "IMPORTED_DATA"

        # Cleanup test records
        db.query(FieldPhoto).filter(FieldPhoto.provenance == "IMPORTED_DATA").delete()
        db.query(GeospatialDataset).filter(GeospatialDataset.id == result["dataset_id"]).delete()
        db.commit()
    finally:
        db.close()

def test_csv_import_missing_coordinates():
    """Tests rejection of CSV without latitude and longitude columns."""
    db = SessionLocal()
    try:
        invalid_csv = """site_id,water_level,sample_date
SITE-01,4.2,2024-05-01
SITE-02,3.8,2024-05-02
"""
        with pytest.raises(ValueError) as exc_info:
            DataImporter.import_csv(
                db=db,
                csv_content=invalid_csv,
                watershed_id=1,
                dataset_type="FIELD_PHOTOS"
            )
        assert "must contain latitude and longitude columns" in str(exc_info.value).lower()
    finally:
        db.close()

def test_exif_extraction_from_synthetic_image():
    """Creates an in-memory JPEG with EXIF GPS tags and validates precision extraction."""
    from fractions import Fraction
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    exif = img.getexif()
    # Tag 34853 is GPSInfo IFD
    gps_ifd = exif.get_ifd(34853)
    # 19 deg 2' 42" N = 19.045
    gps_ifd[1] = "N"
    gps_ifd[2] = (Fraction(19, 1), Fraction(2, 1), Fraction(42, 1))
    # 74 deg 36' 18" E = 74.605
    gps_ifd[3] = "E"
    gps_ifd[4] = (Fraction(74, 1), Fraction(36, 1), Fraction(18, 1))
    gps_ifd[6] = Fraction(620, 1) # 620m altitude
    exif[271] = "Trimble GeoXR" # Make
    exif[272] = "Handheld GNSS" # Model

    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    img_bytes = buf.getvalue()

    result = ExifExtractor.extract_from_bytes(img_bytes)
    assert result["has_gps"] is True
    assert abs(result["latitude"] - 19.045) < 0.001
    assert abs(result["longitude"] - 74.605) < 0.001
    assert result["altitude_m"] == 620.0
    assert result["device_make"] == "Trimble GeoXR"

def test_watershed_spatial_association():
    """Tests spatial containment verification against Hiware Bazar polygon boundary."""
    hb_boundary = {
        "type": "Polygon",
        "coordinates": [[[74.580, 19.030], [74.630, 19.030], [74.630, 19.070], [74.580, 19.070], [74.580, 19.030]]]
    }
    # Point inside
    assert check_point_in_watershed(19.050, 74.600, hb_boundary) is True
    # Point in New Delhi (far outside)
    assert check_point_in_watershed(28.6139, 77.2090, hb_boundary) is False

def test_feature_pipeline_with_imported_data_normalization():
    """Verifies that imported data is transparently normalized into Step 4 FeatureExtractor."""
    db = SessionLocal()
    try:
        features = FeatureExtractor.extract_watershed_features(db, watershed_id=1)
        assert "data_provenance" in features
        # Must retain backward-compatible keys expected by RidgePredictor
        predictor = RidgePredictor()
        pred = predictor.predict(features, "WATER_STRESS_INDEX_12M")
        assert 0.0 <= pred.predicted_value <= 100.0
        assert pred.confidence_lower <= pred.predicted_value <= pred.confidence_upper
    finally:
        db.close()
