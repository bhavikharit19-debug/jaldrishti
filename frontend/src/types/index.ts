export interface StateHierarchy {
  id: number;
  name: string;
  code: string;
  districts: {
    id: number;
    name: string;
    code?: string;
    state_id: number;
  }[];
}

export interface WatershedBoundary {
  id: number;
  watershed_id: number;
  geometry: any;
  centroid_lat: number;
  centroid_lng: number;
  bbox: [number, number, number, number]; // [min_lng, min_lat, max_lng, max_lat]
}

export interface WatershedListItem {
  id: number;
  code: string;
  name: string;
  district_id: number;
  district_name?: string;
  state_id: number;
  state_name?: string;
  area_hectares: number;
  health_score: number;
  risk_level: string;
  status: string;
}

export interface WatershedDetail extends WatershedListItem {
  river_basin?: string;
  sub_basin?: string;
  agro_climatic_zone?: string;
  primary_drainage?: string;
  boundary?: WatershedBoundary;
}

export interface GISLayer {
  id: number;
  watershed_id: number;
  layer_type: 'BOUNDARY' | 'DRAINAGE' | 'WATER_BODIES' | 'LULC' | 'VEGETATION_NDVI' | 'ELEVATION' | 'RISK_ZONES' | 'INTERVENTIONS';
  name: string;
  format: string;
  data_payload?: any;
  url?: string;
  metadata_json?: any;
  is_active: boolean;
  source_type: string;
  provenance?: string;
}

export interface LULCCategoryStat {
  category: string;
  area_ha: number;
  percentage: number;
  color: string;
  description?: string;
}

export interface DrainageStat {
  total_length_km: number;
  density_km_per_sqkm: number;
  order_counts: Record<string, number>;
  primary_stream: string;
  total_streams: number;
}

export interface WaterBodyStat {
  total_count: number;
  total_spread_ha: number;
  cumulative_capacity_tcm: number;
  structures_by_type: Record<string, number>;
}

export interface VegetationStat {
  mean_ndvi: number;
  dense_pct: number;
  moderate_pct: number;
  low_pct: number;
  sparse_pct: number;
  vigor_class: string;
}

export interface ElevationBandStat {
  band_name: string;
  elevation_range_m: string;
  area_ha: number;
  percentage: number;
  slope_class: string;
  color: string;
}

export interface ElevationStat {
  min_elevation_m: number;
  max_elevation_m: number;
  relief_m: number;
  dominant_slope_class: string;
  elevation_bands: ElevationBandStat[];
}

export interface WatershedGISStats {
  watershed_id: number;
  watershed_name: string;
  watershed_code: string;
  total_area_ha: number;
  lulc: LULCCategoryStat[];
  drainage: DrainageStat;
  water_bodies: WaterBodyStat;
  vegetation: VegetationStat;
  elevation: ElevationStat;
  interventions_count: number;
  field_photos_count: number;
  data_provenance: string;
  disclaimer: string;
}

export interface FieldPhoto {
  id: number;
  watershed_id: number;
  latitude: number;
  longitude: number;
  captured_at: string;
  uploaded_at: string;
  photo_url: string;
  category: string;
  description?: string;
  intervention_id?: number;
  verification_status: 'VERIFIED' | 'PENDING' | 'REJECTED';
  source_type: string;
  provenance?: string;
  exif_metadata?: any;
  uploader_role: string;
}

export interface HealthScoreComponent {
  name: string;
  category: string;
  weight: number;
  score: number;
  weighted_contribution: number;
  status: string;
  description: string;
}

export interface HealthScore {
  watershed_id: number;
  watershed_name: string;
  overall_health_score: number;
  category_rating: 'EXCELLENT' | 'GOOD' | 'VULNERABLE' | 'CRITICAL';
  components: HealthScoreComponent[];
  data_source_disclaimer: string;
}

export interface IndicatorDelta {
  indicator_code: string;
  indicator_name: string;
  from_value: number;
  to_value: number;
  unit: string;
  delta_absolute: number;
  delta_percentage: number;
  trend: 'IMPROVED' | 'STABLE' | 'DEGRADED';
}

export interface YearlyDataPoint {
  year: number;
  ndvi: number;
  ndwi: number;
  soil_moisture: number;
  water_spread_ha: number;
}

export interface ChangeDetection {
  watershed_id: number;
  from_year: number;
  to_year: number;
  indicators: IndicatorDelta[];
  yearly_trends: YearlyDataPoint[];
  summary_analysis: string;
  priority_hotspots_count: number;
  disclaimer: string;
}

export interface PredictionItem {
  id: number;
  target_metric: string;
  prediction_horizon_months: number;
  predicted_value: number;
  confidence_lower: number;
  confidence_upper: number;
  confidence_score: number;
  model_name: string;
  features_used: string[];
  rationale: string;
  created_at: string;
}

export interface PredictionResponse {
  watershed_id: number;
  predictions: PredictionItem[];
  model_architecture: string;
  disclaimer: string;
}

export interface RiskItem {
  id: number;
  risk_category: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  score: number;
  primary_driver: string;
  evidence_summary: string;
  spatial_hotspots?: any;
}

export interface RiskAssessmentResponse {
  watershed_id: number;
  overall_risk_level: string;
  risks: RiskItem[];
  disclaimer: string;
}

export interface RecommendationItem {
  id: number;
  intervention_type: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  problem_statement: string;
  evidence_basis: string;
  estimated_cost_inr?: string;
  expected_impact: string;
  target_location_geojson?: any;
  status: string;
}

export interface RecommendationResponse {
  watershed_id: number;
  recommendations: RecommendationItem[];
  notice: string;
}

export interface InterventionItem {
  id: number;
  code: string;
  name: string;
  intervention_type: string;
  status: string;
  sanction_year: number;
  completion_date?: string;
  latitude: number;
  longitude: number;
  target_capacity_cum: number;
  beneficiary_count: number;
  cost_inr: number;
  before_metrics?: any;
  after_metrics?: any;
  observed_change_summary?: string;
  source_type?: string;
}

export interface AlertItem {
  id: number;
  alert_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  trigger_reason: string;
  supporting_indicator?: string;
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
  created_at: string;
}

export interface WatershedReport {
  watershed: WatershedDetail;
  health_score: HealthScore;
  active_alerts_count: number;
  high_risks_count: number;
  completed_interventions_count: number;
  total_beneficiaries: number;
  change_summary: string;
  top_recommendations: RecommendationItem[];
  generated_at: string;
}

export interface GeospatialDataset {
  id: number;
  dataset_code: string;
  dataset_name: string;
  dataset_type: string;
  provider: string;
  watershed_id?: number;
  acquisition_date?: string;
  processing_date?: string;
  spatial_resolution?: string;
  temporal_resolution?: string;
  coverage_bounds?: number[];
  crs: string;
  provenance: 'DEMO_DATA' | 'IMPORTED_DATA' | 'OFFICIAL_SOURCE' | string;
  format: string;
  record_count: number;
  license_info?: string;
  metadata_json?: any;
  status: string;
  created_at: string;
}

export interface DatasetCatalogResponse {
  total_datasets: number;
  datasets: GeospatialDataset[];
  provenance_summary: {
    total_datasets: number;
    demo_datasets_count: number;
    imported_datasets_count: number;
    official_source_count: number;
    active_watershed_filter?: number;
  };
}

export interface ProviderAdapterInfo {
  provider_code: string;
  provider_name: string;
  status: string;
  endpoint: string;
  has_credentials: boolean;
  spatial_resolution?: string;
  operational_notes?: string;
  supported_bands?: string[];
  thematic_layers?: string[];
  derived_indices?: string[];
}

export interface DataIngestionJob {
  id: number;
  job_id: string;
  watershed_id?: number;
  dataset_id?: number;
  source_format: string;
  status: string;
  records_processed: number;
  records_failed: number;
  log_messages: string[];
  started_at: string;
  completed_at?: string;
}

// ==========================================
// Authentication & Role-Based Access Types
// ==========================================

export type UserRole = 'ADMIN' | 'STATE_OFFICER' | 'DISTRICT_OFFICER' | 'FIELD_OFFICER' | 'ANALYST';

export interface UserProfile {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  state_id?: number | null;
  district_id?: number | null;
  watershed_id?: number | null;
  organization?: string | null;
  designation?: string | null;
  is_active: boolean;
  created_at: string;
  last_login?: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
  user: UserProfile;
}

export interface AccessRequest {
  id: number;
  name: string;
  email: string;
  requested_role: UserRole;
  state_id?: number | null;
  district_id?: number | null;
  organization: string;
  designation?: string | null;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  reviewed_by?: number | null;
  reviewed_at?: string | null;
  rejection_reason?: string | null;
  created_at: string;
}

export interface AuditLogEntry {
  id: number;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id?: string | null;
  details?: any;
  timestamp: string;
  ip_address?: string | null;
}

export interface DemoAccount {
  name: string;
  email: string;
  role: UserRole;
  jurisdiction: string;
  organization: string;
  demo_password: string;
  description: string;
}

export interface UserRegisterRequest {
  name: string;
  email: string;
  organization: string;
  state_id?: number | null;
  district_id?: number | null;
  requested_role: string;
  password: string;
  confirm_password: string;
}

export interface RegistrationResponse {
  message: string;
  status: string;
  request_id?: number;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ForgotPasswordResponse {
  message: string;
  status: string;
  support_contact: string;
}



