import type {
  AdvisoryResponse,
  CropHealth,
  DashboardReport,
  DashboardStats,
  DiagnosisResponse,
  FarmConditions,
  FederationReport,
  FederationSignal,
  Kvk,
  LanguageCode,
  Outbreak,
  PersonalizedAlerts,
  RegenerativeResponse,
  SoilData,
  SourceStatus,
  StateConfig,
  WeatherRisk,
} from './types';

export const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

/** Error codes the UI knows how to explain; anything else maps to a generic message. */
export type ApiErrorCode =
  | 'NETWORK_ERROR'
  | 'TIMEOUT'
  | 'SERVICE_UNAVAILABLE'
  | 'RATE_LIMITED'
  | 'INVALID_INPUT'
  | 'PAYLOAD_TOO_LARGE'
  | 'IMAGE_TOO_LARGE'
  | 'IMAGE_TOO_SMALL'
  | 'UNSUPPORTED_MEDIA_TYPE'
  | 'UNAUTHORIZED'
  | 'TOKEN_EXPIRED'
  | 'FORBIDDEN'
  | 'AUTH_NOT_CONFIGURED'
  | 'NOT_FOUND'
  | 'NO_SPEECH'
  | 'INTERNAL_ERROR'
  | string;

export class ApiError extends Error {
  constructor(
    message: string,
    public code: ApiErrorCode,
    public status: number | null,
    public retryable: boolean,
    public requestId: string | null = null,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST';
  body?: BodyInit | null;
  json?: unknown;
  headers?: Record<string, string>;
  timeoutMs?: number;
  signal?: AbortSignal;
}

const DEFAULT_TIMEOUT_MS = 20_000;
export const AI_TIMEOUT_MS = 70_000;

export async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(new DOMException('timeout', 'TimeoutError')), opts.timeoutMs ?? DEFAULT_TIMEOUT_MS);
  const onAbort = () => controller.abort(opts.signal?.reason);
  opts.signal?.addEventListener('abort', onAbort);

  const headers: Record<string, string> = { Accept: 'application/json', ...opts.headers };
  let body = opts.body ?? null;
  if (opts.json !== undefined) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(opts.json);
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method: opts.method ?? (body ? 'POST' : 'GET'),
      headers,
      body,
      signal: controller.signal,
      cache: 'no-store',
    });
  } catch (err) {
    if (opts.signal?.aborted) throw err;
    const timedOut = controller.signal.aborted;
    throw new ApiError(timedOut ? 'Request timed out.' : 'Network error.', timedOut ? 'TIMEOUT' : 'NETWORK_ERROR', null, true);
  } finally {
    clearTimeout(timer);
    opts.signal?.removeEventListener('abort', onAbort);
  }

  const requestId = response.headers.get('x-request-id');
  if (!response.ok) {
    let payload: { error?: { code?: string; message?: string; retryable?: boolean } } = {};
    try {
      payload = await response.json();
    } catch {
      /* non-JSON error body (e.g. proxy error page) */
    }
    const e = payload.error ?? {};
    throw new ApiError(
      e.message || response.statusText || 'Request failed.',
      e.code || (response.status >= 500 ? 'SERVICE_UNAVAILABLE' : 'INTERNAL_ERROR'),
      response.status,
      e.retryable ?? response.status >= 500,
      requestId,
    );
  }
  return (await response.json()) as T;
}

const q = (params: Record<string, string | number | null | undefined>) =>
  new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== null && v !== undefined && v !== '') as [string, string][],
  ).toString();

// --- Farmer ---------------------------------------------------------------------

export const getFarmConditions = (lat: number, lng: number, signal?: AbortSignal) =>
  request<FarmConditions>(`/api/farm/conditions?${q({ lat, lng })}`, { signal });

export const getRegenerative = (lat: number, lng: number, crop: string | null, signal?: AbortSignal) =>
  request<RegenerativeResponse>(`/api/farm/regenerative?${q({ lat, lng, crop })}`, { signal, timeoutMs: 30_000 });

export const getSoil = (lat: number, lng: number, signal?: AbortSignal) =>
  request<SoilData>(`/api/farm/soil?${q({ lat, lng })}`, { signal, timeoutMs: 30_000 });

export const getCropHealth = (lat: number, lng: number, signal?: AbortSignal) =>
  request<CropHealth>(`/api/farm/crop-health?${q({ lat, lng })}`, { signal, timeoutMs: 40_000 });

export const getPersonalizedAlerts = (lat: number, lng: number, crop: string | null, signal?: AbortSignal) =>
  request<PersonalizedAlerts>(`/api/alerts/personalized?${q({ lat, lng, crop_type: crop })}`, { signal });

export const getNearestKvk = (lat: number, lng: number, signal?: AbortSignal) =>
  request<Kvk>(`/api/kvk/nearest?${q({ lat, lng })}`, { signal });

export function diagnoseCrop(
  image: Blob,
  opts: { crop: string | null; lat: number | null; lng: number | null; language: LanguageCode; idempotencyKey: string; signal?: AbortSignal },
) {
  const form = new FormData();
  form.append('file', image, 'crop.jpg');
  if (opts.crop) form.append('crop_type', opts.crop);
  if (opts.lat !== null && opts.lng !== null) {
    form.append('latitude', String(opts.lat));
    form.append('longitude', String(opts.lng));
  }
  form.append('language', opts.language);
  return request<DiagnosisResponse>('/api/diagnose', {
    method: 'POST',
    body: form,
    headers: { 'Idempotency-Key': opts.idempotencyKey },
    timeoutMs: AI_TIMEOUT_MS,
    signal: opts.signal,
  });
}

export interface AdvisoryInput {
  query: string;
  latitude: number;
  longitude: number;
  crop_type?: string | null;
  language: LanguageCode;
  image_base64?: string;
  disease_name?: string | null;
  severity?: string | null;
}

export const getAdvisory = (input: AdvisoryInput, signal?: AbortSignal) =>
  request<AdvisoryResponse>('/api/advisory', { json: input, timeoutMs: AI_TIMEOUT_MS, signal });

export const getFollowUpAdvisory = (input: AdvisoryInput, signal?: AbortSignal) =>
  request<AdvisoryResponse>('/api/advisory/followup', { json: input, timeoutMs: AI_TIMEOUT_MS, signal });

export const transcribeAudio = (audioBase64: string, language: LanguageCode) =>
  request<{ text: string }>('/api/advisory/transcribe', { json: { audio_base64: audioBase64, language }, timeoutMs: AI_TIMEOUT_MS });

export const ttsUrl = (text: string, lang: LanguageCode) => `${API_BASE}/api/advisory/tts?${q({ text: text.slice(0, 1500), lang })}`;

// --- Policymaker ----------------------------------------------------------------

export const getDashboardStats = (signal?: AbortSignal) => request<DashboardStats>('/api/dashboard/stats', { signal });
export const getOutbreaks = (signal?: AbortSignal) => request<Outbreak[]>('/api/dashboard/outbreaks', { signal });
export const getWeatherRisk = (signal?: AbortSignal) => request<WeatherRisk>('/api/dashboard/weather-risk', { signal, timeoutMs: 30_000 });
export const getDashboardReport = (language: LanguageCode, signal?: AbortSignal) =>
  request<DashboardReport>(`/api/dashboard/report?${q({ language })}`, { signal, timeoutMs: AI_TIMEOUT_MS });
export const getStates = (signal?: AbortSignal) =>
  request<{ states: StateConfig[] }>('/api/states', { signal }).then((r) => r.states);
export const getExchangeSignals = (signal?: AbortSignal) => request<FederationReport>('/api/states/exchange/signals', { signal });
export const getSources = (signal?: AbortSignal) => request<{ sources: SourceStatus[] }>('/api/sources', { signal }).then((r) => r.sources);

export function postExchangeSignal(signal: Partial<FederationSignal>, token: string) {
  return request<FederationSignal>('/api/states/exchange/signals', {
    json: signal,
    headers: { Authorization: `Bearer ${token}` },
  });
}
