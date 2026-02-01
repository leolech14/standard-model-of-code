// Pipeline and monitoring types

import {
  CanonicalStage,
  PipelineId,
  RunStatus,
  StageStatus,
  AlertSeverity
} from './enums';

// Pipeline stage configuration
export interface PipelineStageConfig {
  name: CanonicalStage;
  description: string;
  isLoopStart?: boolean;
  isLoopEnd?: boolean;
  loopTarget?: CanonicalStage;
  status: StageStatus;
  queueDepth: number;
  lastUpdated: number;
}

// Pipeline run
export interface Run {
  id: string;
  projectId: string;
  pipelineId: PipelineId;
  status: RunStatus;
  startTime: number;
  duration: string;
  triggeredBy: string;
}

// Alert
export interface Alert {
  id: string;
  severity: AlertSeverity;
  message: string;
  timestamp: number;
  acknowledged: boolean;
  source: string;
}

// Observer status (from SMC theory)
export type ObserverType = 'structural' | 'operational' | 'generative';

export interface ObserverStatus {
  type: ObserverType;
  active: boolean;
  lastUpdate: number;
  metrics: Record<string, number>;
}

// Overlay system
export type OverlayType = 'drawer' | 'modal';

export type OverlayKind =
  | 'pipeline'
  | 'artifact'
  | 'run'
  | 'alert'
  | 'log'
  | 'stack'
  | 'stack-list'
  | 'infra-buffer'
  | 'infra-cluster'
  | 'infra-network'
  | 'project-list'
  | 'storage-analysis'
  | 'pipeline-metrics';

export interface OverlayItem {
  id: string;
  type: OverlayType;
  kind: OverlayKind;
  data: unknown;
  breadcrumb?: string;
  returnFocus?: HTMLElement | null;
}

// Context menu
export interface ContextMenuRequest {
  x: number;
  y: number;
  kind: 'artifact' | 'stack' | 'file';
  data: unknown;
}

// View types
export type ViewType =
  | 'overview'
  | 'pipelines'
  | 'inventory'
  | 'vault'
  | 'runs'
  | 'alerts'
  | 'settings'
  | 'search'
  | 'explorer'
  | 'metrics';
