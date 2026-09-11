import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.ml.feature_pipeline import FeatureExtractor
from app.ml.ridge_predictor import RidgePredictor
from app.ml.risk_engine import RiskEngine
from app.ml.recommendation_engine import RecommendationEngine

client = TestClient(app)

def test_feature_extractor():
    db = SessionLocal()
    try:
        features = FeatureExtractor.extract_watershed_features(db, watershed_id=1)
        assert features["watershed_id"] == 1
        assert "latest_ndvi" in features
        assert 0.0 <= features["latest_ndvi"] <= 1.0
        assert "latest_ndwi" in features
        assert "latest_smi" in features
        assert "ndvi_slope" in features
        assert "relief_m" in features
        assert features["relief_m"] > 0
        assert "drainage_density" in features
        assert "forest_veg_pct" in features
        assert "interventions_count" in features
        assert "DEMO DATA" in features["data_provenance"]
    finally:
        db.close()

def test_ridge_predictor_all_targets():
    db = SessionLocal()
    try:
        features = FeatureExtractor.extract_watershed_features(db, watershed_id=1)
        predictor = RidgePredictor(alpha=1.0)

        targets = [
            "WATER_STRESS_INDEX_12M",
            "VEGETATION_DEGRADATION_RISK",
            "LAND_CONDITION_DETERIORATION_24M"
        ]

        for target in targets:
            res = predictor.predict(features, target_metric=target)
            assert res.target_metric == target
            assert 0.0 <= res.predicted_value <= 100.0
            assert res.confidence_lower <= res.predicted_value <= res.confidence_upper
            assert res.status == "PROTOTYPE_CALIBRATED"
            assert len(res.features_used) >= 3
            assert len(res.feature_importances) >= 3
            # Check feature importance sum is reasonable (~1.0)
            importance_sum = sum(res.feature_importances.values())
            assert 0.8 <= importance_sum <= 1.2
            assert len(res.rationale) > 20
            assert res.trend_direction in ["INCREASING", "DECREASING", "STABLE"]
    finally:
        db.close()

def test_risk_engine_classification_and_evidence():
    db = SessionLocal()
    try:
        features = FeatureExtractor.extract_watershed_features(db, watershed_id=1)
        predictor = RidgePredictor()
        pred_dict = {
            "WATER_STRESS_INDEX_12M": predictor.predict(features, "WATER_STRESS_INDEX_12M").predicted_value,
            "VEGETATION_DEGRADATION_RISK": predictor.predict(features, "VEGETATION_DEGRADATION_RISK").predicted_value,
            "LAND_CONDITION_DETERIORATION_24M": predictor.predict(features, "LAND_CONDITION_DETERIORATION_24M").predicted_value
        }

        risks = RiskEngine.evaluate_risks(features, pred_dict)
        assert len(risks) == 3
        categories = [r.risk_category for r in risks]
        assert "WATER_STRESS" in categories
        assert "VEGETATION_DEGRADATION" in categories
        assert "SOIL_EROSION" in categories

        for r in risks:
            assert r.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            assert 0.0 <= r.score <= 100.0
            assert len(r.primary_driver) > 5
            assert len(r.evidence_summary) > 20
            assert len(r.contributing_factors) >= 1

        overall = RiskEngine.calculate_overall_risk(risks)
        assert overall in ["LOW", "MEDIUM", "HIGH"]
    finally:
        db.close()

def test_recommendation_engine_coupling():
    db = SessionLocal()
    try:
        features = FeatureExtractor.extract_watershed_features(db, watershed_id=1)
        predictor = RidgePredictor()
        pred_dict = {
            "WATER_STRESS_INDEX_12M": predictor.predict(features, "WATER_STRESS_INDEX_12M").predicted_value,
            "VEGETATION_DEGRADATION_RISK": predictor.predict(features, "VEGETATION_DEGRADATION_RISK").predicted_value,
            "LAND_CONDITION_DETERIORATION_24M": predictor.predict(features, "LAND_CONDITION_DETERIORATION_24M").predicted_value
        }
        risks = RiskEngine.evaluate_risks(features, pred_dict)
        recs = RecommendationEngine.synthesize_recommendations(features, risks)

        assert len(recs) >= 2
        categories = [rec.category for rec in recs]
        # Should include monitoring or water harvesting or conservation
        valid_cats = [
            "WATER_HARVESTING", "SOIL_CONSERVATION", 
            "VEGETATION_RESTORATION", "DRAINAGE_TREATMENT", 
            "INTERVENTION_MONITORING"
        ]
        for cat in categories:
            assert cat in valid_cats

        for rec in recs:
            assert rec.priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            assert len(rec.problem_statement) > 10
            assert len(rec.evidence_basis) > 10
            assert "₹" in rec.estimated_cost_inr
            assert len(rec.expected_impact) > 10
    finally:
        db.close()

def test_predictions_api_live():
    res = client.get("/api/v1/predictions?watershed_id=1")
    assert res.status_code == 200
    data = res.json()
    assert data["watershed_id"] == 1
    assert len(data["predictions"]) >= 3
    targets = [p["target_metric"] for p in data["predictions"]]
    assert "WATER_STRESS_INDEX_12M" in targets
    assert "VEGETATION_DEGRADATION_RISK" in targets
    assert "LAND_CONDITION_DETERIORATION_24M" in targets

    first = data["predictions"][0]
    assert first["confidence_lower"] <= first["predicted_value"] <= first["confidence_upper"]
    assert first["status"] == "PROTOTYPE_CALIBRATED"
    assert "feature_importances" in first
    assert "PROTOTYPE" in data["disclaimer"]

    # Test RESTful route
    res_rest = client.get("/api/v1/watersheds/1/predictions")
    assert res_rest.status_code == 200
    assert len(res_rest.json()["predictions"]) >= 3

def test_risks_api_live():
    res = client.get("/api/v1/risks?watershed_id=1")
    assert res.status_code == 200
    data = res.json()
    assert data["watershed_id"] == 1
    assert data["overall_risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert len(data["risks"]) >= 3
    
    first = data["risks"][0]
    assert "contributing_factors" in first
    assert len(first["contributing_factors"]) >= 1
    assert len(first["evidence_summary"]) > 15
    assert len(first["primary_driver"]) > 5

    # Test RESTful route
    res_rest = client.get("/api/v1/watersheds/1/risks")
    assert res_rest.status_code == 200
    assert res_rest.json()["overall_risk_level"] in ["LOW", "MEDIUM", "HIGH"]

def test_recommendations_api_live():
    res = client.get("/api/v1/recommendations?watershed_id=1")
    assert res.status_code == 200
    data = res.json()
    assert data["watershed_id"] == 1
    assert len(data["recommendations"]) >= 2

    first = data["recommendations"][0]
    assert first["category"] is not None
    assert "DECISION SUPPORT NOTICE" in data["notice"]

    # Test RESTful route
    res_rest = client.get("/api/v1/watersheds/1/recommendations")
    assert res_rest.status_code == 200
    assert len(res_rest.json()["recommendations"]) >= 2
