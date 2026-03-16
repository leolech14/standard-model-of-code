/**
 * Domain Configuration Registry.
 *
 * Maps each domain string to the metadata SemanticPage needs
 * for page chrome: icon, title, tab layout, header data extraction.
 *
 * This is the only place domain metadata lives. Pages never hardcode
 * icons, titles, or tab structures — they read from here.
 */

import {
  Server,
  Mic,
  Brain,
  Zap,
  MessageSquare,
  TrendingUp,
  Wallet,
  Database,
  Wrench,
  Box,
  HardDrive,
  Mail,
  Settings,
  BookOpen,
  Globe,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export interface TabConfig {
  id: string;
  label: string;
  /** Representation groups shown in this tab */
  groups: string[];
}

export interface DomainConfig {
  icon: LucideIcon;
  title: string;
  description?: string;
  /** If tabs defined, nodes are organized into tab panels by group */
  tabs?: TabConfig[];
  /** Fields to extract from sourceMap for page header */
  headerExtract?: {
    /** Endpoint to read status from */
    statusEndpoint?: string;
    /** fieldPath to status value (e.g. 'status') */
    statusField?: string;
    /** Fields to compose subtitle: 'hostname', 'version' → "{hostname} · {version}" */
    subtitleFields?: { endpoint: string; field: string }[];
  };
  /** Footer text showing polling intervals */
  pollingFooter?: string;
}

export const DOMAIN_CONFIGS: Record<string, DomainConfig> = {
  system: {
    icon: Server,
    title: 'System',
    headerExtract: {
      statusEndpoint: 'health',
      statusField: 'status',
      subtitleFields: [
        { endpoint: 'system/current', field: 'hostname' },
        { endpoint: 'health', field: 'version' },
      ],
    },
    pollingFooter: 'health 10s · metrics 10s · history 30s',
  },

  voice: {
    icon: Mic,
    title: 'Voice & LLM',
    pollingFooter: 'providers 15s · gateway 15s · meet 15s',
  },

  trading: {
    icon: TrendingUp,
    title: 'Trading',
    tabs: [
      {
        id: 'status',
        label: 'Status',
        groups: ['metrics', 'market', 'positions', 'control', 'alerts'],
      },
      {
        id: 'opportunities',
        label: 'Opportunities',
        groups: ['opportunities'],
      },
    ],
    headerExtract: {
      statusEndpoint: 'trading/current',
      subtitleFields: [
        { endpoint: 'trading/current', field: 'positions' },
      ],
    },
    pollingFooter: 'positions 10s · market 15s · auto-entry 15s · ranking 30s',
  },

  comms: {
    icon: MessageSquare,
    title: 'Communications',
    pollingFooter: 'commlog 15s',
  },

  memory: {
    icon: Database,
    title: 'Memory',
    pollingFooter: 'chunks 30s · stats 30s',
  },

  llm: {
    icon: Brain,
    title: 'LLM',
    pollingFooter: 'mode 15s',
  },

  automations: {
    icon: Zap,
    title: 'Automations',
  },

  finance: {
    icon: Wallet,
    title: 'Finance',
  },

  tools: {
    icon: Wrench,
    title: 'Tools',
  },

  projects: {
    icon: Box,
    title: 'Projects',
  },

  infra: {
    icon: HardDrive,
    title: 'Infrastructure',
  },

  google: {
    icon: Mail,
    title: 'Google',
  },

  settings: {
    icon: Settings,
    title: 'Settings',
  },

  journal: {
    icon: BookOpen,
    title: 'Developer Journal',
    description: 'Daily development activity across the ecosystem',
    pollingFooter: 'local filesystem · on-demand refresh',
  },

  ecosystem: {
    icon: Globe,
    title: 'Ecosystem Atlas',
    description: '10 cloud services · context token visualization · interactive',
    pollingFooter: 'static data · click to toggle services',
  },
};

export function getDomainConfig(domain: string): DomainConfig | undefined {
  return DOMAIN_CONFIGS[domain];
}
