import { 
  DiagnosisResponse, 
  AdvisoryResponse, 
  WeatherData, 
  DashboardStats, 
  OutbreakData, 
  CropHealthData, 
  BricsCountry, 
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
  temperature: 28,
  humidity: 65,
  condition: "Partly Cloudy",
  forecast: [
    { date: "Tomorrow", high: 30, low: 24, condition: "Rain" },
    { date: "Day 3", high: 29, low: 23, condition: "Thunderstorms" }
  ]
};

export const mockDashboardStats: DashboardStats = {
  total_diagnoses: 125430,
  active_outbreaks: 12,
  farmers_reached: 543000,
  languages_served: 10,
  diagnoses_trend: 14.5
};

export const mockOutbreaks: OutbreakData[] = [
  { id: "1", disease: "Wheat Rust", region: "Punjab, India", severity: "Severe", reports_count: 1450, date: "2024-05-10" },
  { id: "2", disease: "Fall Armyworm", region: "Goias, Brazil", severity: "Critical", reports_count: 3200, date: "2024-05-08" },
  { id: "3", disease: "Rice Blast", region: "Hunan, China", severity: "Moderate", reports_count: 890, date: "2024-05-12" },
  { id: "4", disease: "Late Blight", region: "Moscow Oblast, Russia", severity: "Moderate", reports_count: 450, date: "2024-05-11" },
  { id: "5", disease: "Maize Lethal Necrosis", region: "KwaZulu-Natal, SA", severity: "High", reports_count: 670, date: "2024-05-09" }
] as any; // Cast for High vs Severe mismatch in mock for demo

export const mockCropHealth: CropHealthData[] = [
  { region: "Maharashtra", ndvi_score: 0.65, drought_risk: "Low", primary_crop: "Sugarcane", health_status: "Good" },
  { region: "Karnataka", ndvi_score: 0.45, drought_risk: "High", primary_crop: "Cotton", health_status: "Poor" },
  { region: "Punjab", ndvi_score: 0.82, drought_risk: "Low", primary_crop: "Wheat", health_status: "Excellent" },
  { region: "Gujarat", ndvi_score: 0.55, drought_risk: "Moderate", primary_crop: "Groundnut", health_status: "Fair" }
];

export const mockBrics: BricsCountry[] = [
  { code: "BR", name: "Brazil", farmers_reached: 120000, active_alerts: 3, top_crop: "Soybean" },
  { code: "RU", name: "Russia", farmers_reached: 45000, active_alerts: 1, top_crop: "Wheat" },
  { code: "IN", name: "India", farmers_reached: 320000, active_alerts: 5, top_crop: "Rice" },
  { code: "CN", name: "China", farmers_reached: 210000, active_alerts: 2, top_crop: "Corn" },
  { code: "ZA", name: "South Africa", farmers_reached: 38000, active_alerts: 1, top_crop: "Maize" }
];

export const mockAlerts: Alert[] = [
  { id: "1", title: "Heat Wave Warning", message: "Temperatures expected to exceed 40°C in Northern regions.", date: "2024-05-15", severity: "Severe" },
  { id: "2", title: "Locust Swarm Sighted", message: "Movement detected near western border. Prepare preventative measures.", date: "2024-05-14", severity: "Critical" }
];
