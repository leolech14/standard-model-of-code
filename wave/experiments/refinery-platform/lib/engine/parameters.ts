/**
 * Parameter Registry — every tunable seed and coefficient in Algebra-UI.
 *
 * Each parameter defines its beauty region (min/max safe range),
 * default values per theme, and metadata for the control panel.
 * Values outside the beauty region are blocked by the UI.
 */

export type ParamDomain = 'achromatic' | 'chromatic' | 'spacing' | 'radius' | 'shadow' | 'motion' | 'glass' | 'coefficient';
export type ParamType = 'seed' | 'coefficient';

export interface ParameterDef {
  id: string;
  domain: ParamDomain;
  type: ParamType;
  label: string;
  unit: string;
  dark: number;
  light: number;
  min: number;
  max: number;
  step: number;
}

export const PARAMETERS: ParameterDef[] = [
  // ── Achromatic Seeds ──
  { id: '--bg-l', domain: 'achromatic', type: 'seed', label: 'Background Lightness', unit: '', dark: 0.145, light: 0.965, min: 0.05, max: 0.99, step: 0.005 },
  { id: '--text-l', domain: 'achromatic', type: 'seed', label: 'Text Lightness', unit: '', dark: 0.922, light: 0.178, min: 0.1, max: 0.99, step: 0.005 },
  { id: '--text-secondary-l', domain: 'achromatic', type: 'seed', label: 'Secondary Text', unit: '', dark: 0.556, light: 0.439, min: 0.2, max: 0.8, step: 0.005 },
  { id: '--text-muted-l', domain: 'achromatic', type: 'seed', label: 'Muted Text', unit: '', dark: 0.439, light: 0.556, min: 0.2, max: 0.8, step: 0.005 },
  { id: '--accent-text-l', domain: 'achromatic', type: 'seed', label: 'Accent Text', unit: '', dark: 0.145, light: 0.993, min: 0.05, max: 0.99, step: 0.005 },

  // ── Chromatic Seeds (lightness per hue) ──
  { id: '--emerald-l', domain: 'chromatic', type: 'seed', label: 'Emerald L', unit: '', dark: 0.696, light: 0.596, min: 0.35, max: 0.85, step: 0.005 },
  { id: '--rose-l', domain: 'chromatic', type: 'seed', label: 'Rose L', unit: '', dark: 0.645, light: 0.577, min: 0.35, max: 0.85, step: 0.005 },
  { id: '--blue-l', domain: 'chromatic', type: 'seed', label: 'Blue L', unit: '', dark: 0.623, light: 0.553, min: 0.35, max: 0.85, step: 0.005 },
  { id: '--purple-l', domain: 'chromatic', type: 'seed', label: 'Purple L', unit: '', dark: 0.583, light: 0.513, min: 0.35, max: 0.85, step: 0.005 },
  { id: '--amber-l', domain: 'chromatic', type: 'seed', label: 'Amber L', unit: '', dark: 0.769, light: 0.700, min: 0.40, max: 0.90, step: 0.005 },
  { id: '--sky-l', domain: 'chromatic', type: 'seed', label: 'Sky L', unit: '', dark: 0.685, light: 0.615, min: 0.35, max: 0.85, step: 0.005 },

  // ── Spacing Seeds ──
  { id: '--space-unit', domain: 'spacing', type: 'seed', label: 'Space Unit', unit: 'rem', dark: 0.25, light: 0.25, min: 0.125, max: 0.5, step: 0.0125 },
  { id: '--density', domain: 'spacing', type: 'coefficient', label: 'Density', unit: 'x', dark: 1.0, light: 1.0, min: 0.5, max: 2.0, step: 0.05 },

  // ── Radius ──
  { id: '--radius-seed', domain: 'radius', type: 'seed', label: 'Radius Seed', unit: 'rem', dark: 0.5, light: 0.5, min: 0, max: 1.5, step: 0.0625 },

  // ── Shadow & Glass ──
  { id: '--shadow-strength', domain: 'shadow', type: 'coefficient', label: 'Shadow Strength', unit: 'x', dark: 1.0, light: 0.5, min: 0, max: 2.0, step: 0.05 },
  { id: '--glass-alpha', domain: 'glass', type: 'coefficient', label: 'Glass Opacity', unit: '', dark: 0.5, light: 0.7, min: 0.1, max: 1.0, step: 0.05 },
  { id: '--glass-blur-px', domain: 'glass', type: 'coefficient', label: 'Glass Blur', unit: 'px', dark: 12, light: 12, min: 0, max: 32, step: 1 },

  // ── Motion ──
  { id: '--motion-unit', domain: 'motion', type: 'seed', label: 'Motion Unit', unit: 'ms', dark: 50, light: 50, min: 10, max: 200, step: 5 },

  // ── Coefficients (surface/border derivation) ──
  { id: '--coeff-hover-l', domain: 'coefficient', type: 'coefficient', label: 'Hover Shift', unit: '', dark: 0.05, light: -0.05, min: -0.15, max: 0.15, step: 0.005 },
  { id: '--coeff-surface-l', domain: 'coefficient', type: 'coefficient', label: 'Surface Offset', unit: '', dark: 0.033, light: 0.028, min: 0.005, max: 0.08, step: 0.002 },
  { id: '--coeff-elevated-l', domain: 'coefficient', type: 'coefficient', label: 'Elevated Offset', unit: '', dark: 0.060, light: 0.028, min: 0.01, max: 0.10, step: 0.002 },
  { id: '--coeff-border-l', domain: 'coefficient', type: 'coefficient', label: 'Border Offset', unit: '', dark: 0.086, light: -0.096, min: -0.20, max: 0.20, step: 0.002 },
  { id: '--coeff-border-subtle-l', domain: 'coefficient', type: 'coefficient', label: 'Subtle Border', unit: '', dark: 0.150, light: -0.043, min: -0.25, max: 0.25, step: 0.002 },
  { id: '--coeff-dim-l', domain: 'coefficient', type: 'coefficient', label: 'Dim Shift', unit: '', dark: -0.10, light: -0.10, min: -0.20, max: 0, step: 0.005 },
  { id: '--coeff-dim-c', domain: 'coefficient', type: 'coefficient', label: 'Dim Chroma', unit: 'x', dark: 0.7, light: 0.7, min: 0.3, max: 1.0, step: 0.05 },
  { id: '--coeff-glow-alpha', domain: 'coefficient', type: 'coefficient', label: 'Glow Alpha', unit: '', dark: 0.25, light: 0.15, min: 0.05, max: 0.5, step: 0.01 },
];

export const PARAM_MAP = new Map(PARAMETERS.map(p => [p.id, p]));

export const DOMAINS: ParamDomain[] = ['achromatic', 'chromatic', 'spacing', 'radius', 'shadow', 'glass', 'motion', 'coefficient'];

export function getParamsByDomain(domain: ParamDomain): ParameterDef[] {
  return PARAMETERS.filter(p => p.domain === domain);
}
