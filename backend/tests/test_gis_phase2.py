import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_phase2_gis_layers_hiware():
    response = client.get("/api/v1/layers?watershed_id=1")
    assert response.status_code == 200
    layers = response.json()
    layer_types = [l["layer_type"] for l in layers]
    assert "DRAINAGE" in layer_types
    assert "WATER_BODIES" in layer_types
    assert "LULC" in layer_types
    assert "VEGETATION_NDVI" in layer_types
    assert "ELEVATION" in layer_types

    # Validate LULC features have 5 categories
    lulc = next(l for l in layers if l["layer_type"] == "LULC")
    assert lulc["data_payload"] is not None
    classes = [f["properties"]["class"] for f in lulc["data_payload"]["features"]]
    assert "Agriculture" in classes
    assert "Forest/Vegetation" in classes
    assert "Water" in classes
    assert "Built-up" in classes
    assert "Barren/Open Land" in classes

def test_phase2_gis_layers_all_watersheds():
    for ws_id in [1, 2, 3]:
        response = client.get(f"/api/v1/layers?watershed_id={ws_id}")
        assert response.status_code == 200
        layers = response.json()
        assert len(layers) >= 4

def test_watershed_gis_stats_endpoint():
    for ws_id in [1, 2, 3]:
        response = client.get(f"/api/v1/watersheds/{ws_id}/gis-stats")
        assert response.status_code == 200
        data = response.json()
        assert data["watershed_id"] == ws_id
        assert data["total_area_ha"] > 0
        assert data["data_provenance"] == "DEMO DATA"

        # LULC breakdown
        assert len(data["lulc"]) >= 5
        total_pct = sum(c["percentage"] for c in data["lulc"])
        assert 95.0 <= total_pct <= 105.0

        # Drainage
        assert data["drainage"]["total_length_km"] > 0
        assert data["drainage"]["density_km_per_sqkm"] > 0
        assert len(data["drainage"]["order_counts"]) > 0

        # Water bodies
        assert data["water_bodies"]["total_count"] > 0
        assert data["water_bodies"]["total_spread_ha"] > 0
        assert data["water_bodies"]["cumulative_capacity_tcm"] > 0

        # Vegetation
        assert 0.1 <= data["vegetation"]["mean_ndvi"] <= 1.0
        assert data["vegetation"]["vigor_class"] is not None

        # Elevation
        assert data["elevation"]["min_elevation_m"] > 0
        assert data["elevation"]["max_elevation_m"] > data["elevation"]["min_elevation_m"]
        assert data["elevation"]["relief_m"] > 0

def test_invalid_watershed_gis_stats():
    response = client.get("/api/v1/watersheds/9999/gis-stats")
    assert response.status_code == 404
