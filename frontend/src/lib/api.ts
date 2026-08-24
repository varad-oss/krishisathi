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
import { 
  mockDiagnosis, 
  mockAdvisory, 
  mockWeather, 
  mockDashboardStats, 
  mockOutbreaks, 
  mockCropHealth, 
  mockStates, 
  mockAlerts 
} from './mock-data';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchWithFallback<T>(url: string, options: RequestInit, fallback: T): Promise<T> {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      console.warn(`API call failed: ${url}, using fallback data.`);
      return fallback;
    }
    return await response.json() as T;
  } catch (error) {
    console.warn(`API call error: ${url}, using fallback data. Error:`, error);
    return fallback;
  }
}

export async function diagnoseCrop(
  imageFile: File, 
  cropType: string, 
  lat: number, 
  lng: number, 
  language: string
): Promise<DiagnosisResponse> {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('crop_type', cropType);
  formData.append('latitude', lat.toString());
  formData.append('longitude', lng.toString());
  formData.append('language', language);

  try {
    const response = await fetch(`${API_BASE}/api/diagnose`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) return mockDiagnosis;
    const data = await response.json();
    // Map backend response shape to frontend types
    return {
      disease_name: data.disease_name,
      scientific_name: data.scientific_name,
      confidence: typeof data.confidence === 'number' && data.confidence <= 1 
        ? data.confidence * 100 
        : data.confidence,
      severity: data.severity,
      spread_risk: data.spread_risk || 'Unknown',
      treatment_plan: {
        immediate_actions: data.treatment?.immediate || data.treatment_plan?.immediate_actions || [],
        organic_treatment: data.treatment?.organic || data.treatment_plan?.organic_treatment || [],
        chemical_treatment: data.treatment?.chemical || data.treatment_plan?.chemical_treatment || [],
        prevention: data.treatment?.prevention || data.treatment_plan?.prevention || [],
      },
    };
  } catch (error) {
    console.warn('Diagnosis API failed, using fallback:', error);
    return mockDiagnosis;
  }
}

export async function getAdvisory(
  query: string, 
  lat: number, 
  lng: number, 
  language: string
): Promise<AdvisoryResponse> {
  try {
    const response = await fetch(`${API_BASE}/api/advisory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, latitude: lat, longitude: lng, language }),
    });
    if (!response.ok) return mockAdvisory;
    const data = await response.json();
    return {
      query: query,
      answer: data.advisory_text || data.answer || 'No advisory available.',
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    console.warn('Advisory API failed, using fallback:', error);
    return mockAdvisory;
  }
}

export async function getWeather(lat: number, lng: number): Promise<WeatherData> {
  return fetchWithFallback<WeatherData>(
    `${API_BASE}/api/weather?lat=${lat}&lng=${lng}`,
    { method: 'GET' },
    mockWeather
  );
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return fetchWithFallback<DashboardStats>(
    `${API_BASE}/api/dashboard/stats`,
    { method: 'GET' },
    mockDashboardStats
  );
}

export async function getDashboardReport(language: string = 'en'): Promise<string> {
  try {
    const response = await fetch(`${API_BASE}/api/dashboard/report?language=${language}`, { cache: 'no-store' });
    if (!response.ok) throw new Error('Failed to fetch report');
    const data = await response.json();
    return data.report_text || data.report;
  } catch (error) {
    return "## Weekly Agriculture Intelligence Report\n\nBased on data across 8 Indian states, we are observing a 15% increase in Late Blight cases in Western Maharashtra due to heavy monsoon rainfall. Wheat rust remains a concern in Punjab and UP. Fall Armyworm migration tracking suggests Karnataka maize fields should prepare preventive measures. Cross-state data exchange between Punjab and UP has enabled early warning advisories in the Gangetic wheat belt.";
  }
}

export async function getOutbreaks(): Promise<OutbreakData[]> {
  try {
    const response = await fetch(`${API_BASE}/api/dashboard/outbreaks`);
    if (!response.ok) return mockOutbreaks;
    const data = await response.json();
    return data.map((item: any) => ({
      ...item,
      date: item.date || item.first_reported,
      severity: item.severity ? item.severity.charAt(0).toUpperCase() + item.severity.slice(1) : 'Moderate'
    }));
  } catch (error) {
    console.warn('Outbreaks API failed, using fallback:', error);
    return mockOutbreaks;
  }
}

export async function getCropHealth(): Promise<CropHealthData[]> {
  try {
    const response = await fetch(`${API_BASE}/api/dashboard/crop-health`);
    if (!response.ok) return mockCropHealth;
    const data = await response.json();
    
    // The backend might return an array directly, or an object with a 'regions' array
    if (Array.isArray(data)) {
      return data;
    } else if (data && Array.isArray(data.regions)) {
      // Map the new backend schema to match the frontend CropHealthData interface
      return data.regions.map((region: any) => ({
        region: region.name || region.region,
        ndvi_score: region.ndvi || region.ndvi_score,
        drought_risk: region.drought_risk,
        primary_crop: region.primary_crop,
        health_status: region.status === 'healthy' ? 'Good' : region.status === 'stressed' ? 'Poor' : 'Fair'
      }));
    }
    return mockCropHealth;
  } catch (error) {
    console.warn('Crop Health API failed, using fallback:', error);
    return mockCropHealth;
  }
}

export async function getIndianStates(): Promise<IndianState[]> {
  try {
    const response = await fetch(`${API_BASE}/api/states`);
    if (!response.ok) return mockStates;
    const data = await response.json();
    if (data && Array.isArray(data.states)) {
      return data.states;
    } else if (Array.isArray(data)) {
      return data;
    }
    return mockStates;
  } catch (error) {
    console.warn('States API failed, using fallback:', error);
    return mockStates;
  }
}

export async function getAlerts(): Promise<Alert[]> {
  return fetchWithFallback<Alert[]>(
    `${API_BASE}/api/dashboard/alerts`,
    { method: 'GET' },
    mockAlerts
  );
}

export async function getExchangeSignals(): Promise<any> {
  return fetchWithFallback<any>(
    `${API_BASE}/api/states/exchange/signals`,
    { method: 'GET' },
    { signals: [] }
  );
}

export async function getPersonalizedAlerts(lat: number, lng: number, cropType?: string): Promise<any[]> {
  const cropQuery = cropType ? `&crop_type=${encodeURIComponent(cropType)}` : '';
  try {
    const response = await fetch(`${API_BASE}/api/alerts/personalized?lat=${lat}&lng=${lng}${cropQuery}`);
    if (!response.ok) return [];
    const data = await response.json();
    return data.alerts || [];
  } catch (error) {
    console.warn('Personalized Alerts API failed:', error);
    return [];
  }
}
