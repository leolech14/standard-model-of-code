/**
 * Refinery Platform Types
 *
 * Universal data models for multi-tenant context processing
 */

export interface Project {
  id: string;                    // Unique identifier (e.g., "elements")
  name: string;                  // Display name ("PROJECT_elements")
  path: string;                  // Local path or git URL
  status: 'active' | 'archived' | 'processing';
  created_at: string;
  last_processed: string;
  health: ProjectHealth;
}

export interface ProjectHealth {
  chunk_count: number;
  token_count: number;
  file_count: number;
  coverage: number;              // 0.0-1.0 (how much of project is processed)
  freshness_hours: number;       // Hours since last update
  error_count: number;
}

export interface Chunk {
  chunk_id: string;              // Unique across platform
  project_id: string;            // Which tenant
  file: string;                  // Relative path within project
  content: string;               // The actual text
  tokens: number;                // Token count
  semantic_hash: string;         // For deduplication
  embedding?: number[];          // Vector (if computed)
  metadata: ChunkMetadata;
}

export interface ChunkMetadata {
  created: string;
  updated: string;
  category: 'code' | 'docs' | 'config' | 'test';
  language?: string;             // "python", "typescript", "markdown"
  level?: number;                // L3, L5, L6 (if detectable)
}

export interface SearchResult {
  chunk: Chunk;
  score: number;                 // Relevance 0.0-1.0
  highlights: string[];          // Matched text snippets
  project: Project;              // Parent project metadata
}

export interface PlatformMetrics {
  total_projects: number;
  total_chunks: number;
  total_tokens: number;
  active_tenants: number;
  storage_bytes: number;
  last_24h: Activity24h;
}

export interface Activity24h {
  queries: number;
  processing_jobs: number;
  chunks_created: number;
  chunks_updated: number;
  errors: number;
}

export interface ProcessingJob {
  job_id: string;
  project_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  progress: {
    files_processed: number;
    files_total: number;
    chunks_created: number;
  };
  error?: string;
}

// API Response wrappers
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  has_more: boolean;
}
