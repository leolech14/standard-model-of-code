# Research: CONSOLIDATION TASK: Based on your knowledge of Collider's pipeline (18+ stages, no caching, full res...

> **Date:** 2026-01-31 04:07:11
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:03c0f6d5ad21b0493ba4bbf8dfd36a1af7e7ea03a83f1fdbe83d5505b9d9f491`
> **Raw JSON:** `raw/20260131_040711_consolidation_task__based_on_your_knowledge_of_col.json`

---

## Query

CONSOLIDATION TASK: Based on your knowledge of Collider's pipeline (18+ stages, no caching, full rescan each run), and external research showing:

1. SQLite caching: file path + content hash keys, WAL mode, prepared statements, incremental invalidation
2. Incremental graph: event-based delta propagation, deletion-to-addition transforms, CodeQL achieves ~15s updates
3. Schema: nodes table (id, type, name, file_id, properties JSON), edges table (from_id, to_id, type), files table (path, hash, mtime)

SYNTHESIZE a concrete implementation plan for adding a SQLite caching layer to Collider that:
- Caches parsed AST results and classification decisions
- Detects file changes via hash/mtime
- Enables incremental analysis (only changed files)
- Maintains compatibility with existing JSON output

Output: Specific files to modify, schema design, and integration points in the pipeline.

---

## Response

The Collider analysis pipeline, with its 18+ stages and full rescan on each run, presents a significant performance bottleneck for large codebases and frequent analyses. Introducing a SQLite caching layer is a critical step towards enabling incremental analysis, drastically reducing analysis times by only processing changed files.

Based on the codebase context and external research, here's a concrete implementation plan for integrating SQLite caching into Collider.

## 1. High-Level Implementation Plan

The core idea is to persist the outputs of expensive, file-level operations (AST parsing, initial particle classification, and edges originating from a file) into a SQLite database. Subsequent runs will:
1.  **Identify changed files:** By comparing file hashes and modification times (`mtime`) against the cache.
2.  **Process only changed files:** Rerunning `TreeSitterUniversalEngine` and initial particle/edge extraction only for modified or new files.
3.  **Retrieve unchanged data from cache:** Fetching previously processed nodes and edges for files that haven't changed.
4.  **Reconstruct the full graph:** Combining live-processed and cached data to present a complete, up-to-date graph to the later, graph-level analysis stages (e.g., `graph_type_inference`, `purpose_field`, `markov`, `knots`).
5.  **Maintain JSON output compatibility:** The final `UnifiedAnalysisOutput` will be constructed from the merged live and cached data, ensuring consistency with the existing schema.

This approach will make the initial file-parsing and particle extraction stages incremental, which are often the most time-consuming steps.

## 2. SQLite Schema Design

A single SQLite database file (e.g., `.collider_cache.db` within the `.collider` output directory) will store the necessary data. WAL (Write-Ahead Logging) mode will be enabled for better concurrency and durability.

**Tables:**

### `files`
Tracks metadata for each analyzed source file to detect changes.

*   `id` INTEGER PRIMARY KEY AUTOINCREMENT
*   `path` TEXT NOT NULL UNIQUE_INDEX: Absolute canonical path to the file.
*   `hash` TEXT NOT NULL: SHA256 hash of the file's content.
*   `mtime` REAL NOT NULL: Unix timestamp of the last modification time.
*   `size` INTEGER NOT NULL: File size in bytes.
*   `language` TEXT: Detected language of the file (e.g., 'python', 'javascript').
*   `last_cached_at` REAL NOT NULL: Unix timestamp of when this file's associated nodes/edges were last successfully cached.
*   `status` TEXT NOT NULL DEFAULT 'active': 'active', 'deleted'.

### `nodes`
Stores individual code "particles" and their initial classification results.

*   `id` TEXT PRIMARY KEY: The canonical node ID (e.g., `file_path:name`).
*   `file_id` INTEGER NOT NULL: FOREIGN KEY REFERENCES `files(id)`.
*   `name` TEXT NOT NULL
*   `kind` TEXT NOT NULL: 'class', 'function', 'method', 'module'.
*   `properties_json` TEXT NOT NULL: A JSON blob containing all other `UnifiedNode` fields (role, confidence, dimensions, body_source, start_line, end_line, params, return_type, base_classes, decorators, docstring, signature, etc.). This allows for flexible schema evolution without altering table structure directly. `body_source` is crucial here.

### `edges`
Stores relationships between nodes.

*   `source_id` TEXT NOT NULL: REFERENCES `nodes(id)` (or external module name).
*   `target_id` TEXT NOT NULL: REFERENCES `nodes(id)` (or external module name/path).
*   `edge_type` TEXT NOT NULL: 'calls', 'imports', 'contains', 'inherits', 'exposes'.
*   `file_id` INTEGER NOT NULL: FOREIGN KEY REFERENCES `files(id)`: The file where this edge was *extracted*.
*   `properties_json` TEXT NOT NULL: A JSON blob for `weight`, `confidence`, `resolution`, `metadata`, `line`.
*   PRIMARY KEY (`source_id`, `target_id`, `edge_type`, `file_id`)

## 3. File Modifications & Integration Points

### 3.1. NEW: `src/core/cache_manager.py`

This new module will encapsulate all SQLite interactions, providing a clean API for the rest of the Collider pipeline.

**Key Responsibilities:**
*   Database initialization, connection, and setup (WAL mode, prepared statements).
*   Schema creation/migration.
*   Methods for interacting with `files`, `nodes`, and `edges` tables.
*   Calculating file hashes and comparing `mtime`.

**Example Methods:**
*   `__init__(self, db_path: Path)`: Connects to DB, creates tables if not exists.
*   `_get_file_checksum(self, file_path: Path) -> Tuple[str, float, int]`: Returns (hash, mtime, size).
*   `get_file_status(self, file_path: Path) -> Tuple[str, Optional[int], str]`: Checks DB for file (`'new'`, `'modified'`, `'unchanged'`, `'deleted'`). Returns (status, file_id, current_hash).
*   `add_or_update_file(self, file_path: Path, language: str, current_hash: str, current_mtime: float, current_size: int) -> int`: Inserts or updates a file's metadata, returns `file_id`.
*   `get_cached_nodes_for_file(self, file_id: int) -> List[Dict]`: Retrieves nodes belonging to a file.
*   `cache_nodes_for_file(self, file_id: int, nodes: List[Dict])`: Deletes old nodes for `file_id`, inserts new ones.
*   `get_cached_edges_for_file(self, file_id: int) -> List[Dict]`: Retrieves edges originating from a file.
*   `cache_edges_for_file(self, file_id: int, edges: List[Dict])`: Deletes old edges for `file_id`, inserts new ones.
*   `get_all_active_nodes(self) -> List[Dict]`: Retrieves all nodes from currently active files.
*   `get_all_active_edges(self) -> List[Dict]`: Retrieves all edges from currently active files.
*   `mark_file_deleted(self, file_path: Path)`: Sets `status` to 'deleted' for files no longer on disk.
*   `delete_file_cache(self, file_id: int)`: Physically removes all associated nodes/edges and file entry.
*   `commit()` / `rollback()`.

### 3.2. MODIFY: `src/core/unified_analysis.py`

This is the central point for cache integration within the `analyze` function.

**Changes in `analyze` function:**
1.  **Initialize `CacheManager`:**
    ```python
    from src.core.cache_manager import CacheManager
    # ...
    cache_enabled = options.get('cache', True)
    cache_manager = None
    if cache_enabled:
        cache_db_path = _resolve_output_dir(target, output_dir) / ".collider_cache.db"
        cache_manager = CacheManager(cache_db_path)
    ```

2.  **Stage 1: AST Parse (Modified to use cache)**
    *   The `TreeSitterUniversalEngine.analyze_directory` (or `analyze_file`) logic will be wrapped.
    *   Iterate through all relevant files in `target_path`. For each file:
        *   Get `file_status` from `cache_manager`.
        *   **If `status` is `'unchanged'`:**
            *   Retrieve `raw_results` (parsed AST data), `particles` (initial from AST), and `edges` (initial from AST) from `cache_manager`.
            *   Add them to the lists for the current analysis run.
        *   **If `status` is `'new'` or `'modified'`:**
            *   Call `ts_engine.analyze_file()` (live parse).
            *   Process the raw particles into initial `particles` and `edges` (e.g., containment, initial RPBL if integrated early).
            *   `cache_manager.cache_file_data()`, `cache_nodes_for_file()`, `cache_edges_for_file()` for this file.
            *   Add them to the lists for the current analysis run.
        *   **If `status` is `'deleted'`:**
            *   `cache_manager.mark_file_deleted(file_path)` (or `delete_file_cache` if immediate deletion is preferred).
    *   **Post-iteration:** After iterating through all files on disk, identify any `files` in the cache marked 'active' but not found on disk, and mark them 'deleted'.

3.  **Refactor `_emit_file_nodes`:**
    *   This function should *also* consult the cache. File nodes for unchanged files should be retrieved directly. For new/modified files, they are created and then cached.

4.  **Graph Reconstruction for Later Stages:**
    *   After the file iteration, `particles` and `edges` lists for subsequent stages will be built by `cache_manager.get_all_active_nodes()` and `cache_manager.get_all_active_edges()`. This ensures all later stages (Stages 3-6) operate on a complete and up-to-date graph, combining cached and newly processed data.

5.  **LLM Enrichment (Stage 3.5):**
    *   If `llm_enrichment` is enabled and a node is re-classified, this new classification should also be pushed back to the cache for that specific node (updating its `properties_json`).

6.  **Edge Resolution (Stage 4):**
    *   `resolve_edges` will still run on the *full merged* `edges` list. Its `resolution` property will be part of the `properties_json` in the `edges` table.

7.  **Subsequent Stages (5 - 5.6):**
    *   `graph_type_inference`, `purpose_field`, `standard_model_enricher` operate on the *full* `particles` and `edges` lists. If they modify a particle's properties (e.g., adding `layer`, `dimensions`, `rpbl`), these changes should be reflected back into the `nodes` table's `properties_json` for that specific node. This ensures *derived* properties are also cached. This implies granular updates to the `properties_json` field.

### 3.3. MODIFY: `src/core/tree_sitter_engine.py`

*   The `analyze_directory` method will be modified to accept the `CacheManager` instance (or be called by `unified_analysis.analyze` for each file, which already has the `CacheManager`).
*   It should skip calling `analyze_file` for files identified as `'unchanged'` by the cache.

### 3.4. MODIFY: `src/core/full_analysis.py`

*   **Initialize Cache:** The `run_full_analysis` function will initialize the `CacheManager` and pass it down to `unified_analysis.analyze` (or enable caching via options).
*   **Performance Tracking:** Update `PerformanceManager` to track cache hits/misses and time saved.
*   **Merkle Root / Provenance:** The `calculate_merkle_root` logic should be aware of the cache. The Merkle root would ideally be calculated over the *final, active set of nodes* (retrieved from cache or newly processed), ensuring the signature reflects the current state of the codebase.

### 3.5. MODIFY: `src/core/edge_extractor.py`

*   **`JSModuleResolver`:** This is a stateful component. If any JavaScript file is `modified` or `new`, the `JSModuleResolver` needs to re-analyze those files. A full reset and rebuild of the resolver's internal state for all *active* JS files (cached or live-parsed) might be necessary whenever a JS file changes, ensuring cross-file JS imports are correctly resolved. This is a subtle but important detail for correctness.

## 4. Incremental Analysis Flow (Example Run)

1.  **Start `full_analysis.py`:** Initializes `CacheManager`.
2.  **`unified_analysis.analyze()` is called:**
    *   **File Scan:** It walks the `target_path`.
    *   **For `file_A.py`:**
        *   `cache_manager.get_file_status('file_A.py')` returns `'unchanged'` (matching hash/mtime in DB).
        *   `raw_results_A`, `particles_A`, `edges_A` are retrieved from cache.
    *   **For `file_B.py`:**
        *   `cache_manager.get_file_status('file_B.py')` returns `'modified'` (hash/mtime mismatch).
        *   `ts_engine.analyze_file('file_B.py')` is called.
        *   `raw_results_B`, `particles_B`, `edges_B` are generated live.
        *   `cache_manager.add_or_update_file()`, `cache_nodes_for_file()`, `cache_edges_for_file()` for `file_B.py`.
    *   **For `file_C.py`:**
        *   `cache_manager.get_file_status('file_C.py')` returns `'new'`.
        *   `ts_engine.analyze_file('file_C.py')` is called.
        *   `raw_results_C`, `particles_C`, `edges_C` are generated live.
        *   `cache_manager.add_or_update_file()`, `cache_nodes_for_file()`, `cache_edges_for_file()` for `file_C.py`.
    *   **For `file_D.py` (deleted from disk):**
        *   `file_D.py` is in the cache but not on disk. `cache_manager.mark_file_deleted('file_D.py')`.
    *   **Reconstruct Global Graph:** `unified_analysis` now calls `cache_manager.get_all_active_nodes()` and `cache_manager.get_all_active_edges()` to build the complete `particles` and `edges` lists, comprising cached data from A, live data from B and C.
3.  **Remaining Stages (Graph Inference, Purpose Field, Markov, Knots, etc.):**
    *   These stages receive the full, up-to-date `particles` and `edges` lists.
    *   If they enrich nodes (e.g., add `rpbl`, `dimensions`), these updates are pushed back to the cache for the specific node in the `nodes` table's `properties_json` field.
4.  **Output Generation (Stage 12):**
    *   The final `UnifiedAnalysisOutput` is generated from the complete, processed `particles` and `edges` lists. The JSON output schema remains unchanged.

## 5. Considerations & Trade-offs

*   **Transitive Invalidation:** The proposed plan primarily handles direct file changes. If a file `A` changes and `B` depends on `A`'s API, `B` is not automatically re-analyzed unless `B` itself changes. This is a common trade-off in incremental analysis for performance. Full transitive invalidation is significantly more complex (requiring dependency graphs *between* cached items) and beyond the scope of a first caching iteration. For Collider, later graph-wide stages re-run anyway, mitigating some of this risk.
*   **Global State (e.g., `JSModuleResolver`):** Must be carefully managed. If any relevant file changes, its internal state must be re-evaluated for correctness.
*   **Cache Coherence for Graph-Level Features:** Features like `purpose_field` or `graph_type_inference` modify node properties based on graph context. When a file is processed live, these modifications need to be written back to the cache for the affected nodes. This requires specific `update_node_properties(node_id, new_properties_dict)` methods in `CacheManager`.
*   **Disk I/O vs. Recomputation:** Reading/writing from SQLite still incurs I/O. For very small files, the overhead of hashing, DB lookup, and JSON serialization/deserialization might approach the cost of live parsing. However, for average-sized and large files, the gains will be substantial.
*   **Schema Evolution:** Using `properties_json` for dynamic fields in `nodes` and `edges` tables greatly simplifies future schema changes, as new fields can be added to the JSON without altering the SQL table structure.
*   **Merges and Conflicts:** For version control systems, if the `.collider_cache.db` file is checked in, merge conflicts can arise. It might be better to keep the cache local and excluded (`.gitignore`), allowing each user to build their own.

---

## Citations

_No citations provided_
