/**
 * Journal Domain — purpose-driven node definitions.
 *
 * First domain to use PurposeDefinition + ContextDefinition.
 * Each node declares WHY it exists, WHAT question it answers,
 * and WHAT context it needs nearby.
 *
 * Page mission: Track development activity across the ecosystem
 * to identify patterns, breakthroughs, and concerns.
 *
 * Data source: local API (filesystem, ~/.devjournal/days/)
 */

import type { NodeDefinition, PageDefinition } from '../types';

/* ─── Page Definition ─── */

export const journalPageDef: PageDefinition = {
  id: 'journal',
  mission:
    'Track development activity across the ecosystem to identify patterns, ' +
    'breakthroughs, and concerns — enabling informed decisions about where ' +
    'to focus effort next.',
  audience: 'developer-owner',
  cadence: 'daily-review',
  successCriteria: [
    'Identify which projects got most effort today',
    'Spot breakthroughs worth celebrating',
    'Detect concerns worth investigating',
    'See the shape of the day (when, what, how much)',
  ],
};

/* ─── Node Definitions ─── */

export const journalNodes: Record<string, NodeDefinition> = {
  'journal.velocity': {
    id: 'journal.velocity',
    domain: 'journal',
    title: 'Velocity',
    description: 'Development intensity metrics for the day',
    kind: 'composite',
    purpose: {
      answers: 'How productive was this day?',
      serves: ['Identify which projects got most effort today', 'See the shape of the day (when, what, how much)'],
      relevance: 0.95,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    context: {
      requiresNearby: ['journal.timeline'],
      enables: ['journal.highlights'],
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.velocity',
    },
    representation: {
      preferredView: 'composite',
      salience: 'high',
      group: 'overview',
      order: 0,
      layout: 'grid',
      children: [
        'journal.velocity.events',
        'journal.velocity.commits',
        'journal.velocity.prompts',
        'journal.velocity.files',
        'journal.velocity.lines',
        'journal.velocity.hours',
      ],
    },
    tags: ['velocity', 'anchor'],
  },

  'journal.velocity.events': {
    id: 'journal.velocity.events',
    domain: 'journal',
    title: 'Events',
    kind: 'metric',
    purpose: {
      answers: 'How much total activity?',
      relevance: 0.9,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.total_events',
    },
    interpret: { format: 'count' },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'overview',
      order: 1,
    },
  },

  'journal.velocity.commits': {
    id: 'journal.velocity.commits',
    domain: 'journal',
    title: 'Commits',
    kind: 'metric',
    purpose: {
      answers: 'How many code changes?',
      relevance: 0.88,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.velocity.commits',
    },
    interpret: { format: 'count' },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'overview',
      order: 2,
    },
  },

  'journal.velocity.prompts': {
    id: 'journal.velocity.prompts',
    domain: 'journal',
    title: 'Prompts',
    kind: 'metric',
    purpose: {
      answers: 'How many CLI interactions?',
      relevance: 0.85,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.velocity.prompts',
    },
    interpret: { format: 'count' },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'overview',
      order: 3,
    },
  },

  'journal.velocity.files': {
    id: 'journal.velocity.files',
    domain: 'journal',
    title: 'Files Created',
    kind: 'metric',
    purpose: {
      answers: 'How many new files?',
      relevance: 0.82,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.velocity.files_created',
    },
    interpret: { format: 'count' },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'overview',
      order: 4,
    },
  },

  'journal.velocity.lines': {
    id: 'journal.velocity.lines',
    domain: 'journal',
    title: 'Net Lines',
    kind: 'metric',
    purpose: {
      answers: 'How much code was written?',
      relevance: 0.80,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.velocity.net_lines',
    },
    interpret: {
      format: 'count',
      colorMode: 'pnl',
    },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'overview',
      order: 5,
      detailTemplate: '+{lines_added} / -{lines_removed}',
    },
  },

  'journal.velocity.hours': {
    id: 'journal.velocity.hours',
    domain: 'journal',
    title: 'Active Hours',
    kind: 'metric',
    purpose: {
      answers: 'How long was the workday?',
      relevance: 0.75,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.velocity.active_hours',
    },
    interpret: {
      format: 'count',
      unit: 'h',
    },
    representation: {
      preferredView: 'stat',
      salience: 'high',
      group: 'overview',
      order: 6,
    },
  },

  'journal.timeline': {
    id: 'journal.timeline',
    domain: 'journal',
    title: 'Activity Timeline',
    description: 'Hourly activity distribution across the day',
    kind: 'feed',
    purpose: {
      answers: 'When did work happen?',
      serves: ['See the shape of the day (when, what, how much)'],
      relevance: 0.85,
      attentionCost: 'scan',
      narrativeRole: 'detail',
    },
    context: {
      requiresNearby: ['journal.velocity'],
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.timeline',
    },
    representation: {
      preferredView: 'custom',
      customViewId: 'timeline-chart',
      salience: 'high',
      group: 'activity',
      order: 0,
    },
    tags: ['timeline', 'detail'],
  },

  'journal.projects': {
    id: 'journal.projects',
    domain: 'journal',
    title: 'Projects',
    description: 'Effort distribution across active projects',
    kind: 'table',
    purpose: {
      answers: 'Where did effort concentrate?',
      serves: ['Identify which projects got most effort today'],
      relevance: 0.80,
      attentionCost: 'scan',
      narrativeRole: 'detail',
    },
    context: {
      requiresNearby: ['journal.timeline'],
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.events_by_project',
    },
    representation: {
      preferredView: 'custom',
      customViewId: 'project-breakdown',
      salience: 'normal',
      group: 'activity',
      order: 1,
    },
    tags: ['projects', 'detail'],
  },

  'journal.highlights': {
    id: 'journal.highlights',
    domain: 'journal',
    title: 'Highlights',
    description: 'Notable events: milestones, sessions, inbox arrivals',
    kind: 'feed',
    purpose: {
      answers: 'What actually happened?',
      serves: ['Spot breakthroughs worth celebrating', 'Detect concerns worth investigating'],
      relevance: 0.75,
      attentionCost: 'study',
      narrativeRole: 'evidence',
    },
    context: {
      requiresNearby: ['journal.projects'],
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.highlights',
    },
    representation: {
      preferredView: 'feed',
      salience: 'normal',
      group: 'evidence',
      order: 0,
      maxItems: 15,
    },
    tags: ['highlights', 'evidence'],
  },

  'journal.milestones': {
    id: 'journal.milestones',
    domain: 'journal',
    title: 'Milestones',
    description: 'High-impact events detected from commit patterns',
    kind: 'feed',
    purpose: {
      answers: 'What breakthroughs occurred?',
      serves: ['Spot breakthroughs worth celebrating'],
      relevance: 0.70,
      attentionCost: 'scan',
      narrativeRole: 'evidence',
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.milestones',
    },
    representation: {
      preferredView: 'feed',
      salience: 'normal',
      group: 'evidence',
      order: 1,
      maxItems: 5,
    },
    tags: ['milestones', 'evidence'],
  },

  /* ─── ETS Trace Nodes ─── */

  'journal.sources': {
    id: 'journal.sources',
    domain: 'journal',
    title: 'Trace Sources',
    description: 'Event distribution across all active ETS collectors',
    kind: 'table',
    purpose: {
      answers: 'Which trace sources contributed today?',
      serves: ['See the shape of the day (when, what, how much)'],
      relevance: 0.82,
      attentionCost: 'scan',
      narrativeRole: 'detail',
    },
    context: {
      requiresNearby: ['journal.velocity'],
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.events_by_source',
    },
    representation: {
      preferredView: 'custom',
      customViewId: 'source-breakdown',
      salience: 'normal',
      group: 'activity',
      order: 2,
    },
    tags: ['ets', 'sources'],
  },

  'journal.signatures': {
    id: 'journal.signatures',
    domain: 'journal',
    title: 'AI Attribution',
    description: 'Signature protocol: which AI models authored work today',
    kind: 'feed',
    purpose: {
      answers: 'Who (human or AI) did the work?',
      serves: ['Identify which projects got most effort today'],
      relevance: 0.72,
      attentionCost: 'glance',
      narrativeRole: 'evidence',
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.highlights',
    },
    representation: {
      preferredView: 'custom',
      customViewId: 'signature-panel',
      salience: 'normal',
      group: 'evidence',
      order: 2,
    },
    tags: ['ets', 'signatures', 'attribution'],
  },

  'journal.correlations': {
    id: 'journal.correlations',
    domain: 'journal',
    title: 'Work Sessions',
    description: 'Corroborated clusters: linked events across multiple sources',
    kind: 'feed',
    purpose: {
      answers: 'What connected actions happened together?',
      serves: ['Detect concerns worth investigating', 'Spot breakthroughs worth celebrating'],
      relevance: 0.68,
      attentionCost: 'study',
      narrativeRole: 'evidence',
    },
    context: {
      requiresNearby: ['journal.timeline', 'journal.sources'],
    },
    sense: {
      source: 'local',
      endpoint: 'journal',
      intervalMs: 0,
      fieldPath: 'data.highlights',
    },
    representation: {
      preferredView: 'custom',
      customViewId: 'correlation-view',
      salience: 'normal',
      group: 'evidence',
      order: 3,
    },
    tags: ['ets', 'correlations'],
  },
};

/* ─── Exports ─── */

export const journalNodeList: NodeDefinition[] = Object.values(journalNodes);
