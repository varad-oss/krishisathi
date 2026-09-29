import type { Page, Route } from '@playwright/test';
import fixtures from './fixtures/api.json';

// Test-only API stubs. Fixture bodies were produced by the real FastAPI routes with upstream
// services (Open-Meteo, SoilGrids, Gemini) stubbed, so they follow the live contract.
export const API = 'http://127.0.0.1:8765';
type Fixtures = typeof fixtures;

const minutesAgo = (m: number) => new Date(Date.now() - m * 60_000).toISOString();

function fresh(): Fixtures {
  const f = structuredClone(fixtures);
  f.alerts.alerts.forEach((a) => (a.last_report_at = minutesAgo(90)));
  f.outbreaks.forEach((o, i) => (o.timestamp = minutesAgo(60 * (i + 1))));
  f.signals.signals.forEach((s) => (s.timestamp = minutesAgo(300)));
  f.stats.generated_at = new Date().toISOString();
  return f;
}

export type Override = { status?: number; body?: unknown; delayMs?: number; times?: number; abort?: boolean };
export type Overrides = Partial<Record<string, Override>>;

const json = (route: Route, status: number, body: unknown) =>
  route.fulfill({ status, contentType: 'application/json', headers: { 'access-control-allow-origin': '*', 'x-request-id': 'e2e-request-0001' }, body: JSON.stringify(body) });

/** Installs API stubs. `overrides` are keyed by route name (see ROUTES) and can inject failures. */
export async function mockApi(page: Page, overrides: Overrides = {}) {
  const f = fresh();
  const ROUTES: Record<string, { match: RegExp; body: unknown }> = {
    conditions: { match: /\/api\/farm\/conditions/, body: f.conditions },
    regenerative: { match: /\/api\/farm\/regenerative/, body: f.regenerative },
    cropHealth: { match: /\/api\/farm\/crop-health/, body: f.crop_health },
    alerts: { match: /\/api\/alerts\/personalized/, body: f.alerts },
    kvk: { match: /\/api\/kvk\/nearest/, body: f.kvk },
    diagnose: { match: /\/api\/diagnose$/, body: f.diagnosis },
    followup: { match: /\/api\/advisory\/followup/, body: f.advisory },
    advisory: { match: /\/api\/advisory$/, body: f.advisory },
    stats: { match: /\/api\/dashboard\/stats/, body: f.stats },
    outbreaks: { match: /\/api\/dashboard\/outbreaks/, body: f.outbreaks },
    weatherRisk: { match: /\/api\/dashboard\/weather-risk/, body: f.weather_risk },
    report: { match: /\/api\/dashboard\/report/, body: f.report },
    signals: { match: /\/api\/states\/exchange\/signals/, body: f.signals },
    states: { match: /\/api\/states$/, body: f.states },
    sources: { match: /\/api\/sources/, body: f.sources },
    voices: { match: /\/api\/advisory\/tts\/voices$/, body: { languages: { en: 'gemini', hi: 'gemini', mr: 'gemini', ta: 'gemini', te: 'gemini', bn: 'gemini', kn: 'gtts', gu: 'gtts', pa: 'gtts', ml: 'gtts' } } },
  };
  const remaining: Record<string, number> = {};

  await page.route(`${API}/**`, async (route) => {
    const url = new URL(route.request().url());
    if (route.request().method() === 'OPTIONS') return route.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*' } });
    if (/\/api\/advisory\/tts$/.test(url.pathname)) {
      // A short silent WAV so read-aloud can be exercised without a speech service.
      const o = overrides.tts;
      if (o?.status && o.status >= 400) return json(route, o.status, o.body);
      if (o?.delayMs) await new Promise((res) => setTimeout(res, o.delayMs));
      return route.fulfill({ status: 200, contentType: 'audio/wav', headers: { 'access-control-allow-origin': '*', 'x-tts-provider': 'gemini' }, body: silentWav() });
    }
    const entry = Object.entries(ROUTES).find(([, r]) => r.match.test(url.pathname));
    if (!entry && url.pathname === '/health/live' && overrides.health?.abort) return route.abort('failed');
    if (!entry) return json(route, 404, { error: { code: 'NOT_FOUND', message: 'No mock', request_id: 'x', retryable: false } });
    const [name, r] = entry;
    const o = overrides[name];
    if (o) {
      remaining[name] ??= o.times ?? Infinity;
      if (remaining[name] > 0) {
        remaining[name] -= 1;
        if (o.delayMs) await new Promise((res) => setTimeout(res, o.delayMs));
        if (o.abort) return route.abort('failed'); // what the browser sees for CORS blocks and dropped connections
        return json(route, o.status ?? 200, o.body ?? r.body);
      }
    }
    return json(route, 200, r.body);
  });
  return f;
}

/** 1.5 s of silence, 8 kHz mono 16-bit. */
function silentWav(): Buffer {
  const samples = 12_000;
  const b = Buffer.alloc(44 + samples * 2);
  b.write('RIFF', 0);
  b.writeUInt32LE(36 + samples * 2, 4);
  b.write('WAVEfmt ', 8);
  b.writeUInt32LE(16, 16);
  b.writeUInt16LE(1, 20);
  b.writeUInt16LE(1, 22);
  b.writeUInt32LE(8000, 24);
  b.writeUInt32LE(16000, 28);
  b.writeUInt16LE(2, 32);
  b.writeUInt16LE(16, 34);
  b.write('data', 36);
  b.writeUInt32LE(samples * 2, 40);
  return b;
}

export const unavailable = (message = 'Service is temporarily unavailable.'): Override => ({
  status: 503,
  body: { error: { code: 'SERVICE_UNAVAILABLE', message, request_id: '3f2a9c1e7b2d4a0f', retryable: true } },
});

/** Pre-seeds the farm profile so tests can open the dashboard directly. */
export async function withFarmProfile(page: Page, profile = { location: { lat: 18.52, lng: 73.856, source: 'place', placeId: 'pune' }, crop: 'Tomato' }) {
  await page.addInitScript((p) => localStorage.setItem('krishi_farm_profile', JSON.stringify(p)), profile);
}

export const fixtureData = fixtures;
