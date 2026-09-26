'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError } from './api';

export type Resource<T> =
  | { status: 'idle' | 'loading'; data: T | null; error: null; updatedAt: number | null; reload: () => void }
  | { status: 'success'; data: T; error: null; updatedAt: number; reload: () => void }
  | { status: 'error'; data: T | null; error: ApiError; updatedAt: number | null; reload: () => void };

/**
 * Loads data for one independent panel. On failure the last good data is kept
 * (callers must label it as stale via updatedAt), never replaced with placeholders.
 * Pass `null` as the loader to stay idle (e.g. while a required input is missing).
 */
export function useResource<T>(loader: ((signal: AbortSignal) => Promise<T>) | null, deps: unknown[]): Resource<T> {
  const [state, setState] = useState<{ status: Resource<T>['status']; data: T | null; error: ApiError | null; updatedAt: number | null }>({
    status: loader ? 'loading' : 'idle',
    data: null,
    error: null,
    updatedAt: null,
  });
  const [nonce, setNonce] = useState(0);
  const lastNonce = useRef(0);
  const loaderRef = useRef(loader);
  // Keep the latest loader without re-running the fetch effect on every render (declared first so it runs first).
  useEffect(() => {
    loaderRef.current = loader;
  });

  useEffect(() => {
    const load = loaderRef.current;
    if (!load) {
      setState({ status: 'idle', data: null, error: null, updatedAt: null });
      return;
    }
    const controller = new AbortController();
    // A retry keeps the last good data (labelled stale by the caller); new inputs (e.g. another
    // location) must never show the previous input's data while loading.
    const isRetry = lastNonce.current !== nonce;
    lastNonce.current = nonce;
    setState((s) => (isRetry ? { ...s, status: 'loading', error: null } : { status: 'loading', data: null, error: null, updatedAt: null }));
    load(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setState({ status: 'success', data, error: null, updatedAt: Date.now() });
      })
      .catch((err) => {
        if (controller.signal.aborted) return;
        const error = err instanceof ApiError ? err : new ApiError('Unexpected error', 'INTERNAL_ERROR', null, true);
        setState((s) => ({ ...s, status: 'error', error }));
      });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);

  const reload = useCallback(() => setNonce((n) => n + 1), []);
  return { ...state, reload } as Resource<T>;
}
