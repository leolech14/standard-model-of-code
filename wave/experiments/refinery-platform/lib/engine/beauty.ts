/**
 * Beauty Region Validator — cross-parameter coherence constraints.
 *
 * Individual parameters have min/max (per-param beauty region).
 * This module checks COMBINATIONS that could be incoherent even
 * when each individual param is within its own range.
 *
 * Example: bg-l=0.5 and text-l=0.55 are both valid individually,
 * but together they produce unreadable text (contrast too low).
 */

export interface BeautyConstraint {
  id: string;
  description: string;
  check: (p: Record<string, number>) => { ok: boolean; message?: string };
}

function g(p: Record<string, number>, key: string, fallback: number): number {
  return p[key] ?? fallback;
}

export const BEAUTY_CONSTRAINTS: BeautyConstraint[] = [
  {
    id: 'text-contrast',
    description: 'Primary text must have sufficient contrast against background',
    check: (p) => {
      const delta = Math.abs(g(p, '--text-l', 0.9) - g(p, '--bg-l', 0.15));
      return delta >= 0.4
        ? { ok: true }
        : { ok: false, message: `Text contrast ${delta.toFixed(3)} < 0.4 minimum` };
    },
  },
  {
    id: 'text-hierarchy',
    description: 'Text lightness must maintain primary > secondary > muted hierarchy',
    check: (p) => {
      const bg = g(p, '--bg-l', 0.15);
      const primary = Math.abs(g(p, '--text-l', 0.9) - bg);
      const secondary = Math.abs(g(p, '--text-secondary-l', 0.55) - bg);
      const muted = Math.abs(g(p, '--text-muted-l', 0.44) - bg);
      return primary > secondary && secondary > muted
        ? { ok: true }
        : { ok: false, message: `Hierarchy broken: primary(${primary.toFixed(2)}) > secondary(${secondary.toFixed(2)}) > muted(${muted.toFixed(2)})` };
    },
  },
  {
    id: 'surface-elevation',
    description: 'Surface must be visually above background',
    check: (p) => {
      const coeff = g(p, '--coeff-surface-l', 0.033);
      return coeff > 0
        ? { ok: true }
        : { ok: false, message: `Surface coefficient ${coeff} must be positive` };
    },
  },
  {
    id: 'border-visible',
    description: 'Borders must be distinguishable from background',
    check: (p) => {
      const coeff = Math.abs(g(p, '--coeff-border-l', 0.086));
      return coeff >= 0.03
        ? { ok: true }
        : { ok: false, message: `Border offset |${coeff.toFixed(3)}| < 0.03 minimum` };
    },
  },
  {
    id: 'hover-perceptible',
    description: 'Hover state must produce a visible change',
    check: (p) => {
      const coeff = Math.abs(g(p, '--coeff-hover-l', 0.05));
      return coeff >= 0.02
        ? { ok: true }
        : { ok: false, message: `Hover shift |${coeff.toFixed(3)}| < 0.02 minimum` };
    },
  },
  {
    id: 'chromatic-contrast',
    description: 'Accent colors must be readable on background',
    check: (p) => {
      const bg = g(p, '--bg-l', 0.15);
      const hues = ['--emerald-l', '--rose-l', '--blue-l', '--purple-l', '--amber-l', '--sky-l'];
      const defaults = [0.696, 0.645, 0.623, 0.583, 0.769, 0.685];
      const violations: string[] = [];
      hues.forEach((h, i) => {
        const delta = Math.abs(g(p, h, defaults[i]) - bg);
        if (delta < 0.25) violations.push(`${h.replace('--', '').replace('-l', '')}: ${delta.toFixed(2)}`);
      });
      return violations.length === 0
        ? { ok: true }
        : { ok: false, message: `Low contrast hues: ${violations.join(', ')}` };
    },
  },
  {
    id: 'density-bounds',
    description: 'Density must stay within usable range',
    check: (p) => {
      const d = g(p, '--density', 1.0);
      return d >= 0.5 && d <= 2.0
        ? { ok: true }
        : { ok: false, message: `Density ${d} outside 0.5-2.0 range` };
    },
  },
  {
    id: 'shadow-coherence',
    description: 'Glass surfaces need shadows for depth perception',
    check: (p) => {
      const shadow = g(p, '--shadow-strength', 1.0);
      const glass = g(p, '--glass-alpha', 0.5);
      if (glass < 0.9 && shadow <= 0) {
        return { ok: false, message: 'Glass surfaces (alpha < 0.9) need shadow-strength > 0' };
      }
      return { ok: true };
    },
  },
];

export function validateBeauty(params: Record<string, number>): {
  allOk: boolean;
  results: { id: string; ok: boolean; message?: string }[];
} {
  const results = BEAUTY_CONSTRAINTS.map(c => ({
    id: c.id,
    ...c.check(params),
  }));
  return {
    allOk: results.every(r => r.ok),
    results,
  };
}
