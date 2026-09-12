import pytest
from fastapi.testclient import TestClient
from app.main import app, init_db
from app.core.database import SessionLocal
from app.models.domain import Intervention, Observation
from data.seed_data import seed_interventions

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    """Generates valid JWT auth headers for testing protected endpoints."""
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "admin@jaldrishti.gov.in",
        "password": "JalDrishti@2026"
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_seed_interventions_idempotency():
    """Verifies that seed_interventions is completely idempotent and does not create duplicate records."""
    db = SessionLocal()
    try:
        # Run seeding once
        seed_interventions(db)
        count_after_first = db.query(Intervention).count()
        obs_after_first = db.query(Observation).filter(Observation.intervention_id != None).count()
        assert count_after_first >= 15, f"Expected at least 15 interventions, got {count_after_first}"
        assert obs_after_first >= 6, f"Expected at least 6 observations, got {obs_after_first}"

        # Run seeding second time
        seed_interventions(db)
        count_after_second = db.query(Intervention).count()
        obs_after_second = db.query(Observation).filter(Observation.intervention_id != None).count()

        assert count_after_second == count_after_first, (
            f"Intervention count changed on second run: {count_after_first} -> {count_after_second}"
        )
        assert obs_after_second == obs_after_first, (
            f"Observation count changed on second run: {obs_after_first} -> {obs_after_second}"
        )

        # Check all 3 watersheds have their 5 distinct codes
        expected_ws_codes = {
            1: ["INT-HB-CD-01", "INT-HB-CCT-02", "INT-HB-PT-03", "INT-HB-GP-04", "INT-HB-FP-05"],
            2: ["INT-RS-CD-01", "INT-RS-PT-02", "INT-RS-LBS-03", "INT-RS-FP-04", "INT-RS-CCT-05"],
            3: ["INT-ARV-JD-01", "INT-ARV-AN-02", "INT-ARV-CCT-03", "INT-ARV-AFF-04", "INT-ARV-RS-05"]
        }
        for ws_id, codes in expected_ws_codes.items():
            for c in codes:
                intv = db.query(Intervention).filter(Intervention.code == c).first()
                assert intv is not None, f"Expected intervention {c} not found in DB"
                assert intv.watershed_id == ws_id, f"Intervention {c} has incorrect watershed_id {intv.watershed_id}"
                assert intv.source_type == "DEMO / SEEDED DATA", f"Intervention {c} has wrong source_type: {intv.source_type}"
    finally:
        db.close()

def test_api_interventions_filtering_and_provenance(auth_headers):
    """Tests /api/v1/interventions endpoint with watershed and status filters, and verifies provenance."""
    # 1. Query all interventions
    res = client.get("/api/v1/interventions", headers=auth_headers)
    assert res.status_code == 200
    all_items = res.json()
    assert len(all_items) >= 15
    for item in all_items:
        assert item.get("source_type") == "DEMO / SEEDED DATA"

    # 2. Query per watershed
    for ws_id in [1, 2, 3]:
        res_ws = client.get(f"/api/v1/interventions?watershed_id={ws_id}", headers=auth_headers)
        assert res_ws.status_code == 200
        items = res_ws.json()
        assert len(items) >= 5, f"Watershed {ws_id} expected at least 5 interventions, got {len(items)}"
        for item in items:
            assert item["watershed_id"] == ws_id
            assert item["source_type"] == "DEMO / SEEDED DATA"

    # 3. Query status filters for Watershed 1
    for st in ["COMPLETED", "WORK_IN_PROGRESS", "SANCTIONED", "PROPOSED"]:
        res_st = client.get(f"/api/v1/interventions?watershed_id=1&status={st}", headers=auth_headers)
        assert res_st.status_code == 200
        items = res_st.json()
        assert len(items) >= 1, f"Expected at least 1 {st} intervention for watershed 1"
        for item in items:
            assert item["status"] == st

def test_api_intervention_observations_history(auth_headers):
    """Tests observation logging and retrieval on seeded completed interventions."""
    # Find a completed intervention
    res_list = client.get("/api/v1/interventions?watershed_id=1&status=COMPLETED", headers=auth_headers)
    assert res_list.status_code == 200
    completed = res_list.json()
    assert len(completed) >= 1
    intv_id = completed[0]["id"]

    # Retrieve inspection observations
    res_obs = client.get(f"/api/v1/interventions/{intv_id}/observations", headers=auth_headers)
    assert res_obs.status_code == 200
    obs_list = res_obs.json()
    assert len(obs_list) >= 1, f"Expected inspection observations for intervention {intv_id}"
    
    first_obs = obs_list[0]
    assert first_obs["intervention_id"] == intv_id
    assert first_obs["condition_rating"] in ["EXCELLENT", "GOOD", "MODERATE", "CRITICAL"]
    assert len(first_obs["observer_name"]) > 0
    assert "DEMO / SEEDED DATA" in first_obs["remarks"]
