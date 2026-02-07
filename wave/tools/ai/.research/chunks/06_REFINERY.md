# 06 - REFINERY DEEP DIVE

## The Central Nervous System of Context Intelligence

The Refinery is the context atomization and knowledge refinement engine within PROJECT_elements.
It breaks large raw data (code, docs, config) into atomic, searchable, scorable chunks called
RefineryNodes, and integrates them into a broader pipeline of query routing, semantic matching,
caching, and multi-tier AI execution. This document maps every component, data structure,
pipeline stage, and data flow.

---

## 1. Architecture Overview

The Refinery lives inside the **ACI (Adaptive Context Intelligence)** subsystem, located at
`wave/tools/ai/aci/`. ACI is the "Curriculum Compiler" -- it prepares optimal context for AI
models before they answer questions. The Refinery is one of seven core ACI modules:

```
ACI System (wave/tools/ai/aci/)
|
|-- __init__.py           # Module orchestrator, exports all public APIs
|-- intent_parser.py      # Classifies query intent, complexity, scope
|-- tier_orchestrator.py  # Routes queries to execution tiers (0-4)
|-- semantic_finder.py    # Maps queries to semantic space (PURPOSE, LAYER, ROLE)
|-- context_builder.py    # Builds optimized context with token budgets
|-- context_cache.py      # Manages Gemini cached contexts (TTL-based)
|-- refinery.py           # CORE: Atomizes files into RefineryNodes
|-- schema.py             # RefineryNode dataclass definition
|-- feedback_store.py     # Logs every query for learning/tuning
|-- research_orchestrator.py  # Multi-config query execution engine
|-- temporal_resolver.py  # Resolves conflicting canonical sources via git
|-- repopack.py           # Deterministic repo context formatter
|-- refinery/publishers/  # Output publishers
|   |-- neo4j_publisher.py  # Graph database publication
```

### Position in the Ecosystem

The Refinery sits at the intersection of three "holons" born from PROJECT_elements:

1. **Standard Model of Code (SMoC)** -- The theoretical framework (atoms, dimensions, scales)
2. **Collider** -- The analysis tool that classifies code into SMoC particles
3. **Refinery** -- The context platform that processes, stores, indexes, and serves knowledge

The Refinery is evolving from an L6 Package (part of Elements) to an L7 System (independent)
to potentially an L8 Platform (universal infrastructure).

---

## 2. Data Structures

### 2.1 RefineryNode (The Atom)

**File:** `/Users/lech/PROJECTS_all/PROJECT_elements/wave/tools/ai/aci/schema.py`

The fundamental unit. A dataclass with:

```python
@dataclass
class RefineryNode:
    content: str                    # The chunk text
    source_file: str                # Origin file path
    chunk_id: str                   # SHA256-based unique ID (16 hex chars)
    chunk_type: str                 # function, class, imports, h1, h2, yaml_key, etc.
    relevance_score: float = 0.0    # 0.0-1.0 heuristic relevance
    start_line: int = 0             # Start line in source
    end_line: int = 0               # End line in source
    metadata: Dict[str, Any]        # file_type, file_name, layer, role
    created_at: float               # Unix timestamp (time.time())
    embedding: List[float]          # 384-dim vector (MiniLM, optional)
    waybill: Dict[str, Any]         # Logistics tracking {parcel_id, parent_id, route}
```

Key properties:
- `token_estimate` -- `len(content) // 4` (rough chars-to-tokens)
- `to_dict()` -- JSON-serializable via `dataclasses.asdict`

### 2.2 RefineryNode Schema (Canonical YAML)

**File:** `/Users/lech/PROJECTS_all/PROJECT_elements/.agent/schema/refinery_node.schema.yaml`

The full canonical schema (v1.1.0) defines a much richer structure than the Python dataclass.
This is the "ideal" target schema that the system is evolving toward. It includes:

- **Identity (R1):** ID patterns like `ATOM-XXXX`, `NODE-xxx`, `CLUSTER-xxx`, `FILE-xxx`
- **Provenance (R8):** `source_path`, `content_hash` (SHA256 for delta detection), `derived_from`
- **Content:** `summary`, `body_source`, `keywords`
- **Relationships (R5):** `contains`, `contained_by`, `calls`, `called_by`, `imports`, `imported_by`, `inherits`, `inherited_by`, `implements`, `related_to`, `documents`, `documented_by`
- **Confidence (4D Scoring):** `factual`, `alignment`, `current`, `onwards`, `composite` (min of 4), plus `evidence` array and `requires_review` flag
- **Purpose Intelligence (Q-Scores):** `atomic_purpose` (pi1), `composite_purpose` (pi2), `layer_purpose` (pi3), and Q-scores: `Q_alignment`, `Q_coherence`, `Q_density`, `Q_completeness`, `Q_simplicity`, `Q_intrinsic`
- **Dimensions (D1-D8):** Full 8-dimensional classification from SMoC
- **Holonic Context:** Level (L1-L16), parent/children IDs, emergence contribution
- **Topology:** Local (in/out degree, leaf/root), Global (pagerank, betweenness centrality, community), Disconnection analysis
- **Timestamps:** created_at, updated_at, source_modified_at, last_analyzed_at, expires_at
- **LLM Enrichment:** Ring-fenced area for AI-generated insights (model, summary, intent, refactoring suggestions, semantic tags)
- **Definitions:** ClusterNode (aggregation), BoundaryNode (analysis region)

### 2.3 Waybill (Logistics Tracking)

Each RefineryNode carries a waybill dict:

```python
waybill = {
    "parcel_id": "pcl_<12-hex-uuid>",      # Unique parcel ID for this chunk
    "parent_id": "<parent_parcel_id>",      # Input parcel that produced this
    "route": [
        {
            "event": "chunked",
            "timestamp": <unix_epoch>,
            "agent": "refinery.py",
            "context": {
                "source_file": "<filename>",
                "batch_id": "<batch_id>"
            }
        }
    ]
}
```

The waybill system implements the **Logistics Hyper-Layer** theory (documented at
`.agent/intelligence/concepts/THEORY_DATA_LOGISTICS.md`) which treats code as matter
with mass, velocity, and provenance, aligned with W3C PROV-DM.

### 2.4 SemanticMatch and SemanticTarget

**File:** `/Users/lech/PROJECTS_all/PROJECT_elements/wave/tools/ai/aci/semantic_finder.py`

These structures carry the query-to-codebase mapping:

```python
@dataclass
class SemanticTarget:
    purpose: Optional[str]           # pi2 purpose (Retrieve, Transform, etc.)
    layer: Optional[str]             # Architecture layer
    roles: List[str]                 # DDD roles
    direction: EdgeDirection         # UPSTREAM, DOWNSTREAM, BOTH
    scale_focus: Optional[str]       # L3 (NODE), L4 (CONTAINER), L5 (FILE)
    confidence: float                # Match confidence

@dataclass
class SemanticMatch:
    query: str
    targets: List[SemanticTarget]
    suggested_files: List[str]
    suggested_sets: List[str]
    traversal_strategy: str          # "focused", "exploratory", "hierarchical"
    context_flow: str                # "laminar" (coherent) or "turbulent" (mixed)
    reasoning: str
```

### 2.5 Routing and Query Structures

- **QueryProfile** (intent_parser.py): `query`, `intent` (9 types), `complexity` (3 levels), `scope` (internal/external/hybrid), `needs_agent_context`, `suggested_sets`, `keywords`, `confidence`
- **RoutingDecision** (tier_orchestrator.py): `tier` (7 options), `primary_sets`, `fallback_tier`, `use_truths`, `inject_agent`, `reasoning`, `semantic`, `context_flow`, `traversal_direction`
- **OptimizedContext** (context_builder.py): `sets`, `truths`, `positioning`, `critical_files`, `estimated_tokens`, `budget_warning`
- **CacheEntry** (context_cache.py): `cache_name`, `model`, `workspace_key`, `created_at`, `expires_at`, `token_count`

---

## 3. The Refinement Pipeline

### 3.1 Complete Pipeline: Raw Data --> Refined Knowledge

```
                    PIPELINE STAGES
                    ===============

[SOURCE FILES]  .py, .md, .yaml, .yml, generic
       |
       v
  FILE TYPE DETECTION  (Refinery._get_chunker)
       |
       v
  SEMANTIC CHUNKING  (PythonChunker / MarkdownChunker / YamlChunker / GenericChunker)
       |
       v
  CONTEXT DEPTH FILTERING  (shallow / medium / deep)
       |
       v
  CHUNK ID GENERATION  (SHA256 of filepath + content, 16 hex chars)
       |
       v
  RELEVANCE SCORING  (heuristic: type weight + length + docstrings + type hints)
       |
       v
  WAYBILL MINTING  (parcel_id, parent_id, route events)
       |
       v
  ATTENTION GATE  (semantic distance boost + flow-based thresholding)
       |
       v
  EMBEDDING (optional)  (all-MiniLM-L6-v2, 384 dims, via sentence-transformers)
       |
       v
  CACHING  (in-memory dict keyed by file path)
       |
       v
  PUBLICATION  (Neo4j graph store, if available)
       |
       v
  EXPORT  (JSON with validation, atomic writes)
       |
       v
[REFINERY NODES]  Stored in .agent/intelligence/chunks/*.json
```

### 3.2 Chunking Strategies (Input Processing)

**PythonChunker** -- Splits Python files by semantic units:
- Extracts import blocks at top of file
- Identifies class and function definitions at column 0
- Captures constants (UPPER_CASE) and variables (lower_case)
- Returns tuples: `(content, chunk_type, start_line, end_line)`

**MarkdownChunker** -- Splits by header hierarchy:
- Detects `#` through `######` headers
- Each section becomes a chunk typed as `h1`, `h2`, ..., `h6`
- Pre-header content typed as `preamble`

**YamlChunker** -- Splits by top-level keys:
- Detects non-indented key patterns (`key:`)
- Each top-level block becomes a chunk typed as `yaml_key:<keyname>`

**GenericChunker** -- Fallback for unknown types:
- Splits by blank lines (paragraph boundaries)
- Each paragraph becomes a chunk typed as `paragraph`

### 3.3 Context Depth Filtering

Three depth modes control what survives chunking:

| Mode | Kept | Discarded |
|------|------|-----------|
| `shallow` | class, h1, h2 | Everything else |
| `medium` | class, function, h1, h2, h3, imports, yaml_key | constant, variable, h4-h6, paragraph |
| `deep` | Everything | Nothing |

Configured in `wave/config/refinery_config.yaml` under `refinery.context_depth`.

### 3.4 Relevance Scoring

Base score: 0.5, then additive:

| Factor | Bonus |
|--------|-------|
| class | +0.20 |
| function | +0.15 |
| h1 | +0.20 |
| h2 | +0.15 |
| h3 | +0.10 |
| yaml_key | +0.10 |
| imports | +0.05 |
| preamble | +0.05 |
| paragraph | +0.00 |
| Content > 50 chars | +0.05 * log10(length) (max +0.20) |
| Has docstring | +0.10 |
| Has type hints | +0.05 |

Score clamped to [0.0, 1.0].

### 3.5 Attention Gate (Semantic Boosting)

When a `SemanticMatch` is provided, the gate boosts relevance:

1. Maps RefineryNode dimensions to a "particle" dict
2. Computes `compute_semantic_distance` against each SemanticTarget
3. Converts distance to similarity: `1 - distance`
4. Boosts score: `relevance + (similarity * 0.3)`
5. Applies flow-based threshold:
   - **Laminar flow** (coherent query): higher threshold (0.6 default) -- strict filtering
   - **Turbulent flow** (mixed query): lower threshold (0.3 default) -- broader retention
6. If boosted score < threshold, score becomes 0.0 (node filtered out)

### 3.6 Embedding Engine

Singleton `EmbeddingEngine` using `sentence-transformers`:
- Model: `all-MiniLM-L6-v2` (22M params, 384 dims)
- Lazy-loaded on first use
- Embeds lists of texts via `model.encode()`
- Used for semantic search: cosine similarity between query embedding and node embeddings

### 3.7 Validation Before Export

`_validate_chunks()` enforces invariants:
- Every chunk must have content, source_file, chunk_id, chunk_type
- token_estimate must be in [0, 200000]
- relevance_score must be in [0.0, 1.0]
- Line numbers must be non-negative, end >= start
- Total tokens across all chunks must be < 10,000,000

Export uses atomic writes: write to `.tmp`, verify JSON, then rename.

---

## 4. What Feeds INTO the Refinery

### 4.1 Direct Input: Source Files

The Refinery processes files from disk. Current configuration (via `./pe wire`):

| Source | Target | Description |
|--------|--------|-------------|
| `.agent/` directory | `agent_chunks.json` | Agent tools, intelligence, registry |
| `particle/src/core/` | `core_chunks.json` | Collider core pipeline and analysis |
| `wave/tools/ai/aci/` | `aci_chunks.json` | ACI tools (self-referential) |

Default extensions: `.py`, `.md`, `.yaml`, `.yml`
Safety limit: 100 files per directory scan.
Skip directories: `.git`, `.venv`, `.tools_venv`, `__pycache__`, `node_modules`, `.pytest_cache`, `.mypy_cache`, `.tox`, `dist`, `build`, `.eggs`

### 4.2 Semantic Input: Query-Driven Context

When invoked via the ACI pipeline (not standalone), the Refinery receives:
- `parent_parcel_id` -- from the Scanner/Ingester that identified the file
- `batch_id` -- for copresence tracking (which files were processed together)
- `semantic_match` -- from `semantic_finder.py`, influences the attention gate

### 4.3 Configuration Input

**File:** `/Users/lech/PROJECTS_all/PROJECT_elements/wave/config/refinery_config.yaml`

```yaml
pipeline:
  query: "What are the core constituents of the Standard Model of Code?"
  max_files: 50
  use_cache: true
  batch_mode: true

refinery:
  context_depth: "deep"
  attention_mode: "laminar"
  threshold_high: 0.6
  threshold_low: 0.3

output:
  publish_to_neo4j: true
  publish_to_gcs: true
  generate_report: true
```

### 4.4 Intelligence Input

The semantic finder loads a dynamic index from `wave/data/intel/semantic_index.json`
(generated by `cerebras_rapid_intel.py`). This index maps concepts to files,
elevating from Tier 0 (regex) to Tier 1/2 (semantic matching).

The context builder loads "repo truths" from
`.agent/intelligence/truths/repo_truths.yaml` for instant-tier answers.

---

## 5. What Comes OUT of the Refinery

### 5.1 Chunk Files (Primary Output)

Stored at `.agent/intelligence/chunks/`:

| File | Size | Description |
|------|------|-------------|
| `agent_chunks.json` | ~1.9MB | 1,952 chunks, ~218K tokens |
| `core_chunks.json` | ~1.5MB | 598 chunks, ~289K tokens |
| `aci_chunks.json` | ~175KB | 108 chunks, ~30K tokens |
| `metadata.json` | ~368B | Timestamp, git SHA, totals |
| `cache.yaml` | ~119B | Incremental processing cache |

**Total:** 2,658 chunks, ~538K tokens

JSON structure:
```json
{
  "exported_at": <unix_timestamp>,
  "node_count": <int>,
  "total_tokens": <int>,
  "nodes": [
    {
      "content": "...",
      "source_file": "...",
      "chunk_id": "...",
      "chunk_type": "...",
      "relevance_score": 0.0-1.0,
      "start_line": <int>,
      "end_line": <int>,
      "metadata": {...},
      "created_at": <float>,
      "embedding": [],
      "waybill": {...}
    }
  ]
}
```

### 5.2 Neo4j Graph (Optional Output)

**File:** `/Users/lech/PROJECTS_all/PROJECT_elements/wave/tools/ai/aci/refinery/publishers/neo4j_publisher.py`

Publishes to a Neo4j graph database with this schema:

```
(:Atom {id, type, content, start_line, end_line, relevance, embedding})
(:Parcel {id, created_at})
(:Batch {id, created_at})
(:TelemetryEvent {timestamp, atoms_count, duration_seconds, event_type})

(Atom)-[:BELONGS_TO]->(Parcel)
(Atom)-[:GENERATED_IN]->(Batch)
(TelemetryEvent)-[:RECORDED_IN]->(Batch)
```

Uses `UNWIND` for batch ingestion. Includes telemetry recording for feedback loops.

### 5.3 State Synthesis (Intelligence Output)

**File:** `/Users/lech/PROJECTS_all/PROJECT_elements/wave/intelligence/state/live.yaml`

The state synthesizer produces a live snapshot:
- Corpus stats: 4,615 files, 3.4GB, 2.5M lines, 11 languages
- 38 boundaries mapped (analysis sets like brain, body, viz, agent, aci, etc.)
- 295 atoms generated (130 body + 165 brain)
- Delta tracking: 14 pending changes
- Health indicators: corpus_fresh, boundaries_fresh, delta_fresh

### 5.4 Routing Decisions (Query Output)

The tier orchestrator outputs `RoutingDecision` objects that determine:
- Which execution tier handles the query (INSTANT, CEREBRAS, RAG, LONG_CONTEXT, PERPLEXITY, FLASH_DEEP, HYBRID)
- Which analysis sets to load
- Whether to check cached truths first
- Whether to inject agent context
- Semantic matching results (purpose, layer, roles, traversal direction)

### 5.5 Feedback Data

**File:** `.agent/intelligence/aci_feedback.yaml`

Every query execution is logged:
- Query text, intent, complexity, scope
- Tier selected, sets used
- Token counts (in/out)
- Success/failure, retry count, fallback usage
- Duration in ms
- Rolling statistics: total queries, by-tier breakdown, success rate, avg tokens

### 5.6 Refinery Report (Human-Readable)

**File:** `/Users/lech/PROJECTS_all/PROJECT_elements/wave/tools/refinery/refinery_report.py`

CLI tool producing three report modes:
- `--summary`: Current status (freshness, chunk counts, token breakdown)
- `--library`: Top 20 files by chunk count, organized by source file
- `--changes`: Recent filesystem watcher activity
- Full report: All sections combined

---

## 6. How Chunks Are Created, Stored, Indexed, and Searched

### 6.1 Creation Flow

1. **Trigger:** `./pe wire` runs the pipeline, or direct `python refinery.py <path>`
2. **File discovery:** `process_directory()` walks the target directory recursively
3. **Per-file processing:** `process_file()` calls the appropriate chunker
4. **Chunking:** Language-specific strategy splits content into semantic units
5. **Filtering:** Context depth mode filters out low-priority chunk types
6. **Scoring:** Each chunk gets a relevance score via heuristics
7. **ID generation:** SHA256(filepath + content)[:16] gives deterministic chunk IDs
8. **Waybill minting:** UUID-based parcel IDs with route tracking
9. **Attention gate:** Semantic matching boosts/filters based on query intent
10. **Embedding (optional):** all-MiniLM-L6-v2 generates 384-dim vectors
11. **Validation:** All invariants checked before export
12. **Export:** Atomic JSON write to `.agent/intelligence/chunks/`

### 6.2 Storage Layout

```
.agent/intelligence/chunks/
|-- .gitignore            # Selective tracking
|-- agent_chunks.json     # Agent directory chunks (1,952 chunks)
|-- core_chunks.json      # Collider core chunks (598 chunks)
|-- aci_chunks.json       # ACI module chunks (108 chunks)
|-- metadata.json         # Generation metadata (timestamp, git SHA, totals)
|-- cache.yaml            # Incremental processing cache (file hashes)
```

Additional intelligence data at `wave/intelligence/`:
```
wave/intelligence/
|-- state/
|   |-- live.yaml         # Live corpus state snapshot
|-- logs/
|   |-- hsl_local.log     # Local processing logs
|   |-- hsl_local_err.log # Error logs
```

And the main intelligence directory at `.agent/intelligence/`:
```
.agent/intelligence/
|-- chunks/               # Refinery chunk output (above)
|-- truths/               # Repo truths for instant-tier answers
|-- atoms/                # Collider-generated atoms
|-- comm_analysis/        # Communication analysis documents
|-- concepts/             # Theoretical concepts (DATA_LOGISTICS, etc.)
|-- evolution/            # Evolution reports
|-- centripetal_scans/    # Multi-scale scanning results
|-- autopilot_logs/       # Autopilot execution logs
|-- comms/                # Communication fabric state
|-- corpus_inventory.json # Full file inventory
|-- boundaries.json       # Analysis set boundary definitions
|-- delta_state.json      # Change detection state
|-- cache_registry.json   # Gemini context cache registry
|-- FILE_INDEX.csv        # File metadata index
|-- DOCS_INDEX.csv        # Documentation index
```

### 6.3 Indexing

Currently two indexing mechanisms:

**Text-based index (in-memory):**
- Chunks are loaded from JSON files at query time
- Text search via substring matching in `query_chunks.py`
- Ranked by match count and relevance score

**Vector index (optional):**
- If embeddings are generated, cosine similarity search via numpy
- `Refinery.semantic_search(query, nodes, top_k)` embeds the query and finds nearest neighbors
- Not yet persisted to a dedicated vector store (FAISS planned for Tier 2)

**Semantic index (external):**
- `semantic_index.json` from `cerebras_rapid_intel.py` maps concepts to files
- Used by `semantic_finder.py` for Tier 1/2 concept matching
- Cached with LRU to avoid repeated disk reads

### 6.4 Search and Retrieval

Three search paths:

1. **Text search** (`./pe refinery search "query"`):
   - Loads all `*_chunks.json` files
   - Substring match on content
   - Ranks by relevance score
   - Returns file path, line numbers, chunk type, preview

2. **Semantic search** (programmatic, requires embeddings):
   - Embeds query via MiniLM
   - Cosine similarity against embedded nodes
   - Returns (node, similarity_score) tuples sorted by similarity

3. **Context-aware retrieval** (via ACI pipeline):
   - Intent parsing classifies the query
   - Semantic finder maps to PURPOSE/LAYER/ROLE
   - Tier orchestrator selects execution tier
   - Context builder assembles optimized context with token budgets
   - Refinery provides chunks filtered through attention gate

---

## 7. The Broader ACI Pipeline

The Refinery does not operate in isolation. The full ACI query pipeline is:

```
USER QUERY
    |
    v
INTENT PARSER  -->  QueryProfile (intent, complexity, scope)
    |
    v
SEMANTIC FINDER  -->  SemanticMatch (purpose, layer, roles, direction)
    |
    v
TIER ORCHESTRATOR  -->  RoutingDecision (tier, sets, flow)
    |
    v
CONTEXT BUILDER  -->  OptimizedContext (sets, truths, positioning, budget)
    |
    v
EXECUTION (varies by tier):
  - INSTANT: Check repo_truths.yaml, return cached answer
  - CEREBRAS: Fast bulk ops (3000 t/s)
  - RAG: File Search with citations
  - LONG_CONTEXT: Gemini 3 Pro (1M context)
  - PERPLEXITY: External web research
  - FLASH_DEEP: Gemini 2.0 Flash (2M context)
  - HYBRID: Multi-tier combined
    |
    v
FEEDBACK STORE  -->  Log query, tier, tokens, success for learning
```

The Refinery feeds this pipeline at multiple points:
- Provides pre-chunked context for RAG tier
- Attention gate filters chunks based on semantic match
- Chunk metadata informs context budget calculations
- Waybills enable provenance tracking across the entire chain

---

## 8. The Refinery Platform (Next.js UI)

**Location:** `/Users/lech/PROJECTS_all/PROJECT_elements/wave/experiments/refinery-platform/`

A multi-tenant Next.js 15 web application providing visual access to refinery data.

### Pages
- `/` -- Platform overview (stats grid: projects, chunks, tokens, coverage)
- `/projects` -- All project grid
- `/chunks` -- Chunk browser with split-pane detail view
- `/search` -- Context search with highlights
- `/activity` -- Event timeline (6h/12h/24h/48h/7d filters)
- `/settings` -- Platform configuration

### API Routes
- `GET /api/v1/projects` -- Lists tenants (currently Elements only)
- `GET /api/v1/projects/:id/chunks` -- Paginated chunk retrieval
- Reads directly from `.agent/intelligence/chunks/*.json` on disk

### Multi-Tenant Architecture
- Each project is a tenant with isolated data
- Elements = first tenant, others planned (Atman, Sentinel)
- Project discovery via hardcoded paths (future: database/config)
- Data isolation per project ID

### Evolution Path
- **Current:** L6 Package (part of Elements)
- **Next:** L7 System (independent holon)
- **Goal:** L8+ Platform (universal infrastructure, separate repo)

---

## 9. Configuration and Control

### 9.1 refinery_config.yaml

**File:** `/Users/lech/PROJECTS_all/PROJECT_elements/wave/config/refinery_config.yaml`

Controls the Refinery's behavior:
- `pipeline.query` -- The attention mechanism signal
- `pipeline.max_files` -- Safety limit
- `refinery.context_depth` -- shallow/medium/deep
- `refinery.attention_mode` -- laminar (high purity) / turbulent (high discovery)
- `refinery.threshold_high/low` -- Attention gate thresholds
- `output.publish_to_neo4j` -- Enable graph publication
- `output.publish_to_gcs` -- Enable cloud backup
- `output.generate_report` -- Enable report generation

### 9.2 Execution Tiers

| Tier | Name | Model | Context Window | Speed | Cost |
|------|------|-------|---------------|-------|------|
| 0 | INSTANT | None | Cached truths | <100ms | $0 |
| 0.5 | CEREBRAS | Fast model | Bulk ops | ~2s | Low |
| 1 | RAG | Gemini 3 Pro | File search | ~5s | $0.01 |
| 2 | LONG_CONTEXT | Gemini 3 Pro | 1M tokens | ~60s | $0.10 |
| 3 | PERPLEXITY | Sonar Pro | External web | ~30s | $0.05 |
| 4 | FLASH_DEEP | Gemini 2.0 Flash | 2M tokens | ~90s | $0.20 |
| H | HYBRID | Multiple | Combined | ~120s | $0.15 |

---

## 10. Theoretical Foundations

### 10.1 Logistics Hyper-Layer

**File:** `/Users/lech/PROJECTS_all/PROJECT_elements/.agent/intelligence/concepts/THEORY_DATA_LOGISTICS.md`

The Refinery implements the **Logistics Hyper-Layer** -- a unified field theory of data provenance
treating code as matter with physical properties:

- **Code Mass:** `m(p) = alpha * tokens(p) + beta * complexity(p)`
- **Code Velocity:** `v(p) = delta_state / delta_t` (how fast code moves through the pipeline)
- **Three Laws:**
  1. Conservation of Information (lossless transforms preserve mass)
  2. Entropy and Bit-Rot (structure degrades without energy)
  3. Action and Traceability (every action produces a metadata reaction)

The waybill is the **MHC Complex** -- code with valid provenance is "self", code without is "pathogen".

### 10.2 Standard Model Integration

The Refinery maps to the SMoC's 8-dimensional classification:
- D1 (WHAT): Chunk type maps to atom type
- D2 (LAYER): Architecture layer for distance calculation
- D3 (ROLE): DDD role for semantic clustering
- D4-D8: Boundary, state, effect, lifecycle, trust

The semantic finder uses weighted dimension comparison (D3_ROLE has highest weight at 0.25)
to compute semantic distance between particles, enabling the attention gate to boost
relevance based on query intent.

### 10.3 Context Flow Theory

- **Laminar flow** (coherent query): Single purpose, adjacent layers -- strict filtering
  produces focused, high-precision context
- **Turbulent flow** (mixed query): Multiple purposes, distant layers -- broad filtering
  produces exploratory, high-recall context

---

## 11. Current State and Gaps

### What Works
- File atomization into typed, scored, waybill-tracked chunks
- Three chunk files totaling 2,658 chunks (~538K tokens)
- Text search via CLI (`./pe refinery search`)
- Metadata tracking with git SHA and timestamps
- Integration into `./pe wire` pipeline
- Query routing through 7 execution tiers
- Semantic matching against PURPOSE/LAYER/ROLE
- Feedback logging for learning
- Neo4j publication (when available)
- Refinery Platform UI (Next.js, multi-tenant)

### What Is Missing
- Persistent vector index (FAISS or similar) for semantic search
- Continuous/scheduled execution (runs on-demand only)
- Time-series tracking (only current state, no historical snapshots)
- Cross-project search (platform ready but not connected)
- Full schema implementation (Python dataclass is minimal vs YAML schema)
- Cloud deployment of platform (Cloud Run ready but not deployed)
- Integration with Decision Deck system
- Incremental processing (cache.yaml exists but unused)

---

## 12. File Index

All files constituting the Refinery system:

| File | Purpose |
|------|---------|
| `wave/tools/ai/aci/refinery.py` | Core atomization engine (976 lines) |
| `wave/tools/ai/aci/schema.py` | RefineryNode dataclass (33 lines) |
| `wave/tools/ai/aci/__init__.py` | ACI module orchestrator, public API |
| `wave/tools/ai/aci/intent_parser.py` | Query intent/complexity/scope classification |
| `wave/tools/ai/aci/tier_orchestrator.py` | Tier routing with decision matrix |
| `wave/tools/ai/aci/semantic_finder.py` | PURPOSE/LAYER/ROLE semantic matching |
| `wave/tools/ai/aci/context_builder.py` | Token budget management, context optimization |
| `wave/tools/ai/aci/context_cache.py` | Gemini cached context lifecycle management |
| `wave/tools/ai/aci/feedback_store.py` | Query execution logging and analytics |
| `wave/tools/ai/aci/research_orchestrator.py` | Multi-config research execution engine |
| `wave/tools/ai/aci/temporal_resolver.py` | Git-based canonical source resolution |
| `wave/tools/ai/aci/repopack.py` | Deterministic repo context formatting |
| `wave/tools/ai/aci/refinery/publishers/neo4j_publisher.py` | Graph database publication |
| `wave/tools/ai/aci/GEMINI.md` | ACI component documentation for agents |
| `wave/config/refinery_config.yaml` | Parametric configuration |
| `wave/tools/refinery/refinery_report.py` | CLI report generator |
| `.agent/schema/refinery_node.schema.yaml` | Canonical schema (v1.1.0, 648 lines) |
| `.agent/intelligence/chunks/*.json` | Chunk storage (3 files + metadata) |
| `.agent/intelligence/chunks/cache.yaml` | Incremental processing cache |
| `wave/intelligence/state/live.yaml` | Live corpus state |
| `wave/experiments/refinery-platform/` | Next.js multi-tenant platform |
| `.agent/intelligence/concepts/THEORY_DATA_LOGISTICS.md` | Logistics theory |
| `.agent/intelligence/comm_analysis/REFINERY_MINIMAL_PATH.md` | Implementation plan |
| `.agent/intelligence/comm_analysis/REFINERY_TIER1_EXECUTION_PLAN.md` | Execution plan |
| `.agent/intelligence/comm_analysis/CLOUD_REFINERY_KNOWLEDGE_MAP.md` | Cloud deployment plan |
