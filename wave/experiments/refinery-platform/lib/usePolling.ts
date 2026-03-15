'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiGet, ApiError } from './api';

/**
 * Polling hook for OpenClaw API endpoints.
 *
 * Three polling tiers (from the plan):
 *   10s  -- live ops (health, system/current, commlog/recent)
 *   15s  -- semi-live (voice, llm, providers)
 *   30s  -- stable data (automations, settings, indicators)
 *
 * Usage:
 *   const { data, loading, error, refresh } = usePolling<HealthData>('health', 10_000);
 *
 * Features:
 *   - Fetches immediately on mount
 *   - Auto-polls at interval
 *   - Pauses when tab is hidden (saves bandwidth on VPS)
 *   - Cleans up on unmount
 *   - `refresh()` for manual re-fetch
 *   - `enabled` param to conditionally pause (for lazy tabs)
 */

interface UsePollingOptions {
  /** Polling interval in milliseconds. 0 = fetch once, no polling. */
  interval?: number;
  /** Whether polling is active. Default true. Set false for lazy-loaded tabs. */
  enabled?: boolean;
  /** Fetch timeout override (default 10s from api.ts) */
  timeout?: number;
}

interface UsePollingResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  /** Manually trigger a re-fetch */
  refresh: () => void;
}

export function usePolling<T = unknown>(
  path: string,
  opts: UsePollingOptions = {}
): UsePollingResult<T> {
  const { interval = 30_000, enabled = true, timeout } = opts;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Keep latest path/options in refs so interval callback always sees current values
  const pathRef = useRef(path);
  const timeoutRef = useRef(timeout);
  pathRef.current = path;
  timeoutRef.current = timeout;

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await apiGet<T>(pathRef.current, {
        timeout: timeoutRef.current,
      });
      setData(result);
      setError(null);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(
          err.status === 0
            ? 'Connection failed -- is OpenClaw running?'
            : err.status === 408
            ? 'Request timed out'
            : `Error ${err.status}: ${typeof err.body === 'string' ? err.body : JSON.stringify(err.body)}`
        );
      } else {
        setError(String(err));
      }
    } finally {
      setLoading(false);
    }
  }, []); // stable -- uses refs internally

  // Initial fetch + polling
  useEffect(() => {
    if (!enabled) return;

    fetchData();

    if (interval <= 0) return; // one-shot mode

    const id = setInterval(fetchData, interval);
    return () => clearInterval(id);
  }, [enabled, interval, fetchData]);

  // Pause polling when tab is hidden
  useEffect(() => {
    if (!enabled || interval <= 0) return;

    const handleVisibility = () => {
      if (document.visibilityState === 'visible') {
        // Fetch immediately when tab regains focus
        fetchData();
      }
    };

    document.addEventListener('visibilitychange', handleVisibility);
    return () => document.removeEventListener('visibilitychange', handleVisibility);
  }, [enabled, interval, fetchData]);

  return { data, loading, error, refresh: fetchData };
}
