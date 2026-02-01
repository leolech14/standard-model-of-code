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

export type ViewType = 'overview' | 'pipelines' | 'inventory' | 'vault' | 'runs' | 'alerts' | 'settings';

export type OverlayType = 'drawer' | 'modal';

export interface OverlayItem {
    id: string; // unique ID for stack management
    type: OverlayType;
    kind: 'pipeline' | 'artifact' | 'run' | 'alert' | 'log' | 'stack' | 'stack-list' | 'generic';
    data: any; // Context data for the inspector
    breadcrumb?: string; // Context anchor for navigation
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
