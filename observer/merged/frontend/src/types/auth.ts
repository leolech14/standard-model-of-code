// Authentication types

export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  error: string | null;
  loading: boolean;
}

export interface AuthResponse {
  authenticated: boolean;
  token?: string;
  error?: string;
}

export interface AuthContextValue extends AuthState {
  login: () => Promise<void>;
  logout: () => void;
  verify: () => Promise<boolean>;
}

// App settings
export interface AppSettings {
  pollInterval: number;
  showNotifications: boolean;
  autoPin: boolean;
  apiBaseUrl: string;
}

// App state
export interface AppState {
  lastVisit: number;
  theme: 'dark';
  settings: AppSettings;
}

// WebSocket message types
export type WSEventType =
  | 'file_change'
  | 'observer_status'
  | 'pipeline_progress'
  | 'alert_broadcast'
  | 'connection';

export interface WSMessage {
  type: WSEventType;
  event: string;
  data?: unknown;
  room?: string;
  timestamp?: number;
}

export interface FileChangeEvent {
  type: 'file_change';
  event: 'created' | 'modified' | 'deleted';
  path: string;
  name: string;
}

export interface PipelineProgressEvent {
  type: 'pipeline_progress';
  pipelineId: string;
  stage: string;
  status: 'in_progress' | 'completed' | 'failed';
}

export interface AlertBroadcastEvent {
  type: 'alert_broadcast';
  alertId: string;
  message: string;
  severity: 'info' | 'warning' | 'error';
}
