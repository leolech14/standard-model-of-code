# 05 - Configuration and Data Layer Map

> Maps every config file and data directory that the Wave AI toolkit depends on.
> Generated: 2026-02-07

---

## CONFIG MAP

### 1. `wave/config/prompts.yaml` -- Prompt Templates and Backend Config

| Aspect | Detail |
|--------|--------|
| **Purpose** | Master prompt library + LLM backend/model config + pricing table |
| **Consumers** | `analyze.py` (primary), `analyze/config.py`, `analyze/modes/__init__.py` |
| **Key sections** | `analysis_prompts.insights`, `insights_source`, `plan_validation`, `role_validation`, `task_assessment`, `modes.*` |
| **Backend** | `backend: "aistudio"` (default) or `"vertex"` (enterprise GCP) |
| **Default model** | `gemini-3-pro-preview` (flagship), `gemini-2.0-flash-001` (fast) |
| **Fallback chain** | gemini-3-pro-preview -> gemini-2.5-pro -> gemini-3-flash-preview -> gemini-2.0-flash-001 |
| **Pricing** | Per-1M-token rates for 6 models (input/output, long-context surcharges) |
| **Modes** | `standard`, `forensic` (requires file:line citations), `architect` (theory-grounded), `interactive` |
| **Required env** | `GEMINI_API_KEY` (AI Studio) or `gcloud auth` (Vertex) |

### 2. `wave/config/analysis_sets.yaml` -- Context Window Composition

| Aspect | Detail |
|--------|--------|
| **Purpose** | Defines named "analysis sets" -- glob-based slices of the codebase for AI context injection |
| **Consumers** | `analyze.py`, `aci/tier_orchestrator.py`, `aci/context_builder.py`, `boundary_mapper.py`, `maintenance/analyze_sets.py` |
| **Total sets** | ~38 named sets across 7 categories |
| **Categories** | Box sets (archive, repo_docs, repo_theory, repo_tool), Micro-sets (constraints, viz_core, theory, schema), Composed sets (pipeline, classifiers, architecture_review, implementation_review), Filtered sets (brain_active, recent_30d, recent_7d, docs_active), Agent sets (deck, agent_session, agent_kernel, agent_tasks, agent_intelligence, agent_specs, agent_full), ACI sets (aci_core, aci_siblings, aci_audit), Research sets |
| **Key features** | `max_tokens` budget per set, `includes` for composition, `critical_files` + `positional_strategy` for attention engineering ("sandwich" or "front-load"), `filters` for temporal/size exclusion |
| **Recommendations** | Maps question patterns (e.g. "how does * work") to suggested sets |
| **Defaults** | No default set; user must specify via `--set` flag |

### 3. `wave/config/analysis_sets_v2.yaml` -- Filtered Sets Extension

| Aspect | Detail |
|--------|--------|
| **Purpose** | Extends v1 with smart filtering: exclude patterns, recency, size, confidence scoring |
| **Status** | Partially implemented (phase 1 filters work; `min_confidence` is NOT_IMPLEMENTED) |
| **Filter types** | `exclude_patterns` (glob), `max_age_days` (temporal), `max_file_size_kb`, `sort_by`, `limit`, `min_confidence` (future) |
| **Key sets** | `brain_active` (90-day, no archive), `recent_30d`, `recent_7d`, `docs_small`, `high_confidence` (future) |

### 4. `wave/config/aci_config.yaml` -- Adaptive Context Intelligence

| Aspect | Detail |
|--------|--------|
| **Purpose** | Controls ACI tier routing, intent detection, token budgets, agent context injection, evidence protocol |
| **Consumers** | `aci/__init__.py` (module-level load), `aci/tier_orchestrator.py`, `aci/intent_parser.py`, `aci/context_builder.py`, `research/precision_fetcher.py` |
| **Tiers** | `instant` (<100ms, cached truths), `rag` (<5s, file search), `long_context` (<60s, full reasoning), `perplexity` (<30s, web research) |
| **Token budgets** | guru=50K, architect=150K, archeologist=200K, hard_cap=200K |
| **Intent keywords** | architecture, debug, research, task -- supplements `intent_parser.py` |
| **Agent injection** | Trigger keywords -> levels (minimal/standard/full) -> injects agent context sets |
| **External indicators** | "best practice", "latest", "2026", "state of the art" etc. -- routes to Perplexity |
| **Feedback** | Stores to `.agent/intelligence/aci_feedback.yaml`, max 1000 entries |
| **Evidence protocol** | Requires file:line citations in AI responses |
| **Research config** | Perplexity sonar-pro, $5/month budget, 1-week cache TTL |

### 5. `wave/config/semantic_models.yaml` -- Truth Definitions (HSL)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Defines the "Map" (documentation) that the "Territory" (code) must match. Core of the Holographic-Socratic Layer. |
| **Consumers** | `analyze.py`, `drift_guard.py`, `continuous_cartographer.py`, `refine_context_loop.py` |
| **Concordances** | Pipeline (Stage, PipelineManager, CodebaseState, Extractor), Theory (Atom, Dimension), Architecture (Tool) |
| **Invariants** | Each concept has `description`, `role`, `invariants` (rules), `anchors` (file:pattern bindings) |
| **Antimatter Laws** | AM001 (Context Myopia), AM002 (Architectural Drift), AM003 (Supply Chain Hallucination), AM004 (Orphan Code) |

### 6. `wave/config/research_schemas.yaml` -- Multi-Run Research Orchestration

| Aspect | Detail |
|--------|--------|
| **Purpose** | Defines reusable research patterns that orchestrate multiple ACI queries with different configs |
| **Consumer** | `aci/research_orchestrator.py` |
| **Schemas** | `validation_trio`, `depth_ladder`, `adversarial_pair`, `forensic_investigation`, `confidence_calibration`, `semantic_probe`, `claude_history_ingest`, `mind_map_builder`, `theoretical_discussion`, `communication_fabric`, `quick_validate`, `foundations`, `perplexity_optimized`, `deterministic_implementation` |
| **Synthesis strategies** | consensus, quality_gradient, dialectic, triangulation, bayesian, hierarchical |
| **Run types** | `internal` (repo context), `external` (web/Perplexity -- membrane enforced) |
| **Guardrails** | max 1M tokens/run, 2M tokens/schema, 10 runs/schema, 30 req/min, $1 cost alert |
| **Defaults** | gemini-3-pro-preview, long_context tier, temp=0.2, 100K budget |

### 7. `wave/config/refinery_config.yaml` -- Refinery Pipeline Parameters

| Aspect | Detail |
|--------|--------|
| **Purpose** | Controls the Refinery context-processing pipeline |
| **Consumer** | `refinery/pipeline.py` |
| **Key settings** | `context_depth` (shallow/medium/deep), `attention_mode` (laminar/turbulent), thresholds (0.6 high, 0.3 low) |
| **Outputs** | Publishes to Neo4j, GCS, generates reports |
| **Pipeline query** | Configurable "attention mechanism signal" -- the driving question |

### 8. `wave/config/documentation_map.yaml` -- Holographic Index

| Aspect | Detail |
|--------|--------|
| **Purpose** | Maps documentation files to semantic concepts for drift detection |
| **Consumer** | `ops/verify_symmetry.py` |
| **Structure** | Each doc file -> `covers` (concepts), `validates_against` (code files), `critical` flag |
| **Validation** | Critical docs validated on-change, standard docs daily; minimum 1 anchor, line numbers required |

### 9. `wave/config/query_manifest_schema.yaml` -- Query Record Format

| Aspect | Detail |
|--------|--------|
| **Purpose** | Canonical schema for recording AI query metadata (model, context, metrics, quality, result) |
| **Storage** | gemini/perplexity/claude docs directories, `.agent/intelligence/query_logs/` |
| **Key fields** | model config, context injection details, token metrics, quality scores (confidence/completeness/specificity), result takeaway, implications |
| **Pricing** | Reference pricing for gemini-2.0-flash, gemini-3-pro-preview, sonar-pro |

### 10. `wave/config/insights_schema.json` -- AI Insights Output Schema

| Aspect | Detail |
|--------|--------|
| **Purpose** | JSON Schema for structured output from AI analysis of Collider results |
| **Consumer** | `analyze.py` (validates insight responses) |
| **Sections** | meta, executive_summary, patterns_detected, refactoring_opportunities, topology_analysis, rpbl_interpretation, domain_insights, risk_areas |

### 11. `wave/config/docling_config.yaml` -- Document Processing Config

| Aspect | Detail |
|--------|--------|
| **Purpose** | Batch processing of academic PDFs via Docling-Granite |
| **Consumer** | `docling_processor/config.py` |
| **Key settings** | OCR on/off, table extraction, fallback strategies, chunking (512 tokens, 50 overlap), 4 OMP threads |
| **Paths** | Input: `wave/library/references/pdf`, Output: `wave/library/references/docling_output` |

### 12. `wave/config/docling_gpu_profiles.yaml` -- GPU Acceleration Profiles

| Aspect | Detail |
|--------|--------|
| **Purpose** | Pre-configured profiles for different GPU hardware (CPU, Apple Silicon, RTX 3090-5090, A100) |
| **Consumer** | `docling_processor/` (via DOCLING_GPU_PROFILE env var) |

### 13. `wave/config/docling_kubernetes.yaml` -- K8s Deployment Manifests

| Aspect | Detail |
|--------|--------|
| **Purpose** | Production Kubernetes deployment for Docling Serve (CPU + GPU variants) |
| **Not consumed** | Reference/deployment spec only |

### 14. `wave/config/registries/DOMAINS.yaml` -- Code-Context Symmetry

| Aspect | Detail |
|--------|--------|
| **Purpose** | Tracks Codome/Contextome symmetry for each domain (Pipeline, Refinery, Viz, Atoms, Governance, AI_Tools) |
| **Consumer** | Governance/audit tools |
| **Tracks** | code paths, entrypoints, context paths, registries, health checks, known drift |

### 15. `wave/config/registries/REFINERY_INTERNAL.yaml` -- Refinery Subsystem Registry

| Aspect | Detail |
|--------|--------|
| **Purpose** | Internal registry of Refinery subsystems (scanner, chunker, indexer, querier, synthesizer, reporter, reference_analyzer) |
| **Status tracking** | Lines of code, last modified, healthy/unhealthy, issues, deprecated subsystems |

### 16. `wave/tools/archive/config.yaml` -- Cloud Archive Config

| Aspect | Detail |
|--------|--------|
| **Purpose** | GCS archive bucket settings for large file offloading |
| **Consumer** | `archive/archive.py` |
| **Bucket** | `gs://elements-archive-2026` (ARCHIVE class = $0.0012/GB/month) |
| **Account** | leonardolech3@gmail.com |

### 17. `wave/tools/docsintel/providers.yaml` -- Documentation Provider Registry

| Aspect | Detail |
|--------|--------|
| **Purpose** | Registry of external documentation sources (MCP servers, self-indexed, future custom RAG) |
| **Layers** | Pre-indexed (context7, anthropic_docs, aws), Self-indexed (docs-mcp-server), Custom RAG (future) |

### 18. `wave/registry/SERVICE_REGISTRY.yaml` -- Runtime Service Health

| Aspect | Detail |
|--------|--------|
| **Purpose** | Tracks live service status (daemons, cloud integrations, API providers, pipelines) |
| **Services** | HSL daemon, GCS archive, Neo4j, Gemini, Cerebras, Perplexity, HuggingFace, Refinery pipeline |

---

## SECRET MANAGEMENT: DOPPLER

Doppler is the secret management layer. It is NOT configured in YAML -- it is called at runtime.

| Secret | Doppler project | Consumers |
|--------|----------------|-----------|
| `GEMINI_API_KEY` | ai-tools/dev | `analyze.py`, `analyze/clients.py` |
| `CEREBRAS_API_KEY` | ai-tools/dev | `cerebras_spiral_intel.py`, `cerebras_doc_validator.py` |
| `PERPLEXITY_API_KEY` | ai-tools/dev | `perplexity_research.py`, `perplexity_mcp_server.py` |
| `HF_TOKEN` | ai-tools/dev | `hf_space.py`, `hf_spaces.py` |

**Fallback chain**: env var -> Doppler CLI (`doppler secrets get KEY --plain`) -> error.

**Doppler lookup**: `_find_doppler()` searches PATH, `~/.local/bin/doppler`, `/usr/local/bin/doppler`, `/opt/homebrew/bin/doppler`.

---

## DATA DIRECTORY MAP

### `wave/data/` -- Primary Data Store (~95 MB total)

| Directory/File | Format | Size | Writers | Readers | Purpose |
|---------------|--------|------|---------|---------|---------|
| `unified_analysis.json` | JSON | 27 MB | Collider (particle) | `analyze.py`, enrichment tools | Full Collider output for the repo |
| `project_elements_file_timestamps.csv` | CSV | 7.2 MB | Timestamp scanner | Analysis tools | File modification timestamps for recency filtering |
| `collider_runs/` | JSON+HTML | ~51 MB (7 files) | Collider | `analyze.py`, comparison tools | Historical Collider run outputs (3 HTML, 3 LLM-JSON, 1 unified) |
| `enriched/enriched_latest.json` | JSON | 385 KB | `cerebras_spiral_intel.py` | `analyze.py`, intelligence | AI-enriched node data (latest snapshot) |
| `tags/tags_latest.json` | JSON | 329 KB | Tag extraction tools | Analysis, query tools | Extracted code tags |
| `tags/validation_prompt.txt` | Text | 7.6 KB | Manual/generated | Validation tools | Prompt for tag validation |
| `repo_map/repo_map_latest.json` | JSON | 1.2 MB | Repo mapper | Dashboards, analysis | Repository structure map |
| `repo_map/analysis_latest.json` | JSON | 1.8 KB | Analysis tools | Dashboards | Latest analysis metadata |
| `repo_map/processing_plan.json` | JSON | 1.8 KB | Repo mapper | Pipeline tools | Current processing plan |
| `intel/unified_intel.json` | JSON | 46 KB | Intelligence pipeline | ACI, query tools | Consolidated intelligence data |
| `intel/file_intel_cache.json` | JSON | 49 KB | `cerebras_spiral_intel.py` | Analysis tools | Cached file-level intelligence |
| `intel/semantic_index.json` | JSON | 17 KB | Indexer | Query/search tools | Semantic search index |
| `intel/context_latest.md` | Markdown | 22 KB | Context builder | AI tools, dashboards | Latest context snapshot |
| `intel/spiral/file_intel.json` | JSON | 11 MB | `cerebras_spiral_intel.py` | Intelligence tools | Detailed per-file intelligence from Cerebras |
| `intel/spiral/spiral_state.json` | JSON | 683 B | Spiral processor | Spiral processor | Processing state/checkpoint |
| `intel/zoo_comparisons/` | JSON+YAML | ~398 KB | Comparison tools | Research, analysis | SWEBOK comparison data |
| `cerebras_queue/queue.json` | JSON | 636 B | Cerebras queue manager | Cerebras workers | Pending Cerebras inference jobs |
| `cerebras_queue/results/` | JSON | ~583 B | Cerebras workers | Queue manager | Completed inference results |
| `cerebras_hire/hire_state.json` | JSON | 106 B | Cerebras hiring tool | Cerebras tools | Hiring/scaling state |
| `file_formats/` | JSON | ~35 KB | Format classifier | Analysis, validation | File format taxonomy + metadata schema |
| `.archive_20260131/` | JSON | ~18 files | Archive rotation | Historical reference | Timestamped snapshots of enriched, repo_map, tags |

### `wave/intelligence/` -- Runtime Intelligence Store (~5+ MB active, growing)

| File/Directory | Format | Size | Writers | Readers | Purpose |
|---------------|--------|------|---------|---------|---------|
| `corpus_inventory.json` | JSON | 2.9 MB | `refinery/corpus_inventory.py` | Synthesizer, ACI | Full file inventory |
| `boundaries.json` | JSON | 104 KB | `boundary_mapper.py` | ACI context builder | Set boundary definitions |
| `delta_state.json` | JSON | 271 KB | Delta detector | Synthesizer, watcher | Change tracking state |
| `delta_report.json` | JSON | 5 KB | Delta detector | Reporter, dashboards | Latest change report |
| `atoms/atoms_body.json` | JSON | 159 KB | Atom generator | ACI, graph tools | Codome atoms |
| `atoms/atoms_brain.json` | JSON | 206 KB | Atom generator | ACI, graph tools | Contextome atoms |
| `state/live.yaml` | YAML | 1.6 KB | `state_synthesizer.py` | ACI, dashboards | Consolidated project state |
| `socratic_audit_*.json` | JSON | ~15 KB each, 100+ files | Socratic daemon | Audit review, drift | Hourly audit results (continuous) |
| `logs/` | JSON | 30+ files | Various tools | Debugging | Execution logs |
| `drift_guard_state.json` | JSON | 306 B | `drift_guard.py` | Drift guard | Last drift check |
| `hsl_daemon_state.json` | JSON | 303 B | HSL daemon | Health checks | Daemon state |
| `cache_registry.json` | JSON | 930 B | Cache manager | Cache tools | Gemini cache registry |
| `chunks/` | (empty) | 0 | Refinery chunker | ACI | Not yet populated |

---

## DATA FLOW DIAGRAM

```
                            SECRET MANAGEMENT
                         Doppler (ai-tools/dev)
                    GEMINI_API_KEY, CEREBRAS_API_KEY,
                    PERPLEXITY_API_KEY, HF_TOKEN
                                |
                                v
   +---------------------------------------------------------+
   |                   CONFIG LAYER                          |
   |                                                         |
   |  prompts.yaml -----> analyze.py (prompts, backend,     |
   |                       model selection, pricing)         |
   |                                                         |
   |  analysis_sets.yaml -> analyze.py, ACI, boundary_mapper |
   |                        (context window composition)     |
   |                                                         |
   |  aci_config.yaml ----> ACI module (tier routing,       |
   |                        intent detection, budgets)       |
   |                                                         |
   |  semantic_models.yaml -> drift_guard, analyze.py       |
   |                          (truth definitions, anchors)   |
   |                                                         |
   |  research_schemas.yaml -> research_orchestrator        |
   |                           (multi-run research patterns) |
   |                                                         |
   |  refinery_config.yaml --> refinery/pipeline.py         |
   |                           (pipeline parameters)         |
   |                                                         |
   |  documentation_map.yaml -> ops/verify_symmetry.py      |
   |                            (drift detection)            |
   +---------------------------------------------------------+
                                |
                                v
   +---------------------------------------------------------+
   |                   TOOL LAYER                            |
   |                                                         |
   |  analyze.py ---------> Gemini API (via AI Studio/Vertex)|
   |  cerebras_*.py ------> Cerebras API (3000 t/s)         |
   |  perplexity_research -> Perplexity sonar-pro           |
   |  hf_space.py --------> HuggingFace Spaces              |
   |  drift_guard.py -----> semantic_models.yaml validation  |
   |  refinery/pipeline ---> corpus processing               |
   |  archive/archive.py --> GCS (gs://elements-archive-2026)|
   +---------------------------------------------------------+
                                |
                                v
   +---------------------------------------------------------+
   |                   DATA LAYER                            |
   |                                                         |
   |  wave/data/                                             |
   |    unified_analysis.json  <-- Collider output (27 MB)   |
   |    collider_runs/         <-- Historical runs (51 MB)   |
   |    enriched/              <-- AI-enriched nodes (385K)  |
   |    tags/                  <-- Code tags (329K)          |
   |    repo_map/              <-- Repo structure (1.2 MB)   |
   |    intel/                 <-- Intelligence cache (11 MB)|
   |    cerebras_queue/        <-- Job queue (<1 KB)         |
   |                                                         |
   |  wave/intelligence/                                     |
   |    corpus_inventory.json  <-- File inventory (2.9 MB)   |
   |    boundaries.json        <-- Set boundaries (104 KB)   |
   |    atoms/                 <-- Generated atoms (365 KB)  |
   |    state/live.yaml        <-- Project state (1.6 KB)    |
   |    socratic_audit_*.json  <-- Hourly audits (~1.5 MB+)  |
   |    delta_*.json           <-- Change tracking (276 KB)  |
   |                                                         |
   |  External:                                              |
   |    GCS bucket             <-- Large file archive         |
   |    Neo4j                  <-- Graph database (optional)  |
   +---------------------------------------------------------+
```

---

## DATA FLOW: READ/WRITE MATRIX

```
Writer Tool               --> Output File                --> Reader Tool
========================      ==========================     ========================
Collider (particle)           data/unified_analysis.json     analyze.py, enrichment
cerebras_spiral_intel.py      data/enriched/latest.json      analyze.py, intelligence
cerebras_spiral_intel.py      data/intel/spiral/file_intel   intelligence pipeline
Tag extractor                 data/tags/tags_latest.json     analysis, query
Repo mapper                   data/repo_map/latest.json      dashboards, analysis
corpus_inventory.py           intelligence/corpus_inv.json   synthesizer, ACI
boundary_mapper.py            intelligence/boundaries.json   ACI context builder
state_synthesizer.py          intelligence/state/live.yaml   ACI, dashboards
Socratic daemon (sentinel)    intelligence/socratic_audit_*  audit review, drift
atom_generator                intelligence/atoms/*.json      ACI, graph tools
delta_detector                intelligence/delta_*.json      reporter, watcher
drift_guard.py                intelligence/drift_guard.json  drift guard
archive.py                    GCS bucket + manifests         query, restore
refinery/pipeline.py          intelligence/chunks/ (future)  ACI, search
```

---

## CRITICAL CONFIGURATION DEPENDENCIES

1. **analyze.py** depends on THREE config files simultaneously:
   - `prompts.yaml` (prompt templates + backend + model + pricing)
   - `analysis_sets.yaml` (context composition)
   - `semantic_models.yaml` (truth definitions)

2. **ACI module** loads `aci_config.yaml` at **module import time** (not lazy):
   - `wave/tools/ai/aci/__init__.py` line 34 loads config on first import
   - All ACI submodules inherit this config

3. **research_orchestrator.py** depends on:
   - `research_schemas.yaml` (schema definitions)
   - `analysis_sets.yaml` (via ACI for set resolution)
   - `aci_config.yaml` (via ACI for tier routing)

4. **Socratic audit** (runs hourly via sentinel) depends on:
   - `semantic_models.yaml` (truth definitions)
   - `documentation_map.yaml` (file -> concept mappings)
   - Writes to `intelligence/socratic_audit_pipeline_*.json` (100+ files, growing)

5. **Doppler** is a hard dependency for all API-consuming tools. Without it configured (`doppler setup --project ai-tools --config dev`), tools fall back to env vars or fail.

---

## NOTES

- The `intelligence/` directory grows unboundedly from hourly Socratic audits (~15 KB/hr = ~10 MB/month). Consider rotation.
- `data/collider_runs/` stores 51 MB of historical runs. Only latest is typically needed.
- `data/.archive_20260131/` contains rotated snapshots. Not cleaned automatically.
- `analysis_sets_v2.yaml` extends v1; v2 filtered sets are merged into the v1 config at runtime.
- The `chunks/` directory under intelligence is empty -- Refinery chunks are computed on-the-fly or stored elsewhere.
- Neo4j integration is optional; `refinery_config.yaml` has `publish_to_neo4j: true` but requires running Neo4j.
