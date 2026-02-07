# wave/tools/ai/ -- Unified Architecture Map

**Compiled:** 2026-02-07
**Source:** 7 deep exploration chunks (160KB total)
**Scope:** Complete architectural map of the AI toolkit -- 40+ tools, 6 subsystems, 4 project connections

---

## Executive Summary

The AI toolkit at `wave/tools/ai/` is a **context intelligence platform** organized into 6 subsystems:

| # | Subsystem | Files | Purpose | Key Pattern |
|---|-----------|-------|---------|-------------|
| 1 | **Cerebras Tools** | 8 scripts | Fast inference (3000 t/s) -- sweep, spiral, tag, enrich | Standalone scripts, no shared client |
| 2 | **ACI System** | 12 modules | Query routing + context optimization | "Curriculum Compiler" -- decides what AI gets what context |
| 3 | **Decision Deck** | 4 modules + 26 cards | Constrained action governance | Card game metaphor -- agents pick certified moves |
| 4 | **Support Tools** | 22 scripts | Utilities, bridges, research | Intel aggregator, Perplexity, Gemini, HuggingFace |
| 5 | **Config Layer** | 8 YAML files | Prompts, sets, tiers, models | Attention engineering via positional strategies |
| 6 | **Refinery** | 7 core modules | Context atomization + knowledge serving | RefineryNode is the atom, everything feeds into it |

**Total:** ~40 Python files, ~8 YAML configs, ~26 CARD YAMLs, 38 analysis sets

---

## System Topology

```
                    USER QUERY
                        |
                        v
                  +-----------+
                  | analyze.py|  <-- Main CLI entry point
                  +-----+-----+
                        |
            +-----------+-----------+
            |                       |
            v                       v
     +------+------+        +------+------+
     |  ACI System |        | Cerebras T0 |
     | (Tier 1-4)  |        | (Fast path) |
     +------+------+        +------+------+
            |                       |
    +-------+-------+              |
    |   |   |   |   |              |
    v   v   v   v   v              v
  Intent Tier Semantic Context   cerebras_
  Parser Orch Finder  Builder   rapid_intel
    |     |     |       |
    v     v     v       v
  Query  Route Match   Load    +----------+
  Profile Decide Files  Optimize-->| Refinery |
                                +-----+----+
                                      |
                                      v
                                RefineryNodes
                                (atomic chunks)
                                      |
                            +---------+---------+
                            |         |         |
                            v         v         v
                         Search    Cache    Publish
                         (local)  (Gemini)  (Neo4j)
```

### Data Flow Summary

```
Code Repo --> Collider --> unified_analysis.json
                              |
                     +--------+--------+
                     |                 |
              cerebras_enricher   insights_generator
                     |                 |
              enriched_analysis   ai_insights.json
                     |
              cerebras_rapid_intel (sweep)
                     |
              semantic_index.json --> semantic_finder
                                          |
                                    Refinery (atomize)
                                          |
                                    RefineryNode[]
                                          |
                              +-----------+-----------+
                              |           |           |
                        context_builder  cache     neo4j_pub
                              |
                        Optimized Context Window
                              |
                        AI Model (Gemini/Cerebras/Perplexity)
```

---

## Subsystem 1: Cerebras Tools (8 files)

**Location:** `wave/tools/ai/cerebras_*.py`
**Shared Pattern:** Each file independently implements Cerebras API calls, rate limiting, and CLI. No shared client module (acknowledged debt in `CONSOLIDATION_2026.yaml`).

| File | Lines | Purpose | CLI Commands |
|------|-------|---------|-------------|
| `cerebras_rapid_intel.py` | 920 | Full codebase sweep | `sweep`, `gaps`, `context`, `stats`, `integrate` |
| `cerebras_spiral_intel.py` | 1081 | Multi-pass refinement (P1-P5) | `run`, `status`, `export` |
| `cerebras_tagger.py` | 680 | D1-D8 dimensional tagging | `tag`, `report`, `export` |
| `cerebras_enricher.py` | 785 | Semantic enrichment of Collider output | `enrich`, `export`, `status` |
| `cerebras_zoo_compare.py` | 540 | Multi-model comparison testing | `compare`, `report` |
| `cerebras_doc_validator.py` | 450 | Theory document validation | `validate`, `report` |
| `cerebras_queue.py` | 380 | Queue-based batch processing | `enqueue`, `run`, `status` |
| `cerebras_hire.py` | 290 | Agent spawning coordinator | `hire`, `status` |

**Key Data Flows:**
- `rapid_intel` --> `semantic_index.json` --> `aci/semantic_finder.py`
- `enricher` --> `enriched_analysis.json` --> `rapid_intel.integrate_with_enriched()`
- `spiral_intel` --> `spiral_state.json` --> standalone (no ACI integration yet)
- `tagger` --> `tagged_files.json` --> `enricher` (dimensional enrichment)

**Architectural Debt:**
- No shared `CerebrasClient` -- each file reimplements API calls
- `cerebras_queue.py` and `cerebras_hire.py` appear unused (no external imports)
- Rate limiter duplicated 8 times (150ms interval)

---

## Subsystem 2: ACI System (12 modules)

**Location:** `wave/tools/ai/aci/`
**Metaphor:** "Curriculum Compiler" -- prepares optimal context before AI answers queries

### Module Map

| Module | Purpose | Key Export |
|--------|---------|-----------|
| `__init__.py` | Package orchestrator, config loader | `analyze_and_route()` |
| `schema.py` | RefineryNode dataclass (the atom) | `RefineryNode` |
| `intent_parser.py` | Query classification (intent/complexity/scope) | `analyze_query()` |
| `tier_orchestrator.py` | Route to execution tier | `route_query()` |
| `semantic_finder.py` | Map to Standard Model semantic space | `semantic_match()` |
| `context_builder.py` | Build optimized context window | `build_context()` |
| `context_cache.py` | Gemini cached context management | `get_or_create_cache()` |
| `refinery.py` | File atomization into RefineryNodes | `Refinery.process()` |
| `feedback_store.py` | Query logging for learning | `log_query()` |
| `research_orchestrator.py` | Multi-config query execution | `run_research()` |
| `temporal_resolver.py` | Git-based conflict resolution | `resolve_canonical()` |
| `repopack.py` | Deterministic repo formatter | `pack_repo()` |

### Execution Tiers

| Tier | Latency | Backend | Use Case |
|------|---------|---------|----------|
| INSTANT | <100ms | Cached truths | Simple factual lookups |
| CEREBRAS | <2s | Cerebras API | Fast semantic queries |
| RAG | <5s | Local file search | Code-specific questions |
| LONG_CONTEXT | <60s | Gemini (full reasoning) | Complex architectural analysis |
| PERPLEXITY | <30s | Perplexity Sonar | External/web research |
| FLASH_DEEP | <15s | Gemini Flash | Deep but fast |
| HYBRID | varies | Multiple | Multi-source synthesis |

### Intent Classification (9 types)

`ARCHITECTURE`, `DEBUG`, `RESEARCH`, `VALIDATE`, `TASK`, `COUNT`, `LOCATE`, `EXPLAIN`, `IMPLEMENT`

### Routing Matrix

```
(intent, complexity, scope) --> Tier
  ARCHITECTURE + COMPLEX + INTERNAL --> LONG_CONTEXT
  DEBUG + SIMPLE + INTERNAL --> RAG
  RESEARCH + any + EXTERNAL --> PERPLEXITY
  TASK + SIMPLE + INTERNAL --> CEREBRAS
  ... (full matrix in tier_orchestrator.py)
```

---

## Subsystem 3: Decision Deck (4 modules + 26 cards)

**Location:** `wave/tools/ai/deck/`
**Metaphor:** Card game -- agents pick certified moves instead of free-form improvisation

### Modules

| Module | Role | Key Class |
|--------|------|-----------|
| `deck_router.py` | Game Master -- loads cards, routes intents, deals hands | `DeckRouter`, `Card` |
| `play_card.py` | Executor -- runs card steps with checkpoints | `CardPlayer` |
| `deck_context.py` | ACI bridge -- injects context for deck queries | `DeckContextBuilder` |
| `fabric_bridge.py` | System health -- checks fabric state for preconditions | `FabricBridge` |

### Cards (26 total)

**9 Handcrafted:**

| Card ID | Title | Phase |
|---------|-------|-------|
| CARD-ANA-001 | Run Collider Analysis | EXECUTE |
| CARD-AUD-001 | Skeptical Audit | VERIFY |
| CARD-DOC-001 | Write Specification | BUILD |
| CARD-GIT-001 | Commit Checkpoint | SAVE |
| CARD-RES-001 | Research with Perplexity | RESEARCH |
| CARD-RES-002 | Research with Gemini | RESEARCH |
| CARD-SES-001 | Start Session | BOOT |
| CARD-SYS-001 | System Config Audit | MAINTAIN |
| CARD-WLD-000 | Wildcard (escape hatch) | any |

**15 Auto-generated (OPP cards):** CARD-OPP-059 through CARD-OPP-084

**2 Reserved:** CARD-TST-001, CARD-TST-002 (testing)

### Meters System

5 gauges that track cumulative agent state:

| Meter | Range | Meaning |
|-------|-------|---------|
| `focus` | 0-100 | Task coherence |
| `reliability` | 0-100 | Trust in outputs |
| `discovery` | 0-100 | Learning progress |
| `debt` | 0-100 | Accumulated shortcuts |
| `readiness` | 0-100 | System preparation |

Cards declare `meter_effects` that shift these gauges.

---

## Subsystem 4: Support Tools (22 files)

**Location:** `wave/tools/ai/` (top-level, non-Cerebras/ACI/Deck)

### Core Utilities

| Tool | Purpose |
|------|---------|
| `intel.py` | Unified context provider ("narrator's voice") -- aggregates meters, cards, truths, session |
| `context_filters.py` | Smart file filtering (recency, size, confidence) |
| `token_estimator.py` | Token counting for context budget management |
| `industrial_ui.py` | Terminal UI rendering (progress bars, tables) |
| `boundary_analyzer.py` | Validates architectural boundary alignment |
| `boundary_mapper.py` | Maps analysis sets to declared boundaries |

### Research Tools

| Tool | Backend | Purpose |
|------|---------|---------|
| `perplexity_research.py` | Perplexity Sonar | Web research with citations |
| `research/precision_fetcher.py` | Perplexity API | Focused query fetching |
| `research/loop.py` | Multi-round | Iterative research refinement |

### Bridges

| Tool | Connects |
|------|----------|
| `laboratory_bridge.py` | wave/ <-> particle/ (Collider Laboratory facade) |
| `insights_generator.py` | Collider output <-> Gemini analysis |
| `gemini_status.py` | Gemini API health and session tracking |

### HuggingFace Integration

| Tool | Purpose |
|------|---------|
| `hf_query.py` | Search HuggingFace Hub for models/datasets |
| `hf_eval.py` | Evaluate model performance benchmarks |

---

## Subsystem 5: Configuration Layer (8 YAML files)

**Location:** `wave/config/`

| Config | Purpose | Consumers |
|--------|---------|-----------|
| `prompts.yaml` | Master prompt library + model/pricing config | `analyze.py`, `analyze/config.py` |
| `analysis_sets.yaml` | 38 named context sets (glob-based file slices) | ACI, analyze.py, boundary tools |
| `analysis_sets_v2.yaml` | Smart filtering extension (recency, size) | `context_filters.py` |
| `aci_config.yaml` | Tier routing, token budgets, agent injection | All ACI modules |
| `semantic_models.yaml` | Truth definitions (HSL: Hypotheses, Specifications, Laws) | `intel.py`, Deck cards |
| `refinery_config.yaml` | Chunk sizes, overlap, embedding settings | `aci/refinery.py` |
| `CONSOLIDATION_2026.yaml` | Tech debt tracker (pending tasks) | Meta-documentation |
| `cards_registry.yaml` | Card catalog and metadata | `deck_router.py` |

### Attention Engineering

`analysis_sets.yaml` implements attention engineering for AI models:
- **Positional strategies:** `sandwich` (critical at start+end), `front-load` (critical first)
- **Token budgets:** Per-set caps (e.g., `brain: 50000`, `architecture_review: 150000`)
- **Critical files:** Priority files loaded first regardless of glob order
- **Temporal filters:** `recent_30d`, `recent_7d` for recency-biased analysis

---

## Subsystem 6: Refinery (The Central Nervous System)

**Location:** `wave/tools/ai/aci/refinery.py` + `aci/schema.py` + `aci/refinery/publishers/`

### The Atom: RefineryNode

```python
@dataclass
class RefineryNode:
    content: str              # The chunk text
    source_file: str          # Origin file path
    chunk_id: str             # SHA256-based ID (16 hex)
    chunk_type: str           # function, class, h1, yaml_key, etc.
    relevance_score: float    # 0.0-1.0 heuristic
    start_line: int           # Source line range
    end_line: int
    metadata: Dict            # file_type, layer, role
    created_at: float         # Unix timestamp
    embedding: List[float]    # 384-dim MiniLM vector
    waybill: Dict             # Logistics: parcel_id, parent_id, route
```

### Pipeline Stages

```
Raw File --> Language-Aware Chunker --> RefineryNodes[]
                                           |
                    +-----+-----+-----+----+----+
                    |     |     |     |         |
                 Relevance Embedding Waybill  Metadata
                 Scoring   (MiniLM)  Assign   Enrich
                    |     |     |     |         |
                    +-----+-----+-----+---------+
                                |
                          Processed Nodes
                                |
                    +-----------+-----------+
                    |           |           |
                 context_    context_    neo4j_
                 builder     cache      publisher
```

### Language-Aware Chunking

The Refinery chunks by language-specific boundaries:
- **Python:** function/class definitions, import blocks
- **JavaScript/TypeScript:** function/class/export blocks
- **Markdown:** heading sections (h1, h2, h3)
- **YAML:** top-level keys
- **Generic:** Sliding window with overlap

### Evolution Path

```
L6 Package (inside Elements) --> L7 System (independent) --> L8 Platform (universal)
```

Current state: **L6 transitioning to L7**. The Refinery Platform (`wave/experiments/refinery-platform/`) is the first L7 manifestation.

---

## Cross-Project Connections

### Direct Integration

```
PROJECT_elements (Host)
├── Collider --> unified_analysis.json --> AI Toolkit
├── particle/ schema --> semantic_finder dimensions (D1-D8)
├── Refinery Platform --> visualizes RefineryNodes
└── Standard Model --> classification framework for all tools

PROJECT_openclaw (Runtime Engine)
├── Skills --> governed by Decision Deck cards
├── VPS deployment target for MCP servers (future)
└── Trust tiers --> map to Deck preconditions

PROJECT_atman (Data Viz)
├── Planned consumer of Refinery chunks
├── Agent orchestration --> will use Deck governance
└── Data visualization of analysis outputs

PROJECT_sentinel (Automations)
├── Monitors AI toolkit health
└── Scheduled Cerebras sweeps (planned)

PROJECT_central-mcp (Archaeological Source)
├── MCP integration patterns --> inform MCP wrapping
├── Agent coordination patterns --> inform Deck design
└── Quality scoring --> maps to Refinery relevance scores
```

### Zero Direct Code Imports

All cross-project connections are via:
1. **Data files** (JSON/YAML exchange)
2. **CLI invocation** (subprocess calls)
3. **Config references** (path conventions)
4. **Shared concepts** (Standard Model types, dimensions, scales)

No project imports Python modules from another project directly. This is both a strength (loose coupling) and a limitation (no shared type system).

---

## MCP Wrapping Readiness

### Planned 3-Server Architecture

| Server | Tools | Source |
|--------|-------|--------|
| `cerebras-intelligence-mcp` | 12-15 | cerebras_*.py + perplexity_research |
| `adaptive-context-intelligence-mcp` | 10-12 | aci/ + analyze.py + intel.py |
| `decision-automation-mcp` | 10-12 | deck/ + token_estimator + gemini_status |

### Wrapping Challenges

1. **No shared client** -- Each Cerebras tool reimplements API calls; MCP wrapper needs unified client
2. **File-based coupling** -- Tools read/write `wave/data/` files; MCP tools need data passing
3. **CLI-oriented design** -- argparse CLIs need function extraction for `@mcp.tool()` decoration
4. **Long-running ops** -- Spiral analysis (5-pass) needs MCP Tasks primitive
5. **Large outputs** -- Sweep results exceed 10KB; need pagination/resource URIs
6. **Session state** -- ACI caching needs per-session isolation

### Quick Wins (wrap today)

| Tool | Complexity | Reason |
|------|-----------|--------|
| `cerebras_rapid_intel.py` (sweep) | Medium | Pure function, JSON output |
| `cerebras_tagger.py` (tag) | Low | Single file in, tags out |
| `perplexity_research.py` | Low | Query in, markdown out |
| `token_estimator.py` | Trivial | Pure utility function |
| `intel.py` (get_context) | Low | Returns formatted string |

---

## Dependency Graph (Simplified)

```
analyze.py (CLI entry)
    |
    +-- aci/intent_parser     (classifies query)
    +-- aci/tier_orchestrator  (routes to tier)
    |       +-- aci/semantic_finder  (semantic space mapping)
    +-- aci/context_builder    (builds context window)
    |       +-- aci/refinery         (atomizes files)
    |       |       +-- aci/schema   (RefineryNode dataclass)
    |       +-- aci/context_cache    (Gemini cache)
    +-- aci/feedback_store     (logs queries)
    +-- aci/research_orchestrator  (multi-config execution)
    |
    +-- cerebras_rapid_intel   (Tier 0.5 fast path)
    +-- perplexity_research    (Tier PERPLEXITY)
    +-- intel.py               (agent context injection)
    +-- deck/deck_router       (card governance)
    |       +-- deck/play_card
    |       +-- deck/deck_context
    |       +-- deck/fabric_bridge
    +-- insights_generator     (Collider -> Gemini bridge)
    +-- laboratory_bridge      (wave -> particle bridge)
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Python files | ~40 |
| Total YAML configs | ~8 |
| Total CARD definitions | 26 |
| Total analysis sets | 38 |
| Lines of Python (est.) | ~15,000 |
| External APIs | 4 (Cerebras, Gemini, Perplexity, HuggingFace) |
| Data directories | 5 (intel/, enriched/, research/, tags/, spiral/) |
| Execution tiers | 7 (INSTANT through HYBRID) |
| Query intents | 9 |
| SMoC dimensions | 8 (D1-D8) |
| RefineryNode embedding dims | 384 (MiniLM) |

---

## Reading Order

For understanding this system, read in this order:

1. **Chunk 06** (Refinery) -- The core data model and pipeline
2. **Chunk 02** (ACI System) -- The routing and context intelligence
3. **Chunk 01** (Cerebras Tools) -- The fast inference layer
4. **Chunk 05** (Config/Data) -- The configuration that controls behavior
5. **Chunk 03** (Decision Deck) -- The governance layer
6. **Chunk 04** (Support Tools) -- The utility belt
7. **Chunk 07** (Cross-Project) -- How it all connects outward

---

*Compiled from 7 exploration chunks. Each chunk contains file-by-file analysis with function signatures, data flows, and connection maps. See `.research/chunks/` for full details.*
