/**
 * Node Registry — aggregator and selectors.
 *
 * All domain registries re-export through here.
 * Pages import from this file, never directly from domain files.
 */

import type { NodeDefinition } from '../types';
import { systemNodeList } from './system';
import { voiceNodeList } from './voice';
import { tradingNodeList } from './trading';
import { commsNodeList } from './comms';
import { memoryNodeList } from './memory';

/** All registered nodes across all domains */
const ALL_NODES: NodeDefinition[] = [
  ...systemNodeList,
  ...voiceNodeList,
  ...tradingNodeList,
  ...commsNodeList,
  ...memoryNodeList,
];

/** Index by ID for O(1) lookup */
const NODE_MAP = new Map<string, NodeDefinition>(
  ALL_NODES.map((n) => [n.id, n]),
);

/* ─── Selectors ─── */

export function getAllNodes(): NodeDefinition[] {
  return ALL_NODES;
}

export function getNodesByDomain(domain: string): NodeDefinition[] {
  return ALL_NODES.filter((n) => n.domain === domain);
}

export function getNodeById(id: string): NodeDefinition | undefined {
  return NODE_MAP.get(id);
}

export function getNodesByGroup(domain: string, group: string): NodeDefinition[] {
  return ALL_NODES
    .filter((n) => n.domain === domain && n.representation.group === group)
    .sort((a, b) => (a.representation.order ?? 0) - (b.representation.order ?? 0));
}

/**
 * Deduplicate endpoints from a set of nodes.
 * Returns endpoint → shortest intervalMs (so shared endpoints
 * poll at the fastest rate any consumer needs).
 */
export function getUniqueEndpoints(
  nodes: NodeDefinition[],
): Map<string, number> {
  const map = new Map<string, number>();
  for (const node of nodes) {
    const ep = node.sense.endpoint;
    const existing = map.get(ep);
    if (existing == null || node.sense.intervalMs < existing) {
      map.set(ep, node.sense.intervalMs);
    }
  }
  return map;
}

/* ─── Re-exports ─── */

export { systemNodes, systemNodeList, getSystemNodesByGroup } from './system';
export { voiceNodes, voiceNodeList } from './voice';
export { tradingNodes, tradingNodeList, getTradingNodesByGroup } from './trading';
export { commsNodes, commsNodeList } from './comms';
export { memoryNodes, memoryNodeList } from './memory';
