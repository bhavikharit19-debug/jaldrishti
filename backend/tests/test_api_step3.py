import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_states_and_districts_hierarchy():
    # List states
    res = client.get("/api/v1/states")
    assert res.status_code == 200
    states = res.json()
    assert len(states) >= 2
    state_names = [s["name"] for s in states]
    assert "Maharashtra" in state_names

    # Get single state
    state_id = states[0]["id"]
    res = client.get(f"/api/v1/states/{state_id}")
    assert res.status_code == 200
    assert "districts" in res.json()

    # Get districts for state
    res = client.get(f"/api/v1/states/{state_id}/districts")
    assert res.status_code == 200
    districts = res.json()
    assert len(districts) >= 1

    # List all districts
    res = client.get("/api/v1/districts")
    assert res.status_code == 200
    all_districts = res.json()
    assert len(all_districts) >= 2

    # Get single district
    dist_id = all_districts[0]["id"]
    res = client.get(f"/api/v1/districts/{dist_id}")
    assert res.status_code == 200
    assert res.json()["id"] == dist_id

    # Get watersheds for district
    res = client.get(f"/api/v1/districts/{dist_id}/watersheds")
    assert res.status_code == 200
    ws_list = res.json()
    assert len(ws_list) >= 1

def test_watershed_spatial_locate():
    # Hiware Bazar is around lat: 19.04, lng: 74.88
    res = client.get("/api/v1/watersheds/spatial/locate?lat=19.04&lng=74.88")
    assert res.status_code == 200
    data = res.json()
    assert data["watershed_id"] == 1
    assert "Hiware Bazar" in data["watershed_name"]
    assert "is_inside" in data
    assert "distance_to_centroid_km" in data

    # Invalid latitude out of range (-95)
    res_bad = client.get("/api/v1/watersheds/spatial/locate?lat=-95.0&lng=74.88")
    assert res_bad.status_code in [400, 422]

def test_watershed_boundary_endpoint():
    res = client.get("/api/v1/watersheds/1/boundary")
    assert res.status_code == 200
    feat = res.json()
    assert feat["type"] == "Feature"
    assert feat["geometry"]["type"] in ["Polygon", "MultiPolygon"]
    assert feat["properties"]["watershed_id"] == 1

def test_gis_layers_enhanced():
    # Summary mode
    res_summary = client.get("/api/v1/layers?summary_only=true")
    assert res_summary.status_code == 200
    summaries = res_summary.json()
    assert len(summaries) >= 8
    assert "data_payload" not in summaries[0]
    assert "feature_count" in summaries[0]

    # Dedicated watershed layers
    res_ws = client.get("/api/v1/watersheds/1/layers")
    assert res_ws.status_code == 200
    assert len(res_ws.json()) >= 5

    # Specific layer by type
    res_lulc = client.get("/api/v1/watersheds/1/layers/LULC")
    assert res_lulc.status_code == 200
    assert res_lulc.json()["layer_type"] == "LULC"

def test_photo_crud_and_validation():
    # 1. Coordinate validation failure
    bad_payload = {
        "watershed_id": 1,
        "latitude": 105.0, # invalid
        "longitude": 74.88,
        "photo_url": "https://example.com/bad.jpg",
        "category": "CHECK_DAM"
    }
    res_bad = client.post("/api/v1/photos", json=bad_payload)
    assert res_bad.status_code in [400, 422]

    # 2. Create valid photo
    valid_payload = {
        "watershed_id": 1,
        "latitude": 19.042,
        "longitude": 74.881,
        "photo_url": "https://images.unsplash.com/photo-1544376798-89aa6b82c6cd",
        "category": "CHECK_DAM",
        "description": "Upstream siltation survey post-monsoon 2024",
        "exif_metadata": {"camera": "SurveyPhone-V2", "accuracy_m": 3.5}
    }
    res_create = client.post("/api/v1/photos", json=valid_payload)
    assert res_create.status_code == 201
    created_photo = res_create.json()
    photo_id = created_photo["id"]
    assert created_photo["verification_status"] == "PENDING"
    assert created_photo["latitude"] == 19.042

    # 3. Get photo by ID
    res_get = client.get(f"/api/v1/photos/{photo_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == photo_id

    # 4. Update photo verification
    update_payload = {
        "verification_status": "VERIFIED",
        "description": "Verified by nodal officer on-site"
    }
    res_update = client.put(f"/api/v1/photos/{photo_id}", json=update_payload)
    assert res_update.status_code == 200
    assert res_update.json()["verification_status"] == "VERIFIED"

    # 5. Delete photo
    res_del = client.delete(f"/api/v1/photos/{photo_id}")
    assert res_del.status_code == 200

    # 6. Verify 404 after deletion
    res_deleted = client.get(f"/api/v1/photos/{photo_id}")
    assert res_deleted.status_code == 404

def test_interventions_and_observations():
    # 1. List interventions
    res = client.get("/api/v1/interventions?watershed_id=1")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 1
    inv_id = items[0]["id"]

    # 2. Get single intervention
    res_inv = client.get(f"/api/v1/interventions/{inv_id}")
    assert res_inv.status_code == 200
    assert res_inv.json()["id"] == inv_id

    # 3. Create intervention
    new_inv = {
        "watershed_id": 1,
        "code": "HB-CD-NEW-01",
        "name": "Sub-surface Dyke Test",
        "intervention_type": "Sub-surface Dyke",
        "status": "PROPOSED",
        "sanction_year": 2024,
        "latitude": 19.045,
        "longitude": 74.885,
        "target_capacity_cum": 850.0,
        "beneficiary_count": 30,
        "cost_inr": 250000.0,
        "observed_change_summary": "Proposed to arrest downstream sub-surface baseflow."
    }
    res_create = client.post("/api/v1/interventions", json=new_inv)
    assert res_create.status_code == 201
    created_id = res_create.json()["id"]

    # 4. Update intervention
    res_update = client.put(f"/api/v1/interventions/{created_id}", json={"status": "SANCTIONED"})
    assert res_update.status_code == 200
    assert res_update.json()["status"] == "SANCTIONED"

    # 5. Post observation for this intervention
    obs_payload = {
        "watershed_id": 1,
        "observer_name": "Dr. R. Sharma, Ground Hydrologist",
        "condition_rating": "GOOD",
        "remarks": "Site pegged; baseline infiltration rate measured at 12 mm/hr.",
        "recommended_action": "Proceed with trench excavation before next monsoon."
    }
    res_obs = client.post(f"/api/v1/interventions/{created_id}/observations", json=obs_payload)
    assert res_obs.status_code == 201
    obs_id = res_obs.json()["id"]

    # 6. List observations for intervention
    res_inv_obs = client.get(f"/api/v1/interventions/{created_id}/observations")
    assert res_inv_obs.status_code == 200
    assert len(res_inv_obs.json()) >= 1

    # 7. Get observation by ID
    res_obs_single = client.get(f"/api/v1/observations/{obs_id}")
    assert res_obs_single.status_code == 200
    assert res_obs_single.json()["condition_rating"] == "GOOD"

def test_analytics_and_indicators_endpoints():
    # 1. Indicators catalog
    res_ind = client.get("/api/v1/indicators")
    assert res_ind.status_code == 200
    indicators = res_ind.json()
    assert len(indicators) >= 4
    codes = [i["code"] for i in indicators]
    assert "NDVI" in codes

    # 2. Watershed indicator values
    res_ws_ind = client.get("/api/v1/watersheds/1/indicators")
    assert res_ws_ind.status_code == 200
    assert len(res_ws_ind.json()) >= 1

    # 3. RESTful analytics routes
    res_health = client.get("/api/v1/watersheds/1/health-score")
    assert res_health.status_code == 200
    assert "overall_health_score" in res_health.json()

    res_changes = client.get("/api/v1/watersheds/1/changes?from_year=2018&to_year=2024")
    assert res_changes.status_code == 200
    assert len(res_changes.json()["indicators"]) >= 1

    res_pred = client.get("/api/v1/watersheds/1/predictions")
    assert res_pred.status_code == 200
    assert len(res_pred.json()["predictions"]) >= 1

    res_risk = client.get("/api/v1/watersheds/1/risks")
    assert res_risk.status_code == 200
    assert len(res_risk.json()["risks"]) >= 1

    res_rec = client.get("/api/v1/watersheds/1/recommendations")
    assert res_rec.status_code == 200
    assert len(res_rec.json()["recommendations"]) >= 1

def test_alerts_and_reports_enhanced():
    # 1. Alerts listing & creation
    res_alerts = client.get("/api/v1/alerts")
    assert res_alerts.status_code == 200
    assert len(res_alerts.json()) >= 1

    new_alert = {
        "watershed_id": 1,
        "alert_type": "SOIL_MOISTURE_DEFICIT",
        "severity": "HIGH",
        "trigger_reason": "Root-zone soil moisture below 15% threshold across 42 ha pediment.",
        "supporting_indicator": "SMI"
    }
    res_post_alert = client.post("/api/v1/alerts", json=new_alert)
    assert res_post_alert.status_code == 201
    alert_id = res_post_alert.json()["id"]

    # Dedicated watershed alert endpoint
    res_ws_alerts = client.get("/api/v1/watersheds/1/alerts")
    assert res_ws_alerts.status_code == 200
    alert_ids = [a["id"] for a in res_ws_alerts.json()]
    assert alert_id in alert_ids

    # 2. Reports summary listing
    res_reports = client.get("/api/v1/reports")
    assert res_reports.status_code == 200
    reports = res_reports.json()
    assert len(reports) >= 3
    assert "health_score" in reports[0]

    # RESTful watershed report
    res_ws_rep = client.get("/api/v1/watersheds/1/report")
    assert res_ws_rep.status_code == 200
    assert res_ws_rep.json()["watershed"]["id"] == 1

def test_error_handling_and_nonexistent_resources():
    # Non-existent watershed
    assert client.get("/api/v1/watersheds/99999").status_code == 404
    assert client.get("/api/v1/watersheds/99999/boundary").status_code == 404
    assert client.get("/api/v1/watersheds/99999/gis-stats").status_code == 404
    assert client.get("/api/v1/watersheds/99999/health-score").status_code == 404

    # Non-existent state / district
    assert client.get("/api/v1/states/99999").status_code == 404
    assert client.get("/api/v1/districts/99999").status_code == 404

    # Non-existent photo / intervention / alert
    assert client.get("/api/v1/photos/99999").status_code == 404
    assert client.get("/api/v1/interventions/99999").status_code == 404
    assert client.delete("/api/v1/photos/99999").status_code == 404
    assert client.patch("/api/v1/alerts/99999/status?status=RESOLVED").status_code == 404
