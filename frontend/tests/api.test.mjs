// Connectivity and error classification: never report "check your internet" for a server-side failure.
import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import { ApiError, apiMisconfigured, codeForStatus, request, resetReachabilityProbe } from '../src/lib/api.ts';

const realFetch = globalThis.fetch;
const realNavigator = Object.getOwnPropertyDescriptor(globalThis, 'navigator');
afterEach(() => {
  globalThis.fetch = realFetch;
  if (realNavigator) Object.defineProperty(globalThis, 'navigator', realNavigator);
  resetReachabilityProbe();
});

const json = (status, body, headers = {}) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', ...headers } });

/** fetch stub: `api` answers API calls, `probe` answers the no-cors liveness probe. */
function stubFetch({ api, probe }) {
  const calls = [];
  globalThis.fetch = async (url, init = {}) => {
    calls.push({ url: String(url), mode: init.mode });
    if (init.mode === 'no-cors') return probe();
    return api(init);
  };
  return calls;
}

async function failure(promise) {
  try {
    await promise;
  } catch (e) {
    return e;
  }
  assert.fail('expected the request to fail');
}

test('503 with the error envelope keeps its code, message and request id', async () => {
  stubFetch({ api: async () => json(503, { error: { code: 'SERVICE_UNAVAILABLE', message: 'Weather down', retryable: true } }, { 'x-request-id': 'abc12345' }) });
  const e = await failure(request('/api/x'));
  assert.ok(e instanceof ApiError);
  assert.deepEqual([e.code, e.status, e.retryable, e.requestId, e.message], ['SERVICE_UNAVAILABLE', 503, true, 'abc12345', 'Weather down']);
});

test('non-JSON platform error pages are classified by status', async () => {
  for (const [status, code, retryable] of [[504, 'TIMEOUT', true], [502, 'SERVICE_UNAVAILABLE', true], [404, 'NOT_FOUND', false], [429, 'RATE_LIMITED', true], [422, 'INVALID_INPUT', false]]) {
    stubFetch({ api: async () => new Response('<html>error</html>', { status }) });
    const e = await failure(request('/api/x'));
    assert.deepEqual([e.code, e.retryable], [code, retryable], `status ${status}`);
  }
});

test('fetch failure with a reachable server is a service problem, not "no internet"', async () => {
  // e.g. a CORS-blocked 500 or a platform timeout page without CORS headers
  const calls = stubFetch({ api: async () => { throw new TypeError('Failed to fetch'); }, probe: async () => new Response(null, { status: 200 }) });
  const e = await failure(request('/api/dashboard/stats'));
  assert.equal(e.code, 'SERVICE_UNAVAILABLE');
  assert.equal(e.retryable, true);
  assert.ok(calls.some((c) => c.mode === 'no-cors' && c.url.endsWith('/health/live')));
});

test('fetch failure with nothing reachable is a network error', async () => {
  stubFetch({ api: async () => { throw new TypeError('Failed to fetch'); }, probe: async () => { throw new TypeError('Failed to fetch'); } });
  const e = await failure(request('/api/x'));
  assert.deepEqual([e.code, e.retryable], ['NETWORK_ERROR', true]);
});

test('browser offline is reported as offline without probing', async () => {
  Object.defineProperty(globalThis, 'navigator', { value: { onLine: false }, configurable: true });
  const calls = stubFetch({ api: async () => { throw new TypeError('Failed to fetch'); }, probe: async () => new Response(null) });
  const e = await failure(request('/api/x'));
  assert.equal(e.code, 'OFFLINE');
  assert.equal(calls.filter((c) => c.mode === 'no-cors').length, 0);
});

test('parallel failures share one reachability probe', async () => {
  const calls = stubFetch({ api: async () => { throw new TypeError('x'); }, probe: async () => new Response(null) });
  await Promise.all([failure(request('/a')), failure(request('/b')), failure(request('/c'))]);
  assert.equal(calls.filter((c) => c.mode === 'no-cors').length, 1);
});

test('client timeout is TIMEOUT and retryable', async () => {
  globalThis.fetch = (url, init) => new Promise((_, reject) => init.signal.addEventListener('abort', () => reject(init.signal.reason)));
  const e = await failure(request('/api/slow', { timeoutMs: 20 }));
  assert.deepEqual([e.code, e.retryable], ['TIMEOUT', true]);
});

test('caller abort is passed through, not turned into an error message', async () => {
  globalThis.fetch = (url, init) => new Promise((_, reject) => init.signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError'))));
  const controller = new AbortController();
  const p = request('/api/x', { signal: controller.signal });
  controller.abort();
  const e = await failure(p);
  assert.ok(!(e instanceof ApiError));
});

test('retry after a failure succeeds and parses JSON', async () => {
  let n = 0;
  stubFetch({ api: async () => (++n === 1 ? json(503, { error: { code: 'SERVICE_UNAVAILABLE', message: 'x' } }) : json(200, { ok: true })) });
  await failure(request('/api/x'));
  assert.deepEqual(await request('/api/x'), { ok: true });
});

test('custom parser returns binary audio with provider header', async () => {
  stubFetch({ api: async () => new Response(new Uint8Array([1, 2, 3]), { status: 200, headers: { 'x-tts-provider': 'gemini' } }) });
  const r = await request('/api/advisory/tts', { json: { text: 'x' }, parse: async (res) => ({ size: (await res.arrayBuffer()).byteLength, provider: res.headers.get('x-tts-provider') }) });
  assert.deepEqual(r, { size: 3, provider: 'gemini' });
});

test('API misconfiguration is detected for deployed sites', () => {
  const site = { protocol: 'https:', hostname: 'ai-krishisathi.vercel.app' };
  assert.equal(apiMisconfigured('http://localhost:8000', site), true);
  assert.equal(apiMisconfigured('http://api.example.org', site), true); // mixed content
  assert.equal(apiMisconfigured('https://api.example.org', site), false);
  assert.equal(apiMisconfigured('http://localhost:8000', { protocol: 'http:', hostname: 'localhost' }), false);
  assert.equal(apiMisconfigured('not a url', site), true);
  assert.equal(apiMisconfigured('http://localhost:8000', null), false);
});

test('codeForStatus', () => {
  assert.equal(codeForStatus(500), 'SERVICE_UNAVAILABLE');
  assert.equal(codeForStatus(408), 'TIMEOUT');
  assert.equal(codeForStatus(413), 'PAYLOAD_TOO_LARGE');
  assert.equal(codeForStatus(418), 'INTERNAL_ERROR');
});
