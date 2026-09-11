from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.domain import GISLayer, Watershed, WatershedBoundary, Intervention, FieldPhoto
from app.schemas.schemas import (
    GISLayerResponse,
    GISLayerSummary,
    WatershedGISStatsResponse,
    LULCCategoryStat,
    DrainageStat,
    WaterBodyStat,
    VegetationStat,
    ElevationStat,
    ElevationBandStat
)

class GISService:
    @staticmethod
    def get_layers_for_watershed(
        db: Session, 
        watershed_id: int, 
        layer_type: Optional[str] = None
    ) -> List[GISLayerResponse]:
        query = db.query(GISLayer).filter(
            GISLayer.watershed_id == watershed_id,
            GISLayer.is_active == True
        )
        if layer_type:
            query = query.filter(GISLayer.layer_type == layer_type.upper())
            
        layers = query.all()
        return [GISLayerResponse.model_validate(l) for l in layers]

    @staticmethod
    def get_layers_summary(
        db: Session,
        watershed_id: Optional[int] = None,
        layer_type: Optional[str] = None
    ) -> List[GISLayerSummary]:
        """Returns lightweight metadata summaries of GIS layers without transmitting large GeoJSON payloads."""
        query = db.query(GISLayer).filter(GISLayer.is_active == True)
        if watershed_id:
            query = query.filter(GISLayer.watershed_id == watershed_id)
        if layer_type:
            query = query.filter(GISLayer.layer_type == layer_type.upper())
        layers = query.all()
        result = []
        for l in layers:
            cnt = 0
            if l.data_payload and isinstance(l.data_payload, dict):
                cnt = len(l.data_payload.get("features", []))
            result.append(GISLayerSummary(
                id=l.id,
                watershed_id=l.watershed_id,
                layer_type=l.layer_type,
                name=l.name,
                format=l.format,
                feature_count=cnt,
                is_active=l.is_active,
                source_type=l.source_type
            ))
        return result

    @staticmethod
    def get_single_layer(db: Session, watershed_id: int, layer_type: str) -> Optional[GISLayerResponse]:
        """Retrieves specific GIS layer for a watershed."""
        layer = db.query(GISLayer).filter(
            GISLayer.watershed_id == watershed_id,
            GISLayer.layer_type == layer_type.upper(),
            GISLayer.is_active == True
        ).first()
        if not layer:
            return None
        return GISLayerResponse.model_validate(layer)

    @staticmethod
    def get_watershed_boundary_layer(db: Session, watershed_id: int) -> Optional[dict]:
        boundary = db.query(WatershedBoundary).filter(WatershedBoundary.watershed_id == watershed_id).first()
        if not boundary:
            return None
            
        return {
            "type": "Feature",
            "geometry": boundary.geometry,
            "properties": {
                "watershed_id": boundary.watershed_id,
                "centroid_lat": boundary.centroid_lat,
                "centroid_lng": boundary.centroid_lng,
                "bbox": boundary.bbox
            }
        }

    @staticmethod
    def calculate_watershed_gis_stats(db: Session, watershed_id: int) -> WatershedGISStatsResponse:
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed {watershed_id} not found")

        layers = db.query(GISLayer).filter(
            GISLayer.watershed_id == watershed_id,
            GISLayer.is_active == True
        ).all()

        layer_map = {l.layer_type: l for l in layers}
        total_area = ws.area_hectares or 1000.0

        # 1. LULC Statistics
        lulc_layer = layer_map.get("LULC")
        lulc_stats: List[LULCCategoryStat] = []
        if lulc_layer and lulc_layer.data_payload:
            features = lulc_layer.data_payload.get("features", [])
            for feat in features:
                props = feat.get("properties", {})
                area = float(props.get("area_ha", 0))
                pct = round((area / total_area) * 100, 1) if total_area > 0 else 0.0
                lulc_stats.append(LULCCategoryStat(
                    category=props.get("class", "Unclassified"),
                    area_ha=round(area, 1),
                    percentage=pct,
                    color=props.get("color", "#9e9e9e"),
                    description=props.get("description")
                ))

        if not lulc_stats:
            # Fallback baseline breakdown
            lulc_stats = [
                LULCCategoryStat(category="Agriculture", area_ha=round(total_area * 0.45, 1), percentage=45.0, color="#8bc34a", description="Cultivated Kharif/Rabi cropland"),
                LULCCategoryStat(category="Forest/Vegetation", area_ha=round(total_area * 0.28, 1), percentage=28.0, color="#2e7d32", description="Ridge afforestation and scrub canopy"),
                LULCCategoryStat(category="Water", area_ha=round(total_area * 0.05, 1), percentage=5.0, color="#0284c7", description="Percolation tanks and farm ponds"),
                LULCCategoryStat(category="Built-up", area_ha=round(total_area * 0.07, 1), percentage=7.0, color="#ff7043", description="Village settlement and roads"),
                LULCCategoryStat(category="Barren/Open Land", area_ha=round(total_area * 0.15, 1), percentage=15.0, color="#d4e157", description="Gravelly slopes and open pastures"),
            ]

        # 2. Drainage Statistics
        drainage_layer = layer_map.get("DRAINAGE")
        total_stream_len = 0.0
        order_counts: Dict[str, int] = {"Order 1": 0, "Order 2": 0, "Order 3": 0}
        total_streams = 0
        primary_stream = ws.primary_drainage or "Dendritic ephemeral drainage"

        if drainage_layer and drainage_layer.data_payload:
            features = drainage_layer.data_payload.get("features", [])
            total_streams = len(features)
            for feat in features:
                props = feat.get("properties", {})
                length = float(props.get("length_km", 0))
                order = props.get("order", 1)
                total_stream_len += length
                key = f"Order {order}"
                order_counts[key] = order_counts.get(key, 0) + 1
            if features:
                primary_stream = features[0].get("properties", {}).get("name", primary_stream)

        area_sqkm = total_area / 100.0
        drainage_density = round(total_stream_len / area_sqkm, 2) if area_sqkm > 0 else 1.8

        drainage_stat = DrainageStat(
            total_length_km=round(total_stream_len, 2),
            density_km_per_sqkm=drainage_density,
            order_counts=order_counts,
            primary_stream=primary_stream,
            total_streams=total_streams
        )

        # 3. Water Bodies Statistics
        wb_layer = layer_map.get("WATER_BODIES")
        wb_count = 0
        wb_spread = 0.0
        wb_capacity = 0.0
        wb_types: Dict[str, int] = {}

        if wb_layer and wb_layer.data_payload:
            features = wb_layer.data_payload.get("features", [])
            wb_count = len(features)
            for feat in features:
                props = feat.get("properties", {})
                wb_spread += float(props.get("spread_area_ha", 0))
                wb_capacity += float(props.get("capacity_tcm", 0))
                st_type = props.get("type", "Water Body")
                wb_types[st_type] = wb_types.get(st_type, 0) + 1

        if wb_spread == 0:
            # Calibrated estimation if not explicit
            wb_spread = round(total_area * 0.045, 1)
            wb_capacity = round(wb_spread * 1.8, 1)

        wb_stat = WaterBodyStat(
            total_count=wb_count if wb_count > 0 else 3,
            total_spread_ha=round(wb_spread, 1),
            cumulative_capacity_tcm=round(wb_capacity, 1),
            structures_by_type=wb_types if wb_types else {"Percolation Tank": 1, "Check Dam Reservoir": 2}
        )

        # 4. Vegetation / NDVI Statistics
        veg_layer = layer_map.get("VEGETATION_NDVI")
        mean_ndvi = 0.52
        dense_pct = 26.0
        mod_pct = 42.0
        low_pct = 22.0
        sparse_pct = 10.0

        if veg_layer and veg_layer.metadata_json:
            meta = veg_layer.metadata_json
            mean_ndvi = float(meta.get("mean_ndvi", mean_ndvi))
            dense_pct = float(meta.get("dense_canopy_pct", dense_pct))
            mod_pct = float(meta.get("moderate_canopy_pct", mod_pct))
            low_pct = float(meta.get("low_canopy_pct", low_pct))
            sparse_pct = float(meta.get("sparse_canopy_pct", sparse_pct))

        veg_stat = VegetationStat(
            mean_ndvi=round(mean_ndvi, 2),
            dense_pct=round(dense_pct, 1),
            moderate_pct=round(mod_pct, 1),
            low_pct=round(low_pct, 1),
            sparse_pct=round(sparse_pct, 1),
            vigor_class="Moderately High Biomass" if mean_ndvi >= 0.5 else ("Moderate Vigor" if mean_ndvi >= 0.4 else "Sparse Canopy")
        )

        # 5. Elevation Statistics
        elev_layer = layer_map.get("ELEVATION")
        min_elev = 580.0
        max_elev = 715.0
        dominant_slope = "Gently Sloping (3-8%)"
        bands: List[ElevationBandStat] = []

        if elev_layer and elev_layer.metadata_json:
            meta = elev_layer.metadata_json
            min_elev = float(meta.get("min_elevation_m", min_elev))
            max_elev = float(meta.get("max_elevation_m", max_elev))
            dominant_slope = meta.get("dominant_slope_class", dominant_slope)
            raw_bands = meta.get("elevation_bands", [])
            for b in raw_bands:
                bands.append(ElevationBandStat(
                    band_name=b.get("name", "Zone"),
                    elevation_range_m=b.get("range", ""),
                    area_ha=float(b.get("area_ha", 0)),
                    percentage=float(b.get("pct", 0)),
                    slope_class=b.get("slope", "3-8%"),
                    color=b.get("color", "#a1887f")
                ))

        if not bands:
            relief = max_elev - min_elev
            bands = [
                ElevationBandStat(band_name="Ridge & Hill Top", elevation_range_m=f"{int(max_elev - relief*0.25)}-{int(max_elev)} m", area_ha=round(total_area*0.22, 1), percentage=22.0, slope_class="Steep (15-25%)", color="#5d4037"),
                ElevationBandStat(band_name="Upper Sloping Foot-hills", elevation_range_m=f"{int(max_elev - relief*0.55)}-{int(max_elev - relief*0.25)} m", area_ha=round(total_area*0.35, 1), percentage=35.0, slope_class="Moderately Sloping (8-15%)", color="#8d6e63"),
                ElevationBandStat(band_name="Pediment & Agriculture Plain", elevation_range_m=f"{int(min_elev + relief*0.15)}-{int(max_elev - relief*0.55)} m", area_ha=round(total_area*0.33, 1), percentage=33.0, slope_class="Gently Sloping (3-8%)", color="#bcaaa4"),
                ElevationBandStat(band_name="Valley Floor & Stream Bed", elevation_range_m=f"{int(min_elev)}-{int(min_elev + relief*0.15)} m", area_ha=round(total_area*0.10, 1), percentage=10.0, slope_class="Nearly Level (1-3%)", color="#d7ccc8")
            ]

        elev_stat = ElevationStat(
            min_elevation_m=round(min_elev, 1),
            max_elevation_m=round(max_elev, 1),
            relief_m=round(max_elev - min_elev, 1),
            dominant_slope_class=dominant_slope,
            elevation_bands=bands
        )

        # 6. Interventions & Photos count
        intv_count = db.query(Intervention).filter(Intervention.watershed_id == watershed_id).count()
        photos_count = db.query(FieldPhoto).filter(FieldPhoto.watershed_id == watershed_id).count()

        return WatershedGISStatsResponse(
            watershed_id=ws.id,
            watershed_name=ws.name,
            watershed_code=ws.code,
            total_area_ha=round(total_area, 1),
            lulc=lulc_stats,
            drainage=drainage_stat,
            water_bodies=wb_stat,
            vegetation=veg_stat,
            elevation=elev_stat,
            interventions_count=intv_count,
            field_photos_count=photos_count,
            data_provenance="DEMO DATA",
            disclaimer="DEMO DATA: Baseline thematic layers and metrics calibrated for SIH 26015 decision-support prototyping."
        )
