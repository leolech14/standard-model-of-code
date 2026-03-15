/**
 * Node helpers — pure utility functions used by the rendering bridge.
 * No React, no DOM, no side effects.
 */

import type { InterpretDefinition } from './types';

/* ─── Field Extraction ─── */

/**
 * Extract a nested field from data using dot-notation path.
 * extractField({ cpu: { percent: 45 } }, 'cpu.percent') → 45
 * extractField({ cpu: { percent: 45 } }, 'cpu') → { percent: 45 }
 * extractField(data, undefined) → data (passthrough)
 */
export function extractField(data: unknown, path?: string): unknown {
  if (!path || !data) return data;
  const parts = path.split('.');
  let current: unknown = data;
  for (const part of parts) {
    if (current == null || typeof current !== 'object') return undefined;
    current = (current as Record<string, unknown>)[part];
  }
  return current;
}

/* ─── Template Interpolation ─── */

/**
 * Interpolate {field} placeholders in a template string from data object.
 * interpolateTemplate('{used} / {total}', { used: '3.2GB', total: '8GB' }) → '3.2GB / 8GB'
 */
export function interpolateTemplate(
  template: string,
  data: Record<string, unknown>,
): string {
  return template.replace(/\{(\w+)\}/g, (_, key) => {
    const val = data[key];
    if (val == null) return '--';
    return String(val);
  });
}

/* ─── Value Formatting ─── */

/**
 * Format a value based on interpretation hints.
 */
export function formatNodeValue(
  value: unknown,
  interpret?: InterpretDefinition,
): string {
  if (value == null) return '--';

  const format = interpret?.format;
  const unit = interpret?.unit ?? '';
  const precision = interpret?.precision;
  const scale = interpret?.scale;

  // Count format: array → length, else passthrough
  if (format === 'count') {
    return Array.isArray(value) ? String(value.length) : String(value);
  }

  // Currency format: +$123.45 / -$67.89
  if (format === 'currency') {
    const num = Number(value);
    if (isNaN(num)) return '--';
    const sign = num > 0 ? '+' : '';
    return `${sign}$${num.toFixed(precision ?? 2)}`;
  }

  // Apply scale multiplier for numeric formats
  let numVal = Number(value);
  if (scale && !isNaN(numVal)) {
    numVal = numVal * scale;
  }

  switch (format) {
    case 'duration': {
      const seconds = Number(value); // duration uses raw value, not scaled
      if (isNaN(seconds) || seconds <= 0) return '--';
      const d = Math.floor(seconds / 86400);
      const h = Math.floor((seconds % 86400) / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      if (d > 0) return `${d}d ${h}h ${m}m`;
      if (h > 0) return `${h}h ${m}m`;
      return `${m}m`;
    }
    case 'percent': {
      const pv = scale ? numVal : Number(value);
      return `${precision != null ? pv.toFixed(precision) : Math.round(pv)}%`;
    }
    case 'number': {
      const nv = scale ? numVal : Number(value);
      if (precision != null) return `${nv.toFixed(precision)}${unit ? ` ${unit}` : ''}`;
      return `${nv.toLocaleString()}${unit ? ` ${unit}` : ''}`;
    }
    case 'bytes':
      return `${value}${unit ? ` ${unit}` : ''}`;
    case 'text':
    default:
      return `${value}${unit ? ` ${unit}` : ''}`;
  }
}

/* ─── Status Mapping ─── */

/**
 * Map a status string to a Badge variant.
 * Generalizes the per-page serviceStatusToBadge pattern.
 */
export function statusToBadgeVariant(status?: string): string {
  if (!status) return 'idle';
  const map: Record<string, string> = {
    running: 'success',
    active: 'success',
    healthy: 'success',
    ok: 'success',
    connected: 'success',
    online: 'success',
    stopped: 'idle',
    inactive: 'idle',
    offline: 'idle',
    disconnected: 'idle',
    error: 'failed',
    failed: 'failed',
    critical: 'critical',
    degraded: 'warning',
    warning: 'warning',
    starting: 'running',
    restarting: 'running',
    pending: 'running',
  };
  return map[status.toLowerCase()] || 'idle';
}

/* ─── PnL Color ─── */

/**
 * Return a Tailwind text color class based on value sign.
 * Positive → green, negative → red, zero/null → neutral.
 */
export function pnlColorClass(v?: number | null): string {
  if (v == null || v === 0) return 'text-text';
  return v > 0 ? 'text-emerald' : 'text-danger';
}

/* ─── Data Normalization ─── */

/**
 * Apply a normalization hint to raw data before rendering.
 * 'find-array': scan object values for the first array (ranking response pattern).
 */
export function normalizeNodeData(data: unknown, hint?: string): unknown {
  if (!hint || !data) return data;
  if (hint === 'find-array') {
    if (Array.isArray(data)) return data;
    if (typeof data === 'object' && data !== null) {
      for (const v of Object.values(data)) {
        if (Array.isArray(v)) return v;
      }
    }
    return [];
  }
  return data;
}

/* ─── Badge Map Resolution ─── */

/**
 * Resolve a value against a badgeMap to get a Badge variant.
 * Returns undefined if no match found.
 */
export function resolveBadgeFromMap(
  value: unknown,
  map?: Record<string, string>,
): string | undefined {
  if (!map || value == null) return undefined;
  return map[String(value)];
}

/* ─── Severity Color ─── */

/**
 * Map severity string to a Tailwind text color class.
 */
export function severityColorClass(severity?: string): string {
  switch (severity?.toLowerCase()) {
    case 'error':
    case 'critical':
      return 'text-danger';
    case 'warning':
      return 'text-warning';
    case 'info':
      return 'text-info';
    default:
      return 'text-text-secondary';
  }
}
