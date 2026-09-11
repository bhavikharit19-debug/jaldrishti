"""
JalDrishti AI — Feature Engineering Pipeline
Prepares multi-temporal biophysical, land use, morphometric, and intervention
features from database indicators and GIS layers for predictive modeling and risk classification.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from sqlalchemy.orm import Session
from app.models.domain import Watershed, Indicator, IndicatorValue, GISLayer, Intervention
from app.services.gis_service import GISService
from app.data_pipeline.normalizer import DataNormalizer

class FeatureExtractor:
    """
    Extracts, normalizes, and structures input features for AI/ML modules.
    Designed so live satellite raster feeds (Sentinel-2, Landsat-9) can plug in seamlessly.
    """

    @staticmethod
    def extract_watershed_features(db: Session, watershed_id: int) -> Dict[str, Any]:
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed with ID {watershed_id} not found.")

        # 1. Fetch Indicators & Time Series
        indicators = db.query(Indicator).all()
        ind_map = {ind.id: ind.code for ind in indicators}
        
        all_values = db.query(IndicatorValue).filter(
            IndicatorValue.watershed_id == watershed_id
        ).order_by(IndicatorValue.recorded_year.asc()).all()

        years = sorted(list(set(v.recorded_year for v in all_values))) if all_values else []
        
        # Organize values by indicator code and year
        time_series: Dict[str, Dict[int, float]] = {
            "NDVI": {}, "NDWI": {}, "SMI": {}, "WATER_SPREAD": {}, "EROSION_INDEX": {}
        }
        for v in all_values:
            code = ind_map.get(v.indicator_id, "UNKNOWN")
            if code in time_series:
                time_series[code][v.recorded_year] = v.value

        # Calculate latest values & linear trends (slopes per year)
        latest_vals = {}
        slopes = {}
        for code, yearly_data in time_series.items():
            if yearly_data:
                sorted_yrs = sorted(yearly_data.keys())
                latest_vals[code] = yearly_data[sorted_yrs[-1]]
                if len(sorted_yrs) >= 2:
                    X = np.array(sorted_yrs) - sorted_yrs[0]
                    Y = np.array([yearly_data[y] for y in sorted_yrs])
                    # Linear regression slope: (N*sum(xy) - sum(x)*sum(y)) / (N*sum(x^2) - (sum(x))^2)
                    denom = len(X) * np.sum(X**2) - (np.sum(X))**2
                    if denom != 0:
                        slope = (len(X) * np.sum(X * Y) - np.sum(X) * np.sum(Y)) / denom
                        slopes[code] = round(float(slope), 4)
                    else:
                        slopes[code] = 0.0
                else:
                    slopes[code] = 0.0
            else:
                # Default baseline fallbacks
                defaults = {"NDVI": 0.52, "NDWI": 0.22, "SMI": 30.0, "WATER_SPREAD": 15.0, "EROSION_INDEX": 4.5}
                latest_vals[code] = defaults.get(code, 0.5)
                slopes[code] = 0.0

        # Yearly average health score trajectory
        yearly_health_scores = []
        for y in years:
            yr_scores = [v.normalized_score for v in all_values if v.recorded_year == y]
            avg_score = sum(yr_scores) / len(yr_scores) if yr_scores else 65.0
            yearly_health_scores.append(round(avg_score, 1))

        # 2. Topographic and Morphometric Features from GIS Layers
        gis_stats = None
        try:
            gis_stats = GISService.calculate_watershed_gis_stats(db, watershed_id)
        except Exception:
            pass

        # LULC proportions
        lulc_proportions = {
            "forest_veg_pct": 28.0,
            "agriculture_pct": 42.0,
            "barren_pct": 18.0,
            "builtup_pct": 7.0,
            "water_pct": 5.0
        }
        if gis_stats and gis_stats.lulc:
            for item in gis_stats.lulc:
                cat_lower = item.category.lower()
                if "forest" in cat_lower or "vegetation" in cat_lower:
                    lulc_proportions["forest_veg_pct"] = item.percentage
                elif "agri" in cat_lower:
                    lulc_proportions["agriculture_pct"] = item.percentage
                elif "barren" in cat_lower or "open" in cat_lower:
                    lulc_proportions["barren_pct"] = item.percentage
                elif "built" in cat_lower:
                    lulc_proportions["builtup_pct"] = item.percentage
                elif "water" in cat_lower:
                    lulc_proportions["water_pct"] = item.percentage

        # Check if imported LULC layer exists to override baseline
        imported_lulc_layer = db.query(GISLayer).filter(
            GISLayer.watershed_id == watershed_id,
            GISLayer.layer_type == "LULC",
            GISLayer.source_type == "FIELD_UPLOAD"
        ).first()
        if imported_lulc_layer and imported_lulc_layer.data_payload:
            imp_props = DataNormalizer.extract_imported_lulc_proportions(
                imported_lulc_layer.data_payload, ws.area_hectares or 1000.0
            )
            if imp_props:
                lulc_proportions.update(imp_props)

        # Topography & Drainage
        relief_m = gis_stats.elevation.relief_m if (gis_stats and gis_stats.elevation) else 135.0
        drainage_density = gis_stats.drainage.density_km_per_sqkm if (gis_stats and gis_stats.drainage) else 1.2
        water_storage_capacity_tcm = gis_stats.water_bodies.cumulative_capacity_tcm if (gis_stats and gis_stats.water_bodies) else 80.0

        # 3. Interventions
        interventions = db.query(Intervention).filter(Intervention.watershed_id == watershed_id).all()
        interventions_count = len(interventions)
        storage_per_ha = round(water_storage_capacity_tcm / (ws.area_hectares or 1000.0), 3)

        # Dynamic Provenance Evaluation
        prov_summary = DataNormalizer.get_watershed_provenance_summary(db, watershed_id)
        provenance = prov_summary.get("overall_provenance", "DEMO DATA — Calibrated historical indicators (2018–2024)")

        return {
            "watershed_id": ws.id,
            "watershed_name": ws.name,
            "watershed_code": ws.code,
            "area_hectares": ws.area_hectares,
            "recorded_years": years,
            "latest_ndvi": latest_vals["NDVI"],
            "latest_ndwi": latest_vals["NDWI"],
            "latest_smi": latest_vals["SMI"],
            "latest_water_spread_ha": latest_vals["WATER_SPREAD"],
            "latest_erosion_index": latest_vals["EROSION_INDEX"],
            "ndvi_slope": slopes["NDVI"],
            "ndwi_slope": slopes["NDWI"],
            "smi_slope": slopes["SMI"],
            "water_spread_slope": slopes["WATER_SPREAD"],
            "erosion_slope": slopes["EROSION_INDEX"],
            "yearly_health_scores": yearly_health_scores,
            "forest_veg_pct": lulc_proportions["forest_veg_pct"],
            "agriculture_pct": lulc_proportions["agriculture_pct"],
            "barren_pct": lulc_proportions["barren_pct"],
            "builtup_pct": lulc_proportions["builtup_pct"],
            "water_pct": lulc_proportions["water_pct"],
            "relief_m": relief_m,
            "drainage_density": drainage_density,
            "water_storage_capacity_tcm": water_storage_capacity_tcm,
            "interventions_count": interventions_count,
            "storage_per_ha": storage_per_ha,
            "data_provenance": provenance
        }
