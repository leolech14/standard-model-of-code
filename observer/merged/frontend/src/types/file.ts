// File and Artifact types

import {
  CanonicalStage,
  PipelineId,
  TruthStatus,
  ArtifactStatus
} from './enums';

// Base file from Source B (file_explorer)
export interface FileItem {
  path: string;
  name: string;
  size: number;
  type: string;
  modified: number;  // Unix timestamp
  isDirectory: boolean;
}

// Artifact from Source A (refinery-dashboard)
export interface Artifact {
  id: string;
  name: string;
  projectId: string;
  pipelineId: PipelineId;
  stage: CanonicalStage;
  type: string;
  size: string;
  updatedAt: number;
  tags: string[];
  status: ArtifactStatus;
  isVaulted?: boolean;
  atomClass: string;
  truthStatus: TruthStatus;
}

// UnifiedFile - bridges Artifact and FileItem
export interface UnifiedFile extends Artifact {
  path: string;
  modified: number;
  isDirectory: boolean;
}

// Directory listing response
export interface DirectoryListing {
  path: string;
  files: FileItem[];
  total: number;
}

// File preview response
export interface FilePreview {
  path: string;
  preview: string | null;
  type: string;
  language?: string;
  lineCount?: number;
}

// File metadata
export interface FileMetadata {
  path: string;
  size: number;
  created: number;
  modified: number;
  accessed: number;
  permissions: string;
  owner: string;
  mimeType: string;
}

// Operation request types
export interface PasteRequest {
  files: string[];
  destination: string;
  operation: 'copy' | 'move';
}

export interface DeleteRequest {
  files: string[];
}

export interface CreateFolderRequest {
  path: string;
  name: string;
}

export interface RenameRequest {
  path: string;
  newName: string;
}

// Operation result
export interface OperationResult {
  success: boolean;
  message?: string;
  error?: string;
}

// Search
export interface SearchResult {
  path: string;
  name: string;
  type: string;
  matchContext?: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
}
