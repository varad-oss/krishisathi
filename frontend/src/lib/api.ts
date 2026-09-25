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

const API_BASE = process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? 'https://krishisathi-iota.vercel.app' : 'http://localhost:8000');
export const IS_DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true';

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function fetchWithFallback<T>(url: string, options: RequestInit, fallback: T): Promise<T> {
  try {
    // Prevent Next.js from statically caching failed local builds
    const fetchOptions = { ...options, cache: 'no-store' as RequestCache };
    const response = await fetch(url, fetchOptions);
    if (!response.ok) {
      if (IS_DEMO_MODE) {
        console.warn(`API call failed: ${url}, using fallback data.`);
        return fallback;
      }
      let errMsg = `Service unavailable: ${response.statusText}`;
      if (response.status === 429) errMsg = "Too many requests. Please slow down.";
      if (response.status === 413) errMsg = "Payload too large.";
      if (response.status === 401 || response.status === 403) errMsg = "Access denied.";
      throw new ApiError(errMsg, response.status);
    }
    return await response.json() as T;
  } catch (error) {
    if (IS_DEMO_MODE) {
      console.warn(`API call error: ${url}, using fallback data. Error:`, error);
      return fallback;
    }
    if (error instanceof ApiError) throw error;
    throw new ApiError(`Network error or service unavailable`);
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
    if (!response.ok) {
      if (IS_DEMO_MODE) return mockDiagnosis;
      let errMsg = 'Service is temporarily unavailable.';
      if (response.status === 429) errMsg = 'Too many requests. Please slow down.';
      if (response.status === 413) errMsg = 'Payload too large.';
      if (response.status === 401 || response.status === 403) errMsg = 'Access denied.';
      throw new ApiError(errMsg, response.status);
    }

    const data = await response.json();
    // Map backend response shape to frontend types
    return {
      disease_name: data.disease_name,
      scientific_name: data.scientific_name,
      model_confidence_score: typeof data.model_confidence_score === 'number' 
        ? data.model_confidence_score 
        : (data.confidence || 0.9),
      model_inferred_severity: data.model_inferred_severity,
      model_inferred_spread_risk: data.model_inferred_spread_risk || 'Unknown',
      treatment_plan: {
        immediate_actions: data.treatment?.immediate || data.treatment_plan?.immediate_actions || [],
        organic_treatment: data.treatment?.organic || data.treatment_plan?.organic_treatment || [],
        chemical_treatment: data.treatment?.chemical || data.treatment_plan?.chemical_treatment || [],
        prevention: data.treatment?.prevention || data.treatment_plan?.prevention || [],
      },
    };
  } catch (error) {
    if (IS_DEMO_MODE) return mockDiagnosis;
    if (error instanceof ApiError) throw error;
    throw new ApiError('Diagnosis service could not be reached.');
  }
}

export async function getAdvisory(
  query: string, 
  lat: number, 
  lng: number, 
  cropType: string | undefined,
  language: string,
  imageBase64?: string
): Promise<AdvisoryResponse> {
  try {
    const payload: Record<string, unknown> = {
      query,
      latitude: lat,
      longitude: lng,
      language
    };
    if (cropType) payload.crop_type = cropType;
    if (imageBase64) payload.image_base64 = imageBase64;
    
    const response = await fetch(`${API_BASE}/api/advisory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      if (IS_DEMO_MODE) return mockAdvisory;
      let errMsg = 'Service is temporarily unavailable.';
      if (response.status === 429) errMsg = 'Too many requests. Please slow down.';
      if (response.status === 413) errMsg = 'Payload too large.';
      if (response.status === 401 || response.status === 403) errMsg = 'Access denied.';
      throw new ApiError(errMsg, response.status);
    }

    const data = await response.json();
    return {
      query: query,
      answer: data.advisory_text || data.answer || 'No advisory available.',
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    if (IS_DEMO_MODE) return mockAdvisory;
    if (error instanceof ApiError) throw error;
    throw new ApiError('Advisory service could not be reached.');
  }
}

export async function getFollowUpAdvisory(
  question: string,
  diseaseName: string,
  severity: string,
  cropType: string,
  lat: number,
  lng: number,
  language: string
): Promise<{ advisory_text: string } | null> {
  try {
    const response = await fetch(`${API_BASE}/api/advisory/followup?disease_name=${encodeURIComponent(diseaseName)}&severity=${encodeURIComponent(severity)}&crop_type=${encodeURIComponent(cropType)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: question,
        latitude: lat,
        longitude: lng,
        language: language,
      }),
    });
    if (!response.ok) {
      if (IS_DEMO_MODE) return null;
      let errMsg = 'Service is temporarily unavailable.';
      if (response.status === 429) errMsg = 'Too many requests. Please slow down.';
      if (response.status === 413) errMsg = 'Payload too large.';
      if (response.status === 401 || response.status === 403) errMsg = 'Access denied.';
      throw new ApiError(errMsg, response.status);
    }

    return await response.json();
  } catch (error) {
    if (IS_DEMO_MODE) return null;
    if (error instanceof ApiError) throw error;
    throw new ApiError(`Follow-up advisory failed: ${error instanceof Error ? error.message : ''}`);
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
    if (!response.ok) {
      if (IS_DEMO_MODE) throw new Error('Failed to fetch report');
      throw new ApiError('Dashboard report is unavailable.', response.status);
    }
    const data = await response.json();
    return data.report_text || data.report;
  } catch (error) {
    if (IS_DEMO_MODE) {
      return "## Weekly Agriculture Intelligence Report\n\nBased on data across 8 Indian states, we are observing a 15% increase in Late Blight cases in Western Maharashtra due to heavy monsoon rainfall. Wheat rust remains a concern in Punjab and UP. Fall Armyworm migration tracking suggests Karnataka maize fields should prepare preventive measures. Cross-state data exchange between Punjab and UP has enabled early warning advisories in the Gangetic wheat belt.";
    }
    throw error;
  }
}

export async function getOutbreaks(): Promise<OutbreakData[]> {
  try {
    const response = await fetch(`${API_BASE}/api/dashboard/outbreaks`);
    if (!response.ok) {
      if (IS_DEMO_MODE) return mockOutbreaks;
      let errMsg = 'Service is temporarily unavailable.';
      if (response.status === 429) errMsg = 'Too many requests. Please slow down.';
      if (response.status === 413) errMsg = 'Payload too large.';
      if (response.status === 401 || response.status === 403) errMsg = 'Access denied.';
      throw new ApiError(errMsg, response.status);
    }

    const data = await response.json();
    return data.map((item: OutbreakData & { first_reported?: string }) => ({
      ...item,
      date: item.date || item.first_reported,
      severity: item.severity ? item.severity.charAt(0).toUpperCase() + item.severity.slice(1) : 'Moderate'
    }));
  } catch (error) {
    if (IS_DEMO_MODE) return mockOutbreaks;
    if (error instanceof ApiError) throw error;
    throw new ApiError('Outbreaks data could not be reached.');
  }
}

export async function getCropHealth(): Promise<CropHealthData[]> {
  try {
    const response = await fetch(`${API_BASE}/api/dashboard/crop-health`);
    if (!response.ok) {
      if (IS_DEMO_MODE) return mockCropHealth;
      let errMsg = 'Service is temporarily unavailable.';
      if (response.status === 429) errMsg = 'Too many requests. Please slow down.';
      if (response.status === 413) errMsg = 'Payload too large.';
      if (response.status === 401 || response.status === 403) errMsg = 'Access denied.';
      throw new ApiError(errMsg, response.status);
    }
    const data = await response.json();
    if (data.status === 'unavailable') {
      return [];
    }
    if (data.regions && Array.isArray(data.regions)) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return data.regions.map((region: any) => ({
        region: region.name,
        ndvi_score: region.ndvi,
        moisture_level: region.moisture || 0.5,
        drought_risk: region.drought_risk || 0,
        primary_crop: region.primary_crop || '',
        health_status: region.status === 'healthy' ? 'Good' : region.status === 'stressed' ? 'Poor' : 'Fair'
      }));
    }
    if (IS_DEMO_MODE) return mockCropHealth;
    return [];
  } catch (error) {
    if (IS_DEMO_MODE) return mockCropHealth;
    if (error instanceof ApiError) throw error;
    throw new ApiError('Crop health data could not be reached.');
  }
}

export async function getIndianStates(): Promise<IndianState[]> {
  try {
    const response = await fetch(`${API_BASE}/api/states`);
    if (!response.ok) {
      if (IS_DEMO_MODE) return mockStates;
      let errMsg = 'Service is temporarily unavailable.';
      if (response.status === 429) errMsg = 'Too many requests. Please slow down.';
      if (response.status === 413) errMsg = 'Payload too large.';
      if (response.status === 401 || response.status === 403) errMsg = 'Access denied.';
      throw new ApiError(errMsg, response.status);
    }

    const data = await response.json();
    if (data && Array.isArray(data.states)) {
      return data.states;
    } else if (Array.isArray(data)) {
      return data;
    }
    if (IS_DEMO_MODE) return mockStates;
    throw new ApiError('Invalid states data format.');
  } catch (error) {
    if (IS_DEMO_MODE) return mockStates;
    if (error instanceof ApiError) throw error;
    throw new ApiError('States data could not be reached.');
  }
}

export async function getAlerts(): Promise<Alert[]> {
  return fetchWithFallback<Alert[]>(
    `${API_BASE}/api/dashboard/alerts`,
    { method: 'GET' },
    mockAlerts
  );
}

export async function getExchangeSignals(): Promise<unknown> {
  return fetchWithFallback<unknown>(
    `${API_BASE}/api/states/exchange/signals`,
    { method: 'GET' },
    { signals: [] }
  );
}

export async function getPersonalizedAlerts(lat: number, lng: number, cropType?: string): Promise<unknown[]> {
  const cropQuery = cropType ? `&crop_type=${encodeURIComponent(cropType)}` : '';
  try {
    const response = await fetch(`${API_BASE}/api/alerts/personalized?lat=${lat}&lng=${lng}${cropQuery}`);
    if (!response.ok) {
      if (IS_DEMO_MODE) return [];
      let errMsg = 'Service is temporarily unavailable.';
      if (response.status === 429) errMsg = 'Too many requests. Please slow down.';
      if (response.status === 413) errMsg = 'Payload too large.';
      if (response.status === 401 || response.status === 403) errMsg = 'Access denied.';
      throw new ApiError(errMsg, response.status);
    }

    const data = await response.json();
    return data.alerts || [];
  } catch (error) {
    if (IS_DEMO_MODE) return [];
    if (error instanceof ApiError) throw error;
    throw new ApiError(`Personalized alerts could not be reached. ${error instanceof Error ? error.message : ''}`);
  }
}


export async function postExchangeSignal(signal: any): Promise<any> {
  const response = await fetch(`${API_BASE}/api/states/exchange/signals`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer mock-system-token-123'
    },
    body: JSON.stringify(signal)
  });
  if (!response.ok) {
    throw new Error('Failed to post exchange signal');
  }
  return response.json();
}
