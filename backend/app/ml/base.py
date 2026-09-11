"""
JalDrishti AI — Machine Learning Base Interfaces & Data Contracts
Defines base predictor contract, ensuring modularity so lightweight Ridge
can later be substituted with Gradient Boosted or Deep Learning models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class PredictionResult:
    target_metric: str
    prediction_horizon_months: int
    predicted_value: float
    confidence_lower: float
    confidence_upper: float
    confidence_score: float
    model_name: str
    model_version: str
    status: str
    features_used: List[str]
    feature_importances: Dict[str, float]
    trend_direction: str # INCREASING, DECREASING, STABLE
    rationale: str

class BasePredictor(ABC):
    """Abstract interface for all watershed predictive models."""

    @abstractmethod
    def predict(
        self, 
        features: Dict[str, Any], 
        target_metric: str, 
        horizon_months: int = 12
    ) -> PredictionResult:
        """
        Generates forward prediction with statistical confidence bounds,
        explainable feature importances, and plain-language scientific rationale.
        """
        pass
