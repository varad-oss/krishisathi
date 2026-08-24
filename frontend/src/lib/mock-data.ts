import { 
  DiagnosisResponse, 
  AdvisoryResponse, 
  WeatherData, 
  DashboardStats, 
  OutbreakData, 
  CropHealthData, 
  IndianState, 
  Alert 
} from './types';

export const mockDiagnosis: DiagnosisResponse = {
  disease_name: "Early Blight",
  scientific_name: "Alternaria solani",
  confidence: 94.5,
  severity: "Severe",
  spread_risk: "High risk of rapid spread in warm, humid conditions.",
  treatment_plan: {
    immediate_actions: [
      "Remove and destroy heavily infected lower leaves.",
      "Improve air circulation around plants."
    ],
    organic_treatment: [
      "Apply copper-based fungicides or bio-fungicides like Bacillus subtilis.",
      "Use neem oil extract as a preventive measure."
    ],
    chemical_treatment: [
      "Apply chlorothalonil or mancozeb according to local regulations.",
      "Rotate fungicides with different modes of action to prevent resistance."
    ],
    prevention: [
      "Practice 3-4 year crop rotation with non-solanaceous crops.",
      "Use certified disease-free seeds or resistant varieties.",
      "Avoid overhead watering."
    ]
  }
};

export const mockAdvisory: AdvisoryResponse = {
  query: "What is the best crop to plant next month?",
  answer: "Based on the upcoming monsoon season and your region's soil type, short-duration rice varieties or pigeon pea (Tur) would be optimal. Ensure proper drainage as rainfall is expected to be 15% above average.",
  timestamp: new Date().toISOString(),
  location: { lat: 19.0760, lng: 72.8777 }
};

export const mockWeather: WeatherData = {
  temp: 28.5,
  humidity: 76,
  rainfall: 12.5,
  wind: 8.2,
  description: "Partly cloudy with scattered showers",
  forecast: [
    { date: "Tomorrow", high: 30, low: 24, condition: "Rain" },
    { date: "Day 3", high: 29, low: 23, condition: "Thunderstorms" }
  ]
};

export const mockDashboardStats: DashboardStats = {
  total_diagnoses: 39020,
  active_outbreaks: 7,
  farmers_reached: 28710000,
  languages_served: 10,
  diagnoses_trend: 14.5
};

export const mockOutbreaks: OutbreakData[] = [
  {id: 'ob-1', disease: 'Late Blight', region: 'Pune, Maharashtra', severity: 'Critical', reports_count: 342, date: '2026-08-20', lat: 18.52, lng: 73.86, affected_area_km2: 1200},
  {id: 'ob-2', disease: 'Wheat Rust', region: 'Ludhiana, Punjab', severity: 'Severe', reports_count: 189, date: '2026-08-18', lat: 30.90, lng: 75.86, affected_area_km2: 800},
  {id: 'ob-3', disease: 'Fall Armyworm', region: 'Belgaum, Karnataka', severity: 'Moderate', reports_count: 156, date: '2026-08-19', lat: 15.85, lng: 74.50, affected_area_km2: 650},
  {id: 'ob-4', disease: 'Rice Blast', region: 'Thanjavur, Tamil Nadu', severity: 'Moderate', reports_count: 98, date: '2026-08-17', lat: 10.79, lng: 79.14, affected_area_km2: 420},
  {id: 'ob-5', disease: 'Yellow Mosaic', region: 'Indore, Madhya Pradesh', severity: 'Severe', reports_count: 134, date: '2026-08-21', lat: 22.72, lng: 75.86, affected_area_km2: 550}
];

export const mockCropHealth: CropHealthData[] = [
  {region: 'Punjab', ndvi_score: 0.72, drought_risk: 'Low', primary_crop: 'Wheat', health_status: 'Good'},
  {region: 'Maharashtra', ndvi_score: 0.58, drought_risk: 'Moderate', primary_crop: 'Cotton', health_status: 'Fair'},
  {region: 'Karnataka', ndvi_score: 0.65, drought_risk: 'Low', primary_crop: 'Rice', health_status: 'Good'},
  {region: 'Tamil Nadu', ndvi_score: 0.71, drought_risk: 'Low', primary_crop: 'Rice', health_status: 'Good'},
  {region: 'Uttar Pradesh', ndvi_score: 0.45, drought_risk: 'High', primary_crop: 'Wheat', health_status: 'Fair'},
  {region: 'Madhya Pradesh', ndvi_score: 0.62, drought_risk: 'Moderate', primary_crop: 'Soybean', health_status: 'Fair'},
  {region: 'Gujarat', ndvi_score: 0.68, drought_risk: 'Moderate', primary_crop: 'Cotton', health_status: 'Good'},
  {region: 'West Bengal', ndvi_score: 0.55, drought_risk: 'Moderate', primary_crop: 'Rice', health_status: 'Fair'}
];

export const mockStates: IndianState[] = [
  {code: 'PB', name: 'Punjab', farmers_reached: 2850000, active_alerts: 3, top_crop: 'Wheat', districts: 23, lat: 31.1471, lng: 75.3412},
  {code: 'MH', name: 'Maharashtra', farmers_reached: 4120000, active_alerts: 5, top_crop: 'Cotton', districts: 36, lat: 19.7515, lng: 75.7139},
  {code: 'KA', name: 'Karnataka', farmers_reached: 3540000, active_alerts: 2, top_crop: 'Rice', districts: 31, lat: 15.3173, lng: 75.7139},
  {code: 'TN', name: 'Tamil Nadu', farmers_reached: 2980000, active_alerts: 1, top_crop: 'Rice', districts: 38, lat: 11.1271, lng: 78.6569},
  {code: 'UP', name: 'Uttar Pradesh', farmers_reached: 5670000, active_alerts: 4, top_crop: 'Wheat', districts: 75, lat: 26.8467, lng: 80.9462},
  {code: 'MP', name: 'Madhya Pradesh', farmers_reached: 3890000, active_alerts: 3, top_crop: 'Soybean', districts: 55, lat: 22.9734, lng: 78.6569},
  {code: 'GJ', name: 'Gujarat', farmers_reached: 2450000, active_alerts: 2, top_crop: 'Cotton', districts: 33, lat: 22.2587, lng: 71.1924},
  {code: 'WB', name: 'West Bengal', farmers_reached: 3210000, active_alerts: 2, top_crop: 'Rice', districts: 23, lat: 22.9868, lng: 87.8550}
];

export const mockAlerts: Alert[] = [
  { id: "1", title: "Heat Wave Warning", message: "Temperatures expected to exceed 40°C in Northern regions.", date: "2026-08-15", severity: "Severe" },
  { id: "2", title: "Locust Swarm Sighted", message: "Movement detected near Western Maharashtra border. Prepare preventative measures.", date: "2026-08-14", severity: "Critical" }
];
