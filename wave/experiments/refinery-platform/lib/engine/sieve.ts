import type { CompassInstruction, Zone } from './compass';

/* ─── Types ─── */

export type ConstraintSeverity = 'must' | 'should' | 'prefer';

export interface Constraint {
  id: string;
  severity: ConstraintSeverity;
  check: (instructions: CompassInstruction[]) => ConstraintResult;
}

export interface ConstraintResult {
  passed: boolean;
  violation?: string;
  correction?: CompassInstruction[];
}

export interface SieveOutput {
  instructions: CompassInstruction[];
  corrections: { constraintId: string; description: string }[];
  warnings: { constraintId: string; description: string }[];
  errors: { constraintId: string; description: string }[];
}

/* ─── Helpers ─── */

function inZone(ins: CompassInstruction[], zone: Zone): CompassInstruction[] {
  return ins.filter(i => i.zone === zone);
}

function cloneInstructions(ins: CompassInstruction[]): CompassInstruction[] {
  return ins.map(i => ({ ...i }));
}

/* ─── Default Constraints ─── */

const anchorMustExist: Constraint = {
  id: 'anchor-must-exist',
  severity: 'must',
  check(instructions) {
    const top = inZone(instructions, 'top');
    if (top.length > 0) return { passed: true };

    // Promote highest-relevance node (first by order since sorted by relevance)
    const corrected = cloneInstructions(instructions);
    const best = corrected.reduce((a, b) => (a.order < b.order ? a : b), corrected[0]);
    if (best) best.zone = 'top';

    return {
      passed: false,
      violation: 'No node in top zone. Promoted highest-relevance node.',
      correction: corrected,
    };
  },
};

const areaBudget: Constraint = {
  id: 'area-budget',
  severity: 'must',
  check(instructions) {
    const total = instructions.reduce((sum, i) => sum + i.areaWeight, 0);
    if (total <= 1.0) return { passed: true };

    // Scale all weights proportionally so they sum to 1.0
    const scale = 1.0 / total;
    const corrected = cloneInstructions(instructions);
    for (const i of corrected) {
      i.areaWeight = Math.round(i.areaWeight * scale * 1000) / 1000;
    }

    return {
      passed: false,
      violation: `Area budget exceeded: ${total.toFixed(3)} > 1.0. Scaled proportionally.`,
      correction: corrected,
    };
  },
};

const zoneBalance: Constraint = {
  id: 'zone-balance',
  severity: 'should',
  check(instructions) {
    const top = inZone(instructions, 'top');
    if (top.length >= 1 && top.length <= 4) return { passed: true };

    if (top.length > 4) {
      // Demote lowest-relevance anchors (highest order number = lowest relevance) to middle
      const corrected = cloneInstructions(instructions);
      const topNodes = corrected
        .filter(i => i.zone === 'top')
        .sort((a, b) => a.order - b.order); // lowest order = highest relevance

      // Keep first 4, demote the rest
      for (let k = 4; k < topNodes.length; k++) {
        topNodes[k].zone = 'middle';
      }

      return {
        passed: false,
        violation: `Top zone has ${top.length} items (max 4). Demoted excess to middle.`,
        correction: corrected,
      };
    }

    // top.length === 0 is handled by anchor-must-exist; just warn here
    return {
      passed: false,
      violation: 'Top zone is empty. See anchor-must-exist constraint.',
    };
  },
};

const noEmptyZones: Constraint = {
  id: 'no-empty-zones',
  severity: 'prefer',
  check(instructions) {
    if (instructions.length < 6) return { passed: true };

    const zones: Zone[] = ['top', 'middle', 'bottom', 'contextual'];
    const empty = zones.filter(z => inZone(instructions, z).length === 0);

    if (empty.length === 0) return { passed: true };

    return {
      passed: false,
      violation: `Empty zones with ${instructions.length} nodes: ${empty.join(', ')}.`,
    };
  },
};

// TODO: V2 -- sieve receives CompassInstructions only, not full NodeDefinitions.
// To check requiresNearby, we need the ContextDefinition from each node.
// For V1 this constraint always passes.
const adjacentRespect: Constraint = {
  id: 'adjacent-respect',
  severity: 'should',
  check() {
    // V1 stub: always passes. Needs NodeDefinition context to check requiresNearby.
    return { passed: true };
  },
};

// TODO: V2 -- same as adjacent-respect. Needs ContextDefinition.contrastsWith
// from full NodeDefinitions to verify contrast pairs share a zone.
const contrastPair: Constraint = {
  id: 'contrast-pair',
  severity: 'prefer',
  check() {
    // V1 stub: always passes. Needs NodeDefinition context to check contrastsWith.
    return { passed: true };
  },
};

export const DEFAULT_CONSTRAINTS: Constraint[] = [
  anchorMustExist,
  areaBudget,
  zoneBalance,
  noEmptyZones,
  adjacentRespect,
  contrastPair,
];

/* ─── Sieve ─── */

export function sieve(
  instructions: CompassInstruction[],
  constraints: Constraint[] = DEFAULT_CONSTRAINTS,
): SieveOutput {
  let current = cloneInstructions(instructions);
  const corrections: SieveOutput['corrections'] = [];
  const warnings: SieveOutput['warnings'] = [];
  const errors: SieveOutput['errors'] = [];

  for (const constraint of constraints) {
    const result = constraint.check(current);

    if (result.passed) continue;

    const entry = { constraintId: constraint.id, description: result.violation ?? 'Constraint violated' };

    switch (constraint.severity) {
      case 'must':
        if (result.correction) {
          current = result.correction;
          corrections.push(entry);
        } else {
          errors.push(entry);
        }
        break;

      case 'should':
        if (result.correction) {
          current = result.correction;
          corrections.push(entry);
        } else {
          warnings.push(entry);
        }
        break;

      case 'prefer':
        warnings.push(entry);
        break;
    }
  }

  return { instructions: current, corrections, warnings, errors };
}
