import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, 
    Text, JSON, Boolean
)
from sqlalchemy.orm import relationship
from app.core.database import Base

class State(Base):
    __tablename__ = "states"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    
    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")
    watersheds = relationship("Watershed", back_populates="state")

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), index=True)
    
    state = relationship("State", back_populates="districts")
    watersheds = relationship("Watershed", back_populates="district")

class Watershed(Base):
    __tablename__ = "watersheds"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    
    area_hectares = Column(Float, nullable=False)
    river_basin = Column(String(100))
    sub_basin = Column(String(100))
    agro_climatic_zone = Column(String(150))
    primary_drainage = Column(String(100))
    
    health_score = Column(Float, default=70.0) # 0-100
    risk_level = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), default="ACTIVE")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    district = relationship("District", back_populates="watersheds")
    state = relationship("State", back_populates="watersheds")
    boundary = relationship("WatershedBoundary", back_populates="watershed", uselist=False, cascade="all, delete-orphan")
    gis_layers = relationship("GISLayer", back_populates="watershed", cascade="all, delete-orphan")
    field_photos = relationship("FieldPhoto", back_populates="watershed", cascade="all, delete-orphan")
    indicator_values = relationship("IndicatorValue", back_populates="watershed", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="watershed", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="watershed", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="watershed", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="watershed", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="watershed", cascade="all, delete-orphan")

class WatershedBoundary(Base):
    __tablename__ = "watershed_boundaries"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), unique=True, nullable=False)
    
    # GeoJSON Feature or Geometry definition
    geometry = Column(JSON, nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lng = Column(Float, nullable=False)
    bbox = Column(JSON, nullable=False) # [min_lng, min_lat, max_lng, max_lat]
    
    watershed = relationship("Watershed", back_populates="boundary")

class DataSource(Base):
    __tablename__ = "data_sources"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    source_type = Column(String(50), nullable=False) # DEMO, OFFICIAL, FIELD_UPLOAD, SATELLITE_API
    provider_name = Column(String(150))
    description = Column(Text)
    reliability_score = Column(Float, default=0.95)
    is_active = Column(Boolean, default=True)

class GISLayer(Base):
    __tablename__ = "gis_layers"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False)
    
    # BOUNDARY, DRAINAGE, WATER_BODIES, LULC, VEGETATION_NDVI, ELEVATION, RISK_ZONES, INTERVENTIONS
    layer_type = Column(String(50), nullable=False)
    name = Column(String(150), nullable=False)
    format = Column(String(50), default="GEOJSON") # GEOJSON, VECTOR_TILE, RASTER_WMS
    data_payload = Column(JSON, nullable=True) # Full GeoJSON FeatureCollection
    url = Column(String(500), nullable=True)
    metadata_json = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    source_type = Column(String(50), default="DEMO") # DEMO, OFFICIAL, FIELD_UPLOAD
    
    watershed = relationship("Watershed", back_populates="gis_layers")

class FieldPhoto(Base):
    __tablename__ = "field_photos"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    captured_at = Column(DateTime, default=datetime.datetime.utcnow)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    photo_url = Column(String(500), nullable=False)
    
    # CHECK_DAM, DESILTATION, WATER_BODY, EROSION, FARM_POND, PLANTATION, AFFORESTATION, CANAL
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    intervention_id = Column(Integer, nullable=True)
    verification_status = Column(String(30), default="VERIFIED") # PENDING, VERIFIED, REJECTED
    source_type = Column(String(50), default="DEMO") # DEMO, OFFICIAL, FIELD_UPLOAD
    provenance = Column(String(50), default="DEMO_DATA") # DEMO_DATA, IMPORTED_DATA, OFFICIAL_SOURCE
    exif_metadata = Column(JSON, default=dict)
    uploader_role = Column(String(50), default="FIELD_OFFICER")
    
    watershed = relationship("Watershed", back_populates="field_photos")
    observations = relationship("Observation", back_populates="field_photo", cascade="all, delete-orphan")

class Observation(Base):
    __tablename__ = "observations"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False, index=True)
    field_photo_id = Column(Integer, ForeignKey("field_photos.id"), nullable=True, index=True)
    intervention_id = Column(Integer, ForeignKey("interventions.id"), nullable=True, index=True)
    
    observer_name = Column(String(100), nullable=False)
    observation_date = Column(DateTime, default=datetime.datetime.utcnow)
    condition_rating = Column(String(30), default="GOOD") # EXCELLENT, GOOD, MODERATE, CRITICAL
    remarks = Column(Text)
    recommended_action = Column(Text)
    
    field_photo = relationship("FieldPhoto", back_populates="observations")
    intervention = relationship("Intervention", back_populates="observations")

class Indicator(Base):
    __tablename__ = "indicators"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False) # NDVI, NDWI, SMI, RUNOFF_COEFF, WATER_SPREAD
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False) # HYDROLOGICAL, VEGETATION, LAND_CONDITION
    unit = Column(String(30))
    description = Column(Text)
    weight_in_health_score = Column(Float, default=0.25)
    
    values = relationship("IndicatorValue", back_populates="indicator")

class IndicatorValue(Base):
    __tablename__ = "indicator_values"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), nullable=False)
    
    recorded_year = Column(Integer, nullable=False)
    recorded_month = Column(Integer, default=6) # 1-12
    value = Column(Float, nullable=False)
    normalized_score = Column(Float, default=50.0) # 0-100 scale
    source_type = Column(String(50), default="DEMO")
    
    watershed = relationship("Watershed", back_populates="indicator_values")
    indicator = relationship("Indicator", back_populates="values")

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False, index=True)
    
    target_metric = Column(String(100), nullable=False) # WATER_STRESS_INDEX_12M, VEGETATION_DEGRADATION_RISK, LAND_CONDITION_DETERIORATION_24M
    prediction_horizon_months = Column(Integer, default=12) # 6, 12, 24
    predicted_value = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=False)
    confidence_upper = Column(Float, nullable=False)
    confidence_score = Column(Float, default=0.88)
    
    model_name = Column(String(100), default="Ridge-EO-Ensemble-v1")
    model_version = Column(String(50), default="1.0.0")
    status = Column(String(50), default="PROTOTYPE_CALIBRATED")
    features_used = Column(JSON, default=list)
    feature_importances = Column(JSON, default=dict)
    rationale = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    watershed = relationship("Watershed", back_populates="predictions")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False, index=True)
    
    risk_category = Column(String(100), nullable=False) # WATER_STRESS, VEGETATION_DEGRADATION, SOIL_EROSION
    risk_level = Column(String(20), nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    score = Column(Float, default=50.0) # 0-100
    primary_driver = Column(String(200))
    evidence_summary = Column(Text)
    contributing_factors = Column(JSON, default=list)
    spatial_hotspots = Column(JSON, default=dict) # GeoJSON points or bounds
    model_version = Column(String(50), default="1.0.0")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    watershed = relationship("Watershed", back_populates="risk_assessments")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False, index=True)
    
    intervention_type = Column(String(100), nullable=False) # CHECK_DAM, FARM_POND, CONTOUR_BUND, PERCOLATION_TANK, AFFORESTATION
    category = Column(String(100), default="WATER_HARVESTING") # WATER_HARVESTING, SOIL_CONSERVATION, VEGETATION_RESTORATION, DRAINAGE_TREATMENT, INTERVENTION_MONITORING
    priority = Column(String(20), default="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    problem_statement = Column(Text, nullable=False)
    evidence_basis = Column(Text, nullable=False)
    estimated_cost_inr = Column(String(50))
    expected_impact = Column(Text)
    target_location_geojson = Column(JSON, default=dict)
    status = Column(String(30), default="DRAFT") # DRAFT, APPROVED, IN_PROGRESS
    
    watershed = relationship("Watershed", back_populates="recommendations")

class Intervention(Base):
    __tablename__ = "interventions"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False)
    
    code = Column(String(50), nullable=False)
    name = Column(String(150), nullable=False)
    intervention_type = Column(String(100), nullable=False)
    status = Column(String(50), default="COMPLETED") # PROPOSED, SANCTIONED, WORK_IN_PROGRESS, COMPLETED
    sanction_year = Column(Integer, default=2021)
    completion_date = Column(DateTime, nullable=True)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    target_capacity_cum = Column(Float, default=1200.0)
    beneficiary_count = Column(Integer, default=45)
    cost_inr = Column(Float, default=450000.0)
    
    before_metrics = Column(JSON, default=dict)
    after_metrics = Column(JSON, default=dict)
    observed_change_summary = Column(Text)
    
    watershed = relationship("Watershed", back_populates="interventions")
    observations = relationship("Observation", back_populates="intervention", cascade="all, delete-orphan")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False)
    
    alert_type = Column(String(100), nullable=False) # RAPID_VEGETATION_DECLINE, WATER_BODY_SHRINKAGE, CRITICAL_STRESS
    severity = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    trigger_reason = Column(Text, nullable=False)
    supporting_indicator = Column(String(100))
    status = Column(String(30), default="ACTIVE") # ACTIVE, ACKNOWLEDGED, RESOLVED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    watershed = relationship("Watershed", back_populates="alerts")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), default="system")
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    ip_address = Column(String(50), nullable=True)

class GeospatialDataset(Base):
    __tablename__ = "geospatial_datasets"
    id = Column(Integer, primary_key=True, index=True)
    dataset_code = Column(String(100), unique=True, nullable=False, index=True)
    dataset_name = Column(String(200), nullable=False)
    dataset_type = Column(String(100), nullable=False) # SATELLITE_OPTICAL, DEM_ELEVATION, LULC, NDVI, NDWI, DRAINAGE_NETWORK, WATER_BODIES, FIELD_SURVEY
    provider = Column(String(150), nullable=False) # Copernicus ESA, USGS, NRSC Bhuvan, Survey of India, Field Survey, Uploaded File
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=True, index=True)
    
    acquisition_date = Column(DateTime, nullable=True)
    processing_date = Column(DateTime, default=datetime.datetime.utcnow)
    spatial_resolution = Column(String(100), default="10m")
    temporal_resolution = Column(String(100), nullable=True)
    coverage_bounds = Column(JSON, default=list) # [min_lng, min_lat, max_lng, max_lat]
    crs = Column(String(50), default="EPSG:4326")
    provenance = Column(String(50), default="DEMO_DATA") # DEMO_DATA, IMPORTED_DATA, OFFICIAL_SOURCE
    format = Column(String(50), default="GEOJSON") # GEOJSON, CSV, SHAPEFILE, GEOTIFF
    
    file_path = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, default=0)
    checksum_sha256 = Column(String(64), nullable=True)
    record_count = Column(Integer, default=0)
    license_info = Column(String(200), default="Open Data / Government Use")
    metadata_json = Column(JSON, default=dict)
    status = Column(String(50), default="ACTIVE") # ACTIVE, PROCESSING, ARCHIVED, FAILED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    watershed = relationship("Watershed", backref="datasets")

class DataIngestionJob(Base):
    __tablename__ = "data_ingestion_jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, nullable=False, index=True)
    dataset_id = Column(Integer, ForeignKey("geospatial_datasets.id"), nullable=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=True)
    source_format = Column(String(50), nullable=False) # GEOJSON, CSV, SHAPEFILE, GEOTIFF
    status = Column(String(50), default="PENDING") # PENDING, VALIDATING, PROCESSING, COMPLETED, FAILED
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    log_messages = Column(JSON, default=list)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="ANALYST") # ADMIN, STATE_OFFICER, DISTRICT_OFFICER, FIELD_OFFICER, ANALYST
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=True)
    organization = Column(String(150), nullable=True)
    designation = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    state = relationship("State")
    district = relationship("District")
    watershed = relationship("Watershed")

class AccessRequest(Base):
    __tablename__ = "access_requests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), index=True, nullable=False)
    requested_role = Column(String(50), nullable=False) # STATE_OFFICER, DISTRICT_OFFICER, FIELD_OFFICER, ANALYST
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    organization = Column(String(150), nullable=False)
    designation = Column(String(150), nullable=True)
    reason = Column(Text, nullable=False)
    status = Column(String(30), default="PENDING") # PENDING, APPROVED, REJECTED
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    state = relationship("State")
    district = relationship("District")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


