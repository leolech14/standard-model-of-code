/**
 * Memory Domain — 4 node definitions
 *
 * Data sources:
 *   memory/chunks    → GET /api/openclaw/memory/chunks    (30s)
 *   memory/stats     → GET /api/openclaw/memory/stats     (30s)
 */

import type { NodeDefinition } from '../types';

export const memoryNodes: Record<string, NodeDefinition> = {
  'memory.chunk-count': {
    id: 'memory.chunk-count',
    domain: 'memory',
    title: 'Total Chunks',
    description: 'Number of memory chunks stored',
    kind: 'metric',
    sense: {
      source: 'openclaw',
      endpoint: 'memory/stats',
      intervalMs: 30_000,
      fieldPath: 'total_chunks',
    },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'stats',
      order: 0,
    },
    tags: ['memory', 'metric'],
  },

  'memory.storage-used': {
    id: 'memory.storage-used',
    domain: 'memory',
    title: 'Storage Used',
    description: 'Total memory storage consumption',
    kind: 'metric',
    sense: {
      source: 'openclaw',
      endpoint: 'memory/stats',
      intervalMs: 30_000,
      fieldPath: 'storage_used',
    },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'stats',
      order: 1,
    },
    tags: ['memory', 'metric'],
  },

  'memory.recent-chunks': {
    id: 'memory.recent-chunks',
    domain: 'memory',
    title: 'Recent Chunks',
    description: 'Most recently stored memory chunks',
    kind: 'table',
    sense: {
      source: 'openclaw',
      endpoint: 'memory/chunks',
      intervalMs: 30_000,
    },
    representation: {
      preferredView: 'table',
      salience: 'normal',
      group: 'chunks',
      order: 0,
      maxItems: 20,
      columns: [
        { key: 'source', label: 'Source', align: 'left', render: 'text' },
        { key: 'type', label: 'Type', align: 'center', render: 'text' },
        { key: 'size', label: 'Size', align: 'right', render: 'mono' },
        { key: 'created_at', label: 'Created', align: 'right', render: 'mono' },
      ],
    },
    tags: ['memory', 'chunks'],
  },

  'memory.collections': {
    id: 'memory.collections',
    domain: 'memory',
    title: 'Collections',
    description: 'Memory collections and their sizes',
    kind: 'table',
    sense: {
      source: 'openclaw',
      endpoint: 'memory/stats',
      intervalMs: 30_000,
      fieldPath: 'collections',
    },
    representation: {
      preferredView: 'table',
      salience: 'normal',
      group: 'stats',
      order: 2,
      columns: [
        { key: 'name', label: 'Collection', align: 'left', render: 'text' },
        { key: 'count', label: 'Chunks', align: 'right', render: 'mono' },
        { key: 'size', label: 'Size', align: 'right', render: 'mono' },
      ],
    },
    tags: ['memory', 'collections'],
  },
};

/** All memory nodes as an array */
export const memoryNodeList: NodeDefinition[] = Object.values(memoryNodes);
