from typing import List
from sqlalchemy.orm import Session
from app.models.domain import Watershed, Prediction
from app.schemas.schemas import PredictionResponse, PredictionItem
from app.ml.feature_pipeline import FeatureExtractor
from app.ml.ridge_predictor import RidgePredictor

TARGETS = [
    ("WATER_STRESS_INDEX_12M", 12),
    ("VEGETATION_DEGRADATION_RISK", 12),
    ("LAND_CONDITION_DETERIORATION_24M", 24)
]

class PredictionService:
    @staticmethod
    def get_predictions_for_watershed(db: Session, watershed_id: int) -> PredictionResponse:
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed with ID {watershed_id} not found.")

        # Check existing predictions in DB
        preds = db.query(Prediction).filter(Prediction.watershed_id == watershed_id).all()
        
        # If none or if we have fewer than 3 targets, generate multi-target predictions dynamically
        if not preds or len(preds) < len(TARGETS):
            PredictionService.generate_and_store_predictions(db, watershed_id)
            preds = db.query(Prediction).filter(Prediction.watershed_id == watershed_id).all()

        items = [PredictionItem.model_validate(p) for p in preds]

        return PredictionResponse(
            watershed_id=watershed_id,
            predictions=items,
            model_architecture="Scikit-Learn Ridge Regression with Monte Carlo Uncertainty Bands",
            disclaimer="PROTOTYPE PREDICTIVE INTELLIGENCE: Projections derived from 2018-2024 calibrated indicator trajectories for SIH 26015. Modular architecture ready for satellite-derived operational models."
        )

    @staticmethod
    def generate_and_store_predictions(db: Session, watershed_id: int):
        """Prepares features and runs modular Ridge models across all 3 target metrics."""
        features = FeatureExtractor.extract_watershed_features(db, watershed_id)
        predictor = RidgePredictor(alpha=1.0)

        # Clear existing outdated predictions for clean update
        db.query(Prediction).filter(Prediction.watershed_id == watershed_id).delete()

        for target_metric, horizon in TARGETS:
            res = predictor.predict(features, target_metric=target_metric, horizon_months=horizon)
            p = Prediction(
                watershed_id=watershed_id,
                target_metric=res.target_metric,
                prediction_horizon_months=res.prediction_horizon_months,
                predicted_value=res.predicted_value,
                confidence_lower=res.confidence_lower,
                confidence_upper=res.confidence_upper,
                confidence_score=res.confidence_score,
                model_name=res.model_name,
                model_version=res.model_version,
                status=res.status,
                features_used=res.features_used,
                feature_importances=res.feature_importances,
                rationale=res.rationale
            )
            db.add(p)

        db.commit()
