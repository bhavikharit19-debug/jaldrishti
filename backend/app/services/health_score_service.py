from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.domain import Watershed, IndicatorValue, Indicator, Intervention
from app.schemas.schemas import HealthScoreResponse, HealthScoreComponent

class HealthScoreService:
    @staticmethod
    def calculate_watershed_health(db: Session, watershed_id: int) -> HealthScoreResponse:
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed {watershed_id} not found")

        # 1. Fetch latest indicator values for 2024 (or latest year)
        indicators = db.query(Indicator).all()
        components: List[HealthScoreComponent] = []

        total_weighted_score = 0.0
        total_weights = 0.0

        for ind in indicators:
            latest_val = db.query(IndicatorValue).filter(
                IndicatorValue.watershed_id == watershed_id,
                IndicatorValue.indicator_id == ind.id
            ).order_by(IndicatorValue.recorded_year.desc()).first()

            score = latest_val.normalized_score if latest_val else 50.0
            weight = ind.weight_in_health_score
            weighted_contrib = round(score * weight, 2)
            total_weighted_score += weighted_contrib
            total_weights += weight

            status = "OPTIMAL" if score >= 75 else ("MODERATE" if score >= 50 else "DEGRADED")

            components.append(HealthScoreComponent(
                name=ind.name,
                category=ind.category,
                weight=weight,
                score=round(score, 1),
                weighted_contribution=weighted_contrib,
                status=status,
                description=f"{ind.description} (Latest raw value: {latest_val.value if latest_val else 'N/A'} {ind.unit})"
            ))

        # Check intervention coverage
        interventions_count = db.query(Intervention).filter(Intervention.watershed_id == watershed_id).count()
        intervention_score = min(100.0, interventions_count * 35.0 + 30.0)
        int_weight = 0.10
        int_contrib = round(intervention_score * int_weight, 2)
        total_weighted_score += int_contrib
        total_weights += int_weight

        components.append(HealthScoreComponent(
            name="Intervention Coverage & Treatment Density",
            category="WATERSHED_MANAGEMENT",
            weight=int_weight,
            score=round(intervention_score, 1),
            weighted_contribution=int_contrib,
            status="OPTIMAL" if intervention_score >= 70 else "MODERATE",
            description=f"Density of sanctioned/completed water retention structures ({interventions_count} structures catalogued)."
        ))

        final_score = round(total_weighted_score / total_weights if total_weights > 0 else 50.0, 1)

        rating = "EXCELLENT" if final_score >= 80 else ("GOOD" if final_score >= 65 else ("VULNERABLE" if final_score >= 50 else "CRITICAL"))

        # Update cache in watershed model
        ws.health_score = final_score
        db.commit()

        return HealthScoreResponse(
            watershed_id=ws.id,
            watershed_name=ws.name,
            overall_health_score=final_score,
            category_rating=rating,
            components=components,
            data_source_disclaimer="Calculated using transparent multi-criteria baseline indicator weights (Vegetation: 25%, Hydrology: 40%, Soil Condition: 15%, Structure Coverage: 10%)."
        )
