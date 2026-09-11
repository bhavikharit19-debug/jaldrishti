"""
JalDrishti AI — Data Normalizer & Pipeline Bridge
Aggregates imported vector/raster and tabular datasets into normalized biophysical metrics
for transparent consumption by Step 4 ML feature extraction without interface modifications.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.domain import GISLayer, IndicatorValue, Indicator, FieldPhoto, Watershed

class DataNormalizer:
    @staticmethod
    def get_watershed_provenance_summary(db: Session, watershed_id: int) -> Dict[str, Any]:
        """
        Calculates the active data provenance breakdown for a watershed across all layers and metrics.
        Returns: { 'overall_provenance': str, 'has_imported_data': bool, 'imported_layers_count': int, 'imported_records_count': int }
        """
        imported_layers = db.query(GISLayer).filter(
            GISLayer.watershed_id == watershed_id,
            GISLayer.source_type == "FIELD_UPLOAD"
        ).count()

        imported_indicators = db.query(IndicatorValue).filter(
            IndicatorValue.watershed_id == watershed_id,
            IndicatorValue.source_type == "IMPORTED"
        ).count()

        imported_photos = db.query(FieldPhoto).filter(
            FieldPhoto.watershed_id == watershed_id,
            FieldPhoto.provenance == "IMPORTED_DATA"
        ).count()

        has_imported = (imported_layers > 0 or imported_indicators > 0 or imported_photos > 0)
        
        if not has_imported:
            provenance = "DEMO DATA (Calibrated baseline trajectories)"
        elif imported_layers >= 3 and imported_indicators >= 5:
            provenance = "IMPORTED DATA (Primary field & vector survey)"
        else:
            provenance = "DEMO DATA / HYBRID (Calibrated baseline + Real imported data)"

        return {
            "overall_provenance": provenance,
            "has_imported_data": has_imported,
            "imported_layers_count": imported_layers,
            "imported_indicators_count": imported_indicators,
            "imported_photos_count": imported_photos
        }

    @staticmethod
    def extract_imported_lulc_proportions(layer_payload: Dict[str, Any], total_area_ha: float) -> Optional[Dict[str, float]]:
        """
        Normalizes arbitrary imported GeoJSON LULC polygon features into the canonical 5 classes.
        """
        if not layer_payload or layer_payload.get("type") != "FeatureCollection":
            return None

        features = layer_payload.get("features", [])
        if not features:
            return None

        class_sums = {
            "forest_veg_pct": 0.0,
            "agriculture_pct": 0.0,
            "barren_pct": 0.0,
            "builtup_pct": 0.0,
            "water_pct": 0.0
        }

        total_computed_area = 0.0
        class_areas = {k: 0.0 for k in class_sums}

        for f in features:
            props = f.get("properties") or {}
            c_name = str(props.get("class") or props.get("category") or props.get("lulc_class") or "").lower()
            area = float(props.get("area_ha") or props.get("area") or 10.0)
            total_computed_area += area

            if any(w in c_name for w in ["forest", "tree", "vegetation", "plantation", "canopy", "woods"]):
                class_areas["forest_veg_pct"] += area
            elif any(w in c_name for w in ["agri", "crop", "farm", "cultivat"]):
                class_areas["agriculture_pct"] += area
            elif any(w in c_name for w in ["barren", "waste", "scrub", "rock", "fallow", "open"]):
                class_areas["barren_pct"] += area
            elif any(w in c_name for w in ["built", "urban", "settlement", "road", "house"]):
                class_areas["builtup_pct"] += area
            elif any(w in c_name for w in ["water", "pond", "reservoir", "lake", "stream", "river"]):
                class_areas["water_pct"] += area
            else:
                class_areas["barren_pct"] += area

        if total_computed_area > 0:
            for k in class_sums:
                class_sums[k] = round((class_areas[k] / total_computed_area) * 100.0, 1)
            return class_sums

        return None
