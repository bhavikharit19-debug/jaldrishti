import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.domain import Watershed, Intervention, Alert, RiskAssessment, Recommendation
from app.schemas.schemas import WatershedReportResponse, ReportSummaryItem, RecommendationItem
from app.services.health_score_service import HealthScoreService
from app.services.watershed_service import WatershedService

class ReportService:
    @staticmethod
    def list_reports_summary(db: Session, limit: int = 100, offset: int = 0) -> List[ReportSummaryItem]:
        """Returns diagnostic report summaries across all catalogued watersheds."""
        watersheds = db.query(Watershed).order_by(Watershed.id).offset(offset).limit(limit).all()
        summaries = []
        for ws in watersheds:
            alerts_count = db.query(Alert).filter(
                Alert.watershed_id == ws.id,
                Alert.status == "ACTIVE"
            ).count()
            completed_inv = db.query(Intervention).filter(
                Intervention.watershed_id == ws.id,
                Intervention.status == "COMPLETED"
            ).count()
            rating = "EXCELLENT" if ws.health_score >= 80 else ("GOOD" if ws.health_score >= 65 else ("VULNERABLE" if ws.health_score >= 50 else "CRITICAL"))
            summaries.append(ReportSummaryItem(
                watershed_id=ws.id,
                watershed_code=ws.code,
                watershed_name=ws.name,
                district_name=ws.district.name if ws.district else None,
                state_name=ws.state.name if ws.state else None,
                health_score=ws.health_score,
                category_rating=rating,
                active_alerts_count=alerts_count,
                completed_interventions_count=completed_inv,
                generated_at=datetime.datetime.utcnow()
            ))
        return summaries

    @staticmethod
    def generate_watershed_report(db: Session, watershed_id: int) -> WatershedReportResponse:
        """Generates comprehensive multi-criteria diagnostic report for a watershed."""
        ws_detail = WatershedService.get_watershed_by_id(db, watershed_id)
        if not ws_detail:
            raise ValueError(f"Watershed {watershed_id} not found")

        health = HealthScoreService.calculate_watershed_health(db, watershed_id)
        
        alerts_count = db.query(Alert).filter(
            Alert.watershed_id == watershed_id,
            Alert.status == "ACTIVE"
        ).count()

        high_risks = db.query(RiskAssessment).filter(
            RiskAssessment.watershed_id == watershed_id,
            RiskAssessment.risk_level.in_(["HIGH", "CRITICAL"])
        ).count()

        interventions = db.query(Intervention).filter(
            Intervention.watershed_id == watershed_id,
            Intervention.status == "COMPLETED"
        ).all()
        
        total_beneficiaries = sum(i.beneficiary_count for i in interventions)

        recs = db.query(Recommendation).filter(
            Recommendation.watershed_id == watershed_id
        ).order_by(Recommendation.priority.asc()).limit(3).all()

        change_summary = (
            f"Official diagnostic summary for {ws_detail.name} ({ws_detail.code}): "
            f"Overall health score stands at {health.overall_health_score}/100 ({health.category_rating}). "
            f"{len(interventions)} completed watershed structures are benefiting approximately {total_beneficiaries} farmers. "
            f"Active alerts: {alerts_count}. Identified critical/high risk zones: {high_risks}."
        )

        return WatershedReportResponse(
            watershed=ws_detail,
            health_score=health,
            active_alerts_count=alerts_count,
            high_risks_count=high_risks,
            completed_interventions_count=len(interventions),
            total_beneficiaries=total_beneficiaries,
            change_summary=change_summary,
            top_recommendations=[RecommendationItem.model_validate(r) for r in recs],
            generated_at=datetime.datetime.utcnow()
        )
