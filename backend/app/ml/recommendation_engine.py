"""
JalDrishti AI — Decision-Support Recommendation Engine
Dynamically generates prioritized, biophysically-grounded engineering and biological
interventions directly coupled to the multi-hazard risk assessment and feature trajectory.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from app.ml.risk_engine import RiskEvaluation

@dataclass
class RecommendationPlan:
    intervention_type: str
    category: str # WATER_HARVESTING, SOIL_CONSERVATION, VEGETATION_RESTORATION, DRAINAGE_TREATMENT, INTERVENTION_MONITORING
    priority: str # CRITICAL, HIGH, MEDIUM, LOW
    problem_statement: str
    evidence_basis: str
    estimated_cost_inr: str
    expected_impact: str
    status: str = "PROPOSED"

class RecommendationEngine:
    """
    Synthesizes decision-support recommendations tailored to the catchment's
    biophysical risks, topographic relief, and current treatment status.
    """

    @staticmethod
    def synthesize_recommendations(
        features: Dict[str, Any], 
        risks: List[RiskEvaluation]
    ) -> List[RecommendationPlan]:
        recs: List[RecommendationPlan] = []
        risk_map = {r.risk_category: r for r in risks}

        # 1. Water Stress -> Water Harvesting
        ws_risk = risk_map.get("WATER_STRESS")
        smi = features.get("latest_smi", 35.0)
        storage = features.get("water_storage_capacity_tcm", 80.0)
        if ws_risk and ws_risk.risk_level in ["HIGH", "MEDIUM"]:
            priority = "CRITICAL" if ws_risk.risk_level == "HIGH" else "HIGH"
            recs.append(RecommendationPlan(
                intervention_type="Percolation Tank with Recharge Shafts",
                category="WATER_HARVESTING",
                priority=priority,
                problem_statement=f"Seasonal water stress evaluated at {ws_risk.score}/100 with root-zone moisture at {smi:.1f}%. Existing storage capacity of {storage:.1f} TCM is insufficient for multi-cropping.",
                evidence_basis=f"Derived from WATER_STRESS evaluation ({ws_risk.risk_level}): {ws_risk.evidence_summary}",
                estimated_cost_inr="₹12,00,000 - ₹18,00,000",
                expected_impact="Augment unconfined basalt/alluvial aquifer storage by 35-50 TCM, stabilizing rabi irrigation across ~60 ha."
            ))
        else:
            recs.append(RecommendationPlan(
                intervention_type="Micro-Irrigation & Water Budgeting Optimization",
                category="WATER_HARVESTING",
                priority="LOW",
                problem_statement=f"Current water retention is stable ({storage:.1f} TCM capacity), but dry-season rabi crop intensification requires demand-side water budgeting to avoid over-draft.",
                evidence_basis=f"Derived from WATER_STRESS evaluation (LOW: {ws_risk.score if ws_risk else 20.0}/100): Preventative conservation needed to maintain groundwater surplus.",
                estimated_cost_inr="₹3,00,000 - ₹5,00,000",
                expected_impact="Sustain unconfined water table levels within the safe recharge zone (>8m depth) and prevent crop moisture stress across 75 ha."
            ))

        # 2. Soil Erosion -> Soil Conservation & Drainage Treatment
        erosion_risk = risk_map.get("SOIL_EROSION")
        relief = features.get("relief_m", 130.0)
        barren = features.get("barren_pct", 18.0)
        if erosion_risk and erosion_risk.risk_level in ["HIGH", "MEDIUM"]:
            priority = "HIGH" if erosion_risk.risk_level == "HIGH" else "MEDIUM"
            recs.append(RecommendationPlan(
                intervention_type="Continuous Contour Trenches (CCT) & Terraced Bunding",
                category="SOIL_CONSERVATION",
                priority=priority,
                problem_statement=f"Topographic relief of {relief:.1f} m and {barren:.1f}% barren exposure causes rapid overland runoff and detachment of fertile topsoil during peak rainfall events.",
                evidence_basis=f"Derived from SOIL_EROSION evaluation ({erosion_risk.risk_level}): {erosion_risk.evidence_summary}",
                estimated_cost_inr="₹5,00,000 - ₹9,00,000",
                expected_impact="Reduce peak runoff velocity by 40-55%, conserving an estimated 12 tonnes/ha/yr of topsoil on slopes."
            ))

            recs.append(RecommendationPlan(
                intervention_type="Loose Boulder Structures (LBS) & Gully Plugs",
                category="DRAINAGE_TREATMENT",
                priority="MEDIUM",
                problem_statement="Second-order ephemeral torrents exhibit active bed scour and headward gully migration.",
                evidence_basis=f"Drainage network density stands at {features.get('drainage_density', 1.2):.2f} km/km².",
                estimated_cost_inr="₹2,50,000 - ₹4,50,000",
                expected_impact="Trap silt upstream of primary nalas, stabilizing stream gradient and recharging shallow riparian aquifers."
            ))
        else:
            recs.append(RecommendationPlan(
                intervention_type="Field Bund Stabilization & Vetiver Grass Hedging",
                category="SOIL_CONSERVATION",
                priority="LOW",
                problem_statement=f"Catchment relief of {relief:.1f} m requires maintenance of arable terrace borders to prevent localized sheet wash during high-intensity rain events.",
                evidence_basis=f"Derived from SOIL_EROSION evaluation (LOW: {erosion_risk.score if erosion_risk else 25.0}/100): Preventative vegetative hedge reinforcement.",
                estimated_cost_inr="₹2,00,000 - ₹3,50,000",
                expected_impact="Maintain soil detachment rates below 2 tonnes/ha/yr and preserve agricultural topsoil nutrients across boundary parcels."
            ))

        # 3. Vegetation Degradation -> Vegetation Restoration
        veg_risk = risk_map.get("VEGETATION_DEGRADATION")
        ndvi = features.get("latest_ndvi", 0.55)
        forest_pct = features.get("forest_veg_pct", 28.0)
        if veg_risk and veg_risk.risk_level in ["HIGH", "MEDIUM"]:
            priority = "HIGH" if veg_risk.risk_level == "HIGH" else "MEDIUM"
            recs.append(RecommendationPlan(
                intervention_type="Ridge Afforestation & Silvi-Pasture Development",
                category="VEGETATION_RESTORATION",
                priority=priority,
                problem_statement=f"Upper catchment protected canopy is limited to {forest_pct:.1f}% with mean NDVI at {ndvi:.2f}, indicating inadequate vegetative cover on ridges.",
                evidence_basis=f"Derived from VEGETATION_DEGRADATION evaluation ({veg_risk.risk_level}): {veg_risk.evidence_summary}",
                estimated_cost_inr="₹7,00,000 - ₹12,00,000",
                expected_impact="Re-establish native drought-hardy canopy (Neem, Subabul, Grasses) over 40 ha, improving biological infiltration by 25%."
            ))

        # 4. Universal Monitoring & Desiltation
        interventions_count = features.get("interventions_count", 0)
        recs.append(RecommendationPlan(
            intervention_type="Reservoir Desiltation & Geo-Tagged Ground Audit",
            category="INTERVENTION_MONITORING",
            priority="LOW" if len(recs) > 2 else "MEDIUM",
            problem_statement=f"{interventions_count} existing conservation structures require periodic silt removal and structural integrity validation.",
            evidence_basis="Cumulative storage efficiency degrades by 3-5% annually due to fine sediment accumulation.",
            estimated_cost_inr="₹1,50,000 - ₹3,00,000",
            expected_impact="Restore 15-20% dead storage capacity and verify ground assets using geo-tagged field photography."
        ))

        return recs
