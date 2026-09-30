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

export type RegenHorizon = 'current' | 'next' | 'long_term';

export interface RegenPlanItem extends RegenRecommendation {
  timing: 'now' | 'before_sowing' | 'at_harvest' | 'after_harvest' | 'ongoing';
  horizon: RegenHorizon;
  confidence: 'moderate' | 'low';
  stage_based: boolean;
}

export interface RegenerativeResponse {
  crop: string | null;
  soil: SoilData;
  inputs: { soil: string; weather: string; crop: string; crop_stage: CropStageEstimate['status'] };
  recommendations: RegenRecommendation[];
  plan: RegenPlanItem[];
  crop_stage: CropStageEstimate;
}

export type PracticeStatus = 'adopted' | 'partial' | 'skipped';

export interface CropOption {
  crop: string;
  group: string | null;
  is_current: boolean;
  water_need_mm: { min: number; max: number } | null;
  season_length_days: number | null;
  verified_disease_entries: number;
  /** null when community reports could not be read (unknown, not zero). */
  nearby_disease_clusters: number | null;
}

interface SourceRef {
  source: string;
  url?: string;
  kind?: string;
}

export interface CropOptions {
  basis: 'farm_crop_and_state_list' | 'all_supported_crops';
  state: string | null;
  crops: CropOption[];
  market: { status: 'unavailable'; reason: string };
  input_costs: { status: 'unavailable'; reason: string };
  ranking: null;
  sources: { water_need: SourceRef; season_length: SourceRef; disease_entries: SourceRef; nearby_clusters: SourceRef; state_list: SourceRef | null };
}

export interface SarSummary {
  status: 'available' | 'no_data' | 'unavailable' | 'insufficient_data';
  reason?: string;
  orbit_pass?: 'ASCENDING' | 'DESCENDING';
  latest_image_date?: string | null;
  vv_db?: number;
  vh_db?: number;
  vh_db_previous?: number | null;
  vh_change_db?: number | null;
  /** UN-SPIDER change-detection screening signal for standing water; null when there is no earlier pass. */
  water_signal?: boolean | null;
}

export interface NdviBaseline {
  status: 'available' | 'insufficient_data';
  years: { year: number; ndvi: number | null; clear_pixel_fraction: number; image_count: number | null }[];
  mean?: number;
  min?: number;
  max?: number;
  position?: 'below_range' | 'within_range' | 'above_range' | null;
}

export interface LandCover {
  status: 'available' | 'unavailable';
  cropland_fraction?: number;
  tree_cover_fraction?: number;
  grass_shrub_fraction?: number;
  built_up_fraction?: number;
  water_fraction?: number;
  other_fraction?: number;
  provenance: { source: string; source_url: string; notes: string };
}

export type SatelliteQualityFlag =
  | 'field_too_small' | 'too_few_clear_pixels' | 'mixed_land_cover' | 'contains_water' | 'contains_trees' | 'contains_built_up'
  | 'point_circle_not_field_boundary';

/** What the satellite numbers describe and how much to trust them (backend: earth_engine_service._quality). */
export interface SatelliteQuality {
  mode: 'polygon' | 'point';
  level: 'good' | 'limited' | 'insufficient';
  flags: SatelliteQualityFlag[];
  pixel_count: number;
  clear_pixel_count: number;
  clear_pixel_fraction: number;
  valid_pixel_fraction: number | null;
  land_cover: LandCover;
  resolution_m: number;
  method: string;
}

export interface CropHealth {
  status: 'available' | 'unavailable' | 'no_data' | 'insufficient_data';
  reason?: string;
  roi?: { mode: 'polygon'; area_ha: number; pixel_count: number | null } | { mode: 'point'; lat?: number; lng?: number; radius_m?: number };
  quality?: SatelliteQuality;
  ndvi?: number;
  ndvi_previous?: number | null;
  change?: number | null;
  window?: { start: string; end: string };
  image_count?: number | null;
  latest_image_date?: string | null;
  clear_pixel_fraction?: number;
  baseline?: NdviBaseline;
  sar?: SarSummary;
  provenance: Provenance;
}

export interface CropHealthHistory {
  status: 'available' | 'insufficient_data' | 'unavailable';
  reason?: string;
  series?: { start: string; end: string; ndvi: number | null; clear_pixel_fraction: number; image_count: number | null }[];
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
  differential: { name: string; likelihood: Level; reason: string }[];
  guidance: { level: 'supported' | 'cautious' | 'escalate' | 'none'; reasons: string[] };
  escalation: Escalation | null;
  context_used: Record<'crop' | 'location' | 'weather' | 'reference' | 'crop_stage' | 'nearby_reports' | 'satellite' | 'farm', string>;
  recorded: boolean;
  language: LanguageCode;
  generated_by: { kind: string; model: string };
  twin: { action: TwinAction } | null;
}

export interface EscalationCase {
  case_id: string;
  crop: string | null;
  location: { lat: number; lng: number } | null;
  ai_diagnosis: { possible_disease: string | null; certainty: Level; observed_symptoms: string[] };
  image_included: boolean;
}

export interface Escalation {
  recommended: boolean;
  reason: 'expert_review_needed' | 'high_severity_unconfirmed';
  kvk: (Omit<Kvk, 'provenance'> & { provenance: Provenance }) | null;
  kvk_portal: string;
  case: EscalationCase;
  submission: { status: 'not_submitted' | 'submitted'; reason?: string };
}

export interface DataSourceUse {
  id: 'weather' | 'soil' | 'outbreaks' | 'disease_reference' | 'kvk' | 'farm_intelligence';
  status: 'used' | 'unavailable' | 'not_provided' | 'none_found';
}

export interface AdvisoryResponse {
  advisory_text: string;
  advisory_type: string;
  data_sources: DataSourceUse[];
  language: LanguageCode;
  generated_at: string;
  recorded: boolean;
  mode?: 'text' | 'speech';
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

export interface DiseaseSignal {
  type: 'disease';
  disease: string;
  crops: string[];
  geography: { kind: 'grid_cell'; size_deg: number; lat: number; lng: number };
  observations: number;
  observations_previous: number;
  trend: 'new' | 'rising' | 'steady' | 'falling';
  severity: Level | null;
  confidence: Level;
  last_report: string;
}

export interface WeatherThreat extends Insight {
  type: 'weather';
  state: string;
  geography: { kind: string; state: string };
}

export interface EarlyWarning {
  generated_at: string;
  period: { start: string; end: string; compared_with: { start: string; end: string } };
  disease: {
    signals: DiseaseSignal[];
    below_threshold: number;
    method: { cell_deg: number; min_reports: number; window_days: number; confidence_rule: string };
    source: string;
    kind: string;
    limitations: string[];
  };
  weather: { threats: WeatherThreat[]; states_unavailable: string[]; provenance: Provenance };
  crop_health: { status: 'unavailable'; reason: 'not_configured' | 'regional_aggregation_not_implemented' };
  coverage: { observations_14d: number; grid_cells_14d: number; cell_deg: number; insufficient_data: boolean; min_observations: number };
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
  /** required: the stated risk level depends on it; supporting: alternative or corroborating; context: shown only. */
  role?: 'required' | 'supporting' | 'context';
  /** Independence group: evidence in one group shares an upstream source. */
  group?: string | null;
  reliability?: Level | null;
}

export interface RuleRef {
  id: string;
  source: string;
  url: string | null;
}

export interface Risk {
  category: RiskCategory;
  severity: RiskSeverity;
  /** Evidence confidence: how reliable the signals are. Independent of severity (the risk level). */
  confidence: Level | null;
  confidence_basis?: string[];
  independent_sources?: number;
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
  confidence_basis?: string[];
  drivers: string[];
  evidence: Evidence[];
  rules?: RuleRef[];
  date: string | null;
  reason: string | null;
  priority_reason?: 'highest_severity' | 'soonest' | 'stronger_evidence' | 'less_reversible' | 'only_action' | null;
}

export type DataStatus = 'available' | 'unavailable' | 'not_configured' | 'no_data' | 'insufficient_data' | 'not_provided' | 'pending';

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
  farm: {
    crop: string | null;
    sowing_date: string | null;
    location: { lat: number; lng: number };
    crop_stage: CropStageEstimate;
    /** What satellite values describe: the drawn field (polygon) or the circle around the farm point. */
    field?: { mode: 'polygon'; area_ha: number } | { mode: 'point' };
  };
  top_action: TopAction;
  risks: Risk[];
  data_quality: DataQualityItem[];
  engine: { id: string; version: string; kind: string; ai_used: boolean };
}

// --- Farm digital twin (/api/farms) -----------------------------------------------------------------

export type Followed = 'yes' | 'partial' | 'no' | 'not_applicable';
export type Outcome = 'improved' | 'same' | 'worse' | 'diagnosis_wrong' | 'not_sure';

export interface TwinAction {
  action_id: string;
  created_at: string;
  source_type: 'intelligence' | 'diagnosis' | 'regenerative';
  source_ref: string | null;
  action: string;
  category: RiskCategory | null;
  severity: RiskSeverity | null;
  confidence: Level | null;
  crop: string | null;
  followed: Followed | null;
  followed_at: string | null;
  outcome: Outcome | null;
  outcome_at: string | null;
}

export interface FarmTwinIntelligence extends FarmIntelligence {
  twin?: { snapshot_id: string | null; action: TwinAction | null };
}

export interface FarmSnapshot {
  snapshot_id: string;
  created_at: string;
  crop: string | null;
  crop_stage: string | null;
  top_action: string | null;
  top_severity: RiskSeverity | null;
  risks: Record<string, RiskSeverity>;
  data_quality: Record<string, DataStatus>;
}

/** GeoJSON Polygon, [lng, lat] positions, closed exterior ring. */
export interface PolygonGeometry {
  type: 'Polygon';
  coordinates: [number, number][][];
}

export interface FarmPlot {
  plot_id: string;
  area_ha: number;
  crop: string | null;
  sowing_date: string | null;
  created_at: string;
  updated_at: string;
  geometry?: PolygonGeometry;
}

export interface FarmHistory {
  farm: { farm_id: string; crop: string | null; sowing_date: string | null };
  plot?: FarmPlot | null;
  snapshots: FarmSnapshot[];
  actions: TwinAction[];
  diagnoses: { diagnosis_id: string; status: string; disease: string | null; certainty: Level | null; date: string }[];
}

export interface FarmTwin {
  farmId: string;
  token: string;
}

// --- Evaluation (GET /api/dashboard/evaluation): KrishiSathi self-reported feedback -------------------------

type Suppressed = { status: 'suppressed' | 'no_data' | 'insufficient_data'; minimum?: number };

export interface DiagnosisFeedback {
  feedback_count: number;
  diagnosis_wrong: number;
  diagnosis_wrong_rate: number | null;
  outcomes: Record<string, number>;
}

export interface AdvisoryFeedback {
  recommendations: number;
  follow_through_answers: number;
  followed_rate: number | null;
  partial_rate: number | null;
  not_followed_rate: number | null;
  not_applicable: number;
  outcome_answers: number;
  outcome_distribution: Record<string, number>;
}

export interface GroupedMetrics<T> {
  groups: Record<string, T>;
  suppressed_groups: number;
}

export interface EvaluationMetrics {
  generated_at: string;
  label: string;
  window_days: number;
  minimum_group_size: number;
  diagnosis: {
    diagnoses: number;
    diagnosis_feedback_count: number;
    diagnosis_wrong?: number;
    diagnosis_wrong_rate?: number | null;
    status?: 'insufficient_data';
    observed_feedback_by_model_confidence: { label: string; tiers: Record<Level, DiagnosisFeedback | Suppressed> };
    by_crop: GroupedMetrics<DiagnosisFeedback>;
  };
  advisory: {
    overall: AdvisoryFeedback | (Suppressed & { recommendations: number });
    by_category: GroupedMetrics<AdvisoryFeedback>;
    by_crop: GroupedMetrics<AdvisoryFeedback>;
  };
  provenance: { source: string; kind: string; label: string; does_not_show: string[]; notes: string };
}

// --- Interoperability comparison (GET /api/interoperability/compare) --------------------------------------

export interface PublishMeta {
  types: string[];
  geography: string;
  period: string;
  provenance_kind: string;
  confidence: string | null;
  access: 'public' | 'partner';
}

export interface CompareSample {
  status: 'available' | 'partner_only' | 'unsupported' | 'unavailable' | string;
  reason?: string;
  total?: number;
  matching_crop?: number;
  items?: Record<string, unknown>[];
}

export interface CountryComparison {
  country_code: string;
  name: string;
  categories: Record<string, 'available' | 'unsupported'>;
  publishes: Record<string, PublishMeta>;
  sources: { id: string; name: string; kind: string; url?: string }[];
  limitations: string[];
  samples: Record<string, CompareSample>;
}

export interface InteropComparison {
  schema_version: string;
  crop_code: string;
  generated_at: string;
  countries: CountryComparison[];
  notes: string;
}
