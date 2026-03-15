/**
 * System Domain — 11 node definitions
 *
 * Data sources:
 *   health          → GET /api/openclaw/health          (10s)
 *   system/current  → GET /api/openclaw/system/current  (10s)
 *   system/history  → GET /api/openclaw/system/history   (30s)
 */

import type { NodeDefinition } from '../types';

export const systemNodes: Record<string, NodeDefinition> = {
  /* ── Header ── */
  'system.health': {
    id: 'system.health',
    domain: 'system',
    title: 'Health',
    description: 'Overall system health status',
    kind: 'status',
    sense: {
      source: 'openclaw',
      endpoint: 'health',
      intervalMs: 10_000,
      fieldPath: 'status',
    },
    interpret: {
      emptyMeans: 'unknown',
    },
    representation: {
      preferredView: 'status-pill',
      salience: 'high',
      group: 'header',
      order: 0,
    },
    tags: ['system', 'health'],
  },

  /* ── Resources (Gauges) ── */
  'system.cpu': {
    id: 'system.cpu',
    domain: 'system',
    title: 'CPU',
    kind: 'metric',
    sense: {
      source: 'openclaw',
      endpoint: 'system/current',
      intervalMs: 10_000,
      fieldPath: 'cpu',
    },
    interpret: {
      thresholds: { warningAbove: 70, dangerAbove: 90 },
      unit: '%',
      format: 'percent',
    },
    representation: {
      preferredView: 'gauge',
      salience: 'high',
      group: 'resources',
      order: 0,
      icon: 'Cpu',
      valueField: 'percent',
      detailTemplate: '{cores} cores',
      subDetailTemplate: 'Load: {load}',
    },
    tags: ['system', 'resource'],
  },

  'system.memory': {
    id: 'system.memory',
    domain: 'system',
    title: 'Memory',
    kind: 'metric',
    sense: {
      source: 'openclaw',
      endpoint: 'system/current',
      intervalMs: 10_000,
      fieldPath: 'memory',
    },
    interpret: {
      thresholds: { warningAbove: 70, dangerAbove: 90 },
      unit: '%',
      format: 'percent',
    },
    representation: {
      preferredView: 'gauge',
      salience: 'high',
      group: 'resources',
      order: 1,
      icon: 'Activity',
      valueField: 'percent',
      detailTemplate: '{used} / {total}',
      subDetailTemplate: '{free} free',
    },
    tags: ['system', 'resource'],
  },

  'system.disk': {
    id: 'system.disk',
    domain: 'system',
    title: 'Disk',
    kind: 'metric',
    sense: {
      source: 'openclaw',
      endpoint: 'system/current',
      intervalMs: 10_000,
      fieldPath: 'disk',
    },
    interpret: {
      thresholds: { warningAbove: 80, dangerAbove: 95 },
      unit: '%',
      format: 'percent',
    },
    representation: {
      preferredView: 'gauge',
      salience: 'high',
      group: 'resources',
      order: 2,
      icon: 'HardDrive',
      valueField: 'percent',
      detailTemplate: '{used} / {total}',
      subDetailTemplate: '{free} free',
    },
    tags: ['system', 'resource'],
  },

  /* ── Info Tiles ── */
  'system.uptime': {
    id: 'system.uptime',
    domain: 'system',
    title: 'Uptime',
    kind: 'metric',
    sense: {
      source: 'openclaw',
      endpoint: 'health',
      intervalMs: 10_000,
      fieldPath: 'uptime',
    },
    interpret: {
      format: 'duration',
    },
    representation: {
      preferredView: 'stat',
      salience: 'normal',
      group: 'info',
      order: 0,
    },
    tags: ['system'],
  },

  'system.version': {
    id: 'system.version',
    domain: 'system',
    title: 'Version',
    kind: 'metric',
    sense: {
      source: 'openclaw',
      endpoint: 'health',
      intervalMs: 10_000,
      fieldPath: 'version',
    },
    interpret: {
      format: 'text',
    },
    representation: {
      preferredView: 'stat',
      salience: 'low',
      group: 'info',
      order: 1,
    },
    tags: ['system'],
  },

  'system.platform': {
    id: 'system.platform',
    domain: 'system',
    title: 'Platform',
    kind: 'metric',
    sense: {
      source: 'openclaw',
      endpoint: 'system/current',
      intervalMs: 10_000,
      fieldPath: 'platform',
    },
    interpret: {
      format: 'text',
    },
    representation: {
      preferredView: 'stat',
      salience: 'low',
      group: 'info',
      order: 2,
    },
    tags: ['system'],
  },

  'system.processes': {
    id: 'system.processes',
    domain: 'system',
    title: 'Processes',
    kind: 'metric',
    sense: {
      source: 'openclaw',
      endpoint: 'system/current',
      intervalMs: 10_000,
      fieldPath: 'processes',
    },
    interpret: {
      format: 'number',
    },
    representation: {
      preferredView: 'stat',
      salience: 'normal',
      group: 'info',
      order: 3,
    },
    tags: ['system'],
  },

  /* ── Services Table ── */
  'system.services': {
    id: 'system.services',
    domain: 'system',
    title: 'Services',
    kind: 'table',
    sense: {
      source: 'openclaw',
      endpoint: 'system/current',
      intervalMs: 10_000,
      fieldPath: 'services',
    },
    mutations: [
      {
        id: 'restart_service',
        label: 'Restart',
        endpoint: 'system/restart',
        method: 'POST',
        confirm: 'Restart {name}? This will briefly interrupt the service.',
        confirmTitle: 'Restart {name}',
        payloadFromRow: { service: 'name' },
        description: 'Restart a system service',
      },
    ],
    representation: {
      preferredView: 'table',
      salience: 'high',
      group: 'services',
      order: 0,
      columns: [
        { key: 'name', label: 'Service', align: 'left', render: 'text' },
        { key: 'status', label: 'Status', align: 'center', render: 'badge' },
        { key: 'pid', label: 'PID', align: 'right', render: 'mono' },
        { key: 'port', label: 'Port', align: 'right', render: 'mono' },
        { key: 'uptime', label: 'Uptime', align: 'right', render: 'text' },
      ],
    },
    tags: ['system', 'service'],
  },

  /* ── Events Feed ── */
  'system.events': {
    id: 'system.events',
    domain: 'system',
    title: 'Recent Events',
    kind: 'feed',
    sense: {
      source: 'openclaw',
      endpoint: 'system/history',
      intervalMs: 30_000,
      fieldPath: 'events',
    },
    representation: {
      preferredView: 'feed',
      salience: 'normal',
      group: 'activity',
      order: 0,
      maxItems: 20,
    },
    tags: ['system', 'events'],
  },

  /* ── Anomalies ── */
  'system.anomalies': {
    id: 'system.anomalies',
    domain: 'system',
    title: 'Active Anomalies',
    kind: 'list',
    sense: {
      source: 'openclaw',
      endpoint: 'system/history',
      intervalMs: 30_000,
      fieldPath: 'anomalies',
    },
    interpret: {
      emptyMeans: 'ok',
    },
    representation: {
      preferredView: 'feed',
      salience: 'high',
      group: 'alerts',
      order: 0,
      icon: 'AlertTriangle',
    },
    tags: ['system', 'anomaly'],
  },
};

/** All system nodes as an array */
export const systemNodeList: NodeDefinition[] = Object.values(systemNodes);

/** Get system nodes by group */
export function getSystemNodesByGroup(group: string): NodeDefinition[] {
  return systemNodeList
    .filter((n) => n.representation.group === group)
    .sort((a, b) => (a.representation.order ?? 0) - (b.representation.order ?? 0));
}
