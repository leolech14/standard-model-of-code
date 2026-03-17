import type { NodeDefinition, NarrativeRole, AttentionCost } from '../nodes/types';

export type Zone = 'top' | 'middle' | 'bottom' | 'contextual';
export type SalienceLevel = 'high' | 'normal' | 'low';

export interface CompassInstruction {
  nodeId: string;
  zone: Zone;
  salience: SalienceLevel;
  order: number;
  areaWeight: number;
}

export function interpret(nodes: NodeDefinition[]): CompassInstruction[] {
  // Sort by relevance descending (nodes without purpose get 0.5)
  const ranked = nodes
    .map(n => ({
      node: n,
      relevance: n.purpose?.relevance ?? 0.5,
      role: n.purpose?.narrativeRole ?? ('detail' as NarrativeRole),
      cost: n.purpose?.attentionCost ?? ('scan' as AttentionCost),
    }))
    .sort((a, b) => b.relevance - a.relevance);

  return ranked.map((item, i) => ({
    nodeId: item.node.id,
    zone: roleToZone(item.role),
    salience: relevanceToSalience(item.relevance),
    order: i,
    areaWeight: relevanceToArea(item.relevance),
  }));
}

function roleToZone(role: NarrativeRole): Zone {
  switch (role) {
    case 'anchor': return 'top';
    case 'detail': return 'middle';
    case 'evidence': return 'bottom';
    case 'action': return 'contextual';
    default: return 'middle';
  }
}

function relevanceToSalience(r: number): SalienceLevel {
  if (r >= 0.8) return 'high';
  if (r >= 0.5) return 'normal';
  return 'low';
}

function relevanceToArea(r: number): number {
  if (r >= 0.9) return 0.30;
  if (r >= 0.7) return 0.20;
  if (r >= 0.5) return 0.12;
  if (r >= 0.3) return 0.08;
  return 0.04;
}
