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
  answer: string;
  timestamp: string;
  location?: {
    lat: number;
    lng: number;
  };
}

export interface WeatherData {
  temperature: number;
  humidity: number;
  condition: string;
  forecast: ForecastDay[];
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
}

export interface CropHealthData {
  region: string;
  ndvi_score: number;
  drought_risk: string;
  primary_crop: string;
  health_status: 'Excellent' | 'Good' | 'Fair' | 'Poor';
}

export interface BricsCountry {
  code: string;
  name: string;
  farmers_reached: number;
  active_alerts: number;
  top_crop: string;
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
