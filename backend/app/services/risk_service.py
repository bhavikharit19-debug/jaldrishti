from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.domain import Watershed, RiskAssessment, Prediction
from app.schemas.schemas import RiskAssessmentResponse, RiskItem
from app.ml.feature_pipeline import FeatureExtractor
from app.ml.risk_engine import RiskEngine

class RiskService:
    @staticmethod
    def get_risk_assessment_for_watershed(db: Session, watershed_id: int) -> RiskAssessmentResponse:
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed with ID {watershed_id} not found.")

        # Check existing risk assessments
        risks = db.query(RiskAssessment).filter(RiskAssessment.watershed_id == watershed_id).all()
        
        # If none exist, or if fewer than 3 categories, evaluate dynamically using RiskEngine
        if not risks or len(risks) < 3:
            RiskService.evaluate_and_store_risks(db, watershed_id)
            risks = db.query(RiskAssessment).filter(RiskAssessment.watershed_id == watershed_id).all()

        risk_items = [RiskItem.model_validate(r) for r in risks]

        # Overall risk level
        levels = [r.risk_level for r in risks]
        if "CRITICAL" in levels or levels.count("HIGH") >= 2:
            overall = "HIGH"
        elif "HIGH" in levels or levels.count("MEDIUM") >= 2:
            overall = "MEDIUM"
        else:
            overall = "LOW"

        ws.risk_level = overall
        db.commit()

        return RiskAssessmentResponse(
            watershed_id=watershed_id,
            overall_risk_level=overall,
            risks=risk_items,
            disclaimer="DECISION SUPPORT RISK ENGINE: Synthesizes biophysical indicators, rate-of-change trajectories, and forward ML predictive outlooks."
        )

    @staticmethod
    def evaluate_and_store_risks(db: Session, watershed_id: int):
        """Evaluates multi-hazard risks and persists structured evidence records."""
        features = FeatureExtractor.extract_watershed_features(db, watershed_id)
        
        # Get forward prediction metrics if available
        preds = db.query(Prediction).filter(Prediction.watershed_id == watershed_id).all()
        pred_dict = {p.target_metric: p.predicted_value for p in preds}

        evaluations = RiskEngine.evaluate_risks(features, pred_dict)

        # Clear existing outdated assessments
        db.query(RiskAssessment).filter(RiskAssessment.watershed_id == watershed_id).delete()

        for ev in evaluations:
            ra = RiskAssessment(
                watershed_id=watershed_id,
                risk_category=ev.risk_category,
                risk_level=ev.risk_level,
                score=ev.score,
                primary_driver=ev.primary_driver,
                evidence_summary=ev.evidence_summary,
                contributing_factors=ev.contributing_factors,
                spatial_hotspots=ev.spatial_hotspots,
                model_version="1.1.0"
            )
            db.add(ra)

        db.commit()
