# 02 ACI System (Adaptive Context Intelligence)

**Created:** 2026-02-07
**Scope:** `wave/tools/ai/aci/` + `wave/tools/ai/analyze/` + `wave/tools/ai/analyze.py`
**Purpose:** Complete architecture map of the ACI subsystem -- the query routing, context optimization, and multi-tier execution engine that powers the Elements AI analysis tool.

---

## 1. System Overview

ACI is the "Curriculum Compiler" -- it takes a raw user query and decides:

1. **What** the query is about (intent, complexity, scope)
2. **Where** to route it (which execution tier)
3. **What context** to load (which analysis sets, which files)
4. **How** to optimize that context (token budgets, positioning, caching)

It bridges the gap between a human question and the right AI model+context combination.

---

## 2. File-by-File Analysis

### 2.1 aci/__init__.py
- **Purpose:** Package entry point. Loads `aci_config.yaml` as singleton `ACI_CONFIG` and re-exports all public symbols from submodules.
- **Key exports:** `analyze_and_route()`, `ACI_CONFIG`, all classes/functions from submodules.
- **Config read:** `wave/config/aci_config.yaml` (navigates up 4 levels from `aci/`).
- **Convenience function:** `analyze_and_route(query, force_tier)` -- combines `analyze_query()` + `route_query()`.

### 2.2 aci/schema.py
- **Purpose:** Shared data model for the Refinery system. Defines `RefineryNode` -- the atomic chunk unit.
- **Key class:** `RefineryNode` dataclass with fields: `content`, `source_file`, `chunk_id` (SHA256), `chunk_type`, `relevance_score`, `start_line`/`end_line`, `metadata`, `embedding` (384-dim MiniLM), `waybill` (logistics tracking dict).
- **No internal imports.** This is the leaf schema used by `refinery.py` and `neo4j_publisher.py`.
- **Imported by:** `aci/refinery.py`, `aci/refinery/publishers/neo4j_publisher.py`, `aci/__init__.py`.

### 2.3 aci/intent_parser.py
- **Purpose:** Parses queries into structured `QueryProfile` (intent, complexity, scope, keywords, suggested sets).
- **Key classes/enums:**
  - `QueryIntent` (9 values: ARCHITECTURE, DEBUG, RESEARCH, VALIDATE, TASK, COUNT, LOCATE, EXPLAIN, IMPLEMENT, UNKNOWN)
  - `QueryComplexity` (SIMPLE, MODERATE, COMPLEX)
  - `QueryScope` (INTERNAL, EXTERNAL, HYBRID)
  - `QueryProfile` dataclass (full query analysis result)
- **Key function:** `analyze_query(query) -> QueryProfile` -- the main entry point.
- **Config dependency:** Lazy-imports `ACI_CONFIG` from parent package to merge configurable keywords with hardcoded defaults.
- **Helpers:** `is_agent_query()`, `is_external_query()` for quick checks.
- **Imported by:** `tier_orchestrator.py`, `research_orchestrator.py`, `feedback_store.py`, `analyze.py` (multiple locations).

### 2.4 aci/tier_orchestrator.py
- **Purpose:** Routes queries to the correct execution tier based on intent/complexity/scope matrix + keyword triggers.
- **Key classes/enums:**
  - `Tier` (7 values: INSTANT, CEREBRAS, RAG, LONG_CONTEXT, PERPLEXITY, FLASH_DEEP, HYBRID)
  - `RoutingDecision` dataclass (tier + sets + fallback + semantic match + reasoning)
- **Key function:** `route_query(query, force_tier, use_semantic) -> RoutingDecision` -- the core router.
- **Internal imports:** `intent_parser` (for `analyze_query`, enums), `semantic_finder` (for `semantic_match`, types).
- **Logic highlights:**
  - Decision matrix `ROUTING_MATRIX` maps `(intent, complexity, scope)` triples to tiers.
  - `CEREBRAS_TRIGGERS` / `FLASH_DEEP_TRIGGERS` keyword sets for fast-path routing.
  - `sanitize_sets()` -- deterministic alias/validate/dedupe/cap pipeline for set names.
  - `SET_ALIASES` maps invalid semantic matcher outputs to valid `analysis_sets.yaml` keys.
  - Fallback chain: INSTANT -> CEREBRAS -> RAG -> LONG_CONTEXT -> FLASH_DEEP -> (end).
  - Semantic flow: laminar (semantic sets first) vs turbulent (profile sets first).
- **API call:** `get_model_token_limit()` optionally queries Gemini API via `google.genai.Client()` for dynamic model limits.
- **Imported by:** `aci/__init__.py`, `feedback_store.py`, `analyze.py`.

### 2.5 aci/semantic_finder.py
- **Purpose:** Maps queries to the Standard Model of Code semantic space (PURPOSE, dimensions, edges, layers, roles).
- **Key classes:**
  - `PurposeLevel` (PI1_ATOMIC through PI4_SYSTEM)
  - `EdgeDirection` (UPSTREAM, DOWNSTREAM, BOTH)
  - `SemanticTarget` dataclass (purpose, layer, roles, direction, scale_focus, confidence)
  - `SemanticMatch` dataclass (targets, suggested files/sets, traversal strategy, context flow, reasoning)
- **Key functions:**
  - `semantic_match(query) -> SemanticMatch` -- the core "Curriculum Compiler" function.
  - `compute_semantic_distance(particle_a, particle_b) -> float` -- weighted 8-dimensional distance.
  - `get_upstream_context()` / `get_downstream_context()` -- graph traversal helpers.
- **Data file read:** `wave/data/intel/semantic_index.json` (from `cerebras_rapid_intel.py` output). LRU-cached.
- **No internal ACI imports.** This is a leaf module within ACI.
- **Imported by:** `tier_orchestrator.py`, `refinery.py`, `aci/__init__.py`.
- **Constants:** `DIMENSION_WEIGHTS` (8 dims), `ROLE_CLUSTERS` (8 clusters), `EDGE_FAMILIES` (5 families), `QUERY_PURPOSE_KEYWORDS`, `QUERY_LAYER_KEYWORDS`, `QUERY_DIRECTION_KEYWORDS`.

### 2.6 aci/context_builder.py
- **Purpose:** Builds optimized context for AI queries -- token budgets, file positioning, truths injection, agent context injection.
- **Key class:** `OptimizedContext` dataclass (sets, truths, positioning strategy, critical files, estimated tokens, budget warning).
- **Key functions:**
  - `optimize_context(sets, sets_config, project_root, ...) -> OptimizedContext`
  - `load_repo_truths(project_root) -> Dict` -- reads `.agent/intelligence/truths/repo_truths.yaml`
  - `answer_from_truths(query, truths) -> Optional[str]` -- attempts to answer from cached data (INSTANT tier logic)
  - `inject_agent_context(sets, inject_level)` -- prepends agent sets at high-attention positions
- **Config dependency:** Lazy-imports `ACI_CONFIG` for token budgets.
- **Data file read:** `.agent/intelligence/truths/repo_truths.yaml`
- **Imported by:** `aci/__init__.py`.

### 2.7 aci/refinery.py
- **Purpose:** Context atomization engine. Breaks files into semantic chunks (`RefineryNode`) with metadata, relevance scoring, optional embeddings, and optional Neo4j publication.
- **Key classes:**
  - `EmbeddingEngine` (singleton, lazy-loads `all-MiniLM-L6-v2`, 384-dim vectors)
  - `FileChunker` (ABC), `PythonChunker`, `MarkdownChunker`, `YamlChunker`, `GenericChunker`
  - `Refinery` (main engine: process_file, process_directory, export_to_json, semantic_search, compact_for_context)
- **Internal imports:** `schema.RefineryNode`, `semantic_finder.compute_semantic_distance`/`SemanticMatch`/`SemanticTarget`, `refinery.publishers.neo4j_publisher.Neo4jPublisher`.
- **Data files written:** Chunks exported to `wave/intelligence/chunks/` directory. JSON format with atomic write (temp+rename).
- **Config:** `context_depth` (shallow/medium/deep), `threshold_high`/`threshold_low`, `attention_mode` from `refinery` config block.
- **External deps:** `sentence-transformers` (optional, for embeddings), `numpy` (optional, for cosine similarity).
- **Imported by:** `aci/__init__.py`.

### 2.8 aci/research_orchestrator.py
- **Purpose:** Multi-configuration query orchestrator. Executes predefined "research schemas" that combine multiple ACI runs with different parameters and synthesize results.
- **Key classes:**
  - `ResearchEngine` (main orchestrator: execute, execute_custom, list_schemas, describe_schema, get_capabilities)
  - `ResearchSchema`, `RunConfig`, `RunResult`, `CompositeResult` dataclasses
  - `SynthesisStrategy` (6 strategies: CONSENSUS, QUALITY_GRADIENT, DIALECTIC, TRIANGULATION, BAYESIAN, HIERARCHICAL)
  - `OutputFormat` (9 formats including domain-specific ones)
- **Internal imports:** `intent_parser.analyze_query`, `intent_parser.QueryScope`/`QueryIntent`.
- **Config file read:** `wave/config/research_schemas.yaml`
- **External calls:**
  - Internal runs: Shells out to `analyze.py` as subprocess.
  - External runs: Imports `perplexity_research.py` for Perplexity API calls.
- **Validation:** Schema loader validates models against `model_catalog`, tiers against `TIER_CATALOG`, enforces external membrane rules, checks guardrails.
- **Imported by:** `aci/__init__.py`.

### 2.9 aci/context_cache.py
- **Purpose:** Manages lifecycle of Gemini cached contexts for the FLASH_DEEP tier ("expensive per snapshot, cheap per question" pattern).
- **Key classes:**
  - `CacheEntry` dataclass (cache_name, model, workspace_key, expires_at, token_count)
  - `CacheRegistry` (register, get_valid_cache, invalidate, cleanup_expired, stats)
- **Key function:** `get_workspace_key()` -- generates cache key from git commit SHA + dirty state.
- **Data file:** `wave/intelligence/cache_registry.json` (JSON persistence).
- **No internal ACI imports.** Leaf module.
- **Imported by:** `aci/__init__.py`, `analyze.py` (FLASH_DEEP tier logic).

### 2.10 aci/feedback_store.py
- **Purpose:** Logs every ACI query execution for learning and routing optimization.
- **Key classes:**
  - `FeedbackEntry` dataclass (timestamp, query, intent, tier, tokens, success, etc.)
  - `FeedbackLoop` (log_query, get_stats, get_recent_entries, get_tier_recommendations)
- **Internal imports:** `intent_parser.QueryProfile`, `tier_orchestrator.RoutingDecision`.
- **Data file written:** `.agent/intelligence/aci_feedback.yaml` (max 1000 entries, rolling).
- **Config:** `PROJECT_ROOT` env var or auto-detection.
- **Imported by:** `analyze.py`.

### 2.11 aci/temporal_resolver.py
- **Purpose:** Resolves conflicting "canonical source" claims using git history + filesystem timestamps.
- **Key class:** `TemporalResolver` (get_git_history, get_file_metadata, resolve_conflict).
- **External calls:** `git log`, `git status` via subprocess.
- **No internal ACI imports.** Standalone utility.
- **Not imported by other ACI modules.** Used as CLI tool or by external callers.

### 2.12 aci/repopack.py
- **Purpose:** Generates deterministic, cacheable repository context snapshots for FLASH_DEEP tier.
- **Key functions:** `format_repopack(repo_path, question)`, `get_cache_key(repo_path)`, `get_repo_id()`, `get_file_tree()`, `get_hot_files()`.
- **External calls:** `git rev-parse`, `git diff` via subprocess.
- **Format:** Sections: REPO_ID, FILE_TREE, HOT_CODE, QUESTION (question last for cache reuse).
- **Imported by:** `analyze.py` (FLASH_DEEP tier).

### 2.13 aci/refinery/publishers/neo4j_publisher.py
- **Purpose:** Publishes RefineryNode atoms to Neo4j graph database.
- **Key class:** `Neo4jPublisher` (publish_atoms, publish_telemetry).
- **Internal imports:** `schema.RefineryNode`.
- **External deps:** `neo4j` driver. Connects via `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` env vars.
- **Graph schema:** `(:Atom)`, `(:Parcel)`, `(:Batch)`, `(:TelemetryEvent)` nodes with `BELONGS_TO`, `GENERATED_IN`, `RECORDED_IN` edges.
- **Imported by:** `refinery.py` (optional, try/except).

---

## 3. Analyze Package (analyze/)

The `analyze/` package provides the execution layer that ACI routes into.

### 3.1 analyze/__init__.py
- **Exports:** `AnalyzeConfig`, `load_config`, `PROJECT_ROOT`, `AnalyzeResult`, `ContextManifest`.
- **Version:** 4.0.0 (modular architecture).

### 3.2 analyze/config.py
- **Purpose:** Configuration loader. Reads `analysis_sets.yaml`, `prompts.yaml`, `semantic_models.yaml`.
- **Key class:** `AnalyzeConfig` (aggregates all config: sets, models, backend, modes, prompts).
- **Key functions:** `load_config()`, `resolve_set()` (recursive include expansion), `recommend_sets()`.
- **Constants:** `PROJECT_ROOT`, `MAX_CONTEXT_TOKENS` (1M), `MAX_FLASH_DEEP_TOKENS` (2M).
- **Config files read:** `wave/config/analysis_sets.yaml`, `wave/config/prompts.yaml`, `wave/config/semantic_models.yaml`.
- **Env vars:** `GEMINI_API_KEY`, `GEMINI_BACKEND`, `ANTIGRAVITY_AGENT`, `CI`, `NONINTERACTIVE`.

### 3.3 analyze/clients.py
- **Purpose:** API client factory. Creates Vertex AI or AI Studio clients with retry logic.
- **Key functions:** `create_client()`, `create_vertex_client()`, `create_developer_client()`, `retry_with_backoff()`.
- **Secrets:** Doppler (preferred) or env var for `GEMINI_API_KEY`. `gcloud` subprocess for Vertex tokens.
- **External calls:** Google Gemini API (via `google.genai`), Doppler CLI, `gcloud` CLI.

### 3.4 analyze/session.py
- **Purpose:** Session/turn logging for audit trail.
- **Key functions:** `log_turn()`, `save_session_log()`, `get_session_stats()`.
- **Data file written:** `particle/docs/research/gemini/sessions/` (JSON session logs).
- **Env var:** `SESSION_LOG=1` enables stderr logging.

### 3.5 analyze/context.py
- **Purpose:** File collection and context string building. Security-sensitive exclusions.
- **Key functions:** `list_local_files()`, `build_context_from_files()`, `count_tokens_estimate()`, `validate_context_size()`.
- **Positional strategies:** "sandwich" (critical files at beginning+end) and "front-load" (beginning only).
- **Security:** Hardcoded exclusion list for secrets, credentials, binary files.

### 3.6 analyze/output.py
- **Purpose:** Stone Tool output contract. Defines structured analysis result format.
- **Key classes:** `AnalyzeResult` (the canonical output), `ContextManifest` (what the model saw).
- **Key functions:** `compute_bundle_hash()` (SHA256 of file contents), `estimate_cost()` (per-model pricing).

### 3.7 analyze/tiers/__init__.py + base.py
- **Purpose:** Tier execution system with abstract base class.
- **Key classes:** `Tier` enum (6 values), `BaseTierExecutor` (ABC with execute/can_handle/get_info), `TierRequest`/`TierResponse` dataclasses.
- **Constants:** `TIER_CHARACTERISTICS` (latency, cost, requirements per tier).

### 3.8 analyze/tiers/long_context.py
- **Purpose:** Tier 2 implementation. Full context Gemini reasoning.
- **Key class:** `LongContextExecutor` (extends `BaseTierExecutor`).
- **External calls:** `google.genai` for Gemini API calls with retry. Auto-saves to research directory.
- **Imports:** `clients.create_client`, `clients.retry_with_backoff`, `output.estimate_cost`.

### 3.9 analyze/modes/__init__.py
- **Purpose:** Analysis mode definitions (standard, forensic, architect, interactive, insights, role_validation, plan_validation, trace).
- **Metadata:** Per-mode requirements (line numbers, output format, auto-inject docs).

### 3.10 analyze/search/__init__.py
- **Purpose:** RAG (File Search) subsystem placeholder. Store/indexer/query modules planned.

---

## 4. Configuration Files

| File | Path | Purpose |
|------|------|---------|
| `aci_config.yaml` | `wave/config/aci_config.yaml` | Tier thresholds, token budgets, intent keywords, agent context, feedback config |
| `research_schemas.yaml` | `wave/config/research_schemas.yaml` | Multi-run research schema definitions for ResearchEngine |
| `analysis_sets.yaml` | `wave/config/analysis_sets.yaml` | File pattern sets (pipeline, theory, agent_*, etc.) |
| `prompts.yaml` | `wave/config/prompts.yaml` | System prompts, mode configs, model defaults |
| `semantic_models.yaml` | `wave/config/semantic_models.yaml` | HSL semantic model configuration |

---

## 5. Data Files Read/Written

| File | Direction | Module | Purpose |
|------|-----------|--------|---------|
| `wave/data/intel/semantic_index.json` | Read | `semantic_finder.py` | Concept-to-file mappings from cerebras_rapid_intel |
| `.agent/intelligence/truths/repo_truths.yaml` | Read | `context_builder.py` | Cached repo statistics for INSTANT tier |
| `wave/intelligence/cache_registry.json` | Read/Write | `context_cache.py` | Gemini context cache tracking |
| `.agent/intelligence/aci_feedback.yaml` | Read/Write | `feedback_store.py` | Query execution feedback log |
| `wave/intelligence/chunks/*.json` | Write | `refinery.py` | Exported atomic chunks |
| `particle/docs/research/gemini/sessions/` | Write | `session.py` | Session logs |

---

## 6. External API Calls

| Service | Module | Model/Endpoint | Purpose |
|---------|--------|----------------|---------|
| Google Gemini API | `clients.py`, `long_context.py` | `gemini-3-pro-preview` (default) | Main analysis LLM |
| Google Gemini API | `tier_orchestrator.py` | `client.models.get()` | Dynamic token limit query |
| Perplexity API | `research_orchestrator.py` | `sonar-pro` | External web research |
| Neo4j | `neo4j_publisher.py` | `bolt://localhost:7687` | Graph storage of atoms |
| Doppler | `clients.py` | CLI `doppler secrets get` | Secret management |
| gcloud | `clients.py`, `context_cache.py` | `gcloud auth`, `gcloud config` | GCP auth + project detection |
| sentence-transformers | `refinery.py` | `all-MiniLM-L6-v2` | 384-dim vector embeddings |

---

## 7. Dependency Graph

```
analyze.py (main entry point, ~162KB monolith)
    |
    +-- aci/ (Adaptive Context Intelligence)
    |   |
    |   +-- __init__.py ---- loads aci_config.yaml
    |   |       |
    |   |       +-- intent_parser.py (query analysis)
    |   |       |       reads: ACI_CONFIG (lazy)
    |   |       |
    |   |       +-- tier_orchestrator.py (routing)
    |   |       |       imports: intent_parser, semantic_finder
    |   |       |       calls: google.genai (optional, for token limits)
    |   |       |
    |   |       +-- semantic_finder.py (SMoC graph matching)
    |   |       |       reads: wave/data/intel/semantic_index.json
    |   |       |
    |   |       +-- context_builder.py (context optimization)
    |   |       |       reads: .agent/intelligence/truths/repo_truths.yaml
    |   |       |       reads: ACI_CONFIG (lazy)
    |   |       |
    |   |       +-- context_cache.py (Gemini cache registry)
    |   |       |       reads/writes: wave/intelligence/cache_registry.json
    |   |       |       calls: git (subprocess)
    |   |       |
    |   |       +-- refinery.py (context atomization)
    |   |       |       imports: schema, semantic_finder, neo4j_publisher
    |   |       |       writes: wave/intelligence/chunks/*.json
    |   |       |       calls: sentence-transformers (optional)
    |   |       |
    |   |       +-- research_orchestrator.py (multi-run orchestration)
    |   |       |       imports: intent_parser
    |   |       |       reads: wave/config/research_schemas.yaml
    |   |       |       calls: analyze.py (subprocess), perplexity_research.py
    |   |       |
    |   |       +-- feedback_store.py (execution logging)
    |   |       |       imports: intent_parser, tier_orchestrator
    |   |       |       writes: .agent/intelligence/aci_feedback.yaml
    |   |       |
    |   |       +-- temporal_resolver.py (conflict resolution)
    |   |       |       calls: git (subprocess)
    |   |       |
    |   |       +-- repopack.py (deterministic context snapshots)
    |   |       |       calls: git (subprocess)
    |   |       |
    |   |       +-- schema.py (shared RefineryNode model)
    |   |
    |   +-- refinery/publishers/
    |       +-- neo4j_publisher.py
    |           imports: schema
    |           calls: Neo4j driver
    |
    +-- analyze/ (execution layer)
        |
        +-- config.py ---- reads analysis_sets.yaml, prompts.yaml, semantic_models.yaml
        +-- clients.py --- creates Gemini API clients (Vertex/AI Studio)
        +-- context.py --- builds context strings from files
        +-- output.py ---- defines AnalyzeResult output contract
        +-- session.py --- session/turn logging
        +-- tiers/
        |   +-- base.py ----------- BaseTierExecutor ABC
        |   +-- long_context.py --- Tier 2 implementation (Gemini full context)
        +-- modes/
        |   +-- __init__.py ------- Mode metadata (standard, forensic, architect, etc.)
        +-- search/
            +-- __init__.py ------- RAG subsystem (placeholder)
```

---

## 8. Data Flow Diagram

```
USER QUERY
    |
    v
[1] intent_parser.analyze_query()
    |  -> QueryProfile (intent, complexity, scope, keywords)
    |
    v
[2] semantic_finder.semantic_match()
    |  -> SemanticMatch (targets, suggested files/sets, flow type)
    |  reads: semantic_index.json (LRU cached)
    |
    v
[3] tier_orchestrator.route_query()
    |  uses: QueryProfile + SemanticMatch
    |  consults: ROUTING_MATRIX, CEREBRAS_TRIGGERS, FLASH_DEEP_TRIGGERS
    |  -> RoutingDecision (tier, sets, fallback, reasoning)
    |
    v
[4] SET SANITIZATION (sanitize_sets)
    |  alias mapping -> validation -> dedup -> cap at 5
    |
    v
[5] TIER EXECUTION (dispatched by analyze.py)
    |
    +--[INSTANT]-------> context_builder.answer_from_truths()
    |                    reads: repo_truths.yaml
    |
    +--[CEREBRAS]------> Cerebras fast inference (3000 t/s)
    |
    +--[RAG]-----------> File Search API (indexed stores)
    |
    +--[LONG_CONTEXT]--> LongContextExecutor.execute()
    |                    uses: analyze/context.py -> build context
    |                    uses: analyze/clients.py -> Gemini API
    |
    +--[PERPLEXITY]----> perplexity_research.py -> Sonar Pro API
    |
    +--[FLASH_DEEP]----> repopack.format_repopack()
    |                    + context_cache.CacheRegistry
    |                    -> Gemini 2.0 Flash (2M context)
    |
    +--[HYBRID]--------> LONG_CONTEXT + PERPLEXITY combined
    |
    v
[6] feedback_store.log_aci_query()
    |  writes: aci_feedback.yaml
    |
    v
[7] OUTPUT -> AnalyzeResult (Stone Tool contract)
    |  includes: context manifest, answer, citations, cost, timing
    |
    v
[OPTIONAL] research_orchestrator.execute()
    |  runs multiple [3-7] cycles with different configs
    |  applies synthesis strategy (consensus, dialectic, etc.)
    |  -> CompositeResult
```

---

## 9. Key Design Patterns

### 9.1 Lazy Configuration Loading
Both `intent_parser.py` and `context_builder.py` use `_get_config()` with lazy `from . import ACI_CONFIG` to avoid circular imports at module load time. Config is loaded once in `__init__.py` and shared.

### 9.2 Tier Fallback Chain
Every tier has a defined fallback: INSTANT -> CEREBRAS -> RAG -> LONG_CONTEXT -> FLASH_DEEP -> (end). Perplexity falls back to LONG_CONTEXT. This ensures graceful degradation.

### 9.3 Set Sanitization Pipeline
Raw sets from semantic matcher go through: alias mapping (`SET_ALIASES`) -> validation against `analysis_sets.yaml` keys -> deduplication -> cap at 5. This prevents invalid sets from crowding out valid ones.

### 9.4 Laminar vs Turbulent Context Flow
When semantic matching produces coherent results (single purpose, adjacent layers), the flow is "laminar" and semantic sets take priority. Mixed results produce "turbulent" flow where profile-based sets take priority. This controls context ordering.

### 9.5 Waybill Architecture (Refinery)
Every `RefineryNode` carries a `waybill` dict tracking its processing lineage: parcel_id, parent_id, route (events with timestamps and agent info). Enables provenance tracking through the atomization pipeline.

### 9.6 Attention Gate (Refinery)
The `_apply_attention_gate()` method boosts chunk relevance based on `compute_semantic_distance()` to the query's semantic targets. Laminar flow uses strict thresholds; turbulent flow uses broader retention.

### 9.7 Research Schemas (Orchestrator)
Predefined YAML schemas orchestrate multiple ACI runs (different models, tiers, sets) and synthesize results. Six synthesis strategies: consensus, quality_gradient, dialectic, triangulation, bayesian, hierarchical.

---

## 10. Environment Variables

| Variable | Module | Purpose |
|----------|--------|---------|
| `GEMINI_API_KEY` | `clients.py` | API key for AI Studio backend |
| `GEMINI_BACKEND` | `config.py` | "vertex" or "aistudio" |
| `NEO4J_URI` | `neo4j_publisher.py` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j_publisher.py` | Neo4j username |
| `NEO4J_PASSWORD` | `neo4j_publisher.py` | Neo4j password |
| `PROJECT_ROOT` | `feedback_store.py` | Override project root detection |
| `SESSION_LOG` | `session.py` | Enable stderr session logging (=1) |
| `ANTIGRAVITY_AGENT` | `config.py` | Disable interactive mode (=1) |
| `CI` | `config.py` | CI environment detection (=true) |
| `NONINTERACTIVE` | `config.py` | Force non-interactive (=true) |

---

## 11. Connection to Refinery Layer

The Refinery is ACI's atomization engine. Data flows through it as follows:

1. **Input:** Raw files (Python, Markdown, YAML, generic) enter via `Refinery.process_file()`.
2. **Chunking:** Type-specific chunkers (`PythonChunker`, `MarkdownChunker`, `YamlChunker`, `GenericChunker`) split files into semantic units.
3. **Context depth filtering:** Chunks are filtered by `context_depth` setting (shallow: only classes/h1-h2; medium: no constants/variables; deep: all).
4. **Relevance scoring:** `_score_relevance()` assigns 0.0-1.0 scores based on type, length, docstrings, type hints.
5. **Attention gating:** `_apply_attention_gate()` boosts/suppresses scores based on semantic distance to query targets.
6. **Embedding (optional):** `EmbeddingEngine` generates 384-dim MiniLM vectors for semantic search.
7. **Waybill stamping:** Each chunk gets a `waybill` with parcel_id, parent_id, and processing route.
8. **Output routes:**
   - **JSON export:** `export_to_json()` with atomic write and validation.
   - **Neo4j publication:** `Neo4jPublisher.publish_atoms()` creates graph nodes with Atom/Parcel/Batch relationships.
   - **In-memory cache:** `_chunk_cache` dict for repeated access.
   - **Token-budgeted selection:** `compact_for_context()` greedily selects by relevance within budget.

---

## 12. Module Counts

| Category | Count |
|----------|-------|
| ACI core modules | 10 (intent_parser, tier_orchestrator, semantic_finder, context_builder, refinery, research_orchestrator, context_cache, feedback_store, temporal_resolver, repopack) |
| ACI support | 2 (schema, neo4j_publisher) |
| Analyze modules | 6 (config, clients, context, output, session, + tiers/modes/search packages) |
| Config files | 5 (aci_config, research_schemas, analysis_sets, prompts, semantic_models) |
| Data files | 6 (semantic_index, repo_truths, cache_registry, aci_feedback, chunks, session logs) |
| Total Python files | ~22 |
| Estimated total LOC | ~5,500 (excluding analyze.py monolith at ~4,000 lines) |
