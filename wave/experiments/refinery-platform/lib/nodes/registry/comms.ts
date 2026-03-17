/**
 * Communications Domain — 4 node definitions
 *
 * Data sources:
 *   commlog/recent    → GET /api/openclaw/commlog/recent    (15s)
 *   commlog/stats     → GET /api/openclaw/commlog/stats     (30s)
 */

import type { NodeDefinition } from '../types';

export const commsNodes: Record<string, NodeDefinition> = {
  'comms.recent': {
    id: 'comms.recent',
    domain: 'comms',
    title: 'Recent Communications',
    description: 'Latest communication log entries',
    kind: 'feed',
    purpose: {
      answers: 'What communications have happened recently?',
      relevance: 0.70,
      attentionCost: 'scan',
      narrativeRole: 'detail',
    },
    context: {
      requiresNearby: ['comms.stats'],
    },
    sense: {
      source: 'openclaw',
      endpoint: 'commlog/recent',
      intervalMs: 15_000,
    },
    representation: {
      preferredView: 'feed',
      salience: 'high',
      group: 'log',
      order: 0,
      maxItems: 20,
    },
    tags: ['comms', 'log'],
  },

  'comms.stats': {
    id: 'comms.stats',
    domain: 'comms',
    title: 'Communication Stats',
    description: 'Communication volume and channel breakdown',
    kind: 'metric',
    purpose: {
      answers: 'What is the overall communication volume and breakdown?',
      relevance: 0.80,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'commlog/stats',
      intervalMs: 30_000,
    },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'stats',
      order: 0,
    },
    tags: ['comms', 'stats'],
  },

  'comms.channels': {
    id: 'comms.channels',
    domain: 'comms',
    title: 'Active Channels',
    description: 'Communication channels and their status',
    kind: 'table',
    purpose: {
      answers: 'Which communication channels are active and what is their status?',
      relevance: 0.60,
      attentionCost: 'scan',
      narrativeRole: 'detail',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'commlog/stats',
      intervalMs: 30_000,
      fieldPath: 'channels',
    },
    representation: {
      preferredView: 'table',
      salience: 'normal',
      group: 'stats',
      order: 1,
      columns: [
        { key: 'name', label: 'Channel', align: 'left', render: 'text' },
        { key: 'type', label: 'Type', align: 'center', render: 'text' },
        { key: 'message_count', label: 'Messages', align: 'right', render: 'mono' },
        { key: 'status', label: 'Status', align: 'center', render: 'badge' },
      ],
    },
    tags: ['comms', 'channels'],
  },

  'comms.message-count': {
    id: 'comms.message-count',
    domain: 'comms',
    title: 'Total Messages',
    description: 'Total messages processed today',
    kind: 'metric',
    purpose: {
      answers: 'How many messages have been processed today?',
      relevance: 0.80,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'commlog/stats',
      intervalMs: 30_000,
      fieldPath: 'total_messages',
    },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'stats',
      order: 2,
    },
    tags: ['comms', 'metric'],
  },
};

/** All comms nodes as an array */
export const commsNodeList: NodeDefinition[] = Object.values(commsNodes);
