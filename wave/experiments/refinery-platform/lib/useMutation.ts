'use client';

import { useState, useCallback, useRef } from 'react';
import { apiPost, apiPut, apiDelete, ApiError } from './api';

/**
 * Mutation hook for OpenClaw API write operations.
 *
 * Follows the plan's pattern: ActionButton -> Modal -> API -> Toast
 * The hook handles API + loading/error state. Modal + Toast handled at component level.
 *
 * Usage:
 *   const { mutate, loading, error } = useMutation<ResponseType>('llm/mode');
 *   // In handler:
 *   const result = await mutate({ mode: 'eco' });
 *
 * Options:
 *   method -- 'POST' (default), 'PUT', 'DELETE'
 *   onSuccess -- callback after successful mutation
 *   onError -- callback on failure
 */

type HttpMethod = 'POST' | 'PUT' | 'DELETE';

interface UseMutationOptions<T> {
  method?: HttpMethod;
  /** Called with response data on success */
  onSuccess?: (data: T) => void;
  /** Called with error message on failure */
  onError?: (error: string) => void;
  /** Fetch timeout override */
  timeout?: number;
}

interface UseMutationResult<T> {
  /** Execute the mutation. Returns response data or null on error. */
  mutate: (body?: unknown) => Promise<T | null>;
  loading: boolean;
  error: string | null;
  /** Reset error state */
  reset: () => void;
}

export function useMutation<T = unknown>(
  path: string,
  opts: UseMutationOptions<T> = {}
): UseMutationResult<T> {
  const { method = 'POST', onSuccess, onError, timeout } = opts;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Keep callbacks in refs to avoid re-renders triggering new mutate identity
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  onSuccessRef.current = onSuccess;
  onErrorRef.current = onError;

  const mutate = useCallback(
    async (body?: unknown): Promise<T | null> => {
      setLoading(true);
      setError(null);

      try {
        let result: T;
        const fetchOpts = { timeout };

        switch (method) {
          case 'PUT':
            result = await apiPut<T>(path, body, fetchOpts);
            break;
          case 'DELETE':
            result = await apiDelete<T>(path, fetchOpts);
            break;
          default:
            result = await apiPost<T>(path, body, fetchOpts);
        }

        onSuccessRef.current?.(result);
        return result;
      } catch (err) {
        const msg =
          err instanceof ApiError
            ? err.status === 0
              ? 'Connection failed'
              : `Error ${err.status}: ${typeof err.body === 'string' ? err.body : JSON.stringify(err.body)}`
            : String(err);

        setError(msg);
        onErrorRef.current?.(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [path, method, timeout]
  );

  const reset = useCallback(() => setError(null), []);

  return { mutate, loading, error, reset };
}
