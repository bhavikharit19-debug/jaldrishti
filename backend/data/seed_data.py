import datetime
import json
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from app.models.domain import (
    State, District, Watershed, WatershedBoundary, DataSource,
    GISLayer, FieldPhoto, Observation, Indicator, IndicatorValue,
    Prediction, RiskAssessment, Recommendation, Intervention,
    Alert, AuditLog, GeospatialDataset, User, AccessRequest
)

def seed_database(db: Session, force_refresh: bool = False):
    # Check if already seeded with Phase 2 layers
    existing_veg = db.query(GISLayer).filter(GISLayer.layer_type == "VEGETATION_NDVI").first()
    if existing_veg and not force_refresh:
        print("Database already contains Phase 2 GIS layers.")
        # Ensure indicators and yearly values are seeded even if GIS layers already exist
        seed_indicators_and_values(db)
        return

    # If watersheds exist but Phase 2 layers are missing, remove old layers to reseed cleanly
    existing_ws = db.query(Watershed).first()
    if existing_ws:
        print("Upgrading database to Phase 2: GIS Intelligence & Geospatial Data Layers...")
        db.query(GISLayer).delete()
        db.commit()
    else:
        print("Seeding JalDrishti AI database with full multi-watershed geospatial dataset...")

    # 1. States & Districts
    mh = db.query(State).filter(State.code == "MH").first()
    if not mh:
        mh = State(code="MH", name="Maharashtra")
        db.add(mh)
        db.flush()

    rj = db.query(State).filter(State.code == "RJ").first()
    if not rj:
        rj = State(code="RJ", name="Rajasthan")
        db.add(rj)
        db.flush()

    ahmednagar = db.query(District).filter(District.code == "MH-AHM").first()
    if not ahmednagar:
        ahmednagar = District(name="Ahmednagar", code="MH-AHM", state_id=mh.id)
        db.add(ahmednagar)
        db.flush()

    alwar = db.query(District).filter(District.code == "RJ-ALW").first()
    if not alwar:
        alwar = District(name="Alwar", code="RJ-ALW", state_id=rj.id)
        db.add(alwar)
        db.flush()

    # 2. Indicators Definition
    if not db.query(Indicator).first():
        ind_ndvi = Indicator(
            code="NDVI",
            name="Normalized Difference Vegetation Index",
            category="VEGETATION",
            unit="Index (-0.2 to 1.0)",
            description="Vegetation vigor and biomass canopy density derived from optical satellite bands.",
            weight_in_health_score=0.25
        )
        ind_ndwi = Indicator(
            code="NDWI",
            name="Normalized Difference Water Index",
            category="HYDROLOGICAL",
            unit="Index (-1.0 to 1.0)",
            description="Surface water presence and leaf water content.",
            weight_in_health_score=0.25
        )
        ind_smi = Indicator(
            code="SMI",
            name="Soil Moisture Index",
            category="HYDROLOGICAL",
            unit="Percentage (%)",
            description="Estimated root-zone moisture level from satellite microwave/optical thermal indices.",
            weight_in_health_score=0.20
        )
        ind_water_spread = Indicator(
            code="WATER_SPREAD",
            name="Surface Water Spread Area",
            category="HYDROLOGICAL",
            unit="Hectares (ha)",
            description="Total surface water spread across water retention structures and ponds.",
            weight_in_health_score=0.15
        )
        ind_erosion = Indicator(
            code="EROSION_INDEX",
            name="Soil Loss Susceptibility",
            category="LAND_CONDITION",
            unit="Index (0 to 10)",
            description="Soil degradation and sediment detachment propensity based on slope and cover.",
            weight_in_health_score=0.15
        )
        db.add_all([ind_ndvi, ind_ndwi, ind_smi, ind_water_spread, ind_erosion])
        db.flush()

    # 3. Data Sources
    if not db.query(DataSource).first():
        src_demo = DataSource(
            code="DEMO-BASELINE-2024",
            name="JalDrishti Calibrated Baseline Seed",
            source_type="DEMO DATA",
            provider_name="JalDrishti AI Geospatial Laboratory",
            description="Pre-calibrated benchmark spatial indicators and boundaries for SIH 26015 decision-support prototyping.",
            reliability_score=0.98
        )
        src_bhuvan = DataSource(
            code="ISRO-BHUVAN-API",
            name="ISRO Bhuvan Watershed Spatial Layer",
            source_type="OFFICIAL DATA",
            provider_name="National Remote Sensing Centre (NRSC / ISRO)",
            description="Official micro-watershed boundaries and LULC datasets (Planned API adapter).",
            reliability_score=0.99
        )
        db.add_all([src_demo, src_bhuvan])
        db.flush()

    # ==========================================
    # WATERSHED 1: Hiware Bazar (Ahmednagar, MH)
    # ==========================================
    ws_hiware = db.query(Watershed).filter(Watershed.code == "WS-MH-AHM-001").first()
    if not ws_hiware:
        ws_hiware = Watershed(
            code="WS-MH-AHM-001",
            name="Hiware Bazar Model Micro-Watershed",
            district_id=ahmednagar.id,
            state_id=mh.id,
            area_hectares=976.0,
            river_basin="Krishna-Godavari Inter-basin",
            sub_basin="Kukadi Sub-basin",
            agro_climatic_zone="Scarcity Zone of Maharashtra (Rain-shadow Western Ghats)",
            primary_drainage="Ephemeral dendritic stream network draining eastwards",
            health_score=82.5,
            risk_level="LOW",
            status="ACTIVE"
        )
        db.add(ws_hiware)
        db.flush()

        hb_coords = [
            [74.582, 19.035],
            [74.595, 19.028],
            [74.620, 19.034],
            [74.632, 19.052],
            [74.625, 19.068],
            [74.601, 19.065],
            [74.586, 19.055],
            [74.582, 19.035]
        ]
        db.add(WatershedBoundary(
            watershed_id=ws_hiware.id,
            geometry={"type": "Polygon", "coordinates": [hb_coords]},
            centroid_lat=19.048,
            centroid_lng=74.605,
            bbox=[74.582, 19.028, 74.632, 19.068]
        ))

    # --- Phase 2 GIS Layers for Hiware Bazar ---
    # 1. Drainage Network
    hb_drainage = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Main Nala", "order": 3, "length_km": 4.2, "flow_direction": "Eastwards", "gradient": "1.2%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[74.588, 19.061], [74.596, 19.052], [74.605, 19.046], [74.618, 19.039]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "North Ridge Tributary", "order": 2, "length_km": 2.1, "flow_direction": "South-East", "gradient": "3.5%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[74.612, 19.064], [74.608, 19.053], [74.605, 19.046]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "South Upper Gully", "order": 1, "length_km": 1.4, "flow_direction": "North-East", "gradient": "4.8%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[74.591, 19.032], [74.598, 19.040], [74.605, 19.046]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "West Ridge Drainage", "order": 1, "length_km": 1.1, "flow_direction": "South-East", "gradient": "5.1%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[74.585, 19.055], [74.592, 19.052], [74.596, 19.052]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_hiware.id,
        layer_type="DRAINAGE",
        name="Drainage & Stream Network",
        format="GEOJSON",
        data_payload=hb_drainage,
        metadata_json={"stream_orders": [1, 2, 3], "total_streams": 4, "total_length_km": 8.8, "drainage_density_km_sqkm": 0.90}
    ))

    # 2. Water Bodies
    hb_water = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Central Percolation Tank", "type": "Percolation Tank", "capacity_tcm": 45.0, "spread_area_ha": 4.8, "max_depth_m": 4.2, "status": "Operational"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.604, 19.045], [74.608, 19.045], [74.609, 19.048], [74.603, 19.048], [74.604, 19.045]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Village Bandhara Pond", "type": "Check Dam Reservoir", "capacity_tcm": 20.0, "spread_area_ha": 2.2, "max_depth_m": 2.8, "status": "Operational"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.615, 19.040], [74.619, 19.039], [74.618, 19.042], [74.614, 19.042], [74.615, 19.040]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Community Farm Pond Cluster", "type": "Farm Pond", "capacity_tcm": 15.0, "spread_area_ha": 1.6, "max_depth_m": 3.0, "status": "Operational"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.597, 19.042], [74.600, 19.042], [74.600, 19.044], [74.597, 19.044], [74.597, 19.042]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_hiware.id,
        layer_type="WATER_BODIES",
        name="Surface Water Bodies & Reservoirs",
        format="GEOJSON",
        data_payload=hb_water,
        metadata_json={"total_structures": 3, "total_spread_ha": 8.6, "cumulative_capacity_tcm": 80.0}
    ))

    # 3. LULC (All 5 Categories: Agriculture, Forest/Vegetation, Water, Built-up, Barren/Open Land)
    hb_lulc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"class": "Forest/Vegetation", "color": "#2e7d32", "area_ha": 275.0, "description": "Continuous contour plantation and protected social forestry on ridge"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.585, 19.055], [74.601, 19.065], [74.625, 19.068], [74.615, 19.058], [74.585, 19.055]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Agriculture", "color": "#8bc34a", "area_ha": 420.0, "description": "Irrigated multi-crop agricultural plots (Onion, Gram, Jowar)"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.595, 19.040], [74.615, 19.045], [74.622, 19.036], [74.602, 19.032], [74.595, 19.040]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Barren/Open Land", "color": "#d4e157", "area_ha": 168.0, "description": "Rocky scrubland with contour bunding and trenches"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.582, 19.035], [74.595, 19.028], [74.602, 19.032], [74.586, 19.045], [74.582, 19.035]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Built-up", "color": "#ff7043", "area_ha": 68.0, "description": "Gram Panchayat settlement, farm houses, and road network"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.600, 19.047], [74.604, 19.047], [74.604, 19.051], [74.600, 19.051], [74.600, 19.047]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Water", "color": "#0284c7", "area_ha": 45.0, "description": "Inundated reservoirs, percolation basins, and streams"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.603, 19.045], [74.609, 19.045], [74.609, 19.048], [74.603, 19.048], [74.603, 19.045]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_hiware.id,
        layer_type="LULC",
        name="Land Use / Land Cover (LULC)",
        format="GEOJSON",
        data_payload=hb_lulc,
        metadata_json={"classification_standard": "NRSC / LISS-IV 5-Class Standard", "total_area_ha": 976.0}
    ))

    # 4. Vegetation / NDVI Layer
    hb_ndvi = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Dense Canopy (>0.6)", "mean_ndvi": 0.68, "area_ha": 312.0, "color": "#1b5e20", "status": "Thriving Vegetation"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.588, 19.057], [74.602, 19.064], [74.622, 19.066], [74.612, 19.057], [74.588, 19.057]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Moderate Canopy (0.4-0.6)", "mean_ndvi": 0.52, "area_ha": 448.0, "color": "#4caf50", "status": "Productive Cropland"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.595, 19.038], [74.618, 19.044], [74.624, 19.035], [74.598, 19.030], [74.595, 19.038]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Low / Scrub (0.2-0.4)", "mean_ndvi": 0.31, "area_ha": 156.0, "color": "#cddc39", "status": "Grassland & Scrub"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.582, 19.036], [74.594, 19.029], [74.600, 19.033], [74.585, 19.044], [74.582, 19.036]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Sparse / Barren (<0.2)", "mean_ndvi": 0.14, "area_ha": 60.0, "color": "#ffe082", "status": "Settlement & Rock Outcrops"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.599, 19.046], [74.605, 19.046], [74.605, 19.052], [74.599, 19.052], [74.599, 19.046]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_hiware.id,
        layer_type="VEGETATION_NDVI",
        name="Vegetation Index (NDVI Canopy Vigor)",
        format="GEOJSON",
        data_payload=hb_ndvi,
        metadata_json={
            "mean_ndvi": 0.62,
            "dense_canopy_pct": 32.0,
            "moderate_canopy_pct": 46.0,
            "low_canopy_pct": 16.0,
            "sparse_canopy_pct": 6.0,
            "sensor": "Sentinel-2 MSI Calibrated Surface Reflectance"
        }
    ))

    # 5. Elevation & Topographic Contours Layer
    hb_elevation = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"contour_m": 700, "zone_name": "Ridge Crest (680-715 m)", "slope_pct": "15-25%", "color": "#5d4037", "treatment": "Continuous Contour Trenches (CCT)"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.590, 19.060], [74.605, 19.067], [74.624, 19.068], [74.615, 19.061], [74.590, 19.060]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"contour_m": 650, "zone_name": "Upper Slope (640-680 m)", "slope_pct": "8-15%", "color": "#8d6e63", "treatment": "Loose Boulder Structures & Afforestation"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.586, 19.052], [74.608, 19.058], [74.626, 19.059], [74.610, 19.049], [74.586, 19.052]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"contour_m": 615, "zone_name": "Agricultural Valley Plain (605-640 m)", "slope_pct": "3-8%", "color": "#bcaaa4", "treatment": "Farm Bunding & Check Dams"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.592, 19.036], [74.616, 19.042], [74.624, 19.034], [74.600, 19.030], [74.592, 19.036]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"contour_m": 590, "zone_name": "Stream Bed / Lowland (585-605 m)", "slope_pct": "1-3%", "color": "#d7ccc8", "treatment": "Nala Bandhara & Desilting"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.602, 19.044], [74.618, 19.039], [74.620, 19.041], [74.604, 19.046], [74.602, 19.044]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_hiware.id,
        layer_type="ELEVATION",
        name="Elevation & Topographic Hypsometry",
        format="GEOJSON",
        data_payload=hb_elevation,
        metadata_json={
            "min_elevation_m": 585.0,
            "max_elevation_m": 715.0,
            "relief_m": 130.0,
            "dominant_slope_class": "Gently Sloping (3-8%)",
            "elevation_bands": [
                {"name": "Ridge Crest", "range": "680-715 m", "area_ha": 215.0, "pct": 22.0, "slope": "15-25%", "color": "#5d4037"},
                {"name": "Upper Slopes", "range": "640-680 m", "area_ha": 340.0, "pct": 34.8, "slope": "8-15%", "color": "#8d6e63"},
                {"name": "Valley Plain", "range": "605-640 m", "area_ha": 325.0, "pct": 33.3, "slope": "3-8%", "color": "#bcaaa4"},
                {"name": "Stream Bed", "range": "585-605 m", "area_ha": 96.0, "pct": 9.9, "slope": "1-3%", "color": "#d7ccc8"}
            ]
        }
    ))

    # ==========================================
    # WATERSHED 2: Ralegan Siddhi (Ahmednagar, MH)
    # ==========================================
    ws_ralegan = db.query(Watershed).filter(Watershed.code == "WS-MH-AHM-002").first()
    if not ws_ralegan:
        ws_ralegan = Watershed(
            code="WS-MH-AHM-002",
            name="Ralegan Siddhi Watershed",
            district_id=ahmednagar.id,
            state_id=mh.id,
            area_hectares=1250.0,
            river_basin="Krishna-Godavari Inter-basin",
            sub_basin="Ghod River Basin",
            agro_climatic_zone="Drought Prone Deccan Plateau",
            primary_drainage="Semi-dendritic system treated with ridge-to-valley structures",
            health_score=78.0,
            risk_level="LOW",
            status="ACTIVE"
        )
        db.add(ws_ralegan)
        db.flush()

        rs_coords = [
            [74.425, 19.008],
            [74.442, 19.002],
            [74.475, 19.015],
            [74.482, 19.038],
            [74.468, 19.052],
            [74.438, 19.045],
            [74.425, 19.008]
        ]
        db.add(WatershedBoundary(
            watershed_id=ws_ralegan.id,
            geometry={"type": "Polygon", "coordinates": [rs_coords]},
            centroid_lat=19.025,
            centroid_lng=74.452,
            bbox=[74.425, 19.002, 74.482, 19.052]
        ))

    # --- Phase 2 GIS Layers for Ralegan Siddhi ---
    rs_drainage = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Ralegan Central Stream", "order": 3, "length_km": 5.1, "flow_direction": "South-East", "gradient": "1.5%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[74.435, 19.042], [74.448, 19.030], [74.458, 19.020], [74.472, 19.012]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "East Gully Branch", "order": 2, "length_km": 2.8, "flow_direction": "South", "gradient": "3.1%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[74.465, 19.045], [74.460, 19.030], [74.458, 19.020]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "North Ridge Stream", "order": 1, "length_km": 1.9, "flow_direction": "South-East", "gradient": "4.2%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[74.440, 19.048], [74.444, 19.038], [74.448, 19.030]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_ralegan.id,
        layer_type="DRAINAGE",
        name="Drainage & Stream Network",
        format="GEOJSON",
        data_payload=rs_drainage,
        metadata_json={"stream_orders": [1, 2, 3], "total_streams": 3, "total_length_km": 9.8, "drainage_density_km_sqkm": 0.78}
    ))

    rs_water = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Major Percolation Tank", "type": "Percolation Tank", "capacity_tcm": 60.0, "spread_area_ha": 6.2, "max_depth_m": 4.5, "status": "Operational"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.446, 19.028], [74.452, 19.028], [74.453, 19.032], [74.447, 19.032], [74.446, 19.028]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Anna Hazare Bandhara Storage", "type": "Check Dam Reservoir", "capacity_tcm": 28.0, "spread_area_ha": 3.1, "max_depth_m": 3.2, "status": "Operational"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.456, 19.019], [74.461, 19.018], [74.460, 19.022], [74.455, 19.022], [74.456, 19.019]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_ralegan.id,
        layer_type="WATER_BODIES",
        name="Surface Water Bodies & Reservoirs",
        format="GEOJSON",
        data_payload=rs_water,
        metadata_json={"total_structures": 2, "total_spread_ha": 9.3, "cumulative_capacity_tcm": 88.0}
    ))

    rs_lulc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"class": "Forest/Vegetation", "color": "#2e7d32", "area_ha": 360.0, "description": "Afforested hill slopes with native dry deciduous species"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.430, 19.040], [74.450, 19.050], [74.475, 19.045], [74.460, 19.035], [74.430, 19.040]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Agriculture", "color": "#8bc34a", "area_ha": 540.0, "description": "Double cropped farmland fed by community borewells"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.435, 19.015], [74.465, 19.025], [74.475, 19.015], [74.445, 19.005], [74.435, 19.015]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Barren/Open Land", "color": "#d4e157", "area_ha": 205.0, "description": "Pastureland with stone bunds and percolation trenches"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.425, 19.008], [74.438, 19.005], [74.442, 19.018], [74.428, 19.025], [74.425, 19.008]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Built-up", "color": "#ff7043", "area_ha": 85.0, "description": "Ralegan Siddhi village nucleus and dairy cooperative"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.450, 19.025], [74.456, 19.025], [74.456, 19.030], [74.450, 19.030], [74.450, 19.025]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Water", "color": "#0284c7", "area_ha": 60.0, "description": "Percolation reservoirs and village recharge ponds"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.446, 19.027], [74.453, 19.027], [74.453, 19.033], [74.446, 19.033], [74.446, 19.027]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_ralegan.id,
        layer_type="LULC",
        name="Land Use / Land Cover (LULC)",
        format="GEOJSON",
        data_payload=rs_lulc,
        metadata_json={"classification_standard": "NRSC / LISS-IV 5-Class Standard", "total_area_ha": 1250.0}
    ))

    rs_ndvi = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Dense Canopy (>0.6)", "mean_ndvi": 0.65, "area_ha": 350.0, "color": "#1b5e20", "status": "Forest Canopy"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.432, 19.038], [74.452, 19.048], [74.472, 19.043], [74.458, 19.035], [74.432, 19.038]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Moderate Canopy (0.4-0.6)", "mean_ndvi": 0.51, "area_ha": 550.0, "color": "#4caf50", "status": "Agriculture"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.436, 19.016], [74.464, 19.024], [74.473, 19.016], [74.446, 19.006], [74.436, 19.016]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Low / Scrub (0.2-0.4)", "mean_ndvi": 0.30, "area_ha": 225.0, "color": "#cddc39", "status": "Fallow & Scrub"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.426, 19.010], [74.437, 19.007], [74.441, 19.017], [74.428, 19.023], [74.426, 19.010]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Sparse / Barren (<0.2)", "mean_ndvi": 0.15, "area_ha": 125.0, "color": "#ffe082", "status": "Settlement & Rock"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.449, 19.024], [74.457, 19.024], [74.457, 19.031], [74.449, 19.031], [74.449, 19.024]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_ralegan.id,
        layer_type="VEGETATION_NDVI",
        name="Vegetation Index (NDVI Canopy Vigor)",
        format="GEOJSON",
        data_payload=rs_ndvi,
        metadata_json={
            "mean_ndvi": 0.58,
            "dense_canopy_pct": 28.0,
            "moderate_canopy_pct": 44.0,
            "low_canopy_pct": 18.0,
            "sparse_canopy_pct": 10.0,
            "sensor": "Sentinel-2 MSI Calibrated Surface Reflectance"
        }
    ))

    rs_elevation = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"contour_m": 720, "zone_name": "Ridge Crest (700-740 m)", "slope_pct": "18-28%", "color": "#5d4037", "treatment": "Ridge Afforestation"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.435, 19.043], [74.455, 19.051], [74.473, 19.046], [74.455, 19.040], [74.435, 19.043]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"contour_m": 660, "zone_name": "Mid Slope (640-700 m)", "slope_pct": "8-15%", "color": "#8d6e63", "treatment": "Contour Bunding"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.432, 19.032], [74.458, 19.038], [74.475, 19.030], [74.450, 19.022], [74.432, 19.032]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"contour_m": 610, "zone_name": "Valley Floor (590-640 m)", "slope_pct": "2-6%", "color": "#bcaaa4", "treatment": "Percolation Tanks"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[74.440, 19.012], [74.468, 19.020], [74.475, 19.012], [74.448, 19.006], [74.440, 19.012]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_ralegan.id,
        layer_type="ELEVATION",
        name="Elevation & Topographic Hypsometry",
        format="GEOJSON",
        data_payload=rs_elevation,
        metadata_json={
            "min_elevation_m": 590.0,
            "max_elevation_m": 740.0,
            "relief_m": 150.0,
            "dominant_slope_class": "Moderately Sloping (8-15%)"
        }
    ))

    # ==========================================
    # WATERSHED 3: Arvari River Catchment (Alwar, RJ)
    # ==========================================
    ws_arvari = db.query(Watershed).filter(Watershed.code == "WS-RJ-ALW-003").first()
    if not ws_arvari:
        ws_arvari = Watershed(
            code="WS-RJ-ALW-003",
            name="Arvari River Catchment & Johad Cluster",
            district_id=alwar.id,
            state_id=rj.id,
            area_hectares=4500.0,
            river_basin="Yamuna Basin",
            sub_basin="Banganga-Sabi River System",
            agro_climatic_zone="Semi-Arid Aravalli Hill Range & Alluvial Plain",
            primary_drainage="Ephemeral hill torrents recharged via traditional Johad earthen dams",
            health_score=68.5,
            risk_level="MEDIUM",
            status="ACTIVE"
        )
        db.add(ws_arvari)
        db.flush()

        ar_coords = [
            [76.220, 27.245],
            [76.255, 27.238],
            [76.288, 27.265],
            [76.292, 27.315],
            [76.262, 27.322],
            [76.230, 27.295],
            [76.220, 27.245]
        ]
        db.add(WatershedBoundary(
            watershed_id=ws_arvari.id,
            geometry={"type": "Polygon", "coordinates": [ar_coords]},
            centroid_lat=27.280,
            centroid_lng=76.255,
            bbox=[76.220, 27.238, 76.292, 27.322]
        ))

    # --- Phase 2 GIS Layers for Arvari River Catchment ---
    ar_drainage = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Arvari Main River Course", "order": 3, "length_km": 11.4, "flow_direction": "Southwards", "gradient": "1.1%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[76.235, 27.310], [76.248, 27.285], [76.265, 27.265], [76.280, 27.245]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Bhanwata Nala", "order": 2, "length_km": 5.2, "flow_direction": "South-East", "gradient": "2.9%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[76.275, 27.315], [76.260, 27.290], [76.248, 27.285]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Hamirpur Hill Stream", "order": 2, "length_km": 4.1, "flow_direction": "Eastwards", "gradient": "3.8%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[76.225, 27.270], [76.242, 27.272], [76.265, 27.265]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Upper Scarp Scour Channel", "order": 1, "length_km": 2.6, "flow_direction": "South", "gradient": "6.2%"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[76.250, 27.320], [76.245, 27.300], [76.235, 27.310]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_arvari.id,
        layer_type="DRAINAGE",
        name="Drainage & Stream Network",
        format="GEOJSON",
        data_payload=ar_drainage,
        metadata_json={"stream_orders": [1, 2, 3], "total_streams": 4, "total_length_km": 23.3, "drainage_density_km_sqkm": 0.52}
    ))

    ar_water = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Bhanwata Traditional Johad", "type": "Johad Earthen Dam", "capacity_tcm": 85.0, "spread_area_ha": 9.4, "max_depth_m": 4.8, "status": "Operational"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.244, 27.282], [76.253, 27.282], [76.254, 27.288], [76.245, 27.288], [76.244, 27.282]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Hamirpur Check Dam Pond", "type": "Check Dam Reservoir", "capacity_tcm": 45.0, "spread_area_ha": 4.8, "max_depth_m": 3.5, "status": "Operational"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.262, 27.262], [76.268, 27.261], [76.267, 27.266], [76.261, 27.266], [76.262, 27.262]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Community Paal Reservoir", "type": "Percolation Tank", "capacity_tcm": 32.0, "spread_area_ha": 3.5, "max_depth_m": 3.0, "status": "Operational"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.275, 27.247], [76.281, 27.245], [76.280, 27.250], [76.274, 27.250], [76.275, 27.247]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_arvari.id,
        layer_type="WATER_BODIES",
        name="Surface Water Bodies & Reservoirs",
        format="GEOJSON",
        data_payload=ar_water,
        metadata_json={"total_structures": 3, "total_spread_ha": 17.7, "cumulative_capacity_tcm": 162.0}
    ))

    ar_lulc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"class": "Forest/Vegetation", "color": "#2e7d32", "area_ha": 1150.0, "description": "Aravalli rocky hill scrub and community protected groves"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.225, 27.290], [76.255, 27.320], [76.290, 27.310], [76.265, 27.285], [76.225, 27.290]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Agriculture", "color": "#8bc34a", "area_ha": 1850.0, "description": "Alluvial river plain cultivated with Mustard and Wheat"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.235, 27.255], [76.270, 27.275], [76.285, 27.250], [76.250, 27.240], [76.235, 27.255]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Barren/Open Land", "color": "#d4e157", "area_ha": 1030.0, "description": "Gravelly pediment and severely eroded Aravalli foot-slopes"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.220, 27.248], [76.236, 27.255], [76.248, 27.242], [76.222, 27.245], [76.220, 27.248]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Built-up", "color": "#ff7043", "area_ha": 260.0, "description": "Hamirpur, Bhanwata villages and rural homesteads"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.250, 27.270], [76.258, 27.270], [76.258, 27.278], [76.250, 27.278], [76.250, 27.270]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"class": "Water", "color": "#0284c7", "area_ha": 210.0, "description": "Johads, stream pools, and percolation tanks"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.245, 27.280], [76.255, 27.280], [76.255, 27.290], [76.245, 27.290], [76.245, 27.280]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_arvari.id,
        layer_type="LULC",
        name="Land Use / Land Cover (LULC)",
        format="GEOJSON",
        data_payload=ar_lulc,
        metadata_json={"classification_standard": "NRSC / LISS-IV 5-Class Standard", "total_area_ha": 4500.0}
    ))

    ar_ndvi = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Dense Canopy (>0.6)", "mean_ndvi": 0.63, "area_ha": 810.0, "color": "#1b5e20", "status": "Valley & Riparian Corridor"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.242, 27.280], [76.268, 27.270], [76.280, 27.248], [76.258, 27.260], [76.242, 27.280]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Moderate Canopy (0.4-0.6)", "mean_ndvi": 0.49, "area_ha": 1710.0, "color": "#4caf50", "status": "Cultivated Cropland"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.234, 27.256], [76.272, 27.276], [76.286, 27.252], [76.248, 27.242], [76.234, 27.256]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Low / Scrub (0.2-0.4)", "mean_ndvi": 0.28, "area_ha": 1260.0, "color": "#cddc39", "status": "Aravalli Scrub & Hillocks"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.226, 27.288], [76.254, 27.318], [76.288, 27.308], [76.264, 27.286], [76.226, 27.288]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"ndvi_class": "Sparse / Barren (<0.2)", "mean_ndvi": 0.12, "area_ha": 720.0, "color": "#ffe082", "status": "Barren Scarp & Settlement"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.220, 27.246], [76.238, 27.254], [76.248, 27.240], [76.222, 27.244], [76.220, 27.246]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_arvari.id,
        layer_type="VEGETATION_NDVI",
        name="Vegetation Index (NDVI Canopy Vigor)",
        format="GEOJSON",
        data_payload=ar_ndvi,
        metadata_json={
            "mean_ndvi": 0.48,
            "dense_canopy_pct": 18.0,
            "moderate_canopy_pct": 38.0,
            "low_canopy_pct": 28.0,
            "sparse_canopy_pct": 16.0,
            "sensor": "Sentinel-2 MSI Calibrated Surface Reflectance"
        }
    ))

    ar_elevation = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"contour_m": 520, "zone_name": "Aravalli Ridge Escarpment (450-540 m)", "slope_pct": "20-35%", "color": "#5d4037", "treatment": "Loose Stone Check Dams"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.230, 27.300], [76.260, 27.320], [76.290, 27.312], [76.270, 27.295], [76.230, 27.300]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"contour_m": 410, "zone_name": "Upper Foot-slopes (360-450 m)", "slope_pct": "10-20%", "color": "#8d6e63", "treatment": "Gully Plugs & CCT"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.228, 27.275], [76.265, 27.285], [76.285, 27.270], [76.255, 27.260], [76.228, 27.275]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"contour_m": 310, "zone_name": "Alluvial River Plain (290-360 m)", "slope_pct": "1-4%", "color": "#bcaaa4", "treatment": "Traditional Johad Water Harvesting"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.235, 27.250], [76.275, 27.265], [76.285, 27.245], [76.245, 27.238], [76.235, 27.250]]]
                }
            }
        ]
    }
    db.add(GISLayer(
        watershed_id=ws_arvari.id,
        layer_type="ELEVATION",
        name="Elevation & Topographic Hypsometry",
        format="GEOJSON",
        data_payload=ar_elevation,
        metadata_json={
            "min_elevation_m": 290.0,
            "max_elevation_m": 540.0,
            "relief_m": 250.0,
            "dominant_slope_class": "Steep Aravalli Escarpment (15-30%)"
        }
    ))

    # Audit log
    db.add(AuditLog(
        user_id="system-phase2",
        action="SEED_PHASE2_GIS_LAYERS",
        resource_type="GIS_LAYERS",
        resource_id="ALL",
        details={"layers_seeded": ["BOUNDARY", "LULC", "DRAINAGE", "WATER_BODIES", "VEGETATION_NDVI", "ELEVATION"], "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    ))

    db.commit()
    print("Phase 2 GIS Layer seeding completed successfully for all 3 watersheds!")

def seed_dataset_catalog(db: Session):
    """Populates baseline dataset catalog with authoritative satellite and GIS layer metadata."""
    if db.query(GeospatialDataset).first():
        return

    watersheds = db.query(Watershed).all()
    if not watersheds:
        return

    for ws in watersheds:
        wb = db.query(WatershedBoundary).filter(WatershedBoundary.watershed_id == ws.id).first()
        bounds = wb.bbox if wb else [74.58, 19.03, 74.63, 19.07]

        # 1. Sentinel-2 L2A Optical
        db.add(GeospatialDataset(
            dataset_code=f"DS-{ws.code}-S2L2A",
            dataset_name=f"Sentinel-2 Level-2A BOA Reflectance — {ws.name}",
            dataset_type="SATELLITE_OPTICAL",
            provider="Copernicus Data Space Ecosystem (CDSE)",
            watershed_id=ws.id,
            acquisition_date=datetime.datetime(2024, 5, 15, 10, 30),
            processing_date=datetime.datetime(2024, 5, 16, 2, 0),
            spatial_resolution="10m VNIR / 20m SWIR",
            temporal_resolution="5-day revisit",
            coverage_bounds=bounds,
            crs="EPSG:4326",
            provenance="DEMO_DATA",
            format="GEOTIFF",
            record_count=6,
            license_info="Copernicus Open Access / EU Free & Open License",
            metadata_json={"cloud_cover_pct": 2.1, "processing_level": "Level-2A BOA", "calibrated_indices": ["NDVI", "NDWI", "SMI"]},
            status="ACTIVE"
        ))

        # 2. CartoDEM / Elevation
        db.add(GeospatialDataset(
            dataset_code=f"DS-{ws.code}-DEM",
            dataset_name=f"CartoDEM 30m Terrain Hypsometry — {ws.name}",
            dataset_type="DEM_ELEVATION",
            provider="ISRO / NRSC Bhuvan",
            watershed_id=ws.id,
            acquisition_date=datetime.datetime(2023, 1, 1),
            processing_date=datetime.datetime(2023, 3, 15),
            spatial_resolution="30m Ground Resolution",
            temporal_resolution="Static Baseline",
            coverage_bounds=bounds,
            crs="EPSG:4326",
            provenance="DEMO_DATA",
            format="GEOJSON",
            record_count=3,
            license_info="Open Government Data (OGD) Platform India",
            metadata_json={"vertical_datum": "EGM96", "terrain_classes": ["Valley", "Footslope", "Escarpment"]},
            status="ACTIVE"
        ))

        # 3. LULC Vector
        db.add(GeospatialDataset(
            dataset_code=f"DS-{ws.code}-LULC",
            dataset_name=f"Thematic Land Use / Land Cover Vector 1:50K — {ws.name}",
            dataset_type="LULC",
            provider="NRSC Bhuvan / National Remote Sensing Centre",
            watershed_id=ws.id,
            acquisition_date=datetime.datetime(2023, 11, 20),
            processing_date=datetime.datetime(2024, 1, 10),
            spatial_resolution="1:50,000 Scale (10m effective)",
            temporal_resolution="Annual Cycle",
            coverage_bounds=bounds,
            crs="EPSG:4326",
            provenance="DEMO_DATA",
            format="GEOJSON",
            record_count=5,
            license_info="National Remote Sensing Centre (NRSC) Open Geoportal",
            metadata_json={"classes_covered": ["Forest/Vegetation", "Agriculture", "Barren", "Built-up", "Water"]},
            status="ACTIVE"
        ))

        # 4. Drainage Network
        db.add(GeospatialDataset(
            dataset_code=f"DS-{ws.code}-DRAIN",
            dataset_name=f"Hydrographic Stream Order Network — {ws.name}",
            dataset_type="DRAINAGE_NETWORK",
            provider="Survey of India / HydroSHEDS",
            watershed_id=ws.id,
            acquisition_date=datetime.datetime(2022, 6, 1),
            processing_date=datetime.datetime(2022, 9, 1),
            spatial_resolution="Vector Streamlines",
            temporal_resolution="Decadal Topographic Survey",
            coverage_bounds=bounds,
            crs="EPSG:4326",
            provenance="DEMO_DATA",
            format="GEOJSON",
            record_count=4,
            license_info="Survey of India Open Series Maps",
            metadata_json={"stream_orders": [1, 2, 3]},
            status="ACTIVE"
        ))

        # 5. Geo-Tagged Field Audit Photos
        db.add(GeospatialDataset(
            dataset_code=f"DS-{ws.code}-PHOTOS",
            dataset_name=f"Ground-Truth Geo-Tagged Verification Photos — {ws.name}",
            dataset_type="FIELD_SURVEY",
            provider="State Watershed Development Mobile Audit",
            watershed_id=ws.id,
            acquisition_date=datetime.datetime(2024, 4, 10),
            processing_date=datetime.datetime(2024, 4, 11),
            spatial_resolution="Sub-meter Ground GNSS Position",
            temporal_resolution="Quarterly Audit",
            coverage_bounds=bounds,
            crs="EPSG:4326",
            provenance="DEMO_DATA",
            format="FIELD_SURVEY",
            record_count=3,
            license_info="Departmental Internal Ground Truth Record",
            metadata_json={"verified_by": "District Watershed Team", "has_exif_gps": True},
            status="ACTIVE"
        ))

    db.commit()
    print("Seeded baseline GeospatialDataset catalog for all demo watersheds.")

def seed_users(db: Session):
    """
    Seeds initial institutional demo accounts for SIH evaluation.
    Clearly marked as demonstration accounts with standard demo password.
    Never exposes real government or production credentials.
    """
    from app.core.security import hash_password

    # Check if admin already exists
    if db.query(User).filter(User.email == "admin@jaldrishti.gov.in").first():
        return

    demo_password_hash = hash_password("JalDrishti@2026")

    demo_users = [
        User(
            name="Dr. Vikram Rathore",
            email="admin@jaldrishti.gov.in",
            password_hash=demo_password_hash,
            role="ADMIN",
            organization="Ministry of Jal Shakti / DoLR",
            designation="National Project Director & System Administrator",
            is_active=True
        ),
        User(
            name="Dr. Ramesh Patil",
            email="state.officer@mahawatershed.gov.in",
            password_hash=demo_password_hash,
            role="STATE_OFFICER",
            state_id=1,  # Maharashtra
            organization="Maharashtra State Watershed Management Agency",
            designation="Joint Secretary & State Nodal Officer",
            is_active=True
        ),
        User(
            name="Anil Sharma",
            email="district.officer@ahmednagar.gov.in",
            password_hash=demo_password_hash,
            role="DISTRICT_OFFICER",
            state_id=1,
            district_id=1,  # Ahmednagar
            organization="Ahmednagar District Rural Development Agency",
            designation="District Project Director",
            is_active=True
        ),
        User(
            name="Suresh Gaikwad",
            email="field.hiware@ahmednagar.gov.in",
            password_hash=demo_password_hash,
            role="FIELD_OFFICER",
            state_id=1,
            district_id=1,
            watershed_id=1,  # Hiware Bazar
            organization="Hiware Bazar Watershed Committee",
            designation="Junior Field Engineer & Geo-Tag Auditor",
            is_active=True
        ),
        User(
            name="Pooja Iyer",
            email="analyst@nrsc.isro.gov.in",
            password_hash=demo_password_hash,
            role="ANALYST",
            organization="National Remote Sensing Centre (NRSC / ISRO)",
            designation="Senior Remote Sensing & GIS Scientist",
            is_active=True
        )
    ]

    for u in demo_users:
        db.add(u)

    # Seed one sample pending access request for demonstration
    sample_request = AccessRequest(
        name="Rajesh Verma",
        email="r.verma@mprural.gov.in",
        requested_role="DISTRICT_OFFICER",
        state_id=2,  # Madhya Pradesh
        district_id=3,  # Jhabua
        organization="Jhabua District Watershed Cell",
        designation="Assistant Project Manager",
        reason="Official deputation for watershed health monitoring and DPR intervention planning under PMKSY-WDC 2.0.",
        status="PENDING"
    )
    db.add(sample_request)

    db.commit()
    print("Seeded 5 institutional demo accounts and 1 sample access request for SIH evaluation.")

def seed_indicators_and_values(db: Session, target_watershed_id: int = None):
    """
    Seeds calibrated multi-temporal historical (2018-2024) and prototype projection (2025-2026) indicator values.
    Clearly identifies all values as DEMO DATA / DEMO / SEEDED DATA.
    Values are deterministic and stable across reloads.
    """
    # 1. Ensure the 5 canonical indicators exist
    indicator_defs = [
        ("NDVI", "Normalized Difference Vegetation Index", "VEGETATION", "Index (-0.2 to 1.0)", "Vegetation vigor and biomass canopy density derived from optical satellite bands.", 0.25),
        ("NDWI", "Normalized Difference Water Index", "HYDROLOGICAL", "Index (-1.0 to 1.0)", "Surface water presence and leaf water content.", 0.25),
        ("SMI", "Soil Moisture Index", "HYDROLOGICAL", "Percentage (%)", "Estimated root-zone moisture level from satellite microwave/optical thermal indices.", 0.20),
        ("WATER_SPREAD", "Surface Water Spread Area", "HYDROLOGICAL", "Hectares (ha)", "Total surface water spread across water retention structures and ponds.", 0.15),
        ("EROSION_INDEX", "Soil Loss Susceptibility", "LAND_CONDITION", "Index (0 to 10)", "Soil degradation and sediment detachment propensity based on slope and cover.", 0.15),
    ]

    for code, name, cat, unit, desc, weight in indicator_defs:
        if not db.query(Indicator).filter(Indicator.code == code).first():
            db.add(Indicator(
                code=code, name=name, category=cat, unit=unit,
                description=desc, weight_in_health_score=weight
            ))
    db.commit()

    ind_map = {ind.code: ind.id for ind in db.query(Indicator).all()}

    # 2. Complete calibrated dataset for Watersheds 1, 2, 3 (2018-2026)
    CALIBRATED_WATERSHED_SERIES = {
        1: {  # Hiware Bazar Model Micro-Watershed
            2018: {"NDVI": (0.42, 42.0), "NDWI": (0.12, 32.0), "SMI": (38.0, 38.0), "WATER_SPREAD": (18.5, 37.0), "EROSION_INDEX": (5.2, 48.0)},
            2019: {"NDVI": (0.46, 46.0), "NDWI": (0.16, 36.0), "SMI": (42.0, 42.0), "WATER_SPREAD": (24.0, 48.0), "EROSION_INDEX": (4.8, 52.0)},
            2020: {"NDVI": (0.52, 52.0), "NDWI": (0.22, 42.0), "SMI": (48.5, 48.5), "WATER_SPREAD": (32.0, 64.0), "EROSION_INDEX": (4.1, 59.0)},
            2021: {"NDVI": (0.55, 55.0), "NDWI": (0.24, 44.0), "SMI": (52.0, 52.0), "WATER_SPREAD": (35.5, 71.0), "EROSION_INDEX": (3.6, 64.0)},
            2022: {"NDVI": (0.58, 58.0), "NDWI": (0.28, 48.0), "SMI": (55.4, 55.4), "WATER_SPREAD": (38.2, 76.4), "EROSION_INDEX": (3.2, 68.0)},
            2023: {"NDVI": (0.60, 60.0), "NDWI": (0.29, 49.0), "SMI": (58.0, 58.0), "WATER_SPREAD": (41.0, 82.0), "EROSION_INDEX": (2.9, 71.0)},
            2024: {"NDVI": (0.62, 62.0), "NDWI": (0.31, 51.0), "SMI": (60.5, 60.5), "WATER_SPREAD": (43.5, 87.0), "EROSION_INDEX": (2.7, 73.0)},
            2025: {"NDVI": (0.635, 63.5), "NDWI": (0.32, 52.0), "SMI": (62.0, 62.0), "WATER_SPREAD": (44.8, 89.6), "EROSION_INDEX": (2.6, 74.0)},
            2026: {"NDVI": (0.65, 65.0), "NDWI": (0.33, 53.0), "SMI": (64.0, 64.0), "WATER_SPREAD": (46.0, 92.0), "EROSION_INDEX": (2.5, 75.0)},
        },
        2: {  # Ralegan Siddhi Watershed
            2018: {"NDVI": (0.38, 38.0), "NDWI": (0.10, 30.0), "SMI": (34.0, 34.0), "WATER_SPREAD": (22.0, 44.0), "EROSION_INDEX": (6.0, 40.0)},
            2019: {"NDVI": (0.42, 42.0), "NDWI": (0.14, 34.0), "SMI": (39.0, 39.0), "WATER_SPREAD": (28.0, 56.0), "EROSION_INDEX": (5.2, 48.0)},
            2020: {"NDVI": (0.48, 48.0), "NDWI": (0.18, 38.0), "SMI": (44.0, 44.0), "WATER_SPREAD": (36.0, 72.0), "EROSION_INDEX": (4.4, 56.0)},
            2021: {"NDVI": (0.51, 51.0), "NDWI": (0.21, 41.0), "SMI": (48.0, 48.0), "WATER_SPREAD": (40.0, 80.0), "EROSION_INDEX": (3.8, 62.0)},
            2022: {"NDVI": (0.53, 53.0), "NDWI": (0.23, 43.0), "SMI": (50.5, 50.5), "WATER_SPREAD": (42.5, 85.0), "EROSION_INDEX": (3.5, 65.0)},
            2023: {"NDVI": (0.56, 56.0), "NDWI": (0.25, 45.0), "SMI": (53.0, 53.0), "WATER_SPREAD": (45.0, 90.0), "EROSION_INDEX": (3.1, 69.0)},
            2024: {"NDVI": (0.58, 58.0), "NDWI": (0.27, 47.0), "SMI": (56.0, 56.0), "WATER_SPREAD": (48.0, 96.0), "EROSION_INDEX": (2.9, 71.0)},
            2025: {"NDVI": (0.595, 59.5), "NDWI": (0.28, 48.0), "SMI": (57.5, 57.5), "WATER_SPREAD": (49.5, 99.0), "EROSION_INDEX": (2.8, 72.0)},
            2026: {"NDVI": (0.61, 61.0), "NDWI": (0.29, 49.0), "SMI": (59.0, 59.0), "WATER_SPREAD": (51.0, 100.0), "EROSION_INDEX": (2.7, 73.0)},
        },
        3: {  # Arvari River Catchment & Johad Cluster
            2018: {"NDVI": (0.28, 28.0), "NDWI": (0.04, 24.0), "SMI": (22.0, 22.0), "WATER_SPREAD": (15.0, 30.0), "EROSION_INDEX": (7.5, 25.0)},
            2019: {"NDVI": (0.32, 32.0), "NDWI": (0.08, 28.0), "SMI": (26.0, 26.0), "WATER_SPREAD": (21.0, 42.0), "EROSION_INDEX": (6.8, 32.0)},
            2020: {"NDVI": (0.37, 37.0), "NDWI": (0.12, 32.0), "SMI": (31.0, 31.0), "WATER_SPREAD": (28.0, 56.0), "EROSION_INDEX": (6.0, 40.0)},
            2021: {"NDVI": (0.41, 41.0), "NDWI": (0.15, 35.0), "SMI": (36.0, 36.0), "WATER_SPREAD": (34.0, 68.0), "EROSION_INDEX": (5.4, 46.0)},
            2022: {"NDVI": (0.44, 44.0), "NDWI": (0.18, 38.0), "SMI": (40.0, 40.0), "WATER_SPREAD": (38.0, 76.0), "EROSION_INDEX": (4.9, 51.0)},
            2023: {"NDVI": (0.46, 46.0), "NDWI": (0.20, 40.0), "SMI": (42.5, 42.5), "WATER_SPREAD": (41.0, 82.0), "EROSION_INDEX": (4.6, 54.0)},
            2024: {"NDVI": (0.48, 48.0), "NDWI": (0.21, 41.0), "SMI": (45.0, 45.0), "WATER_SPREAD": (44.0, 88.0), "EROSION_INDEX": (4.3, 57.0)},
            2025: {"NDVI": (0.50, 50.0), "NDWI": (0.22, 42.0), "SMI": (47.0, 47.0), "WATER_SPREAD": (46.0, 92.0), "EROSION_INDEX": (4.1, 59.0)},
            2026: {"NDVI": (0.52, 52.0), "NDWI": (0.23, 43.0), "SMI": (49.0, 49.0), "WATER_SPREAD": (48.0, 96.0), "EROSION_INDEX": (3.9, 61.0)},
        }
    }

    # Determine which watersheds to seed
    if target_watershed_id is not None:
        watersheds = db.query(Watershed).filter(Watershed.id == target_watershed_id).all()
    else:
        watersheds = db.query(Watershed).all()

    for ws in watersheds:
        ws_id = ws.id
        series = CALIBRATED_WATERSHED_SERIES.get(ws_id)

        # For any watershed not in preset dictionary, generate deterministic prototype values
        if not series:
            series = {}
            for yr in range(2018, 2027):
                t = (yr - 2018) / 8.0
                series[yr] = {
                    "NDVI": (round(0.32 + ((ws_id * 7) % 15) * 0.01 + t * 0.22, 3), round(32.0 + t * 30.0, 1)),
                    "NDWI": (round(0.06 + ((ws_id * 5) % 10) * 0.01 + t * 0.18, 3), round(25.0 + t * 25.0, 1)),
                    "SMI": (round(28.0 + ((ws_id * 11) % 15) + t * 24.0, 1), round(28.0 + t * 24.0, 1)),
                    "WATER_SPREAD": (round(16.0 + ((ws_id * 13) % 15) + t * 26.0, 1), round(35.0 + t * 50.0, 1)),
                    "EROSION_INDEX": (round(6.8 - ((ws_id * 3) % 10) * 0.1 - t * 2.8, 1), round(40.0 + t * 30.0, 1)),
                }

        # Check existing recorded years for this watershed to avoid duplicate inserts
        existing_keys = set(
            (r.indicator_id, r.recorded_year)
            for r in db.query(IndicatorValue.indicator_id, IndicatorValue.recorded_year)
            .filter(IndicatorValue.watershed_id == ws_id).all()
        )

        for year, ind_dict in series.items():
            source = "DEMO / SEEDED DATA" if year >= 2025 else "DEMO DATA"
            for code, (val, norm_score) in ind_dict.items():
                ind_id = ind_map.get(code)
                if not ind_id:
                    continue
                if (ind_id, year) not in existing_keys:
                    db.add(IndicatorValue(
                        watershed_id=ws_id,
                        indicator_id=ind_id,
                        recorded_year=year,
                        recorded_month=6,
                        value=float(val),
                        normalized_score=float(norm_score),
                        source_type=source
                    ))
                    existing_keys.add((ind_id, year))

    db.commit()
    print("Seeded baseline IndicatorValue multi-temporal records for watersheds.")


def seed_interventions(db: Session):
    """
    Seeds calibrated prototype conservation interventions and field inspection observations.
    Clearly marks all records with source_type = 'DEMO / SEEDED DATA'.
    Guaranteed idempotent: safe to execute repeatedly without duplicating interventions or observations.
    Resilient: validates DB table/column presence dynamically and rolls back on failure.
    """
    try:
        inspector = inspect(db.get_bind())
        tables = set(inspector.get_table_names())
        if "interventions" not in tables:
            print("Table 'interventions' not found; skipping intervention seeding.")
            return

        intv_cols = {c["name"] for c in inspector.get_columns("interventions")}
        obs_cols = {c["name"] for c in inspector.get_columns("observations")} if "observations" in tables else set()
        has_source_type = "source_type" in intv_cols
        has_intervention_id = "intervention_id" in obs_cols

        # Robust watershed lookup by code, name keyword, or ID
        ws_hb = (
            db.query(Watershed).filter(Watershed.code == "WS-MH-AHM-001").first()
            or db.query(Watershed).filter(Watershed.name.ilike("%Hiware%")).first()
            or db.query(Watershed).filter(Watershed.id == 1).first()
        )
        ws_rs = (
            db.query(Watershed).filter(Watershed.code == "WS-MH-AHM-002").first()
            or db.query(Watershed).filter(Watershed.name.ilike("%Ralegan%")).first()
            or db.query(Watershed).filter(Watershed.id == 2).first()
        )
        ws_arv = (
            db.query(Watershed).filter(Watershed.code == "WS-RJ-ALW-003").first()
            or db.query(Watershed).filter(Watershed.name.ilike("%Arvari%")).first()
            or db.query(Watershed).filter(Watershed.id == 3).first()
        )

        if not ws_hb and not ws_rs and not ws_arv:
            print("Watersheds not found; skipping intervention seeding.")
            return
    except Exception as inspect_err:
        print(f"Warning during intervention table/watershed inspection: {inspect_err}")
        return

    DEMO_INTERVENTIONS = []

    if ws_hb:
        DEMO_INTERVENTIONS.extend([
            {
                "watershed_id": ws_hb.id,
                "code": "INT-HB-CD-01",
                "name": "Main Stream Cement Nalla Bandhara (CNB-1)",
                "intervention_type": "CHECK_DAM",
                "status": "COMPLETED",
                "sanction_year": 2019,
                "completion_date": datetime.datetime(2020, 3, 15),
                "latitude": 19.0465,
                "longitude": 74.6062,
                "target_capacity_cum": 8500.0,
                "beneficiary_count": 85,
                "cost_inr": 620000.0,
                "before_metrics": {"water_table_depth_m": 18.2, "storage_tcm": 2.0, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"water_table_depth_m": 8.4, "storage_tcm": 8.5, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Groundwater recharge zone expanded by 1.8 km down-gradient; shallow open wells retained water through May.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": [
                    {
                        "observer_name": "Suresh Gaikwad (Junior Field Engineer)",
                        "observation_date": datetime.datetime(2024, 4, 15, 10, 30),
                        "condition_rating": "EXCELLENT",
                        "remarks": "Structure intact post-monsoon; upstream silt trap functioning at 85% efficiency. Water retention sustained through dry spell. (DEMO / SEEDED DATA)",
                        "recommended_action": "Routine pre-monsoon inspection scheduled for May."
                    }
                ]
            },
            {
                "watershed_id": ws_hb.id,
                "code": "INT-HB-CCT-02",
                "name": "Upper Ridge Continuous Contour Trenches (CCT)",
                "intervention_type": "CONTOUR_BUNDING",
                "status": "COMPLETED",
                "sanction_year": 2020,
                "completion_date": datetime.datetime(2021, 5, 20),
                "latitude": 19.0582,
                "longitude": 74.6105,
                "target_capacity_cum": 12000.0,
                "beneficiary_count": 140,
                "cost_inr": 890000.0,
                "before_metrics": {"runoff_coeff": 0.45, "vegetation_cover_pct": 14.0, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"runoff_coeff": 0.18, "vegetation_cover_pct": 46.0, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Substantial reduction in peak runoff velocity; silt accumulation in lower nala reduced by 72%.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": [
                    {
                        "observer_name": "Dr. Vikram Rathore (National Project Director)",
                        "observation_date": datetime.datetime(2024, 5, 2, 11, 0),
                        "condition_rating": "GOOD",
                        "remarks": "Continuous trenches along 400m ridge contour stable with grass cover establishment. Runoff arrest verified. (DEMO / SEEDED DATA)",
                        "recommended_action": "Desilt upper collection trenches before onset of monsoon."
                    }
                ]
            },
            {
                "watershed_id": ws_hb.id,
                "code": "INT-HB-PT-03",
                "name": "Gaothan Percolation Tank Deepening & Spillway",
                "intervention_type": "PERCOLATION_TANK",
                "status": "WORK_IN_PROGRESS",
                "sanction_year": 2023,
                "completion_date": None,
                "latitude": 19.0395,
                "longitude": 74.6010,
                "target_capacity_cum": 16000.0,
                "beneficiary_count": 165,
                "cost_inr": 1150000.0,
                "before_metrics": {"annual_percolation_mcm": 0.08, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"expected_percolation_mcm": 0.22, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Basin de-siltation at 75% progress; percolation velocity improved in trial pit.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": []
            },
            {
                "watershed_id": ws_hb.id,
                "code": "INT-HB-GP-04",
                "name": "Middle Catchment Sub-surface Dyke & Gabion Plugs",
                "intervention_type": "GULLY_CONTROL",
                "status": "SANCTIONED",
                "sanction_year": 2024,
                "completion_date": None,
                "latitude": 19.0512,
                "longitude": 74.6185,
                "target_capacity_cum": 4200.0,
                "beneficiary_count": 55,
                "cost_inr": 480000.0,
                "before_metrics": {"erosion_rate_tons_ha": 6.8, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"expected_soil_retention_pct": 65.0, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Sanctioned under PMKSY-WDC 2.0; geological baseline survey completed.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": []
            },
            {
                "watershed_id": ws_hb.id,
                "code": "INT-HB-FP-05",
                "name": "Farm Pond Clustered Micro-Recharge Shaft",
                "intervention_type": "FARM_POND",
                "status": "PROPOSED",
                "sanction_year": 2024,
                "completion_date": None,
                "latitude": 19.0350,
                "longitude": 74.5950,
                "target_capacity_cum": 5500.0,
                "beneficiary_count": 40,
                "cost_inr": 320000.0,
                "before_metrics": {"terminal_monsoon_drying_month": "December", "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"projected_rabi_irrigation_ha": 18.5, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Site pegged; Gram Sabha approval in draft DPR stage.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": []
            }
        ])

    if ws_rs:
        DEMO_INTERVENTIONS.extend([
            {
                "watershed_id": ws_rs.id,
                "code": "INT-RS-CD-01",
                "name": "Main Nalla Masonry Check Dam (MCD-1)",
                "intervention_type": "CHECK_DAM",
                "status": "COMPLETED",
                "sanction_year": 2018,
                "completion_date": datetime.datetime(2019, 4, 10),
                "latitude": 19.0225,
                "longitude": 74.4485,
                "target_capacity_cum": 9500.0,
                "beneficiary_count": 95,
                "cost_inr": 680000.0,
                "before_metrics": {"dry_season_well_depth_m": 22.4, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"dry_season_well_depth_m": 9.8, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Perennial saturation observed in downstream community open wells; baseflow sustained.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": [
                    {
                        "observer_name": "Anil Sharma (District Project Director)",
                        "observation_date": datetime.datetime(2024, 3, 20, 14, 0),
                        "condition_rating": "EXCELLENT",
                        "remarks": "Masonry crest and wing walls structurally sound. Downstream open wells show +2.2m water level elevation compared to baseline. (DEMO / SEEDED DATA)",
                        "recommended_action": "Maintain downstream apron boulders."
                    }
                ]
            },
            {
                "watershed_id": ws_rs.id,
                "code": "INT-RS-PT-02",
                "name": "Gaothan Percolation Tank (PT-A)",
                "intervention_type": "PERCOLATION_TANK",
                "status": "COMPLETED",
                "sanction_year": 2019,
                "completion_date": datetime.datetime(2020, 2, 18),
                "latitude": 19.0310,
                "longitude": 74.4550,
                "target_capacity_cum": 18000.0,
                "beneficiary_count": 160,
                "cost_inr": 1250000.0,
                "before_metrics": {"recharge_zone_radius_km": 0.4, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"recharge_zone_radius_km": 1.2, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Groundwater table elevated by 2.4m across a 1.2 km radius; post-monsoon storage verified.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": [
                    {
                        "observer_name": "Dr. Ramesh Patil (State Nodal Officer)",
                        "observation_date": datetime.datetime(2024, 4, 2, 16, 15),
                        "condition_rating": "GOOD",
                        "remarks": "Percolation tank holding capacity measured at 17,200 m³. Sub-surface percolation rate active. (DEMO / SEEDED DATA)",
                        "recommended_action": "Clear minor weeds near inlet channel."
                    }
                ]
            },
            {
                "watershed_id": ws_rs.id,
                "code": "INT-RS-LBS-03",
                "name": "Ridge Loose Boulder Structures (LBS-12)",
                "intervention_type": "GULLY_CONTROL",
                "status": "WORK_IN_PROGRESS",
                "sanction_year": 2023,
                "completion_date": None,
                "latitude": 19.0380,
                "longitude": 74.4610,
                "target_capacity_cum": 3200.0,
                "beneficiary_count": 45,
                "cost_inr": 340000.0,
                "before_metrics": {"gully_advance_rate_m_yr": 1.8, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"sediment_capture_pct": 68.0, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Gully erosion halted; sediment capture rate ~68% in upper treatment catchment.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": []
            },
            {
                "watershed_id": ws_rs.id,
                "code": "INT-RS-FP-04",
                "name": "Community Farm Pond Recharge Cluster",
                "intervention_type": "FARM_POND",
                "status": "SANCTIONED",
                "sanction_year": 2024,
                "completion_date": None,
                "latitude": 19.0180,
                "longitude": 74.4420,
                "target_capacity_cum": 6500.0,
                "beneficiary_count": 70,
                "cost_inr": 480000.0,
                "before_metrics": {"summer_irrigation_deficit_pct": 52.0, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"projected_kharif_supplementary_ha": 25.0, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Sanctioned under PMKSY-WDC 2.0; site pegged for excavation.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": []
            },
            {
                "watershed_id": ws_rs.id,
                "code": "INT-RS-CCT-05",
                "name": "North Ridge Continuous Contour Trenches & Grass Seeding",
                "intervention_type": "CONTOUR_BUNDING",
                "status": "PROPOSED",
                "sanction_year": 2024,
                "completion_date": None,
                "latitude": 19.0420,
                "longitude": 74.4680,
                "target_capacity_cum": 7800.0,
                "beneficiary_count": 60,
                "cost_inr": 510000.0,
                "before_metrics": {"runoff_coeff": 0.48, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"projected_runoff_coeff": 0.22, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Technical feasibility completed by DRDA team; awaiting administrative sanction.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": []
            }
        ])

    if ws_arv:
        DEMO_INTERVENTIONS.extend([
            {
                "watershed_id": ws_arv.id,
                "code": "INT-ARV-JD-01",
                "name": "Traditional Earthen Johad Catchment Structure",
                "intervention_type": "WATER_HARVESTING_JOHAD",
                "status": "COMPLETED",
                "sanction_year": 2021,
                "completion_date": datetime.datetime(2022, 2, 10),
                "latitude": 27.2750,
                "longitude": 76.2520,
                "target_capacity_cum": 15000.0,
                "beneficiary_count": 210,
                "cost_inr": 750000.0,
                "before_metrics": {"water_table_depth_m": 35.0, "wells_dry_pct": 80.0, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"water_table_depth_m": 16.5, "wells_dry_pct": 15.0, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Perennial moisture restored to 14 downstream wells; mustard and wheat double cropping enabled.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": [
                    {
                        "observer_name": "Field Verification Team (Alwar District Cell)",
                        "observation_date": datetime.datetime(2024, 3, 10, 15, 30),
                        "condition_rating": "EXCELLENT",
                        "remarks": "Traditional earthen Johad embankment well-compacted. 14 downstream dug wells reporting perennial water availability. (DEMO / SEEDED DATA)",
                        "recommended_action": "Protect downstream earthen bund from cattle trampling."
                    }
                ]
            },
            {
                "watershed_id": ws_arv.id,
                "code": "INT-ARV-AN-02",
                "name": "Bhanwata Upstream Masonry Anicut",
                "intervention_type": "CHECK_DAM",
                "status": "COMPLETED",
                "sanction_year": 2020,
                "completion_date": datetime.datetime(2021, 3, 30),
                "latitude": 27.2620,
                "longitude": 76.2410,
                "target_capacity_cum": 22000.0,
                "beneficiary_count": 280,
                "cost_inr": 1100000.0,
                "before_metrics": {"surface_storage_duration_months": 2.0, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"surface_storage_duration_months": 8.0, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Surface water pool retained through late summer; livestock watering secured.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": [
                    {
                        "observer_name": "Pooja Iyer (Senior Remote Sensing Scientist)",
                        "observation_date": datetime.datetime(2024, 4, 18, 12, 45),
                        "condition_rating": "GOOD",
                        "remarks": "Masonry weir verified via multi-spectral Sentinel-2 NDWI and on-site ground audit. Surface water ponding sustained through March. (DEMO / SEEDED DATA)",
                        "recommended_action": "Desiltation recommended in 2027 cycle."
                    }
                ]
            },
            {
                "watershed_id": ws_arv.id,
                "code": "INT-ARV-CCT-03",
                "name": "Aravalli Ridge Staggered Contour Trenches",
                "intervention_type": "CONTOUR_BUNDING",
                "status": "WORK_IN_PROGRESS",
                "sanction_year": 2023,
                "completion_date": None,
                "latitude": 27.2890,
                "longitude": 76.2680,
                "target_capacity_cum": 8000.0,
                "beneficiary_count": 110,
                "cost_inr": 520000.0,
                "before_metrics": {"slope_wash_severity": "SEVERE", "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"sediment_trapping_pct": 60.0, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Arrested torrential hill-slope runoff and topsoil detachment; stone pitch completed.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": []
            },
            {
                "watershed_id": ws_arv.id,
                "code": "INT-ARV-AFF-04",
                "name": "Silvi-Pasture & Dhok Catchment Afforestation",
                "intervention_type": "AFFORESTATION",
                "status": "SANCTIONED",
                "sanction_year": 2024,
                "completion_date": None,
                "latitude": 27.2950,
                "longitude": 76.2750,
                "target_capacity_cum": 4500.0,
                "beneficiary_count": 90,
                "cost_inr": 380000.0,
                "before_metrics": {"canopy_cover_pct": 6.5, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"projected_canopy_cover_pct": 28.0, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "Community pasture protection initiated with native Anogeissus pendula saplings.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": []
            },
            {
                "watershed_id": ws_arv.id,
                "code": "INT-ARV-RS-05",
                "name": "Upper Drainage Sub-surface Check Dam & Recharge Shaft",
                "intervention_type": "CHECK_DAM",
                "status": "PROPOSED",
                "sanction_year": 2024,
                "completion_date": None,
                "latitude": 27.2710,
                "longitude": 76.2480,
                "target_capacity_cum": 9200.0,
                "beneficiary_count": 125,
                "cost_inr": 640000.0,
                "before_metrics": {"monsoon_flash_runoff_duration_hrs": 4.5, "source_type": "DEMO / SEEDED DATA"},
                "after_metrics": {"projected_baseflow_retention_days": 60.0, "source_type": "DEMO / SEEDED DATA"},
                "observed_change_summary": "DPR prepared under community consultation; pending district sanction.",
                "source_type": "DEMO / SEEDED DATA",
                "observations": []
            }
        ])

    seeded_intv_count = 0
    seeded_obs_count = 0

    try:
        for intv_data in DEMO_INTERVENTIONS:
            code = intv_data["code"]
            existing = db.query(Intervention).filter(Intervention.code == code).first()
            
            if existing:
                # Update attributes to ensure calibrated values and source_type consistency
                existing.watershed_id = intv_data["watershed_id"]
                existing.name = intv_data["name"]
                existing.intervention_type = intv_data["intervention_type"]
                existing.status = intv_data["status"]
                existing.sanction_year = intv_data["sanction_year"]
                existing.completion_date = intv_data["completion_date"]
                existing.latitude = intv_data["latitude"]
                existing.longitude = intv_data["longitude"]
                existing.target_capacity_cum = intv_data["target_capacity_cum"]
                existing.beneficiary_count = intv_data["beneficiary_count"]
                existing.cost_inr = intv_data["cost_inr"]
                existing.before_metrics = intv_data["before_metrics"]
                existing.after_metrics = intv_data["after_metrics"]
                existing.observed_change_summary = intv_data["observed_change_summary"]
                if has_source_type:
                    existing.source_type = intv_data["source_type"]
                intv_record = existing
            else:
                create_kwargs = {
                    "watershed_id": intv_data["watershed_id"],
                    "code": code,
                    "name": intv_data["name"],
                    "intervention_type": intv_data["intervention_type"],
                    "status": intv_data["status"],
                    "sanction_year": intv_data["sanction_year"],
                    "completion_date": intv_data["completion_date"],
                    "latitude": intv_data["latitude"],
                    "longitude": intv_data["longitude"],
                    "target_capacity_cum": intv_data["target_capacity_cum"],
                    "beneficiary_count": intv_data["beneficiary_count"],
                    "cost_inr": intv_data["cost_inr"],
                    "before_metrics": intv_data["before_metrics"],
                    "after_metrics": intv_data["after_metrics"],
                    "observed_change_summary": intv_data["observed_change_summary"]
                }
                if has_source_type:
                    create_kwargs["source_type"] = intv_data["source_type"]
                intv_record = Intervention(**create_kwargs)
                db.add(intv_record)
                db.flush()
            
            seeded_intv_count += 1

            # Seed linked inspection observations only if intervention_id column exists
            if has_intervention_id and intv_record.id:
                for obs_def in intv_data.get("observations", []):
                    existing_obs = db.query(Observation).filter(
                        Observation.intervention_id == intv_record.id,
                        Observation.observer_name == obs_def["observer_name"]
                    ).first()

                    if existing_obs:
                        existing_obs.condition_rating = obs_def["condition_rating"]
                        existing_obs.remarks = obs_def["remarks"]
                        existing_obs.recommended_action = obs_def["recommended_action"]
                        existing_obs.observation_date = obs_def["observation_date"]
                    else:
                        db.add(Observation(
                            watershed_id=intv_record.watershed_id,
                            intervention_id=intv_record.id,
                            observer_name=obs_def["observer_name"],
                            observation_date=obs_def["observation_date"],
                            condition_rating=obs_def["condition_rating"],
                            remarks=obs_def["remarks"],
                            recommended_action=obs_def["recommended_action"]
                        ))
                    seeded_obs_count += 1

        db.commit()
        print(f"Seeded/verified {seeded_intv_count} baseline Intervention structures and {seeded_obs_count} field observations.")
    except Exception as e:
        db.rollback()
        print(f"Warning in seed_interventions: {e}")
        raise



