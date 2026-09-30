'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError } from './api';
import { isConnectivityError, readCached, saveCached } from './offline';

/** `cached` is true when `data` is a saved copy from this device (offline); `updatedAt` is when it was saved. */
export type Resource<T> =
  | { status: 'idle' | 'loading'; data: T | null; error: null; updatedAt: number | null; cached: boolean; reload: () => void }
  | { status: 'success'; data: T; error: null; updatedAt: number; cached: false; reload: () => void }
  | { status: 'error'; data: T | null; error: ApiError; updatedAt: number | null; cached: boolean; reload: () => void };

/**
 * Loads data for one independent panel. On failure the last good data is kept
 * (callers must label it as stale via updatedAt), never replaced with placeholders.
 * Pass `null` as the loader to stay idle (e.g. while a required input is missing).
 *
 * With `cacheKey`, each success is saved on the device; when the device cannot reach the service at all and
 * nothing is loaded yet, the saved copy is returned as an error state with `cached: true` and its save time,
 * so panels show it with "last updated" and the offline reason, never as current. It reloads when the
 * connection returns.
 */
export function useResource<T>(loader: ((signal: AbortSignal) => Promise<T>) | null, deps: unknown[], cacheKey?: string | null): Resource<T> {
  const [state, setState] = useState<{ status: Resource<T>['status']; data: T | null; error: ApiError | null; updatedAt: number | null; cached: boolean }>({
    status: loader ? 'loading' : 'idle',
    data: null,
    error: null,
    updatedAt: null,
    cached: false,
  });
  const keyRef = useRef(cacheKey);
  const [nonce, setNonce] = useState(0);
  const lastNonce = useRef(0);
  const loaderRef = useRef(loader);
  // Keep the latest loader without re-running the fetch effect on every render (declared first so it runs first).
  useEffect(() => {
    loaderRef.current = loader;
    keyRef.current = cacheKey;
  });

  useEffect(() => {
    const load = loaderRef.current;
    if (!load) {
      setState({ status: 'idle', data: null, error: null, updatedAt: null, cached: false });
      return;
    }
    const controller = new AbortController();
    // A retry keeps the last good data (labelled stale by the caller); new inputs (e.g. another
    // location) must never show the previous input's data while loading.
    const isRetry = lastNonce.current !== nonce;
    lastNonce.current = nonce;
    setState((s) => (isRetry ? { ...s, status: 'loading', error: null } : { status: 'loading', data: null, error: null, updatedAt: null, cached: false }));
    load(controller.signal)
      .then((data) => {
        if (controller.signal.aborted) return;
        if (keyRef.current) saveCached(keyRef.current, data);
        setState({ status: 'success', data, error: null, updatedAt: Date.now(), cached: false });
      })
      .catch((err) => {
        if (controller.signal.aborted) return;
        const error = err instanceof ApiError ? err : new ApiError('Unexpected error', 'INTERNAL_ERROR', null, true);
        setState((s) => {
          if (s.data == null && keyRef.current && isConnectivityError(error.code)) {
            const saved = readCached<T>(keyRef.current);
            if (saved) return { status: 'error', data: saved.data, error, updatedAt: saved.savedAt, cached: true };
          }
          return { ...s, status: 'error', error };
        });
      });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);

  const reload = useCallback(() => setNonce((n) => n + 1), []);

  // Back online after a connectivity failure: fetch fresh data instead of leaving the saved copy up.
  const offlineError = state.status === 'error' && isConnectivityError(state.error?.code);
  useEffect(() => {
    if (!offlineError) return;
    window.addEventListener('online', reload);
    return () => window.removeEventListener('online', reload);
  }, [offlineError, reload]);
  return { ...state, reload } as Resource<T>;
}
