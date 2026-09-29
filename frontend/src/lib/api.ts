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

/**
 * True when the build points at an API the browser can never reach from this page: a localhost API
 * on a deployed site (NEXT_PUBLIC_API_URL not set at build time) or an http API on an https page.
 */
export function apiMisconfigured(base: string = API_BASE, page: { protocol: string; hostname: string } | null = typeof location === 'undefined' ? null : location): boolean {
  if (!page) return false;
  let api: URL;
  try {
    api = new URL(base);
  } catch {
    return true;
  }
  const local = (h: string) => h === 'localhost' || h === '127.0.0.1' || h === '[::1]';
  if (local(api.hostname) && !local(page.hostname)) return true;
  return page.protocol === 'https:' && api.protocol === 'http:' && !local(api.hostname);
}

/** Error codes the UI knows how to explain; anything else maps to a generic message. */
export type ApiErrorCode =
  | 'NETWORK_ERROR'
  | 'OFFLINE'
  | 'CONFIG_ERROR'
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
  code: ApiErrorCode;
  status: number | null;
  retryable: boolean;
  requestId: string | null;
  constructor(message: string, code: ApiErrorCode, status: number | null, retryable: boolean, requestId: string | null = null) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.retryable = retryable;
    this.requestId = requestId;
  }
}

/** Code for an error response that has no JSON envelope (proxy/platform error pages). */
export function codeForStatus(status: number): ApiErrorCode {
  if (status === 404) return 'NOT_FOUND';
  if (status === 408 || status === 504) return 'TIMEOUT';
  if (status === 413) return 'PAYLOAD_TOO_LARGE';
  if (status === 429) return 'RATE_LIMITED';
  if (status === 400 || status === 422) return 'INVALID_INPUT';
  if (status >= 500) return 'SERVICE_UNAVAILABLE';
  return 'INTERNAL_ERROR';
}

let probe: { at: number; result: Promise<boolean> } | null = null;
/** Test hook: forget the shared reachability probe. */
export const resetReachabilityProbe = () => void (probe = null);

/**
 * fetch() rejects the same way for "no internet", DNS failure, a CORS block and a server that dropped the
 * connection. Probing the liveness endpoint in no-cors mode separates "the server is reachable, the request
 * failed there" from "nothing is reachable". One probe is shared by panels that fail together.
 */
function apiReachable(): Promise<boolean> {
  if (probe && Date.now() - probe.at < 5_000) return probe.result;
  const result = fetch(`${API_BASE}/health/live`, { mode: 'no-cors', cache: 'no-store', signal: AbortSignal.timeout(5_000) })
    .then(() => true)
    .catch(() => false);
  probe = { at: Date.now(), result };
  return result;
}

export async function classifyNetworkFailure(): Promise<ApiError> {
  if (typeof navigator !== 'undefined' && navigator.onLine === false) return new ApiError('Offline.', 'OFFLINE', null, true);
  if (apiMisconfigured()) return new ApiError('API address is not reachable from this site.', 'CONFIG_ERROR', null, false);
  return (await apiReachable())
    ? new ApiError('The service could not complete the request.', 'SERVICE_UNAVAILABLE', null, true)
    : new ApiError('Network error.', 'NETWORK_ERROR', null, true);
}

interface RequestOptions {
  method?: 'GET' | 'POST';
  body?: BodyInit | null;
  json?: unknown;
  headers?: Record<string, string>;
  timeoutMs?: number;
  signal?: AbortSignal;
  parse?: (response: Response) => Promise<unknown>;
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
    if (controller.signal.aborted) throw new ApiError('Request timed out.', 'TIMEOUT', null, true);
    throw await classifyNetworkFailure();
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
      e.code || codeForStatus(response.status),
      response.status,
      e.retryable ?? (response.status >= 500 || response.status === 429 || response.status === 408),
      requestId,
    );
  }
  return (await (opts.parse ? opts.parse(response) : response.json())) as T;
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

export interface SpeechAudio {
  audio: Blob;
  provider: string | null;
}

/** One chunk of read-aloud audio in the language's own voice (POST: Indic text makes very long URLs). */
export const synthesizeSpeech = (text: string, language: LanguageCode, signal?: AbortSignal) =>
  request<SpeechAudio>('/api/advisory/tts', {
    json: { text: text.slice(0, 1500), language },
    headers: { Accept: 'audio/*' },
    timeoutMs: AI_TIMEOUT_MS,
    signal,
    parse: async (r) => ({ audio: await r.blob(), provider: r.headers.get('x-tts-provider') }),
  });

/** Which server voice each language gets ("gemini" natural voice or "gtts"). */
export const getSpeechVoices = (signal?: AbortSignal) =>
  request<{ languages: Partial<Record<LanguageCode, 'gemini' | 'gtts'>> }>('/api/advisory/tts/voices', { signal });

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
