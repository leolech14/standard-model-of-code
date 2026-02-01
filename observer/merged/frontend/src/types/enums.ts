// Canonical enums - shared between frontend and backend

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

export type TruthStatus =
  | 'VERIFIED'
  | 'SUPPORTED'
  | 'CONFLICTING'
  | 'STALE'
  | 'UNVERIFIED';

export type AlertSeverity = 'critical' | 'warning' | 'info';

export type RunStatus = 'success' | 'failed' | 'running';

export type ArtifactStatus = 'live' | 'archived' | 'failed';

export type StageStatus = 'idle' | 'running' | 'success' | 'failed';
