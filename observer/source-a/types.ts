
export enum CanonicalStage {
    Capture = 'Capture',
    Separate = 'Separate',
    Clean = 'Clean',
    Enrich = 'Enrich',
    Mix = 'Mix',
    Distill = 'Distill',
    Publish = 'Publish'
}

export enum PipelineId {
    Refinery = 'Cloud Refinery Pipeline',
    Factory = 'Canonical Factory Pipeline'
}

export type TruthStatus = "VERIFIED" | "SUPPORTED" | "CONFLICTING" | "STALE" | "UNVERIFIED";

export interface Artifact {
    id: string;
    name: string;
    projectId: string; // New field
    pipelineId: PipelineId;
    stage: CanonicalStage;
    type: string;
    size: string;
    updatedAt: number;
    tags: string[];
    status: 'live' | 'archived' | 'failed';
    isVaulted?: boolean;
    atomClass: string;
    truthStatus: TruthStatus;
}

export interface PipelineStageConfig {
    name: CanonicalStage;
    description: string;
    isLoopStart?: boolean;
    isLoopEnd?: boolean;
    loopTarget?: CanonicalStage;
    status: 'idle' | 'running' | 'success' | 'failed';
    queueDepth: number;
    lastUpdated: number;
}

export interface Run {
    id: string;
    projectId: string; // New field
    pipelineId: PipelineId;
    status: 'success' | 'failed' | 'running';
    startTime: number;
    duration: string;
    triggeredBy: string;
}

export interface Alert {
    id: string;
    severity: 'critical' | 'warning' | 'info';
    message: string;
    timestamp: number;
    acknowledged: boolean;
    source: string;
}

export type ViewType = 'overview' | 'pipelines' | 'inventory' | 'vault' | 'runs' | 'alerts' | 'settings' | 'search' | 'explorer' | 'metrics';

export type OverlayType = 'drawer' | 'modal';

// Expanded overlay kinds
export interface OverlayItem {
    id: string;
    type: OverlayType;
    kind: 'pipeline' | 'artifact' | 'run' | 'alert' | 'log' | 'stack' | 'stack-list' | 'infra-buffer' | 'infra-cluster' | 'infra-network' | 'project-list' | 'storage-analysis' | 'pipeline-metrics';
    data: any;
    breadcrumb?: string;
    returnFocus?: HTMLElement | null;
}

export interface ContextMenuRequest {
    x: number;
    y: number;
    kind: 'artifact' | 'stack';
    data: any;
}

export interface AppSettings {
    pollInterval: number;
    showNotifications: boolean;
    autoPin: boolean;
    apiBaseUrl: string;
}

export interface AppState {
    lastVisit: number;
    theme: 'dark';
    settings: AppSettings;
}
