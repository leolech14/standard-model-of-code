/**
 * Trading Domain — 12 node definitions
 *
 * Data sources:
 *   trading/current      → GET /api/openclaw/trading/current      (10s)
 *   trading/market-state  → GET /api/openclaw/trading/market-state  (15s)
 *   trading/auto-entry    → GET /api/openclaw/trading/auto-entry    (15s)
 *   trading/ranking       → GET /api/openclaw/trading/ranking       (30s, dynamic query params)
 *
 * Friction log:
 *   #1  PnL formatting → format:'currency' + colorMode:'pnl'
 *   #2  Day type badges → badgeMap
 *   #3  Position count from array → format:'count'
 *   #4  BTC sync ×100 → scale:100
 *   #5  Number precision → precision:2
 *   #6  Auto-trading select+execute → parameters[] + ControlView
 *   #7  String array alerts → FeedView normalization
 *   #8  Table PnL/direction columns → render:'pnl'|'direction'
 *   #9  Ranking response normalization → dataNormalize:'find-array'
 *   #10 Market State composite → CompositeView with children (RESOLVED)
 *   #11 OpportunityCard → custom ViewKind
 *   #12 Dynamic ranking query params → filterParams metadata
 */

import type { NodeDefinition } from '../types';

export const tradingNodes: Record<string, NodeDefinition> = {
  /* ── Metrics (Info Tiles) ── */

  'trading.pnl-today': {
    id: 'trading.pnl-today',
    domain: 'trading',
    title: 'PnL Today',
    description: 'Daily realized profit/loss',
    kind: 'metric',
    purpose: {
      answers: 'How much money was made or lost today?',
      relevance: 0.92,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    context: {
      requiresNearby: ['trading.positions'],
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/current',
      intervalMs: 10_000,
      fieldPath: 'pnl.today',
    },
    interpret: {
      format: 'currency',
      colorMode: 'pnl',
    },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'metrics',
      order: 0,
    },
    tags: ['trading', 'pnl'],
  },

  'trading.unrealized': {
    id: 'trading.unrealized',
    domain: 'trading',
    title: 'Unrealized',
    description: 'Unrealized PnL across open positions',
    kind: 'metric',
    purpose: {
      answers: 'What is the floating profit/loss on open positions?',
      relevance: 0.92,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    context: {
      requiresNearby: ['trading.positions'],
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/current',
      intervalMs: 10_000,
      fieldPath: 'pnl.unrealized',
    },
    interpret: {
      format: 'currency',
      colorMode: 'pnl',
    },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'metrics',
      order: 1,
    },
    tags: ['trading', 'pnl'],
  },

  'trading.position-count': {
    id: 'trading.position-count',
    domain: 'trading',
    title: 'Positions',
    description: 'Number of open positions',
    kind: 'metric',
    purpose: {
      answers: 'How many positions are currently open?',
      relevance: 0.85,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/current',
      intervalMs: 10_000,
      fieldPath: 'positions',
    },
    interpret: {
      format: 'count',
    },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'metrics',
      order: 2,
    },
    tags: ['trading', 'positions'],
  },

  'trading.day-type': {
    id: 'trading.day-type',
    domain: 'trading',
    title: 'Day Type',
    description: 'Market day classification (WAVE_UP, CHOP, ROTATION, etc.)',
    kind: 'metric',
    purpose: {
      answers: 'What type of market day is it (trending, choppy, rotating)?',
      relevance: 0.80,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/market-state',
      intervalMs: 15_000,
      fieldPath: 'day_type',
    },
    interpret: {
      format: 'text',
      badgeMap: {
        WAVE_UP: 'success',
        WAVE_DOWN: 'error',
        BTC_ONLY: 'error',
        CHOP: 'warning',
        ROTATION: 'warning',
      },
    },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'metrics',
      order: 3,
    },
    tags: ['trading', 'market'],
  },

  /* ── Market State (Composite → child nodes) ── */

  'trading.market-state': {
    id: 'trading.market-state',
    domain: 'trading',
    title: 'Market State',
    description: 'Composite market state with breadth, dispersion, BTC sync, and top movers',
    kind: 'composite',
    purpose: {
      answers: 'What is the overall market condition across all indicators?',
      relevance: 0.80,
      attentionCost: 'scan',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/market-state',
      intervalMs: 15_000,
    },
    representation: {
      preferredView: 'composite',
      salience: 'normal',
      group: 'market',
      order: 0,
      children: ['trading.breadth', 'trading.dispersion', 'trading.btc-sync', 'trading.movers'],
      layout: 'mini-grid',
    },
    tags: ['trading', 'market'],
  },

  /* ── Top Movers (child of market-state composite) ── */

  'trading.movers': {
    id: 'trading.movers',
    domain: 'trading',
    title: 'Top Movers',
    description: 'Top moving symbols by volume/price change',
    kind: 'table',
    purpose: {
      answers: 'Which symbols are moving the most right now?',
      relevance: 0.70,
      attentionCost: 'scan',
      narrativeRole: 'detail',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/market-state',
      intervalMs: 15_000,
      fieldPath: 'top_movers',
    },
    representation: {
      preferredView: 'table',
      salience: 'normal',
      group: 'market-detail',
      order: 3,
      maxItems: 5,
      columns: [
        { key: 'symbol', label: 'Symbol', render: 'text' },
        { key: 'change_pct', label: 'Change', render: 'pnl', align: 'right' },
        { key: 'volume_rank', label: 'Vol Rank', render: 'mono', align: 'right' },
      ],
    },
    tags: ['trading', 'market'],
  },

  /* ── Market Detail Metrics ── */

  'trading.breadth': {
    id: 'trading.breadth',
    domain: 'trading',
    title: 'Breadth',
    description: 'Market breadth indicator',
    kind: 'metric',
    purpose: {
      answers: 'How broad is market participation across symbols?',
      relevance: 0.60,
      attentionCost: 'glance',
      narrativeRole: 'detail',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/market-state',
      intervalMs: 15_000,
      fieldPath: 'breadth',
    },
    interpret: {
      format: 'number',
      precision: 2,
    },
    representation: {
      preferredView: 'stat',
      salience: 'low',
      group: 'market-detail',
      order: 0,
    },
    tags: ['trading', 'market'],
  },

  'trading.dispersion': {
    id: 'trading.dispersion',
    domain: 'trading',
    title: 'Dispersion',
    description: 'Market dispersion indicator',
    kind: 'metric',
    purpose: {
      answers: 'How spread out are returns across the market?',
      relevance: 0.60,
      attentionCost: 'glance',
      narrativeRole: 'detail',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/market-state',
      intervalMs: 15_000,
      fieldPath: 'dispersion',
    },
    interpret: {
      format: 'number',
      precision: 2,
    },
    representation: {
      preferredView: 'stat',
      salience: 'low',
      group: 'market-detail',
      order: 1,
    },
    tags: ['trading', 'market'],
  },

  'trading.btc-sync': {
    id: 'trading.btc-sync',
    domain: 'trading',
    title: 'BTC Sync',
    description: 'Bitcoin correlation sync (0-1 raw, displayed as percentage)',
    kind: 'metric',
    purpose: {
      answers: 'How correlated is the market with Bitcoin right now?',
      relevance: 0.60,
      attentionCost: 'glance',
      narrativeRole: 'detail',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/market-state',
      intervalMs: 15_000,
      fieldPath: 'btc_sync',
    },
    interpret: {
      format: 'percent',
      scale: 100,
    },
    representation: {
      preferredView: 'stat',
      salience: 'low',
      group: 'market-detail',
      order: 2,
    },
    tags: ['trading', 'market'],
  },

  /* ── Positions Table ── */

  'trading.positions': {
    id: 'trading.positions',
    domain: 'trading',
    title: 'Open Positions',
    description: 'Active trading positions with PnL',
    kind: 'table',
    purpose: {
      answers: 'What positions are open and how is each performing?',
      relevance: 0.85,
      attentionCost: 'scan',
      narrativeRole: 'detail',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/current',
      intervalMs: 10_000,
      fieldPath: 'positions',
    },
    representation: {
      preferredView: 'table',
      salience: 'normal',
      group: 'positions',
      order: 0,
      columns: [
        { key: 'symbol', label: 'Symbol', render: 'text' },
        { key: 'side', label: 'Side', render: 'direction' },
        { key: 'size', label: 'Size', render: 'mono', align: 'right' },
        { key: 'entry', label: 'Entry', render: 'mono', align: 'right' },
        { key: 'current', label: 'Current', render: 'mono', align: 'right' },
        { key: 'pnl', label: 'PnL', render: 'pnl', align: 'right' },
        { key: 'pnl_pct', label: 'PnL %', render: 'pnl', align: 'right' },
      ],
    },
    tags: ['trading', 'positions'],
  },

  /* ── Auto-Trading Control ── */

  'trading.auto-entry': {
    id: 'trading.auto-entry',
    domain: 'trading',
    title: 'Auto-Trading',
    description: 'Auto-trading system control with enable/disable/go_live/advisory actions',
    kind: 'control',
    purpose: {
      answers: 'Is auto-trading enabled and in what mode?',
      relevance: 0.75,
      attentionCost: 'glance',
      narrativeRole: 'action',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/auto-entry',
      intervalMs: 15_000,
    },
    mutations: [
      {
        id: 'toggle',
        label: 'Execute',
        endpoint: 'trading/auto-entry/toggle',
        method: 'POST',
        confirm: 'Execute "{action}" on auto-trading system? This changes live trading behavior.',
        confirmTitle: 'Auto-Trading Control',
        dangerous: true,
        parameters: [
          {
            id: 'action',
            label: 'Action',
            options: [
              { value: 'enable', label: 'Enable' },
              { value: 'disable', label: 'Disable' },
              { value: 'go_live', label: 'Go Live' },
              { value: 'advisory', label: 'Advisory' },
            ],
          },
        ],
      },
    ],
    representation: {
      preferredView: 'toggle',
      salience: 'normal',
      group: 'control',
      order: 0,
      icon: 'Shield',
    },
    tags: ['trading', 'auto-trading', 'control'],
  },

  /* ── Alerts Feed ── */

  'trading.alerts': {
    id: 'trading.alerts',
    domain: 'trading',
    title: 'Alerts',
    description: 'Trading alerts and warnings (string array)',
    kind: 'feed',
    purpose: {
      answers: 'Are there any active trading alerts or warnings?',
      relevance: 0.85,
      attentionCost: 'scan',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/current',
      intervalMs: 10_000,
      fieldPath: 'alerts',
    },
    representation: {
      preferredView: 'feed',
      salience: 'normal',
      group: 'alerts',
      order: 0,
      icon: 'AlertTriangle',
      maxItems: 20,
    },
    tags: ['trading', 'alerts'],
  },

  /* ── Ranking / Opportunities (Custom View with Filters) ── */

  'trading.ranking': {
    id: 'trading.ranking',
    domain: 'trading',
    title: 'Trade Opportunities',
    description: 'Ranked trade opportunities with dynamic timeframe/direction filters',
    kind: 'list',
    purpose: {
      answers: 'What are the best trade opportunities right now?',
      relevance: 0.70,
      attentionCost: 'scan',
      narrativeRole: 'detail',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'trading/ranking',
      intervalMs: 30_000,
      filterParams: [
        {
          id: 'tf',
          label: 'Timeframe',
          options: [
            { value: '', label: 'All' },
            { value: '1m', label: '1m' },
            { value: '5m', label: '5m' },
            { value: '15m', label: '15m' },
            { value: '1h', label: '1h' },
            { value: '4h', label: '4h' },
          ],
        },
        {
          id: 'direction',
          label: 'Direction',
          options: [
            { value: '', label: 'Best' },
            { value: 'long', label: 'Long' },
            { value: 'short', label: 'Short' },
          ],
        },
      ],
    },
    representation: {
      preferredView: 'custom',
      customViewId: 'OpportunityList',
      dataNormalize: 'find-array',
      salience: 'normal',
      group: 'opportunities',
      order: 0,
    },
    tags: ['trading', 'ranking', 'opportunities'],
  },
};

/** All trading nodes as an array */
export const tradingNodeList: NodeDefinition[] = Object.values(tradingNodes);

/** Get trading nodes by group */
export function getTradingNodesByGroup(group: string): NodeDefinition[] {
  return tradingNodeList
    .filter((n) => n.representation.group === group)
    .sort((a, b) => (a.representation.order ?? 0) - (b.representation.order ?? 0));
}
