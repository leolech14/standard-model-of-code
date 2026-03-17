/**
 * Runtime Bridge — live CSS variable manipulation via DOM.
 *
 * Changes CSS custom properties on documentElement. All calc()-derived
 * tokens recompute instantly via the browser's CSS engine. Zero JS
 * recalculation needed — the browser does the math.
 *
 * NOTE: Client-side only. Do not import in server components or API routes.
 */

import { PARAMETERS, PARAM_MAP, type ParameterDef } from './parameters';
import { validateBeauty } from './beauty';

const root = () => {
  if (typeof document === 'undefined') return null;
  return document.documentElement;
};

/** Read current resolved value of a CSS variable from the DOM */
export function getParam(id: string): number {
  const el = root();
  if (!el) return PARAM_MAP.get(id)?.dark ?? 0;

  // First check inline style (our overrides)
  const inline = el.style.getPropertyValue(id).trim();
  if (inline) return parseFloat(inline);

  // Fall back to computed style (from globals.css)
  const computed = getComputedStyle(el).getPropertyValue(id).trim();
  return computed ? parseFloat(computed) : (PARAM_MAP.get(id)?.dark ?? 0);
}

/** Set a single parameter with live update */
export function setParam(id: string, value: number): void {
  const el = root();
  if (!el) return;

  const def = PARAM_MAP.get(id);
  if (def) {
    // Clamp to beauty region
    value = Math.max(def.min, Math.min(def.max, value));
  }

  // Units that need suffix
  const unit = def?.unit ?? '';
  const cssValue = unit === 'rem' ? `${value}rem`
    : unit === 'px' ? `${value}px`
    : unit === 'ms' ? `${value}ms`
    : String(value);

  el.style.setProperty(id, cssValue);
}

/** Set multiple parameters atomically */
export function setParams(params: Record<string, number>): void {
  for (const [id, value] of Object.entries(params)) {
    setParam(id, value);
  }
}

/** Reset all overrides — return to globals.css defaults */
export function resetAll(): void {
  const el = root();
  if (!el) return;
  for (const p of PARAMETERS) {
    el.style.removeProperty(p.id);
  }
}

/** Reset a single domain */
export function resetDomain(domain: string): void {
  const el = root();
  if (!el) return;
  for (const p of PARAMETERS) {
    if (p.domain === domain) el.style.removeProperty(p.id);
  }
}

/** Export current state as a flat record */
export function exportState(): Record<string, number> {
  const state: Record<string, number> = {};
  for (const p of PARAMETERS) {
    state[p.id] = getParam(p.id);
  }
  return state;
}

/** Import state from a flat record */
export function importState(state: Record<string, number>): void {
  setParams(state);
}

/** Get current state + run beauty validation */
export function getStateWithValidation() {
  const state = exportState();
  const beauty = validateBeauty(state);
  return { state, beauty };
}

/** Get all parameter definitions (for rendering the control panel) */
export function getParameterDefs(): ParameterDef[] {
  return PARAMETERS;
}
