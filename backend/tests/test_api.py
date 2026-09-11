import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_list_watersheds():
    response = client.get("/api/v1/watersheds")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    names = [w["name"] for w in data]
    assert any("Hiware Bazar" in n for n in names)
    assert any("Ralegan Siddhi" in n for n in names)
    assert any("Arvari River" in n for n in names)

def test_get_single_watershed():
    response = client.get("/api/v1/watersheds/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["boundary"] is not None
    assert "geometry" in data["boundary"]
    assert len(data["boundary"]["bbox"]) == 4

def test_get_gis_layers():
    response = client.get("/api/v1/layers?watershed_id=1")
    assert response.status_code == 200
    layers = response.json()
    assert len(layers) >= 3
    types = [l["layer_type"] for l in layers]
    assert "DRAINAGE" in types
    assert "WATER_BODIES" in types
    assert "LULC" in types

def test_get_field_photos():
    response = client.get("/api/v1/photos?watershed_id=1")
    assert response.status_code == 200
    photos = response.json()
    assert len(photos) >= 1
    assert photos[0]["latitude"] > 0
    assert photos[0]["photo_url"].startswith("http")

def test_health_score():
    response = client.get("/api/v1/health-score?watershed_id=1")
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["overall_health_score"] <= 100
    assert len(data["components"]) > 0

def test_change_detection():
    response = client.get("/api/v1/changes?watershed_id=1&from_year=2018&to_year=2024")
    assert response.status_code == 200
    data = response.json()
    assert len(data["indicators"]) > 0
    assert len(data["yearly_trends"]) == 7

def test_predictions():
    response = client.get("/api/v1/predictions?watershed_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["predictions"]) > 0

def test_risks():
    response = client.get("/api/v1/risks?watershed_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def test_recommendations():
    response = client.get("/api/v1/recommendations?watershed_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) > 0

def test_alerts():
    response = client.get("/api/v1/alerts?watershed_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_watershed_report():
    response = client.get("/api/v1/reports/1")
    assert response.status_code == 200
    data = response.json()
    assert data["watershed"]["id"] == 1
    assert data["health_score"]["overall_health_score"] > 0

if __name__ == "__main__":
    pytest.main(["-v", __file__])
