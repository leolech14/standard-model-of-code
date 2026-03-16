/**
 * Ecosystem Domain — Parametric Cloud Context Visualization
 *
 * Migrated from Rainmaker's standalone HTML widget to the Semantic Node Architecture.
 * Each cloud service is a NodeDefinition with PurposeDefinition.
 * Positions are DERIVED from relevance tiers, not hardcoded x/y.
 *
 * Page mission: Visualize the living ecosystem — which cloud services feed
 * context into the local development environment, at what cost, and how they
 * connect through the Ecosystem Cloudpoint.
 *
 * Visual metaphor: Cloud (top) → Convergence (middle) → Laptop (bottom)
 */

import type { NodeDefinition, PageDefinition } from '../types';

/* ─── Page Definition ─── */

export const ecosystemPageDef: PageDefinition = {
  id: 'ecosystem',
  mission:
    'Visualize the living ecosystem — which cloud services feed context ' +
    'into the local development environment, at what cost, and how they ' +
    'connect through the Ecosystem Cloudpoint.',
  audience: 'developer-owner',
  cadence: 'on-demand',
  successCriteria: [
    'See all cloud services and their token contributions',
    'Understand which services are active vs standby',
    'Watch context aggregate in real time as services toggle',
    'See the data flow from cloud → cloudpoint → laptop',
  ],
};

/* ─── Service Metadata (source of truth for the widget) ─── */

export interface EcosystemServiceMeta {
  icon: string;
  sub: string;
  hue: string;       // maps to Mint seed name: 'emerald', 'blue', 'rose', etc.
  tokens: number;
}

export const SERVICE_META: Record<string, EcosystemServiceMeta> = {
  notion:      { icon: '📓', sub: 'docs',      hue: 'slate',   tokens: 1200 },
  chatgpt:     { icon: '💬', sub: 'research',  hue: 'emerald', tokens: 850 },
  google:      { icon: '🌐', sub: 'cloud',     hue: 'blue',    tokens: 2100 },
  github:      { icon: '🐙', sub: 'code',      hue: 'slate',   tokens: 3400 },
  anthropic:   { icon: '🤖', sub: 'LLMs',      hue: 'amber',   tokens: 1500 },
  supabase:    { icon: '⚡', sub: 'data',      hue: 'green',   tokens: 900 },
  doppler:     { icon: '🔑', sub: 'secrets',   hue: 'yellow',  tokens: 150 },
  openfinance: { icon: '📊', sub: 'data',      hue: 'indigo',  tokens: 600 },
  cerebras:    { icon: '🧮', sub: 'inference',  hue: 'rose',    tokens: 4500 },
  n8n:         { icon: '🔄', sub: 'flows',     hue: 'red',     tokens: 400 },
};

export const TOTAL_TOKENS = Object.values(SERVICE_META).reduce((s, m) => s + m.tokens, 0);

/* ─── Node Definitions ─── */

function serviceNode(
  id: string,
  title: string,
  relevance: number,
  nearbyIds: string[] = [],
): NodeDefinition {
  const meta = SERVICE_META[id]!;
  return {
    id: `ecosystem.${id}`,
    domain: 'ecosystem',
    title,
    description: `${meta.sub} — ${meta.tokens.toLocaleString()} context tokens`,
    kind: 'metric',
    purpose: {
      answers: `What does ${title} contribute to the ecosystem context?`,
      serves: ['See all cloud services and their token contributions'],
      relevance,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    context: {
      requiresNearby: nearbyIds.map(n => `ecosystem.${n}`),
      enables: ['ecosystem.convergence'],
    },
    sense: {
      source: 'local',
      endpoint: 'ecosystem',
      fieldPath: `services.${id}`,
      intervalMs: 0,
    },
    interpret: { format: 'count', unit: 'tokens' },
    representation: {
      preferredView: 'custom',
      customViewId: 'ecosystem-node',
      salience: relevance >= 0.80 ? 'high' : relevance >= 0.65 ? 'normal' : 'low',
      group: 'cloud-services',
      order: Math.round((1 - relevance) * 100),
      icon: meta.icon,
    },
    tags: [`provider:${id}`, `tier:${meta.sub}`, `hue:${meta.hue}`],
  };
}

export const ecosystemNodes: Record<string, NodeDefinition> = {
  // Tier 1 — highest token consumers / most critical
  'ecosystem.cerebras':    serviceNode('cerebras',    'Cerebras',     0.92, ['anthropic']),
  'ecosystem.github':      serviceNode('github',      'GitHub',       0.90, ['google']),
  'ecosystem.google':      serviceNode('google',      'Google',       0.88, ['github']),
  'ecosystem.anthropic':   serviceNode('anthropic',   'Anthropic',    0.88, ['cerebras']),

  // Tier 2 — significant contributors
  'ecosystem.chatgpt':     serviceNode('chatgpt',     'ChatGPT',      0.78, ['anthropic']),
  'ecosystem.supabase':    serviceNode('supabase',    'Supabase',     0.75),
  'ecosystem.notion':      serviceNode('notion',      'Notion',       0.72),

  // Tier 3 — supporting services
  'ecosystem.openfinance': serviceNode('openfinance', 'Open Finance', 0.65),
  'ecosystem.n8n':         serviceNode('n8n',         'n8n',          0.60),
  'ecosystem.doppler':     serviceNode('doppler',     'Doppler',      0.58),

  // Convergence point — the central hub
  'ecosystem.convergence': {
    id: 'ecosystem.convergence',
    domain: 'ecosystem',
    title: 'Ecosystem Cloudpoint',
    description: 'Where all cloud context converges into a unified token budget',
    kind: 'composite',
    purpose: {
      answers: 'What is the total ecosystem context budget?',
      serves: ['Watch context aggregate in real time as services toggle'],
      relevance: 1.0,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    context: { requiresNearby: ['ecosystem.terminal'] },
    sense: { source: 'local', endpoint: 'ecosystem', fieldPath: 'meta.totalTokens', intervalMs: 0 },
    representation: {
      preferredView: 'custom',
      customViewId: 'convergence-point',
      salience: 'high',
      group: 'convergence',
      order: 0,
    },
    tags: ['convergence', 'anchor', 'central'],
  },

  // Terminal — the local development laptop
  'ecosystem.terminal': {
    id: 'ecosystem.terminal',
    domain: 'ecosystem',
    title: 'Local Development',
    description: 'MacBook running Claude Code — where cloud context becomes local intelligence',
    kind: 'feed',
    purpose: {
      answers: 'Which services are actively loaded in the current session?',
      serves: ['See the data flow from cloud → cloudpoint → laptop'],
      relevance: 0.80,
      attentionCost: 'scan',
      narrativeRole: 'evidence',
    },
    context: { requiresNearby: ['ecosystem.convergence'] },
    sense: { source: 'local', endpoint: 'ecosystem', fieldPath: 'meta.activeServices', intervalMs: 0 },
    representation: {
      preferredView: 'custom',
      customViewId: 'terminal-laptop',
      salience: 'normal',
      group: 'local',
      order: 0,
    },
    tags: ['terminal', 'evidence', 'local-dev'],
  },
};

/* ─── Exports ─── */

export const ecosystemNodeList: NodeDefinition[] = Object.values(ecosystemNodes);
