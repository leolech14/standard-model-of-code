-- Collider Database Schema v1
-- Supports SQLite, PostgreSQL, and DuckDB

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert initial version if not exists
INSERT OR IGNORE INTO schema_version (version, description)
VALUES (1, 'Initial schema with runs, nodes, edges, and file tracking');

-- ============================================================================
-- ANALYSIS RUNS
-- Records each analysis execution with metadata
-- ============================================================================
CREATE TABLE IF NOT EXISTS analysis_runs (
    id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    project_path TEXT NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    collider_version TEXT DEFAULT '1.0.0',
    status TEXT DEFAULT 'running',  -- running, completed, failed
    node_count INTEGER DEFAULT 0,
    edge_count INTEGER DEFAULT 0,
    options_json TEXT,              -- CLI options as JSON
    metadata_json TEXT              -- Additional metadata as JSON
);

CREATE INDEX IF NOT EXISTS idx_runs_project ON analysis_runs(project_path);
CREATE INDEX IF NOT EXISTS idx_runs_status ON analysis_runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_started ON analysis_runs(started_at DESC);

-- ============================================================================
-- FILE TRACKING (Incremental Analysis)
-- Tracks file hashes to skip unchanged files on re-analysis
-- ============================================================================
CREATE TABLE IF NOT EXISTS tracked_files (
    id TEXT PRIMARY KEY,
    project_path TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    blake3_hash TEXT NOT NULL,
    modified_ts INTEGER,            -- Unix timestamp
    last_analyzed_run TEXT,         -- FK to analysis_runs(id)
    UNIQUE(project_path, relative_path)
);

CREATE INDEX IF NOT EXISTS idx_files_project ON tracked_files(project_path);
CREATE INDEX IF NOT EXISTS idx_files_hash ON tracked_files(blake3_hash);

-- ============================================================================
-- NODES
-- Flattened core fields + JSON for flexible/optional fields
-- ============================================================================
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT NOT NULL,
    run_id TEXT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,

    -- Core identity
    name TEXT NOT NULL,
    kind TEXT,                      -- function, class, method, file, etc.
    file_path TEXT,
    start_line INTEGER,
    end_line INTEGER,

    -- Standard Model classification
    role TEXT,                      -- Service, Repository, Controller, etc.
    role_confidence REAL,           -- 0.0-1.0
    atom TEXT,                      -- LOG.FNC.M, DAT.ENT.O, etc.
    ring TEXT,                      -- LOG, DAT, ORG, EXE, EXT
    level TEXT,                     -- L-3 to L12

    -- Graph metrics
    in_degree INTEGER DEFAULT 0,
    out_degree INTEGER DEFAULT 0,
    pagerank REAL,
    betweenness REAL,

    -- Quality metrics
    complexity INTEGER,
    q_score REAL,                   -- Quality score 0.0-1.0

    -- Flexible storage
    dimensions_json TEXT,           -- D1-D8 dimensions
    metadata_json TEXT,             -- All other node data

    PRIMARY KEY (run_id, id)
);

CREATE INDEX IF NOT EXISTS idx_nodes_run ON nodes(run_id);
CREATE INDEX IF NOT EXISTS idx_nodes_file ON nodes(file_path);
CREATE INDEX IF NOT EXISTS idx_nodes_role ON nodes(role);
CREATE INDEX IF NOT EXISTS idx_nodes_kind ON nodes(kind);
CREATE INDEX IF NOT EXISTS idx_nodes_ring ON nodes(ring);
CREATE INDEX IF NOT EXISTS idx_nodes_atom ON nodes(atom);

-- ============================================================================
-- EDGES
-- Relationships between nodes
-- ============================================================================
CREATE TABLE IF NOT EXISTS edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    edge_type TEXT,                 -- calls, imports, inherits, uses, etc.
    weight REAL DEFAULT 1.0,
    confidence REAL,                -- 0.0-1.0
    metadata_json TEXT,             -- Additional edge data
    UNIQUE(run_id, source_id, target_id, edge_type)
);

CREATE INDEX IF NOT EXISTS idx_edges_run ON edges(run_id);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_composite ON edges(run_id, source_id, target_id);

-- ============================================================================
-- QUERY VIEWS
-- Common query patterns as views
-- ============================================================================

-- View: Latest run per project
CREATE VIEW IF NOT EXISTS latest_runs AS
SELECT * FROM analysis_runs
WHERE (project_path, started_at) IN (
    SELECT project_path, MAX(started_at)
    FROM analysis_runs
    WHERE status = 'completed'
    GROUP BY project_path
);

-- View: Node counts by role
CREATE VIEW IF NOT EXISTS role_distribution AS
SELECT
    run_id,
    role,
    COUNT(*) as count,
    AVG(role_confidence) as avg_confidence
FROM nodes
GROUP BY run_id, role;

-- View: Edge counts by type
CREATE VIEW IF NOT EXISTS edge_distribution AS
SELECT
    run_id,
    edge_type,
    COUNT(*) as count,
    AVG(weight) as avg_weight
FROM edges
GROUP BY run_id, edge_type;

-- View: Files with most nodes (hotspots)
CREATE VIEW IF NOT EXISTS file_hotspots AS
SELECT
    run_id,
    file_path,
    COUNT(*) as node_count,
    SUM(complexity) as total_complexity
FROM nodes
WHERE file_path IS NOT NULL
GROUP BY run_id, file_path
ORDER BY node_count DESC;
