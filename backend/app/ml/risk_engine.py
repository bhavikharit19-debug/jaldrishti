"""
JalDrishti AI — Multi-Hazard Risk Assessment Engine
Synthesizes biophysical indicators, multi-temporal change deltas, and forward
predictive outlooks to classify risks into LOW, MEDIUM, or HIGH with transparent scientific evidence.
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class RiskEvaluation:
    risk_category: str
    risk_level: str # LOW, MEDIUM, HIGH, CRITICAL
    score: float
    primary_driver: str
    evidence_summary: str
    contributing_factors: List[str]
    spatial_hotspots: Dict[str, Any]

class RiskEngine:
    """
    Independent risk assessment layer combining current observations,
    historical rate of change, and ML predictive outlooks.
    """

    @staticmethod
    def evaluate_risks(features: Dict[str, Any], predictions: Dict[str, float]) -> List[RiskEvaluation]:
        risks = []
        
        # 1. Water Stress Risk
        water_stress = RiskEngine._evaluate_water_stress(features, predictions.get("WATER_STRESS_INDEX_12M", 35.0))
        risks.append(water_stress)

        # 2. Vegetation Degradation Risk
        veg_degradation = RiskEngine._evaluate_vegetation_degradation(features, predictions.get("VEGETATION_DEGRADATION_RISK", 30.0))
        risks.append(veg_degradation)

        # 3. Soil Erosion & Sediment Detachment Risk
        soil_erosion = RiskEngine._evaluate_soil_erosion(features, predictions.get("LAND_CONDITION_DETERIORATION_24M", 35.0))
        risks.append(soil_erosion)

        return risks

    @staticmethod
    def _evaluate_water_stress(features: Dict[str, Any], pred_12m: float) -> RiskEvaluation:
        smi = features.get("latest_smi", 35.0)
        ndwi_slope = features.get("ndwi_slope", 0.0)
        smi_slope = features.get("smi_slope", 0.0)
        storage_per_ha = features.get("storage_per_ha", 0.08)

        # Multi-factor score
        score = round((100.0 - smi) * 0.4 + pred_12m * 0.4 - (ndwi_slope * 100.0) - (storage_per_ha * 50.0), 1)
        score = max(5.0, min(95.0, score))

        factors = []
        if smi < 30.0:
            factors.append(f"Root-zone soil moisture depressed at {smi:.1f}%")
        if ndwi_slope < 0:
            factors.append(f"Surface water retention contracting at {ndwi_slope:+.3f}/yr")
        if pred_12m > 45.0:
            factors.append(f"12M forward stress projection elevated at {pred_12m:.1f}/100")
        if storage_per_ha < 0.05:
            factors.append(f"Water harvesting storage low ({storage_per_ha:.3f} TCM/ha)")

        if score >= 65.0:
            level = "HIGH"
            driver = "Compound deficit in root-zone soil moisture and declining post-monsoon storage"
        elif score >= 40.0:
            level = "MEDIUM"
            driver = "Seasonal moisture fluctuation and moderate storage capacity"
        else:
            level = "LOW"
            driver = "Adequate surface water retention and resilient soil moisture levels"

        evidence = (
            f"Water stress evaluated at {score}/100 ({level}). "
            f"Evidence: {'; '.join(factors) if factors else 'Multi-seasonal indicators within stable thresholds.'} "
            f"Predicted 12M stress outlook: {pred_12m}/100."
        )

        return RiskEvaluation(
            risk_category="WATER_STRESS",
            risk_level=level,
            score=score,
            primary_driver=driver,
            evidence_summary=evidence,
            contributing_factors=factors or ["Stable soil moisture", "Adequate storage buffer"],
            spatial_hotspots={"zone": "Valley & Pediment Cultivated Zone", "severity": level}
        )

    @staticmethod
    def _evaluate_vegetation_degradation(features: Dict[str, Any], pred_veg: float) -> RiskEvaluation:
        ndvi = features.get("latest_ndvi", 0.55)
        ndvi_slope = features.get("ndvi_slope", 0.0)
        forest_pct = features.get("forest_veg_pct", 28.0)
        barren_pct = features.get("barren_pct", 18.0)

        score = round((1.0 - ndvi) * 50.0 + (pred_veg * 0.3) - (ndvi_slope * 120.0) + (barren_pct * 0.3), 1)
        score = max(5.0, min(95.0, score))

        factors = []
        if ndvi < 0.45:
            factors.append(f"Current mean canopy NDVI low at {ndvi:.2f}")
        if ndvi_slope < -0.005:
            factors.append(f"Vegetative vigor declining at {ndvi_slope:+.4f}/yr")
        if barren_pct > 20.0:
            factors.append(f"High barren scrubland exposure ({barren_pct:.1f}%)")
        if forest_pct < 20.0:
            factors.append(f"Protected forest canopy limited ({forest_pct:.1f}%)")

        if score >= 60.0:
            level = "HIGH"
            driver = "Sparse ridge canopy cover and vegetative biomass regression"
        elif score >= 35.0:
            level = "MEDIUM"
            driver = "Moderate canopy density with localized scrub vulnerability"
        else:
            level = "LOW"
            driver = "Robust vegetative vigor and continuous contour plantation coverage"

        evidence = (
            f"Vegetation degradation evaluated at {score}/100 ({level}). "
            f"Evidence: {'; '.join(factors) if factors else 'Vegetation canopy sustained by existing plantation treatments.'} "
            f"Forward degradation index: {pred_veg}/100."
        )

        return RiskEvaluation(
            risk_category="VEGETATION_DEGRADATION",
            risk_level=level,
            score=score,
            primary_driver=driver,
            evidence_summary=evidence,
            contributing_factors=factors or ["Stable vegetative canopy", "Adequate ridge coverage"],
            spatial_hotspots={"zone": "Upper Ridge & Scrub Escarpment", "severity": level}
        )

    @staticmethod
    def _evaluate_soil_erosion(features: Dict[str, Any], pred_land: float) -> RiskEvaluation:
        relief = features.get("relief_m", 130.0)
        drainage_density = features.get("drainage_density", 1.2)
        erosion_slope = features.get("erosion_slope", 0.0)
        barren_pct = features.get("barren_pct", 18.0)
        interventions_count = features.get("interventions_count", 3)

        score = round((relief / 10.0) * 1.8 + (drainage_density * 7.0) + (barren_pct * 0.4) - (interventions_count * 2.0), 1)
        score = max(5.0, min(95.0, score))

        factors = []
        if relief > 140.0:
            factors.append(f"High topographic relief ({relief:.1f} m)")
        if drainage_density > 1.0:
            factors.append(f"Dense stream scour network ({drainage_density:.2f} km/km²)")
        if barren_pct > 15.0:
            factors.append(f"Unprotected barren pediment ({barren_pct:.1f}%)")
        if erosion_slope > 0:
            factors.append(f"Erosion susceptibility expanding at {erosion_slope:+.3f}/yr")

        if score >= 60.0:
            level = "HIGH"
            driver = "High topographic relief and kinetic runoff detachment across upper scarps"
        elif score >= 35.0:
            level = "MEDIUM"
            driver = "Moderate gully development along second-order ephemeral streams"
        else:
            level = "LOW"
            driver = "Effective soil retention through contour bunds and stabilized stream banks"

        evidence = (
            f"Soil erosion evaluated at {score}/100 ({level}). "
            f"Evidence: {'; '.join(factors) if factors else 'Soil detachment rates controlled by existing treatment structures.'} "
            f"24M land deterioration projection: {pred_land}/100."
        )

        return RiskEvaluation(
            risk_category="SOIL_EROSION",
            risk_level=level,
            score=score,
            primary_driver=driver,
            evidence_summary=evidence,
            contributing_factors=factors or ["Controlled runoff velocity", "Adequate contour terracing"],
            spatial_hotspots={"zone": "Upper Slope Drainage Gully Network", "severity": level}
        )

    @staticmethod
    def calculate_overall_risk(risks: List[RiskEvaluation]) -> str:
        levels = [r.risk_level for r in risks]
        if "CRITICAL" in levels or levels.count("HIGH") >= 2:
            return "HIGH"
        elif "HIGH" in levels or levels.count("MEDIUM") >= 2:
            return "MEDIUM"
        else:
            return "LOW"
