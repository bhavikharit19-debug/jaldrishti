import {
  StateHierarchy,
  WatershedListItem,
  WatershedDetail,
  GISLayer,
  FieldPhoto,
  HealthScore,
  ChangeDetection,
  PredictionResponse,
  RiskAssessmentResponse,
  RecommendationResponse,
  InterventionItem,
  AlertItem,
  WatershedReport,
  WatershedGISStats,
  DatasetCatalogResponse,
  ProviderAdapterInfo,
  UserProfile,
  AuthResponse,
  AccessRequest,
  AuditLogEntry,
  DemoAccount,
  UserRegisterRequest,
  RegistrationResponse,
  ForgotPasswordResponse
} from '@/types';

export const getApiBaseUrl = (): string => {
  // In the browser, always route through same-origin /api/v1 so Next.js rewrites proxy to backend.
  // This avoids CORS preflights, HTTPS mixed-content blocks, and missing protocol issues.
  if (typeof window !== 'undefined') {
    return '/api/v1';
  }

  // On the server (SSR / build time)
  let raw = process.env.INTERNAL_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
  raw = raw.replace(/\/api\/v1\/?$/, '').replace(/\/+$/, '');
  if (!raw.startsWith('http://') && !raw.startsWith('https://')) {
    raw = `https://${raw}`;
  }
  return `${raw}/api/v1`;
};

const API_BASE_URL = {
  toString: () => getApiBaseUrl(),
  valueOf: () => getApiBaseUrl()
};

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const isFormData = typeof FormData !== 'undefined' && options?.body instanceof FormData;
  const headers: Record<string, string> = {
    ...(options?.headers as Record<string, string> || {}),
  };
  if (!isFormData && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  // Inject JWT Bearer token if present
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('jaldrishti_token');
    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const res = await fetch(url, {
    ...options,
    headers,
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error ${res.status}: ${errorText}`);
  }
  return res.json();
}

export const api = {
  // Health
  checkHealth: () => fetchJson<{ status: string; database: string }>(`${API_BASE_URL}/health`),

  // Hierarchy & Watersheds
  getStatesHierarchy: () => fetchJson<StateHierarchy[]>(`${API_BASE_URL}/states-hierarchy`),

  listWatersheds: (stateId?: number, districtId?: number, search?: string) => {
    const params = new URLSearchParams();
    if (stateId) params.append('state_id', stateId.toString());
    if (districtId) params.append('district_id', districtId.toString());
    if (search) params.append('search', search);
    return fetchJson<WatershedListItem[]>(`${API_BASE_URL}/watersheds?${params.toString()}`);
  },

  getWatershed: (id: number) => fetchJson<WatershedDetail>(`${API_BASE_URL}/watersheds/${id}`),

  // GIS Layers & Thematic Statistics
  getLayers: (watershedId: number, layerType?: string) => {
    const params = new URLSearchParams({ watershed_id: watershedId.toString() });
    if (layerType) params.append('layer_type', layerType);
    return fetchJson<GISLayer[]>(`${API_BASE_URL}/layers?${params.toString()}`);
  },

  getWatershedGISStats: (watershedId: number) =>
    fetchJson<WatershedGISStats>(`${API_BASE_URL}/watersheds/${watershedId}/gis-stats`),

  // Field Photos
  getPhotos: (watershedId: number, category?: string) => {
    const params = new URLSearchParams({ watershed_id: watershedId.toString() });
    if (category) params.append('category', category);
    return fetchJson<FieldPhoto[]>(`${API_BASE_URL}/photos?${params.toString()}`);
  },

  uploadPhoto: (data: {
    watershed_id: number;
    latitude: number;
    longitude: number;
    photo_url: string;
    category: string;
    description?: string;
    intervention_id?: number;
    exif_metadata?: any;
  }) => fetchJson<FieldPhoto>(`${API_BASE_URL}/photos`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Analytics & Health Score
  getHealthScore: (watershedId: number) =>
    fetchJson<HealthScore>(`${API_BASE_URL}/health-score?watershed_id=${watershedId}`),

  getChanges: (watershedId: number, fromYear: number = 2018, toYear: number = 2024) =>
    fetchJson<ChangeDetection>(
      `${API_BASE_URL}/changes?watershed_id=${watershedId}&from_year=${fromYear}&to_year=${toYear}`
    ),

  // Predictions
  getPredictions: (watershedId: number) =>
    fetchJson<PredictionResponse>(`${API_BASE_URL}/predictions?watershed_id=${watershedId}`),

  // Risks
  getRisks: (watershedId: number) =>
    fetchJson<RiskAssessmentResponse>(`${API_BASE_URL}/risks?watershed_id=${watershedId}`),

  // Interventions & Structural Monitoring
  getInterventions: (watershedId: number, status?: string) => {
    const params = new URLSearchParams({ watershed_id: watershedId.toString() });
    if (status) params.append('status', status);
    return fetchJson<InterventionItem[]>(`${API_BASE_URL}/interventions?${params.toString()}`);
  },

  createIntervention: (data: {
    watershed_id: number;
    code: string;
    name: string;
    intervention_type: string;
    status: string;
    latitude: number;
    longitude: number;
    sanction_year: number;
    target_capacity_cum: number;
    cost_inr: number;
    beneficiary_count: number;
    description?: string;
  }) =>
    fetchJson<InterventionItem>(`${API_BASE_URL}/interventions`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateIntervention: (id: number, data: Partial<InterventionItem>) =>
    fetchJson<InterventionItem>(`${API_BASE_URL}/interventions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  getInterventionObservations: (id: number) =>
    fetchJson<any[]>(`${API_BASE_URL}/interventions/${id}/observations`),

  createInterventionObservation: (id: number, data: {
    observer_name: string;
    condition_rating: string;
    remarks?: string;
    recommended_action?: string;
  }) =>
    fetchJson<any>(`${API_BASE_URL}/interventions/${id}/observations`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Recommendations
  getRecommendations: (watershedId: number) =>
    fetchJson<RecommendationResponse>(`${API_BASE_URL}/recommendations?watershed_id=${watershedId}`),

  // Alerts
  getAlerts: (watershedId: number) =>
    fetchJson<AlertItem[]>(`${API_BASE_URL}/alerts?watershed_id=${watershedId}`),

  updateAlertStatus: (alertId: number, status: string) =>
    fetchJson<AlertItem>(`${API_BASE_URL}/alerts/${alertId}/status?status=${status}`, {
      method: 'PATCH',
    }),

  // Reports
  getReport: (watershedId: number) =>
    fetchJson<WatershedReport>(`${API_BASE_URL}/reports/${watershedId}`),

  // Data Integration & Provenance
  getDatasetCatalog: (watershedId?: number, datasetType?: string, provenance?: string) => {
    const params = new URLSearchParams();
    if (watershedId) params.append('watershed_id', watershedId.toString());
    if (datasetType) params.append('dataset_type', datasetType);
    if (provenance) params.append('provenance', provenance);
    return fetchJson<DatasetCatalogResponse>(`${API_BASE_URL}/data/catalog?${params.toString()}`);
  },

  getProviderAdapters: () =>
    fetchJson<ProviderAdapterInfo[]>(`${API_BASE_URL}/data/adapters`),

  getWatershedProvenance: (watershedId: number) =>
    fetchJson<{ overall_provenance: string; has_imported_data: boolean; imported_layers_count: number; imported_indicators_count: number; imported_photos_count: number }>(
      `${API_BASE_URL}/data/provenance/${watershedId}`
    ),

  importGeoJSON: (formData: FormData) =>
    fetchJson<any>(`${API_BASE_URL}/data/import/geojson`, {
      method: 'POST',
      body: formData,
    }),

  importCSV: (formData: FormData) =>
    fetchJson<any>(`${API_BASE_URL}/data/import/csv`, {
      method: 'POST',
      body: formData,
    }),

  uploadFieldPhotoFile: (formData: FormData) =>
    fetchJson<FieldPhoto>(`${API_BASE_URL}/photos/upload`, {
      method: 'POST',
      body: formData,
    }),

  // ==========================================
  // Authentication & Access Management
  // ==========================================
  login: (email: string, password: string, remember_me: boolean = false) =>
    fetchJson<AuthResponse>(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      body: JSON.stringify({ email, password, remember_me }),
    }),

  getMe: () =>
    fetchJson<UserProfile>(`${API_BASE_URL}/auth/me`),

  logout: () =>
    fetchJson<{ message: string; status: string }>(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
    }),

  submitAccessRequest: (data: {
    name: string;
    email: string;
    requested_role: string;
    state_id?: number | null;
    district_id?: number | null;
    organization: string;
    designation?: string | null;
    reason: string;
  }) =>
    fetchJson<AccessRequest>(`${API_BASE_URL}/auth/request-access`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  register: (data: UserRegisterRequest) =>
    fetchJson<RegistrationResponse>(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  forgotPassword: (email: string) =>
    fetchJson<ForgotPasswordResponse>(`${API_BASE_URL}/auth/forgot-password`, {
      method: 'POST',
      body: JSON.stringify({ email }),
    }),

  getDemoAccounts: () =>
    fetchJson<DemoAccount[]>(`${API_BASE_URL}/auth/demo-accounts`),

  // ==========================================
  // Administrative Operations (Admin Only)
  // ==========================================
  listUsers: (role?: string, isActive?: boolean) => {
    const params = new URLSearchParams();
    if (role) params.append('role', role);
    if (isActive !== undefined) params.append('is_active', isActive.toString());
    return fetchJson<UserProfile[]>(`${API_BASE_URL}/admin/users?${params.toString()}`);
  },

  updateUser: (userId: number, data: Partial<UserProfile> & { password?: string }) =>
    fetchJson<UserProfile>(`${API_BASE_URL}/admin/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  listAccessRequests: (statusFilter?: string) => {
    const params = new URLSearchParams();
    if (statusFilter) params.append('status_filter', statusFilter);
    return fetchJson<AccessRequest[]>(`${API_BASE_URL}/admin/access-requests?${params.toString()}`);
  },

  approveAccessRequest: (requestId: number, temporaryPassword?: string) =>
    fetchJson<UserProfile>(`${API_BASE_URL}/admin/access-requests/${requestId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ action: 'APPROVE', temporary_password: temporaryPassword }),
    }),

  rejectAccessRequest: (requestId: number, rejectionReason: string) =>
    fetchJson<AccessRequest>(`${API_BASE_URL}/admin/access-requests/${requestId}/reject`, {
      method: 'POST',
      body: JSON.stringify({ action: 'REJECT', rejection_reason: rejectionReason }),
    }),

  listAuditLogs: (action?: string, resourceType?: string) => {
    const params = new URLSearchParams();
    if (action) params.append('action', action);
    if (resourceType) params.append('resource_type', resourceType);
    return fetchJson<AuditLogEntry[]>(`${API_BASE_URL}/admin/audit-logs?${params.toString()}`);
  },
};

