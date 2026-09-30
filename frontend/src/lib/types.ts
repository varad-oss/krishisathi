// Shapes returned by the KrishiSathi API. Keep in sync with backend/models and routers.

export type LanguageCode = 'en' | 'hi' | 'mr' | 'ta' | 'te' | 'bn' | 'kn' | 'gu' | 'pa' | 'ml';

export interface Language {
  code: LanguageCode;
  name: string;
  nativeName: string;
}

export type Level = 'low' | 'moderate' | 'high';
export type InsightSeverity = 'info' | 'watch' | 'warning';

export interface Provenance {
  source: string;
  source_url?: string | null;
  kind: string;
  notes?: string;
  retrieved_at?: string;
  valid_at?: string | null;
  resolution?: string;
  depth?: string;
  verify_url?: string;
}

export interface CurrentConditions {
  valid_at: string | null;
  temperature_c: number | null;
  humidity_pct: number | null;
  precipitation_mm: number | null;
  wind_kmh: number | null;
  weather_code: number | null;
  condition: string;
  soil_moisture_0_1cm: number | null;
  soil_moisture_3_9cm: number | null;
}

export interface ForecastDay {
  date: string;
  weather_code: number | null;
  condition: string;
  temp_max_c: number | null;
  temp_min_c: number | null;
  precipitation_mm: number | null;
  precipitation_probability_pct: number | null;
  et0_mm: number | null;
  humidity_mean_pct: number | null;
  wind_max_kmh: number | null;
}

export interface Insight {
  id: 'heavy_rain' | 'rain_expected' | 'heat_stress' | 'cold_stress' | 'fungal_risk' | 'dry_spell' | 'spray_wind';
  category: 'weather' | 'water' | 'disease' | 'crop_stress' | 'climate';
  severity: InsightSeverity;
  date: string | null;
  params: Record<string, number | null>;
  basis: {
    kind: 'forecast' | 'current_model_estimate';
    threshold: Record<string, number | number[]>;
    source: { name: string; url: string | null };
  };
}

export interface FarmConditions {
  location: { lat: number; lng: number; timezone: string | null; elevation_m: number | null };
  current: CurrentConditions;
  daily: ForecastDay[];
  insights: Insight[];
  provenance: Provenance;
}

export type SoilReason =
  | 'rate_limited'
  | 'timeout'
  | 'upstream_error'
  | 'network_error'
  | 'unknown_error'
  | 'bad_response'
  | 'request_rejected'
  | 'no_coverage';

export interface SoilData {
  status: 'available' | 'unavailable' | 'no_data';
  /** Why data is missing: rate_limited, timeout, upstream_error, network_error, unknown_error, bad_response, request_rejected, no_coverage. */
  reason?: SoilReason;
  retryable?: boolean;
  properties?: {
    ph: number | null;
    organic_carbon_pct: number | null;
    total_nitrogen_g_per_kg: number | null;
    clay_pct: number | null;
    sand_pct: number | null;
  };
  ratings?: {
    ph: 'strongly_acidic' | 'acidic' | 'neutral' | 'alkaline' | 'strongly_alkaline' | null;
    organic_carbon: Level | null;
    source: { name: string; url: string };
  };
  provenance?: Provenance;
}

export interface RegenTrigger {
  signal: string;
  value: number | string | null;
  rating: string | null;
}

export interface RegenRecommendation {
  id: string;
  priority: 'high' | 'medium' | 'low';
  triggers: RegenTrigger[];
  params: Record<string, string>;
}

export interface RegenerativeResponse {
  crop: string | null;
  soil: SoilData;
  inputs: { soil: string; weather: string; crop: string };
  recommendations: RegenRecommendation[];
}

export interface CropHealth {
  status: 'available' | 'unavailable' | 'no_data';
  reason?: string;
  ndvi?: number;
  ndvi_previous?: number | null;
  change?: number | null;
  window?: { start: string; end: string };
  image_count?: number | null;
  provenance: Provenance;
}

export interface Kvk {
  name: string;
  state: string;
  district: string;
  /** "district": matched by nearest district headquarters (no verified address or distance). "site": verified KVK location. */
  match: 'district' | 'site';
  /** Only set for verified sites; a distance to a district reference point is not a distance to the KVK. */
  distance_km: number | null;
  lat: number | null;
  lng: number | null;
  provenance: Provenance;
}

export type DiagnosisStatus = 'disease_detected' | 'healthy' | 'uncertain' | 'not_a_plant';

export interface DiseaseReference {
  id: string;
  name: string;
  scientific_name?: string | null;
  symptoms: string;
  treatment: string;
  sources: { organization: string; title: string; url?: string | null }[];
}

export interface DiagnosisResponse {
  status: DiagnosisStatus;
  certainty: Level;
  certainty_reason: string;
  image_quality: 'good' | 'poor';
  disease_name: string | null;
  scientific_name: string | null;
  affected_part: string | null;
  observed_symptoms: string[];
  alternative_causes: string[];
  severity: Level | null;
  spread_risk: Level | null;
  urgency: 'routine' | 'soon' | 'immediate';
  treatment: { immediate: string[]; organic: string[]; chemical: string[]; prevention: string[] };
  summary: string;
  reference: DiseaseReference | null;
  context_used: { crop: string; location: string; weather: string; reference: string };
  recorded: boolean;
  language: LanguageCode;
  generated_by: { kind: string; model: string };
}

export interface DataSourceUse {
  id: 'weather' | 'soil' | 'outbreaks' | 'disease_reference' | 'kvk';
  status: 'used' | 'unavailable' | 'not_provided' | 'none_found';
}

export interface AdvisoryResponse {
  advisory_text: string;
  advisory_type: string;
  data_sources: DataSourceUse[];
  language: LanguageCode;
  generated_at: string;
  recorded: boolean;
}

export interface DashboardStats {
  generated_at: string;
  total_diagnoses: number;
  diagnoses_last_7_days: number;
  diagnoses_previous_7_days: number;
  total_advisories: number;
  active_outbreaks: number;
  disease_distribution: Record<string, number>;
  crop_distribution_30d: Record<string, number>;
  status_distribution_30d: Record<string, number>;
  daily_diagnoses_30d: { date: string; count: number }[];
  coverage: { grid_cells_30d: number; grid_size_deg: number };
  provenance: Provenance;
}

export interface Outbreak {
  id: string;
  disease: string;
  location: string;
  lat: number;
  lng: number;
  radius_km: number;
  severity: Level;
  report_count: number;
  crop_targets: string[];
  timestamp: string;
  status: string;
}

export interface DashboardReport {
  status: 'available' | 'insufficient_data';
  report_text: string | null;
  generated_at: string;
  data_as_of: string;
  minimum_records?: number;
  records?: number;
}

export interface StateConfig {
  code: string;
  name: string;
  lat: number;
  lng: number;
  default_language: LanguageCode;
  primary_crops: string[];
}

export interface WeatherRisk {
  regions: { state: string; status: 'available' | 'unavailable'; insights: Insight[] }[];
  aggregation: string;
  provenance: Provenance;
}

export interface FederationSignal {
  signal_id: string;
  from_state: string;
  to_state: string | null;
  signal_type: string;
  severity: 'info' | 'low' | 'moderate' | 'high' | 'critical';
  message: string;
  disease_name?: string | null;
  affected_crop?: string | null;
  timestamp: string;
}

export interface FederationReport {
  total_signals: number;
  states_reporting: number;
  signals: FederationSignal[];
  generated_at: string;
  note: string;
}

export interface SourceStatus {
  id: string;
  name: string;
  url: string | null;
  kind: string;
  /** 'unavailable': set up but failing its live check (only the satellite source reports this); `detail` says why. */
  status: 'configured' | 'not_configured' | 'unavailable';
  detail?: string | null;
  used_for: string[];
}

// --- Farm intelligence (GET /api/farm/intelligence) ------------------------------------------------

export type RiskSeverity = 'low' | 'moderate' | 'high' | 'unavailable';
export type RiskCategory = 'waterlogging' | 'water_stress' | 'heat_stress' | 'cold_stress' | 'disease' | 'pest' | 'spray_window' | 'harvest_weather' | 'crop_health';
export type EvidenceBasis =
  | 'observed' | 'forecast' | 'model_estimate' | 'satellite_observation' | 'rule_based'
  | 'ai_generated' | 'ai_classified_reports' | 'farmer_reported' | 'static_reference';

export interface Evidence {
  id: string;
  value: number | string | null;
  unit: string | null;
  date: string | null;
  basis: EvidenceBasis;
  source: string;
  params: Record<string, number | string | null>;
}

export interface RuleRef {
  id: string;
  source: string;
  url: string | null;
}

export interface Risk {
  category: RiskCategory;
  severity: RiskSeverity;
  confidence: Level | null;
  drivers: string[];
  evidence: Evidence[];
  action: string | null;
  reason: string | null;
  date: string | null;
  crop: string | null;
  crop_stage: string | null;
  rules: RuleRef[];
}

export interface TopAction {
  status: 'action' | 'routine' | 'unavailable';
  action: string | null;
  category: RiskCategory | null;
  severity: RiskSeverity | null;
  confidence: Level | null;
  drivers: string[];
  evidence: Evidence[];
  date: string | null;
  reason: string | null;
}

export type DataStatus = 'available' | 'unavailable' | 'not_configured' | 'no_data' | 'not_provided' | 'pending';

export interface DataQualityItem {
  source: 'weather' | 'soil' | 'satellite' | 'crop_stage' | 'outbreaks' | string;
  status: DataStatus;
  kind: string;
  as_of: string | null;
  reason: string | null;
  provider: string | null;
}

export interface CropStageEstimate {
  status: 'estimated' | 'not_provided' | 'no_calendar' | 'before_sowing' | 'beyond_season';
  stage: 'initial' | 'development' | 'mid_season' | 'late_season' | null;
  days_since_sowing: number | null;
  season_length_days: number | null;
  confidence: Level | null;
  calendar: string | null;
  reference: { source: string; url: string; notes: string };
}

export interface FarmIntelligence {
  schema_version: string;
  generated_at: string;
  farm: { crop: string | null; sowing_date: string | null; location: { lat: number; lng: number }; crop_stage: CropStageEstimate };
  top_action: TopAction;
  risks: Risk[];
  data_quality: DataQualityItem[];
  engine: { id: string; version: string; kind: string; ai_used: boolean };
}
