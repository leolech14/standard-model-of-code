# Research: COMPREHENSIVE DATABASE INTEGRATION ANALYSIS FOR COLLIDER

Context: Collider is an AST-based code ana...

> **Date:** 2026-01-31 18:27:43
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:e7abbab37be1d3e602c959c6f30fce8410508b7d971dde1bb73a6e1ba74ae976`
> **Raw JSON:** `raw/20260131_182743_comprehensive_database_integration_analysis_for_co.json`

---

## Query

COMPREHENSIVE DATABASE INTEGRATION ANALYSIS FOR COLLIDER

Context: Collider is an AST-based code analysis tool that currently has NO persistent database. All caching is in-memory. We want to add SQLite for:
1. INCREMENTAL ANALYSIS - Skip unchanged files between runs
2. HISTORICAL QUERIES - Query across multiple runs  
3. CROSS-PROJECT SEARCH - Search across repos
4. GRAPH QUERIES - Traverse dependency graphs

ANALYZE:
1. What data structures in data_management.py, output_generator.py would benefit from DB persistence?
2. Where in full_analysis.py pipeline should the DB layer integrate?
3. What schema design fits our node/edge graph model? SQLite + JSON columns vs normalized?
4. How to handle file hash tracking for incremental analysis?
5. Migration concerns from JSON output to DB-backed?

Be specific with file paths and line numbers.

---

## Response

This analysis outlines a comprehensive strategy to integrate persistent storage into Collider. The current in-memory architecture limits scalability for large codebases and prevents incremental analysis.

### 1. Data Structures Requiring Persistence

Based on the context, the following classes are the primary candidates for O/R mapping.

**File: `src/core/unified_analysis.py`**
*   **`UnifiedNode` (Lines 29-73):** This is the atomic unit.
    *   *Persist:* `id`, `name`, `kind`, `file_path`, `role`, `complexity`, `layer`.
    *   *JSON Blob:* `dimensions`, `rpbl`, `metadata`, `params`, `decorators`.
    *   *Blob/Text:* `body_source` (Consider compressing this if storing logic).
*   **`UnifiedEdge` (Lines 77-90):** Represents the dependency graph.
    *   *Persist:* `source`, `target`, `edge_type`, `weight`.
    *   *JSON Blob:* `metadata`.
*   **`UnifiedAnalysisOutput` (Lines 94-159):** Represents a "Run".
    *   *Persist:* `generated_at`, `target_name`, `analysis_time_ms`, `stats` (as JSON).

**File: `src/core/full_analysis.py`**
*   **File Hash Map:** Currently implicit or calculated partially via `calculate_merkle_root` (Line 1185). We need a dedicated structure mapping `file_path` -> `content_hash` to enable incremental scanning.

---

### 2. Integration Points in `full_analysis.py`

The database layer should act as a "state manager" wrapping the pipeline stages.

**A. Initialization (Start of `run_full_analysis`)**
*   **Location:** Around Line 665 (after performance tracking init).
*   **Action:** Initialize `DatabaseManager`. Check if a DB exists for this project.

**B. Incremental Survey (Stage 0/1 Boundary)**
*   **Location:** Line 765 (Before `unified_analysis.analyze`).
*   **Action:**
    1.  Compute hashes of all files in `target`.
    2.  Query DB for changed/new files.
    3.  Pass only *changed* files to `unified_analysis.analyze` (Stage 1).
    4.  Hydrate `nodes` list with *unchanged* nodes loaded from DB.

**C. Final Commit (Stage 12)**
*   **Location:** Line 1220 (Before `generate_outputs`).
*   **Action:**
    1.  Begin Transaction.
    2.  Update `files` table (new hashes).
    3.  Upsert `nodes` (replace old versions of changed files).
    4.  Regenerate `edges` (edges must be recalculated if either source or target changed, or if graph inference logic changed).
    5.  Commit Transaction.

---

### 3. Schema Design (Hybrid SQLite + JSON)

A hybrid approach is best: normalize structure for querying, use JSON for flexible Standard Model dimensions.

```sql
-- Track analysis runs
CREATE TABLE runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    target_path TEXT,
    stats JSON  -- Store coverage, node counts
);

-- File tracking for incremental analysis
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    project_root TEXT,
    content_hash TEXT, -- SHA256 of file content
    last_analyzed_run_id INTEGER,
    UNIQUE(path, project_root)
);

-- The Particles/Atoms
CREATE TABLE nodes (
    id TEXT PRIMARY KEY, -- canonical id (file_path:name)
    file_id INTEGER,
    name TEXT,
    kind TEXT, -- function, class, module
    role TEXT, -- Controller, Service, etc.
    layer TEXT, -- D2_LAYER (Presentation, Domain)
    complexity INTEGER,
    
    -- Hybrid Data (Standard Model)
    dimensions JSON, -- {D1_WHAT: ..., D6_EFFECT: ...}
    rpbl JSON,       -- {responsibility: 0.5, ...}
    metadata JSON,   -- Decorators, params, docstrings
    
    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
);

-- The Dependency Graph
CREATE TABLE edges (
    source_id TEXT,
    target_id TEXT,
    edge_type TEXT, -- calls, imports, inherits
    weight REAL,
    metadata JSON,
    
    FOREIGN KEY(source_id) REFERENCES nodes(id) ON DELETE CASCADE,
    -- Note: target_id might point to external node not in DB, so no strict FK constraint
    PRIMARY KEY (source_id, target_id, edge_type)
);

-- Indicies for Graph Traversal & Search
CREATE INDEX idx_nodes_kind ON nodes(kind);
CREATE INDEX idx_nodes_role ON nodes(role);
CREATE INDEX idx_edges_source ON edges(source_id);
CREATE INDEX idx_edges_target ON edges(target_id);
```

---

### 4. Handling File Hash Tracking (Incremental Logic)

You need a new module `src/core/cache_manager.py` to handle the diffing logic.

**Algorithm:**
1.  **Survey:** Walk directory tree.
2.  **Hash:** Calculate SHA256 of current content.
3.  **Diff:**
    ```python
    def get_analysis_targets(db_conn, current_files):
        """
        Returns: 
        - files_to_analyze: List[str] (New or Changed)
        - cached_nodes: List[UnifiedNode] (From DB for unchanged files)
        """
        to_analyze = []
        cached_nodes = []
        
        for f_path, f_hash in current_files.items():
            stored_hash = db_conn.execute(
                "SELECT content_hash FROM files WHERE path=?", (f_path,)
            ).fetchone()
            
            if not stored_hash or stored_hash[0] != f_hash:
                to_analyze.append(f_path)
            else:
                # Load nodes associated with this file from DB
                nodes = db_conn.load_nodes_for_file(f_path)
                cached_nodes.extend(nodes)
                
        # Handle Deletions: Remove nodes from DB where file no longer exists on disk
        db_conn.prune_deleted_files(current_files.keys())
        
        return to_analyze, cached_nodes
    ```

**Modification in `src/core/unified_analysis.py`:**
The `analyze` function (Line 233) needs to accept `pre_loaded_nodes` as an optional argument to merge with the results from `TreeSitterUniversalEngine`.

---

### 5. Migration Strategy

To move from JSON output to DB-backed without breaking the existing report generators:

1.  **Dual Output Phase:**
    *   Implement the SQLite logic.
    *   In `full_analysis.py`, keep the `generate_outputs` call (Line 1238) exactly as is.
    *   Add `db_manager.save_snapshot(nodes, edges)` immediately before it.
    *   This allows you to build history without breaking the frontend `output_human-readable.html`.

2.  **Refactor Report Generator:**
    *   Modify `src/core/output_generator.py` to accept a SQLite connection string instead of a huge dictionary.
    *   Update queries to fetch nodes/edges lazily or via SQL filters.

3.  **Graph Queries (Recursive CTEs):**
    *   SQLite supports Recursive CTEs, enabling powerful graph queries directly in SQL (replacing some NetworkX logic in `graph_analyzer.py`).

    *   *Example: Find all dependencies of a node (transitive closure)*
        ```sql
        WITH RECURSIVE downstream AS (
          SELECT target_id FROM edges WHERE source_id = 'target_node'
          UNION
          SELECT e.target_id 
          FROM edges e 
          JOIN downstream d ON e.source_id = d.target_id
        )
        SELECT * FROM nodes WHERE id IN downstream;
        ```

### Summary of Changes Required

1.  **Create** `src/core/database.py`: Handles SQLite connection, schema creation, and CRUD.
2.  **Modify** `src/core/unified_analysis.py`: Update `analyze` signature to accept cached nodes.
3.  **Modify** `src/core/full_analysis.py`:
    *   Import `database`.
    *   Implement "Diff" logic before Stage 1.
    *   Implement "Persist" logic at Stage 12.
4.  **Modify** `src/core/output_generator.py`: (Optional/Phase 2) Read from DB.

---

## Citations

_No citations provided_
