export interface DiagnosisResponse {
  disease_name: string;
  scientific_name?: string;
  confidence: number;
  severity: 'Low' | 'Moderate' | 'Severe' | 'Critical';
  treatment_plan: TreatmentPlan;
  spread_risk: string;
}

export interface TreatmentPlan {
  immediate_actions: string[];
  organic_treatment: string[];
  chemical_treatment: string[];
  prevention: string[];
}

export interface AdvisoryResponse {
  query: string;
  answer?: string;
  advisory_text?: string;
  language?: string;
  translated_text?: string;
  timestamp: string;
  location?: {
    lat: number;
    lng: number;
  };
}

export interface WeatherData {
  temp: number;
  humidity: number;
  rainfall: number;
  wind: number;
  soil_moisture?: number;
  description: string;
  source?: string;
  location?: string;
  forecast?: ForecastDay[];
}

export interface ForecastDay {
  date: string;
  high: number;
  low: number;
  condition: string;
}

export interface DashboardStats {
  total_diagnoses: number;
  active_outbreaks: number;
  farmers_reached: number;
  languages_served: number;
  diagnoses_trend: number;
}

export interface OutbreakData {
  id: string;
  disease: string;
  region: string;
  severity: 'Low' | 'Moderate' | 'Severe' | 'Critical';
  reports_count: number;
  date: string;
  lat?: number;
  lng?: number;
  affected_area_km2?: number;
}

export interface CropHealthData {
  region: string;
  ndvi_score: number;
  drought_risk: string;
  primary_crop: string;
  health_status: 'Excellent' | 'Good' | 'Fair' | 'Poor';
}

export interface IndianState {
  code: string;
  name: string;
  farmers_reached: number;
  active_alerts: number;
  top_crop: string;
  districts: number;
  lat: number;
  lng: number;
}

export interface Alert {
  id: string;
  title: string;
  message: string;
  date: string;
  severity: 'Low' | 'Moderate' | 'Severe' | 'Critical';
}

export interface Language {
  code: string;
  name: string;
  nativeName: string;
}
