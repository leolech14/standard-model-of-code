/**
 * Voice Domain — 5 node definitions
 *
 * Data sources:
 *   voice/providers         → GET /api/openclaw/voice/providers      (15s)
 *   llm/mode               → GET /api/openclaw/llm/mode             (15s)
 *   voice/self-knowledge    → GET /api/openclaw/voice/self-knowledge (15s)
 *   voice/gateway/status    → GET /api/openclaw/voice/gateway/status (15s)
 *   meet/status             → GET /api/openclaw/meet/status          (15s)
 */

import type { NodeDefinition } from '../types';

export const voiceNodes: Record<string, NodeDefinition> = {
  'voice.providers': {
    id: 'voice.providers',
    domain: 'voice',
    title: 'Voice Providers',
    description: 'Configured TTS/STT providers and their status',
    kind: 'table',
    purpose: {
      answers: 'Which voice providers are configured and are they operational?',
      relevance: 0.60,
      attentionCost: 'scan',
      narrativeRole: 'detail',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'voice/providers',
      intervalMs: 15_000,
    },
    representation: {
      preferredView: 'table',
      salience: 'high',
      group: 'providers',
      order: 0,
      columns: [
        { key: 'name', label: 'Provider', align: 'left', render: 'text' },
        { key: 'type', label: 'Type', align: 'center', render: 'text' },
        { key: 'status', label: 'Status', align: 'center', render: 'badge' },
      ],
    },
    tags: ['voice', 'provider'],
  },

  'voice.llm-mode': {
    id: 'voice.llm-mode',
    domain: 'voice',
    title: 'LLM Mode',
    description: 'Current LLM processing mode',
    kind: 'control',
    purpose: {
      answers: 'What LLM processing mode is currently active?',
      relevance: 0.75,
      attentionCost: 'glance',
      narrativeRole: 'action',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'llm/mode',
      intervalMs: 15_000,
    },
    mutations: [
      {
        id: 'set_llm_mode',
        label: 'Switch Mode',
        endpoint: 'llm/mode',
        method: 'POST',
        confirm: 'Switch LLM mode?',
        confirmTitle: 'Switch LLM Mode',
        payloadFromRow: { mode: 'mode' },
      },
    ],
    representation: {
      preferredView: 'status-pill',
      salience: 'high',
      group: 'llm',
      order: 0,
    },
    tags: ['voice', 'llm'],
  },

  'voice.self-knowledge': {
    id: 'voice.self-knowledge',
    domain: 'voice',
    title: 'Self Knowledge',
    description: 'Voice agent self-knowledge and persona configuration',
    kind: 'composite',
    purpose: {
      answers: 'What does the voice agent know about itself and its persona?',
      relevance: 0.50,
      attentionCost: 'study',
      narrativeRole: 'detail',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'voice/self-knowledge',
      intervalMs: 15_000,
    },
    representation: {
      preferredView: 'panel',
      salience: 'normal',
      group: 'knowledge',
      order: 0,
    },
    tags: ['voice', 'knowledge'],
  },

  'voice.gateway': {
    id: 'voice.gateway',
    domain: 'voice',
    title: 'Voice Gateway',
    description: 'Voice gateway connection status',
    kind: 'status',
    purpose: {
      answers: 'Is the voice gateway connected and operational?',
      relevance: 0.95,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'voice/gateway/status',
      intervalMs: 15_000,
    },
    interpret: {
      emptyMeans: 'unknown',
    },
    representation: {
      preferredView: 'status-pill',
      salience: 'high',
      group: 'gateway',
      order: 0,
    },
    tags: ['voice', 'gateway'],
  },

  'voice.call-status': {
    id: 'voice.call-status',
    domain: 'voice',
    title: 'Call Status',
    description: 'Current meeting/call status',
    kind: 'status',
    purpose: {
      answers: 'Is there an active call or meeting in progress?',
      relevance: 0.80,
      attentionCost: 'glance',
      narrativeRole: 'anchor',
    },
    sense: {
      source: 'openclaw',
      endpoint: 'meet/status',
      intervalMs: 15_000,
    },
    interpret: {
      emptyMeans: 'unknown',
    },
    representation: {
      preferredView: 'status-pill',
      salience: 'normal',
      group: 'calls',
      order: 0,
    },
    tags: ['voice', 'call'],
  },
};

/** All voice nodes as an array */
export const voiceNodeList: NodeDefinition[] = Object.values(voiceNodes);
