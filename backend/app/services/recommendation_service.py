from typing import List
from sqlalchemy.orm import Session
from app.models.domain import Watershed, Recommendation, RiskAssessment, Prediction
from app.schemas.schemas import RecommendationResponse, RecommendationItem
from app.ml.feature_pipeline import FeatureExtractor
from app.ml.risk_engine import RiskEngine
from app.ml.recommendation_engine import RecommendationEngine

class RecommendationService:
    @staticmethod
    def get_recommendations_for_watershed(db: Session, watershed_id: int) -> RecommendationResponse:
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed with ID {watershed_id} not found.")

        # Check existing recommendations
        recs = db.query(Recommendation).filter(Recommendation.watershed_id == watershed_id).all()

        # If none exist or if legacy recommendations exist without evidence basis, synthesize dynamically
        if not recs or len(recs) < 2 or any(not r.evidence_basis for r in recs):
            RecommendationService.synthesize_and_store_recommendations(db, watershed_id)
            recs = db.query(Recommendation).filter(Recommendation.watershed_id == watershed_id).all()

        items = [RecommendationItem.model_validate(r) for r in recs]

        return RecommendationResponse(
            watershed_id=watershed_id,
            recommendations=items,
            notice="DECISION SUPPORT NOTICE: These engineering and biophysical intervention suggestions are algorithmic recommendations derived from spatial, hydrological, and predictive risk analysis. All interventions require mandatory ground physical survey, soil permeability testing, and sanctioned DPR (Detailed Project Report) by the competent authority before execution."
        )

    @staticmethod
    def synthesize_and_store_recommendations(db: Session, watershed_id: int):
        """Synthesizes recommendations coupled directly to catchment risks and persists them."""
        features = FeatureExtractor.extract_watershed_features(db, watershed_id)

        # Get risks or evaluate
        preds = db.query(Prediction).filter(Prediction.watershed_id == watershed_id).all()
        pred_dict = {p.target_metric: p.predicted_value for p in preds}
        risk_evals = RiskEngine.evaluate_risks(features, pred_dict)

        plans = RecommendationEngine.synthesize_recommendations(features, risk_evals)

        # Clear existing recommendations for clean update
        db.query(Recommendation).filter(Recommendation.watershed_id == watershed_id).delete()

        for p in plans:
            rec = Recommendation(
                watershed_id=watershed_id,
                intervention_type=p.intervention_type,
                category=p.category,
                priority=p.priority,
                problem_statement=p.problem_statement,
                evidence_basis=p.evidence_basis,
                estimated_cost_inr=p.estimated_cost_inr,
                expected_impact=p.expected_impact,
                target_location_geojson={},
                status=p.status
            )
            db.add(rec)

        db.commit()
