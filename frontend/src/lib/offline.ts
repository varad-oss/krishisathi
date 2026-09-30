'use client';

import { useEffect, useState } from 'react';

/**
 * Offline resilience, kept deliberately small:
 * - a device cache of the last successful response per panel, always returned with the time it was saved so the
 *   UI can label it as a saved copy (never as current);
 * - an outbox for farmer feedback given while offline, sent when the connection returns.
 * Nothing here makes live services work offline.
 */

const CACHE_PREFIX = 'krishi_cache:';
const OUTBOX_KEY = 'krishi_outbox';
const MAX_AGE_MS = 7 * 24 * 3600 * 1000; // older copies are dropped rather than shown

export interface Cached<T> {
  data: T;
  savedAt: number;
}

/** Cache key scoped to the farm inputs, so a copy for one location or crop is never shown for another. */
export const cacheKey = (panel: string, lat: number, lng: number, crop?: string | null) =>
  `${panel}:${lat.toFixed(3)},${lng.toFixed(3)}:${crop ?? '-'}`;

export function saveCached<T>(key: string, data: T) {
  try {
    localStorage.setItem(CACHE_PREFIX + key, JSON.stringify({ data, savedAt: Date.now() }));
  } catch {
    /* storage full or unavailable: the app works without the cache */
  }
}

export function readCached<T>(key: string, now = Date.now()): Cached<T> | null {
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + key);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Cached<T>;
    if (typeof parsed?.savedAt !== 'number' || now - parsed.savedAt > MAX_AGE_MS || parsed.data == null) return null;
    return parsed;
  } catch {
    return null;
  }
}

/** Errors for which a saved copy may be shown: the device cannot reach the service at all. */
export const isConnectivityError = (code: string | undefined) => code === 'OFFLINE' || code === 'NETWORK_ERROR';

export type OutboxItem =
  | { id: string; kind: 'feedback'; farmId: string; token: string; actionId: string; body: Record<string, string> }
  | { id: string; kind: 'practice'; farmId: string; token: string; body: { practice: string; status: string } };

export function readOutbox(): OutboxItem[] {
  try {
    const items = JSON.parse(localStorage.getItem(OUTBOX_KEY) ?? '[]');
    return Array.isArray(items) ? items : [];
  } catch {
    return [];
  }
}

function writeOutbox(items: OutboxItem[]) {
  try {
    localStorage.setItem(OUTBOX_KEY, JSON.stringify(items));
  } catch {
    /* storage unavailable */
  }
  window.dispatchEvent(new Event('krishi-outbox'));
}

export function enqueue(item: OutboxItem) {
  writeOutbox([...readOutbox().filter((i) => i.id !== item.id), item]);
}

/**
 * Sends queued items in order. An item is removed when it is delivered or permanently rejected (4xx);
 * it stays queued when the connection fails again. Returns how many are still waiting.
 */
export async function flushOutbox(send: (item: OutboxItem) => Promise<void>): Promise<number> {
  const remaining: OutboxItem[] = [];
  for (const item of readOutbox()) {
    try {
      await send(item);
    } catch (e) {
      const status = (e as { status?: number | null })?.status;
      if (!(typeof status === 'number' && status >= 400 && status < 500)) remaining.push(item);
    }
  }
  writeOutbox(remaining);
  return remaining.length;
}

export function useOnline(): boolean {
  const [online, setOnline] = useState(true);
  useEffect(() => {
    const update = () => setOnline(navigator.onLine !== false);
    update();
    window.addEventListener('online', update);
    window.addEventListener('offline', update);
    return () => {
      window.removeEventListener('online', update);
      window.removeEventListener('offline', update);
    };
  }, []);
  return online;
}

export function useOutboxCount(): number {
  const [count, setCount] = useState(0);
  useEffect(() => {
    const update = () => setCount(readOutbox().length);
    update();
    window.addEventListener('krishi-outbox', update);
    window.addEventListener('storage', update);
    return () => {
      window.removeEventListener('krishi-outbox', update);
      window.removeEventListener('storage', update);
    };
  }, []);
  return count;
}
