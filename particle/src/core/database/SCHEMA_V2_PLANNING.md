# Schema V2 Planning: Multi-Layer Graph Support

> **Context:** The other session is implementing dynamic observers (runtime, change, human, operational flows).
> **Our Job:** Ensure the database layer can support these new data types.
> **Status:** PLANNING - Toggle features OFF by default

---

## What They're Building

| Module | Purpose | Data Needs |
|--------|---------|------------|
| `dynamics/runtime_ingestor.py` | Ingest OpenTelemetry, cProfile, Coverage.py | Execution metrics per node |
| `evolution/git_miner.py` | PyDriller temporal coupling | Co-change matrix, churn |
| `evolution/social_graph.py` | Authorship, truck factor | Author-node mapping |
| `operational/incident_bridge.py` | DORA metrics, incident correlation | Incident-code links |

---

## Current Schema (V1) - What We Have

```
analysis_runs     → Run metadata, history
tracked_files     → File hashes for incremental (CHANGE FLOW foundation!)
nodes             → Static structure + metadata_json
edges             → Static relationships
```

**Already Supports:**
- Change detection via `tracked_files` + `DeltaResult`
- Run comparison via `compare_runs()`
- Flexible enrichment via `metadata_json`

---

## Schema V2 - What They'll Need

### 1. Runtime Metrics Table (Layer 1)

```sql
-- Toggle: --runtime-metrics
CREATE TABLE IF NOT EXISTS runtime_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    node_id TEXT NOT NULL,

    -- Execution data
    execution_count INTEGER DEFAULT 0,
    total_time_ms REAL,
    avg_time_ms REAL,
    p50_time_ms REAL,
    p95_time_ms REAL,
    p99_time_ms REAL,

    -- Coverage
    line_coverage REAL,          -- 0.0-1.0
    branch_coverage REAL,

    -- Source
    source TEXT,                 -- 'cprofile', 'otel', 'coverage.py'
    collected_at TIMESTAMP,

    UNIQUE(run_id, node_id, source)
);
```

### 2. Temporal Coupling Table (Layer 2)

```sql
-- Toggle: --temporal-analysis
CREATE TABLE IF NOT EXISTS temporal_coupling (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_path TEXT NOT NULL,

    -- Coupled pair
    node_a TEXT NOT NULL,
    node_b TEXT NOT NULL,

    -- Coupling metrics
    coupling_score REAL,         -- 0.0-1.0 (Jaccard-like)
    co_change_count INTEGER,     -- Times changed together
    total_changes_a INTEGER,
    total_changes_b INTEGER,

    -- Time range
    computed_from TIMESTAMP,
    computed_to TIMESTAMP,

    UNIQUE(project_path, node_a, node_b)
);

-- Churn history
CREATE TABLE IF NOT EXISTS churn_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_path TEXT NOT NULL,
    file_path TEXT NOT NULL,

    -- Metrics
    lines_added INTEGER,
    lines_removed INTEGER,
    commit_count INTEGER,
    author_count INTEGER,

    -- Time bucket
    period_start TIMESTAMP,
    period_end TIMESTAMP,

    UNIQUE(project_path, file_path, period_start)
);
```

### 3. Authorship/Social Tables (Layer 3)

```sql
-- Toggle: --social-graph
CREATE TABLE IF NOT EXISTS authors (
    id TEXT PRIMARY KEY,         -- email or unique ID
    name TEXT,
    email TEXT,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP
);

CREATE TABLE IF NOT EXISTS node_authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_path TEXT NOT NULL,
    node_id TEXT NOT NULL,
    author_id TEXT NOT NULL REFERENCES authors(id),

    -- Ownership metrics
    lines_authored INTEGER,
    percentage REAL,             -- 0.0-1.0
    last_touch TIMESTAMP,

    UNIQUE(project_path, node_id, author_id)
);

-- Knowledge risk
CREATE TABLE IF NOT EXISTS knowledge_risk (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES analysis_runs(id),
    node_id TEXT NOT NULL,

    truck_factor INTEGER,        -- Minimum authors to lose
    is_knowledge_island BOOLEAN, -- Only 1 author
    primary_author TEXT,

    UNIQUE(run_id, node_id)
);
```

### 4. Operational Tables (Layer 4)

```sql
-- Toggle: --operational-bridge
CREATE TABLE IF NOT EXISTS incidents (
    id TEXT PRIMARY KEY,
    project_path TEXT NOT NULL,

    -- Incident data
    title TEXT,
    severity TEXT,               -- critical, high, medium, low
    created_at TIMESTAMP,
    resolved_at TIMESTAMP,
    mttr_minutes INTEGER,

    -- Source
    source TEXT,                 -- 'pagerduty', 'opsgenie', 'manual'
    external_id TEXT
);

CREATE TABLE IF NOT EXISTS incident_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL REFERENCES incidents(id),
    node_id TEXT NOT NULL,

    -- Causation
    confidence REAL,             -- 0.0-1.0
    evidence TEXT,               -- 'stack_trace', 'git_blame', 'manual'

    UNIQUE(incident_id, node_id)
);

CREATE TABLE IF NOT EXISTS deployments (
    id TEXT PRIMARY KEY,
    project_path TEXT NOT NULL,
    run_id TEXT REFERENCES analysis_runs(id),

    deployed_at TIMESTAMP,
    environment TEXT,            -- 'prod', 'staging', 'dev'
    commit_sha TEXT,
    success BOOLEAN,

    -- DORA metrics
    lead_time_minutes INTEGER,
    rollback BOOLEAN DEFAULT FALSE
);
```

### 5. Edge Layer Extension

```sql
-- Extend edges table or create layer-specific edge table
CREATE TABLE IF NOT EXISTS dynamic_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,

    -- Layer identification
    layer TEXT NOT NULL,         -- 'runtime', 'temporal', 'social', 'operational'
    edge_type TEXT,              -- 'calls_at_runtime', 'co_changes', 'reviews', 'caused_incident'

    -- Metrics
    weight REAL DEFAULT 1.0,
    confidence REAL,
    discovered_by TEXT,          -- 'otel', 'pydriller', 'git_blame', etc.

    metadata_json TEXT,

    UNIQUE(run_id, source_id, target_id, layer, edge_type)
);
```

---

## Feature Registry Additions

```python
# Add to registry.py FEATURES list

Feature(
    id="runtime_metrics",
    description="Store execution/profiling data per node",
    default=False,
    cli="--runtime-metrics",
    status="experimental",
    requires=["database"],
),
Feature(
    id="temporal_analysis",
    description="Compute and store temporal coupling from git history",
    default=False,
    cli="--temporal-analysis",
    status="experimental",
    requires=["database"],
),
Feature(
    id="social_graph",
    description="Track authorship, ownership, and knowledge risk",
    default=False,
    cli="--social-graph",
    status="experimental",
    requires=["database"],
),
Feature(
    id="operational_bridge",
    description="Link incidents and deployments to code",
    default=False,
    cli="--operational-bridge",
    status="experimental",
    requires=["database"],
),
```

---

## API Extensions Needed

```python
# New abstract methods for DatabaseBackend

# Runtime
def insert_runtime_metrics(self, run_id: str, metrics: List[Dict]) -> int: ...
def get_runtime_metrics(self, run_id: str, node_id: str = None) -> List[Dict]: ...

# Temporal
def compute_temporal_coupling(self, project_path: str, since: datetime) -> int: ...
def get_temporal_coupling(self, project_path: str, threshold: float = 0.3) -> List[Dict]: ...
def get_churn_history(self, project_path: str, file_path: str = None) -> List[Dict]: ...

# Social
def sync_authors(self, project_path: str) -> int: ...
def get_node_authors(self, project_path: str, node_id: str) -> List[Dict]: ...
def compute_knowledge_risk(self, run_id: str) -> int: ...
def get_knowledge_islands(self, run_id: str) -> List[Dict]: ...

# Operational
def link_incident(self, incident: Dict, node_ids: List[str]) -> str: ...
def get_node_incidents(self, node_id: str) -> List[Dict]: ...
def record_deployment(self, deployment: Dict) -> str: ...
def get_dora_metrics(self, project_path: str, period_days: int = 30) -> Dict: ...

# Multi-layer
def insert_dynamic_edges(self, run_id: str, layer: str, edges: List[Dict]) -> int: ...
def get_edges_by_layer(self, run_id: str, layer: str) -> List[Dict]: ...
```

---

## Migration Strategy

```python
# migrations/versions/v002_runtime_metrics.py
# migrations/versions/v003_temporal_coupling.py
# migrations/versions/v004_social_graph.py
# migrations/versions/v005_operational_bridge.py
# migrations/versions/v006_dynamic_edges.py

# Each migration:
# 1. Creates tables ONLY if feature is enabled
# 2. Is idempotent (can run multiple times)
# 3. Updates schema_version
```

---

## Views for Multi-Layer Queries

```sql
-- Unified risk view (combines all layers)
CREATE VIEW IF NOT EXISTS node_risk_score AS
SELECT
    n.run_id,
    n.id as node_id,
    n.name,
    n.complexity,

    -- Runtime risk
    COALESCE(rm.p99_time_ms, 0) as latency_risk,

    -- Change risk
    COALESCE(ch.commit_count, 0) as churn_risk,

    -- Knowledge risk
    COALESCE(kr.truck_factor, 999) as bus_factor,
    COALESCE(kr.is_knowledge_island, 0) as knowledge_island,

    -- Operational risk
    (SELECT COUNT(*) FROM incident_nodes ino WHERE ino.node_id = n.id) as incident_count

FROM nodes n
LEFT JOIN runtime_metrics rm ON n.id = rm.node_id AND n.run_id = rm.run_id
LEFT JOIN churn_history ch ON n.file_path = ch.file_path
LEFT JOIN knowledge_risk kr ON n.id = kr.node_id AND n.run_id = kr.run_id;
```

---

## Compatibility Notes

1. **V1 schema remains untouched** - all new tables are additive
2. **metadata_json fallback** - if tables not created, data can still go to JSON
3. **Feature flags control table creation** - no overhead if disabled
4. **Our transaction wrapping supports multi-table inserts** - already implemented!

---

## What We Should Prepare NOW

1. **Document the extension points** in our code
2. **Add placeholder feature flags** to registry (status=experimental)
3. **Create migration infrastructure** if not already robust
4. **Consider adding `layer` column to edges table** in V1.1 as forward-compatible
