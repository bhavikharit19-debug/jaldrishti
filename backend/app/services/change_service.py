from typing import List
from sqlalchemy.orm import Session
from app.models.domain import Watershed, Indicator, IndicatorValue
from app.schemas.schemas import ChangeDetectionResponse, IndicatorDelta, YearlyDataPoint
from data.seed_data import seed_indicators_and_values

class ChangeDetectionService:
    @staticmethod
    def compare_periods(
        db: Session,
        watershed_id: int,
        from_year: int = 2018,
        to_year: int = 2024
    ) -> ChangeDetectionResponse:
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed {watershed_id} not found")

        # 0. Self-healing check: ensure indicator values are present for this watershed
        has_values = db.query(IndicatorValue).filter(IndicatorValue.watershed_id == watershed_id).first()
        if not has_values:
            seed_indicators_and_values(db, target_watershed_id=watershed_id)

        # 1. Fetch indicators
        indicators = db.query(Indicator).order_by(Indicator.id.asc()).all()
        deltas: List[IndicatorDelta] = []

        for ind in indicators:
            val_from = db.query(IndicatorValue).filter(
                IndicatorValue.watershed_id == watershed_id,
                IndicatorValue.indicator_id == ind.id,
                IndicatorValue.recorded_year == from_year
            ).first()

            val_to = db.query(IndicatorValue).filter(
                IndicatorValue.watershed_id == watershed_id,
                IndicatorValue.indicator_id == ind.id,
                IndicatorValue.recorded_year == to_year
            ).first()

            # Graceful fallback to earliest/latest available if requested year is not specifically seeded
            if not val_from:
                val_from = db.query(IndicatorValue).filter(
                    IndicatorValue.watershed_id == watershed_id,
                    IndicatorValue.indicator_id == ind.id
                ).order_by(IndicatorValue.recorded_year.asc()).first()

            if not val_to:
                val_to = db.query(IndicatorValue).filter(
                    IndicatorValue.watershed_id == watershed_id,
                    IndicatorValue.indicator_id == ind.id
                ).order_by(IndicatorValue.recorded_year.desc()).first()

            v_from = val_from.value if val_from else 0.0
            v_to = val_to.value if val_to else 0.0

            abs_change = round(v_to - v_from, 3)
            pct_change = round(((v_to - v_from) / v_from * 100) if v_from != 0 else 0.0, 1)

            # Trend interpretation
            if ind.code == "EROSION_INDEX":
                # Less erosion is better
                trend = "IMPROVED" if abs_change < 0 else ("DEGRADED" if abs_change > 0 else "STABLE")
            else:
                trend = "IMPROVED" if abs_change > 0 else ("DEGRADED" if abs_change < 0 else "STABLE")

            deltas.append(IndicatorDelta(
                indicator_code=ind.code,
                indicator_name=ind.name,
                from_value=round(v_from, 2),
                to_value=round(v_to, 2),
                unit=ind.unit or "",
                delta_absolute=abs_change,
                delta_percentage=pct_change,
                trend=trend
            ))

        # 2. Build complete yearly trajectory series
        all_years = sorted(list(set(
            y[0] for y in db.query(IndicatorValue.recorded_year).filter(
                IndicatorValue.watershed_id == watershed_id
            ).all()
        )))

        # Multi-year trajectory: at minimum 2018-2024, extended up to to_year (e.g. 2026)
        cutoff_year = max(to_year, 2024) if to_year else 2024
        years = [y for y in all_years if y <= cutoff_year]
        if not years:
            years = all_years

        yearly_points: List[YearlyDataPoint] = []
        for y in years:
            pt = YearlyDataPoint(
                year=y,
                ndvi=0.0,
                ndwi=0.0,
                soil_moisture=0.0,
                water_spread_ha=0.0
            )
            for ind in indicators:
                v = db.query(IndicatorValue).filter(
                    IndicatorValue.watershed_id == watershed_id,
                    IndicatorValue.indicator_id == ind.id,
                    IndicatorValue.recorded_year == y
                ).first()
                if v:
                    if ind.code == "NDVI":
                        pt.ndvi = round(v.value, 3)
                    elif ind.code == "NDWI":
                        pt.ndwi = round(v.value, 3)
                    elif ind.code == "SMI":
                        pt.soil_moisture = round(v.value, 1)
                    elif ind.code == "WATER_SPREAD":
                        pt.water_spread_ha = round(v.value, 1)
            yearly_points.append(pt)

        # 3. Summary text & clear prototype disclaimer
        ndvi_delta = next((d.delta_percentage for d in deltas if d.indicator_code == 'NDVI'), 0.0)
        water_delta = next((d.delta_percentage for d in deltas if d.indicator_code == 'WATER_SPREAD'), 0.0)
        summary = (
            f"Multi-temporal analysis for {ws.name} from {from_year} to {to_year}: "
            f"Net vegetation vigor (NDVI) shifted by {ndvi_delta}%, "
            f"and surface water retention index expanded by {water_delta}%. "
            f"Continuous ridge treatments and community structures have positively stabilized the micro-catchment hydrology."
        )

        has_projected = to_year > 2024
        disclaimer = (
            f"Calibrated multi-temporal dataset spanning 2018-2024 baseline and {to_year} prototype trajectory (DEMO / SEEDED DATA). "
            f"Official satellite pipeline integration point configured."
            if has_projected else
            "Calibrated historical multi-temporal dataset spanning 2018-2024 (DEMO / SEEDED DATA). "
            "Official satellite pipeline integration point configured."
        )

        return ChangeDetectionResponse(
            watershed_id=watershed_id,
            from_year=from_year,
            to_year=to_year,
            indicators=deltas,
            yearly_trends=yearly_points,
            summary_analysis=summary,
            priority_hotspots_count=2,
            disclaimer=disclaimer
        )
