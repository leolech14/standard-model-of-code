'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { apiGet, ApiError } from './api';

/**
 * Multi-endpoint polling hook.
 *
 * Solves: React hooks can't be called in loops.
 * One hook manages N polling intervals imperatively via refs.
 *
 * Usage:
 *   const endpoints = [{ path: 'health', intervalMs: 10_000 }, ...];
 *   const { sourceMap, refreshAll } = useMultiPolling(endpoints);
 */

export interface EndpointConfig {
  /** API path segment, e.g. 'health', 'trading/current' */
  path: string;
  /** Polling interval in milliseconds. 0 = fetch once. */
  intervalMs: number;
}

export type SourceMap = Record<
  string,
  { data: unknown; loading: boolean; error: string | null }
>;

interface SlotState {
  data: unknown;
  loading: boolean;
  error: string | null;
  timer: ReturnType<typeof setInterval> | null;
}

export function useMultiPolling(endpoints: EndpointConfig[]): {
  sourceMap: SourceMap;
  refreshAll: () => void;
  refreshEndpoint: (path: string) => void;
} {
  // Stable serialized key for effect dependency
  const endpointKey = JSON.stringify(
    endpoints.map((e) => `${e.path}:${e.intervalMs}`).sort(),
  );

  // Mutable slot storage — never causes re-render on its own
  const slotsRef = useRef<Map<string, SlotState>>(new Map());
  // Re-render trigger
  const [, setTick] = useState(0);
  const bump = useCallback(() => setTick((t) => t + 1), []);

  // Fetch a single endpoint and update its slot
  const fetchOne = useCallback(
    async (path: string) => {
      const slot = slotsRef.current.get(path);
      if (!slot) return;

      slot.loading = true;
      bump();

      try {
        const result = await apiGet(path);
        // Slot may have been removed during fetch
        const current = slotsRef.current.get(path);
        if (current) {
          current.data = result;
          current.error = null;
          current.loading = false;
          bump();
        }
      } catch (err) {
        const current = slotsRef.current.get(path);
        if (!current) return;

        if (err instanceof ApiError) {
          current.error =
            err.status === 0
              ? 'Connection failed -- is OpenClaw running?'
              : err.status === 408
                ? 'Request timed out'
                : `Error ${err.status}: ${typeof err.body === 'string' ? err.body : JSON.stringify(err.body)}`;
        } else {
          current.error = String(err);
        }
        current.loading = false;
        bump();
      }
    },
    [bump],
  );

  // Setup/teardown on endpoint changes
  useEffect(() => {
    const slots = slotsRef.current;
    const activePaths = new Set(endpoints.map((e) => e.path));

    // Remove stale slots
    for (const [path, slot] of slots) {
      if (!activePaths.has(path)) {
        if (slot.timer) clearInterval(slot.timer);
        slots.delete(path);
      }
    }

    // Add/update slots
    for (const ep of endpoints) {
      let slot = slots.get(ep.path);

      if (!slot) {
        // New endpoint — create slot and fetch immediately
        slot = { data: null, loading: true, error: null, timer: null };
        slots.set(ep.path, slot);
        fetchOne(ep.path);
      }

      // (Re)set interval
      if (slot.timer) clearInterval(slot.timer);
      if (ep.intervalMs > 0) {
        slot.timer = setInterval(() => fetchOne(ep.path), ep.intervalMs);
      }
    }

    return () => {
      for (const [, slot] of slots) {
        if (slot.timer) clearInterval(slot.timer);
        slot.timer = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endpointKey, fetchOne]);

  // Tab visibility: refetch all on focus
  useEffect(() => {
    const handler = () => {
      if (document.visibilityState === 'visible') {
        for (const ep of endpoints) {
          fetchOne(ep.path);
        }
      }
    };
    document.addEventListener('visibilitychange', handler);
    return () => document.removeEventListener('visibilitychange', handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endpointKey, fetchOne]);

  // Build sourceMap snapshot from refs
  const sourceMap: SourceMap = {};
  for (const [path, slot] of slotsRef.current) {
    sourceMap[path] = {
      data: slot.data,
      loading: slot.loading,
      error: slot.error,
    };
  }

  const refreshAll = useCallback(() => {
    for (const ep of endpoints) {
      fetchOne(ep.path);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endpointKey, fetchOne]);

  const refreshEndpoint = useCallback(
    (path: string) => {
      fetchOne(path);
    },
    [fetchOne],
  );

  return { sourceMap, refreshAll, refreshEndpoint };
}
