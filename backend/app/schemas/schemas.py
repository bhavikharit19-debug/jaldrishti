import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

# Health Check
class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    database: str = "connected"
    version: str = "1.0.0"
    timestamp: datetime.datetime

# Geographic Hierarchy
class DistrictResponse(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    state_id: int
    model_config = ConfigDict(from_attributes=True)

class StateResponse(BaseModel):
    id: int
    name: str
    code: str
    districts: List[DistrictResponse] = []
    model_config = ConfigDict(from_attributes=True)

class StateListItem(BaseModel):
    id: int
    name: str
    code: str
    district_count: int = 0
    watershed_count: int = 0
    model_config = ConfigDict(from_attributes=True)

class DistrictListItem(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    state_id: int
    state_name: Optional[str] = None
    watershed_count: int = 0
    model_config = ConfigDict(from_attributes=True)

class WatershedLocateResult(BaseModel):
    watershed_id: int
    watershed_name: str
    watershed_code: str
    district_name: str
    state_name: str
    is_inside: bool
    distance_to_centroid_km: float
    centroid_lat: float
    centroid_lng: float

# Watershed
class WatershedBoundaryResponse(BaseModel):
    id: int
    watershed_id: int
    geometry: Dict[str, Any]
    centroid_lat: float
    centroid_lng: float
    bbox: List[float] # [min_lng, min_lat, max_lng, max_lat]
    model_config = ConfigDict(from_attributes=True)

class WatershedListItem(BaseModel):
    id: int
    code: str
    name: str
    district_id: int
    district_name: Optional[str] = None
    state_id: int
    state_name: Optional[str] = None
    area_hectares: float
    health_score: float
    risk_level: str
    status: str
    model_config = ConfigDict(from_attributes=True)

class WatershedDetail(BaseModel):
    id: int
    code: str
    name: str
    district_id: int
    district_name: Optional[str] = None
    state_id: int
    state_name: Optional[str] = None
    area_hectares: float
    river_basin: Optional[str] = None
    sub_basin: Optional[str] = None
    agro_climatic_zone: Optional[str] = None
    primary_drainage: Optional[str] = None
    health_score: float
    risk_level: str
    status: str
    boundary: Optional[WatershedBoundaryResponse] = None
    model_config = ConfigDict(from_attributes=True)

# GIS Layers
class GISLayerResponse(BaseModel):
    id: int
    watershed_id: int
    layer_type: str
    name: str
    format: str
    data_payload: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    is_active: bool
    source_type: str
    model_config = ConfigDict(from_attributes=True)

class GISLayerSummary(BaseModel):
    id: int
    watershed_id: int
    layer_type: str
    name: str
    format: str
    feature_count: int = 0
    is_active: bool
    source_type: str
    model_config = ConfigDict(from_attributes=True)

# GIS Thematic Statistics
class LULCCategoryStat(BaseModel):
    category: str
    area_ha: float
    percentage: float
    color: str
    description: Optional[str] = None

class DrainageStat(BaseModel):
    total_length_km: float
    density_km_per_sqkm: float
    order_counts: Dict[str, int]
    primary_stream: str
    total_streams: int

class WaterBodyStat(BaseModel):
    total_count: int
    total_spread_ha: float
    cumulative_capacity_tcm: float
    structures_by_type: Dict[str, int]

class VegetationStat(BaseModel):
    mean_ndvi: float
    dense_pct: float
    moderate_pct: float
    low_pct: float
    sparse_pct: float
    vigor_class: str

class ElevationBandStat(BaseModel):
    band_name: str
    elevation_range_m: str
    area_ha: float
    percentage: float
    slope_class: str
    color: str

class ElevationStat(BaseModel):
    min_elevation_m: float
    max_elevation_m: float
    relief_m: float
    dominant_slope_class: str
    elevation_bands: List[ElevationBandStat] = []

class WatershedGISStatsResponse(BaseModel):
    watershed_id: int
    watershed_name: str
    watershed_code: str
    total_area_ha: float
    lulc: List[LULCCategoryStat]
    drainage: DrainageStat
    water_bodies: WaterBodyStat
    vegetation: VegetationStat
    elevation: ElevationStat
    interventions_count: int
    field_photos_count: int
    data_provenance: str = "DEMO DATA"
    disclaimer: str = "DEMO DATA: Baseline geospatial layers and biophysical distributions calibrated for SIH 26015 decision-support prototyping."

# Field Photos
class FieldPhotoCreate(BaseModel):
    watershed_id: int
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees (-90 to +90)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees (-180 to +180)")
    photo_url: str
    category: str
    description: Optional[str] = None
    intervention_id: Optional[int] = None
    exif_metadata: Optional[Dict[str, Any]] = None
    uploader_role: Optional[str] = "FIELD_OFFICER"

class FieldPhotoUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    verification_status: Optional[str] = None # VERIFIED, PENDING, REJECTED
    intervention_id: Optional[int] = None

class FieldPhotoResponse(BaseModel):
    id: int
    watershed_id: int
    latitude: float
    longitude: float
    captured_at: datetime.datetime
    uploaded_at: datetime.datetime
    photo_url: str
    category: str
    description: Optional[str] = None
    intervention_id: Optional[int] = None
    verification_status: str
    source_type: str
    provenance: Optional[str] = "DEMO_DATA"
    exif_metadata: Optional[Dict[str, Any]] = None
    uploader_role: str
    model_config = ConfigDict(from_attributes=True)

# Field Observations
class ObservationCreate(BaseModel):
    watershed_id: int
    observer_name: str
    condition_rating: str = "GOOD" # EXCELLENT, GOOD, MODERATE, CRITICAL
    remarks: Optional[str] = None
    recommended_action: Optional[str] = None
    field_photo_id: Optional[int] = None
    intervention_id: Optional[int] = None
    observation_date: Optional[datetime.datetime] = None

class ObservationUpdate(BaseModel):
    condition_rating: Optional[str] = None
    remarks: Optional[str] = None
    recommended_action: Optional[str] = None

class ObservationResponse(BaseModel):
    id: int
    watershed_id: int
    field_photo_id: Optional[int] = None
    intervention_id: Optional[int] = None
    observer_name: str
    observation_date: datetime.datetime
    condition_rating: str
    remarks: Optional[str] = None
    recommended_action: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Health Score Breakdown
class HealthScoreComponent(BaseModel):
    name: str
    category: str
    weight: float
    score: float # 0-100
    weighted_contribution: float
    status: str
    description: str

class HealthScoreResponse(BaseModel):
    watershed_id: int
    watershed_name: str
    overall_health_score: float
    category_rating: str # EXCELLENT, GOOD, VULNERABLE, CRITICAL
    components: List[HealthScoreComponent]
    data_source_disclaimer: str = "Calculated using seeded baseline indicator weights for demonstration."

# Change Detection
class IndicatorDelta(BaseModel):
    indicator_code: str
    indicator_name: str
    from_value: float
    to_value: float
    unit: str
    delta_absolute: float
    delta_percentage: float
    trend: str # IMPROVED, STABLE, DEGRADED

class YearlyDataPoint(BaseModel):
    year: int
    ndvi: float
    ndwi: float
    soil_moisture: float
    water_spread_ha: float

class ChangeDetectionResponse(BaseModel):
    watershed_id: int
    from_year: int
    to_year: int
    indicators: List[IndicatorDelta]
    yearly_trends: List[YearlyDataPoint]
    summary_analysis: str
    priority_hotspots_count: int
    disclaimer: str = "Based on calibrated historical demo dataset spanning 2018-2024."

# Predictions
class PredictionItem(BaseModel):
    id: int
    target_metric: str
    prediction_horizon_months: int
    predicted_value: float
    confidence_lower: float
    confidence_upper: float
    confidence_score: float
    model_name: str
    model_version: Optional[str] = "1.0.0"
    status: Optional[str] = "PROTOTYPE_CALIBRATED"
    features_used: List[str]
    feature_importances: Optional[Dict[str, float]] = None
    rationale: str
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class PredictionResponse(BaseModel):
    watershed_id: int
    predictions: List[PredictionItem]
    model_architecture: str = "Scikit-Learn Ridge Regression with Monte Carlo Uncertainty Bands"
    disclaimer: str = "PROTOTYPE PREDICTIVE INTELLIGENCE: Calibrated on 2018-2024 historical trajectories. Designed for seamless transition to official satellite/EO models."

# Risk Assessments
class RiskItem(BaseModel):
    id: int
    risk_category: str
    risk_level: str
    score: float
    primary_driver: str
    evidence_summary: str
    contributing_factors: Optional[List[str]] = None
    spatial_hotspots: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = "1.0.0"
    model_config = ConfigDict(from_attributes=True)

class RiskAssessmentResponse(BaseModel):
    watershed_id: int
    overall_risk_level: str
    risks: List[RiskItem]
    disclaimer: str = "Multi-criteria risk engine synthesizing current biophysical indicators, rate of change deltas, and predictive outlooks."

# Recommendations
class RecommendationItem(BaseModel):
    id: int
    intervention_type: str
    category: Optional[str] = "WATER_HARVESTING" # WATER_HARVESTING, SOIL_CONSERVATION, VEGETATION_RESTORATION, DRAINAGE_TREATMENT, INTERVENTION_MONITORING
    priority: str
    problem_statement: str
    evidence_basis: str
    estimated_cost_inr: Optional[str] = None
    expected_impact: str
    target_location_geojson: Optional[Dict[str, Any]] = None
    status: str
    model_config = ConfigDict(from_attributes=True)

class RecommendationResponse(BaseModel):
    watershed_id: int
    recommendations: List[RecommendationItem]
    notice: str = "DECISION SUPPORT NOTICE: Suggestions are algorithmic decision-support recommendations. Mandatory ground DGPS survey, soil testing, and sanctioned DPR required."

# Interventions
class InterventionCreate(BaseModel):
    watershed_id: int
    code: str
    name: str
    intervention_type: str
    status: str = "PROPOSED" # PROPOSED, SANCTIONED, WORK_IN_PROGRESS, COMPLETED
    sanction_year: int = 2024
    completion_date: Optional[datetime.datetime] = None
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    target_capacity_cum: float = 1200.0
    beneficiary_count: int = 45
    cost_inr: float = 450000.0
    before_metrics: Optional[Dict[str, Any]] = None
    after_metrics: Optional[Dict[str, Any]] = None
    observed_change_summary: Optional[str] = None

class InterventionUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    completion_date: Optional[datetime.datetime] = None
    target_capacity_cum: Optional[float] = None
    beneficiary_count: Optional[int] = None
    cost_inr: Optional[float] = None
    before_metrics: Optional[Dict[str, Any]] = None
    after_metrics: Optional[Dict[str, Any]] = None
    observed_change_summary: Optional[str] = None

class InterventionItem(BaseModel):
    id: int
    watershed_id: int
    code: str
    name: str
    intervention_type: str
    status: str
    sanction_year: int
    completion_date: Optional[datetime.datetime] = None
    latitude: float
    longitude: float
    target_capacity_cum: float
    beneficiary_count: int
    cost_inr: float
    before_metrics: Optional[Dict[str, Any]] = None
    after_metrics: Optional[Dict[str, Any]] = None
    observed_change_summary: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Biophysical Indicators
class IndicatorItem(BaseModel):
    id: int
    code: str
    name: str
    category: str
    unit: Optional[str] = None
    description: Optional[str] = None
    weight_in_health_score: float = 0.25
    model_config = ConfigDict(from_attributes=True)

class WatershedIndicatorValue(BaseModel):
    id: int
    indicator_code: str
    indicator_name: str
    category: str
    unit: Optional[str] = None
    recorded_year: int
    recorded_month: int
    value: float
    normalized_score: float
    source_type: str
    model_config = ConfigDict(from_attributes=True)

# Alerts
class AlertCreate(BaseModel):
    watershed_id: int
    alert_type: str
    severity: str = "MEDIUM" # LOW, MEDIUM, HIGH, CRITICAL
    trigger_reason: str
    supporting_indicator: Optional[str] = None

class AlertItem(BaseModel):
    id: int
    watershed_id: int
    alert_type: str
    severity: str
    trigger_reason: str
    supporting_indicator: Optional[str] = None
    status: str
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# Reports
class ReportSummaryItem(BaseModel):
    watershed_id: int
    watershed_code: str
    watershed_name: str
    district_name: Optional[str] = None
    state_name: Optional[str] = None
    health_score: float
    category_rating: str
    active_alerts_count: int
    completed_interventions_count: int
    generated_at: datetime.datetime

class WatershedReportResponse(BaseModel):
    watershed: WatershedDetail
    health_score: HealthScoreResponse
    active_alerts_count: int
    high_risks_count: int
    completed_interventions_count: int
    total_beneficiaries: int
    change_summary: str
    top_recommendations: List[RecommendationItem]
    generated_at: datetime.datetime

# Data Integration & Ingestion
class GeospatialDatasetResponse(BaseModel):
    id: int
    dataset_code: str
    dataset_name: str
    dataset_type: str
    provider: str
    watershed_id: Optional[int] = None
    acquisition_date: Optional[datetime.datetime] = None
    processing_date: Optional[datetime.datetime] = None
    spatial_resolution: Optional[str] = None
    temporal_resolution: Optional[str] = None
    coverage_bounds: Optional[List[float]] = None
    crs: str
    provenance: str
    format: str
    record_count: int
    license_info: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class DatasetCatalogResponse(BaseModel):
    total_datasets: int
    datasets: List[GeospatialDatasetResponse]
    provenance_summary: Dict[str, Any]

class DataIngestionJobResponse(BaseModel):
    id: int
    job_id: str
    watershed_id: Optional[int] = None
    dataset_id: Optional[int] = None
    source_format: str
    status: str
    records_processed: int
    records_failed: int
    log_messages: List[str]
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ProviderAdapterResponse(BaseModel):
    provider_code: str
    provider_name: str
    status: str
    endpoint: str
    has_credentials: bool
    spatial_resolution: Optional[str] = None
    operational_notes: Optional[str] = None
    supported_bands: Optional[List[str]] = None
    thematic_layers: Optional[List[str]] = None
    derived_indices: Optional[List[str]] = None

# ==========================================
# Authentication & Role-Based Access Schemas
# ==========================================

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    watershed_id: Optional[int] = None
    organization: Optional[str] = None
    designation: Optional[str] = None
    is_active: bool
    created_at: datetime.datetime
    last_login: Optional[datetime.datetime] = None
    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str
    remember_me: bool = False

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserResponse

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "ANALYST"
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    watershed_id: Optional[int] = None
    organization: Optional[str] = None
    designation: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    watershed_id: Optional[int] = None
    organization: Optional[str] = None
    designation: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class AccessRequestCreate(BaseModel):
    name: str
    email: str
    requested_role: str
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    organization: str
    designation: Optional[str] = None
    reason: str

class AccessRequestResponse(BaseModel):
    id: int
    name: str
    email: str
    requested_role: str
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    organization: str
    designation: Optional[str] = None
    reason: str
    status: str
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime.datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class AccessRequestReview(BaseModel):
    action: str  # APPROVE or REJECT
    temporary_password: Optional[str] = None
    rejection_reason: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: int
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime.datetime
    ip_address: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class DemoAccountResponse(BaseModel):
    name: str
    email: str
    role: str
    jurisdiction: str
    organization: str
    demo_password: str
    description: str

class UserRegisterRequest(BaseModel):
    name: str
    email: str
    organization: str
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    requested_role: str = "FIELD_OFFICER"
    password: str
    confirm_password: str

class RegistrationResponse(BaseModel):
    message: str
    status: str
    request_id: Optional[int] = None

class ForgotPasswordRequest(BaseModel):
    email: str

class ForgotPasswordResponse(BaseModel):
    message: str
    status: str
    support_contact: str



