// Offline resilience: saved copies are dated, scoped and expire; queued answers are sent once and kept on failure.
import assert from 'node:assert/strict';
import { beforeEach, test } from 'node:test';

const store = new Map();
globalThis.localStorage = {
  getItem: (k) => (store.has(k) ? store.get(k) : null),
  setItem: (k, v) => store.set(k, String(v)),
  removeItem: (k) => store.delete(k),
};
const events = [];
globalThis.window = { dispatchEvent: (e) => events.push(e.type), addEventListener() {}, removeEventListener() {} };

const { cacheKey, enqueue, flushOutbox, isConnectivityError, readCached, readOutbox, saveCached } = await import('../src/lib/offline.ts');

beforeEach(() => {
  store.clear();
  events.length = 0;
});

test('a saved copy comes back with the time it was saved', () => {
  saveCached('k', { ndvi: 0.29 });
  const saved = readCached('k');
  assert.deepEqual(saved.data, { ndvi: 0.29 });
  assert.ok(Math.abs(saved.savedAt - Date.now()) < 1000);
});

test('copies older than a week are not shown', () => {
  saveCached('k', { a: 1 });
  assert.equal(readCached('k', Date.now() + 8 * 24 * 3600 * 1000), null);
});

test('cache keys are scoped to location and crop, so another farm never sees this copy', () => {
  assert.notEqual(cacheKey('conditions', 18.52, 73.86, 'Rice'), cacheKey('conditions', 18.52, 73.86, 'Wheat'));
  assert.notEqual(cacheKey('conditions', 18.52, 73.86, null), cacheKey('conditions', 30.9, 75.85, null));
});

test('corrupt storage is ignored, not shown', () => {
  store.set('krishi_cache:k', '{not json');
  assert.equal(readCached('k'), null);
});

test('only "cannot reach the service" errors allow a saved copy', () => {
  assert.ok(isConnectivityError('OFFLINE') && isConnectivityError('NETWORK_ERROR'));
  for (const code of ['SERVICE_UNAVAILABLE', 'RATE_LIMITED', 'INVALID_INPUT', undefined]) assert.equal(isConnectivityError(code), false);
});

const item = (id) => ({ id, kind: 'practice', farmId: 'f1', token: 't', body: { practice: 'cover_crop', status: 'adopted' } });

test('the same answer queued twice is sent once', async () => {
  enqueue(item('practice:cover_crop'));
  enqueue(item('practice:cover_crop'));
  const sent = [];
  assert.equal(await flushOutbox(async (i) => sent.push(i.id)), 0);
  assert.deepEqual(sent, ['practice:cover_crop']);
  assert.deepEqual(readOutbox(), []);
});

test('answers stay queued while still offline and are dropped when the server rejects them', async () => {
  enqueue(item('a'));
  enqueue(item('b'));
  const left = await flushOutbox(async (i) => {
    if (i.id === 'a') throw Object.assign(new Error('offline'), { status: null });
    throw Object.assign(new Error('bad'), { status: 422 });
  });
  assert.equal(left, 1);
  assert.deepEqual(readOutbox().map((i) => i.id), ['a']);
  assert.ok(events.includes('krishi-outbox'));
});
