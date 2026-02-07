# Chunk 04: Support & Utility Tools

> Mapping of every tool in `wave/tools/ai/` that is NOT part of Cerebras, ACI, or Decision Deck systems.

---

## 1. intel.py -- Unified AI Subsystem Query Interface

**Purpose:** Central context provider ("the narrator's voice") that aggregates system state into structured payloads for any AI agent. Supplies meters, cards, truths, session info, and alerts in configurable context sets.

**Key Functions/Classes:**
- `get_context(set_name, include, format)` -- main API; returns formatted context string
- `get_minimal()` / `get_deck()` / `get_session()` / `get_truths_context()` / `get_full()` -- predefined context sets
- `get_custom(include)` -- build-your-own context from component list
- `load_meters()` / `load_recent_plays()` / `load_available_cards()` / `load_truths()` / `load_session()`
- `get_health()` / `get_alerts()`
- Formatters: `format_yaml`, `format_json`, `format_oneline`

**Internal Imports:** None (self-contained).

**External APIs/Services:** None.

**Data Files Read:**
- `.agent/state/meters.yaml`
- `.agent/state/play_log.yaml`
- `.agent/intelligence/truths/repo_truths.yaml`
- `.agent/state/session.yaml`
- `wave/tools/ai/deck/CARD-*.yaml` (card directory scan)

**Configuration Dependencies:** File paths hardcoded relative to PROJECT_ROOT.

**Connection to Higher Systems:** Feeds context to **analyze.py** (via import or CLI), **Decision Deck** (reads deck state), and any AI agent needing project awareness.

---

## 2. insights_generator.py -- Collider AI Insights Wrapper

**Purpose:** Simplified CLI wrapper that sends Collider's `unified_analysis.json` output to Vertex AI Gemini for pattern analysis and returns structured `ai_insights.json`.

**Key Functions/Classes:**
- `run_insights(collider_json, output, model)` -- shell out to `analyze.py --mode insights`
- `main()` -- argparse CLI

**Internal Imports:** Delegates to `analyze.py` via subprocess.

**External APIs/Services:** Vertex AI Gemini (via analyze.py). Default model: `gemini-2.0-flash-001`.

**Data Files Read:** Collider's `unified_analysis.json` (user-specified path).

**Data Files Written:** `ai_insights.json` (user-specified or same dir as input).

**Configuration Dependencies:** Requires gcloud auth and Vertex AI API enabled.

**Connection to Higher Systems:** Bridge between **Collider** (Particle) output and **Gemini** analysis.

---

## 3. boundary_analyzer.py -- Internal Organization Validator

**Purpose:** Validates that declared architectural boundaries (CODOME/CONTEXTOME/CONCORDANCES) match actual directory structure. Computes an alignment score and generates actionable recommendations.

**Key Functions/Classes:**
- `BoundaryAnalyzer` class with `analyze()` method orchestrating all checks
- `BoundaryIssue` / `BoundaryReport` dataclasses
- `_analyze_realms()` -- checks PARTICLE/WAVE/OBSERVER realm existence
- `_analyze_concordances()` -- validates code/doc alignment per concordance
- `_find_undeclared_directories()` -- flags orphan directories
- `_find_phantom_declarations()` -- flags paths declared but missing
- `_check_partition_integrity()` -- verifies CODOME/CONTEXTOME disjointness
- `_calculate_score()` -- computes 0-100 alignment score
- `print_report()` / `save_report()`

**Internal Imports:** None (self-contained).

**External APIs/Services:** None (purely filesystem-based).

**Data Files Read:** Scans the entire PROJECT_ROOT directory tree.

**Data Files Written:** `.agent/intelligence/boundary_analysis.json` (with `--save` flag).

**Configuration Dependencies:** Hardcoded realm definitions (`REALMS`), concordance map (`DECLARED_CONCORDANCES`), and expected directories.

**Connection to Higher Systems:** Called by **boot.sh**, **pre-commit hooks**, and **CI pipeline**. Part of the Maintenance Layer.

---

## 4. context_filters.py -- Intelligent File Filtering

**Purpose:** Prevents token quota disasters by filtering file lists before they reach an AI API. Provides exclude-pattern matching, age filtering, size filtering, sorting, and hard caps.

**Key Functions/Classes:**
- `apply_filters(files, filters, base_dir, verbose)` -- main orchestrator applying all filters in order
- `filter_by_exclude_patterns()` -- glob-pattern-based exclusion
- `filter_by_age()` -- mtime-based cutoff (max_age_days)
- `filter_by_size()` -- file-size-based cutoff (max_file_size_kb)
- `sort_files()` -- sort by mtime, size, or path
- `estimate_tokens_fast()` -- quick 1-token-per-4-bytes heuristic
- `validate_filters()` -- input validation

**Internal Imports:** None (self-contained).

**External APIs/Services:** None.

**Data Files Read/Written:** None (operates on file path lists passed in).

**Configuration Dependencies:** Filter config passed as dict at call site. Typically driven by `analysis_sets.yaml`.

**Connection to Higher Systems:** Core utility for **analyze.py** context loading pipeline and **ACI context_builder**.

---

## 5. token_estimator.py -- Token Budget Management

**Purpose:** Accurate token counting BEFORE sending to API. Three tiers of estimation (fast/medium/accurate) with budget enforcement and visual reporting.

**Key Functions/Classes:**
- `estimate_tokens_fast(files)` -- size/4 heuristic (~50% accuracy)
- `estimate_tokens_medium(files)` -- char-count/3.5 (~20% accuracy)
- `estimate_tokens_accurate(files, encoding)` -- tiktoken cl100k_base (~5% accuracy)
- `estimate_tokens_smart(files, max_budget)` -- auto-selects method based on proximity to budget
- `check_budget(files, max_budget, warn_threshold, force)` -- budget enforcement with warnings
- `format_budget_report()` -- visual bar chart report
- `get_file_token_breakdown(files, top_n)` -- per-file token ranking

**Internal Imports:** None.

**External APIs/Services:** None.

**Optional Dependency:** `tiktoken` (graceful fallback to char-based if missing).

**Data Files Read/Written:** None (operates on file path lists passed in).

**Connection to Higher Systems:** Used by **analyze.py** and **ACI** for pre-flight budget checks. Also used by **context_filters.py** (which duplicates the fast estimator).

---

## 6. perplexity_research.py -- External Research Tool

**Purpose:** Executes deep research queries via Perplexity's Sonar API. Auto-saves all research output as timestamped markdown.

**Key Functions/Classes:**
- `research(query, model, timeout)` -- core API call returning content, citations, usage
- `get_api_key()` -- Doppler-first, then env fallback
- `auto_save_research(query, result, model)` -- saves to research directory as markdown
- `main()` -- CLI with model selection, file input, JSON output, no-save option

**Internal Imports:** Optionally imports `industrial_ui` for styled terminal output.

**External APIs/Services:**
- **Perplexity API** (`https://api.perplexity.ai/chat/completions`)
- **Doppler** (secrets management for `PERPLEXITY_API_KEY`)

**Dependencies:** `httpx`

**Data Files Written:** `particle/docs/research/perplexity/<timestamp>_<slug>.md`

**Configuration Dependencies:** Doppler project `ai-tools`, config `dev`.

**Connection to Higher Systems:** Called by **loop.py** as the external research step. Also used by **ACI research_orchestrator** for the Perplexity tier.

---

## 7. gemini_status.py -- Gemini API Status & Diagnostics

**Purpose:** Real-time observability dashboard for Gemini API usage, quota tracking, error diagnosis, and model recommendations. Reads session log files to compute usage statistics.

**Key Functions/Classes:**
- `load_sessions(date_filter)` -- loads session JSON files
- `analyze_usage(sessions)` -- computes per-model call counts, token totals, time-windowed rates
- `diagnose_error(error_text)` -- pattern-matches error strings to known issues
- `recommend_model(stats)` -- suggests switching models based on quota proximity
- `print_status()` / `print_diagnosis()` / `print_recommendations()` -- formatted terminal output
- `get_doppler_key()` -- validates API key availability

**Internal Imports:** None.

**External APIs/Services:** **Doppler** (key validation only). No live Gemini API calls.

**Data Files Read:** `particle/docs/research/gemini/sessions/*.json`

**Configuration Dependencies:** Hardcoded `QUOTAS` dict with model-specific rate limits.

**Connection to Higher Systems:** Monitors **analyze.py** sessions. Complements **ACI** routing decisions.

---

## 8. hf_space.py -- HuggingFace CLI (Chat + Image + Spaces)

**Purpose:** CLI tool providing chat (via HF Inference API), image generation (via FLUX.1 Gradio Space), and generic Gradio Space access.

**Key Functions/Classes:**
- `cmd_chat(prompt, model)` -- LLM chat via HF router (OpenAI-compatible endpoint)
- `cmd_image(prompt, output)` -- FLUX.1-schnell image generation
- `cmd_models()` -- list available chat models
- `cmd_info(space_id)` -- inspect Gradio Space endpoints
- `cmd_call(space_id, api_name, *args)` -- generic Space invocation
- `get_token()` -- HF_TOKEN from env or Doppler

**Internal Imports:** None.

**External APIs/Services:**
- **HuggingFace Inference API** (`https://router.huggingface.co/v1`)
- **HuggingFace Gradio Spaces** (FLUX.1-schnell, any Space)
- **Doppler** for HF_TOKEN

**Dependencies:** `requests`, `gradio_client`

**Data Files Written:** Generated images to user-specified paths.

**Connection to Higher Systems:** Standalone CLI tool. No direct integration with analyze.py or ACI.

---

## 9. hf_spaces.py -- HuggingFace Spaces API (Extended)

**Purpose:** More structured version of hf_space.py with multiple model configs (FLUX, FLUX-dev, SD3.5, Whisper), image generation with size/seed control, and audio transcription.

**Key Functions/Classes:**
- `generate_image(prompt, model, width, height, seed, output)` -- multi-model image generation
- `transcribe_audio(audio_path)` -- Whisper-based audio transcription
- `list_spaces()` -- show available models/spaces
- `get_hf_token()` -- with hardcoded fallback token

**Internal Imports:** None.

**External APIs/Services:**
- **HuggingFace Gradio Spaces** (FLUX.1-schnell, FLUX.1-dev, SD3.5, Whisper)
- **Doppler** for HF_TOKEN

**Dependencies:** `gradio_client`, `huggingface_hub`

**Data Files Written:** Generated images to `/tmp/hf_gen_<timestamp>.webp` or user path.

**Connection to Higher Systems:** Standalone. No ACI/Cerebras/Deck integration.

---

## 10. graph_engine.py -- Natural Language to Neo4j Cypher

**Purpose:** Converts natural language queries about code structure into read-only Cypher queries and executes them against a Neo4j graph database. Uses Gemini for NL-to-Cypher translation.

**Key Functions/Classes:**
- `GraphEngine` class with `__init__(uri, auth, client, model)`
- `nl_to_cypher(user_query)` -- Gemini-powered NL to Cypher translation
- `query(user_query)` -- full pipeline: translate then execute
- `_get_schema_summary()` -- returns Neo4j schema description

**Internal Imports:** None.

**External APIs/Services:**
- **Neo4j** (bolt://localhost:7687 default)
- **Google Gemini** (via `google.genai` client, model `gemini-2.0-flash-001`)

**Dependencies:** `neo4j`, `google-genai`

**Environment Variables:** `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `GEMINI_API_KEY`

**Connection to Higher Systems:** Designed to query Collider graph data stored in Neo4j. Could integrate with **ACI Refinery** Neo4j publisher.

---

## 11. laboratory_bridge.py -- Agent-to-Scientist Bridge

**Purpose:** Stable interface for the Wave (Agent) side to invoke the Particle (Scientist) Laboratory facade. Handles process invocation, result parsing, and error handling without importing Scientist internals.

**Key Functions/Classes:**
- `run_laboratory(repo, unified_analysis, hypothesis, ...)` -- THE stable interface
- `measure_coverage(unified_analysis)` -- convenience wrapper for coverage analysis
- `evaluate_hypothesis(unified_analysis, hypothesis)` -- convenience wrapper for hypothesis evaluation
- `find_smc_root(start)` -- locates particle directory via env or directory walk

**Internal Imports:** None (deliberately avoids importing particle internals).

**External APIs/Services:** None (subprocess to `particle/tools/research/laboratory.py`).

**Data Files Read:** `experiment_result.json` (output of Laboratory run).

**Data Files Written:** Experiment artifacts in `.laboratory_runs_agent/` directory.

**Configuration Dependencies:** `SMC_ROOT` env variable or monorepo structure.

**Connection to Higher Systems:** Key bridge between **Wave** and **Particle**. Invokes Collider and hypothesis evaluation from the agent side.

---

## 12. loop.py -- Gemini+Perplexity Research Validation Workflow

**Purpose:** Orchestrates a multi-step research loop: Gemini formulates the question (optional), Perplexity provides external research, Gemini synthesizes with local context (optional).

**Key Functions/Classes:**
- `run_perplexity(query, model)` -- subprocess to perplexity_research.py
- `run_gemini(prompt, context_set)` -- subprocess to analyze.py
- `main()` -- three modes: direct Perplexity, synthesize, full loop

**Internal Imports:** Delegates to `analyze.py` and `perplexity_research.py` via subprocess.

**External APIs/Services:** Perplexity (indirect) and Gemini (indirect).

**Data Files Read/Written:** None directly (delegates write to perplexity_research.py).

**Connection to Higher Systems:** Composes **analyze.py** and **perplexity_research.py** into a validation workflow.

---

## 13. observe_session.py -- Real-Time Session Observer

**Purpose:** Streams interactive analyze.py chat session logs in real-time using file tail pattern. Supports observing from Claude Code or any non-TTY environment.

**Key Functions/Classes:**
- `tail_session(session_file, follow)` -- reads and follows JSONL session log
- `launch_and_observe(args_list, query)` -- starts analyze.py with PTY and watches output
- `find_latest_session()` -- finds most recent session file
- `list_sessions()` -- displays all available session files
- `format_turn(turn)` -- colorized turn formatting

**Internal Imports:** References `analyze.py` path for launch mode.

**External APIs/Services:** None.

**Data Files Read:** `/tmp/analyze_sessions/session_<PID>.jsonl`

**Connection to Higher Systems:** Observes **analyze.py** interactive sessions.

---

## 14. industrial_ui.py -- Shared Terminal Output Styling

**Purpose:** Consistent ANSI-styled terminal output library used across all AI tools. Provides themed UI classes with headers, sections, progress bars, budget bars, and context injection transparency.

**Key Functions/Classes:**
- `IndustrialUI` (base ABC) -- header, footer, section, item, bullet, progress_bar, stats_row
- `GeminiUI` -- BLUE theme; model_info, token_stats, aci_routing, context_summary
- `PerplexityUI` -- GREEN theme; citations_section, query_info, save_location
- `TriageUI` -- YELLOW theme; grade_distribution, promotable_items, needs_research
- `ContextUI` -- MAGENTA theme; injection_header, files_included/excluded, injections, limiting_factor, budget_bar, query_schema, truncation_warning
- `ThreadUI` -- CYAN theme; thread_header, turn, turns_summary
- `Colors` class -- ANSI escape code constants

**Internal Imports:** None (self-contained).

**External APIs/Services:** None.

**Connection to Higher Systems:** Imported by **analyze.py**, **perplexity_research.py**, and any tool needing styled terminal output. The `ContextUI` class specifically supports **ACI** transparency reporting.

---

## 15. research/precision_fetcher.py -- CCI Gap Resolution

**Purpose:** When the Codome Completeness Index identifies parser blind spots (OUR_FAULT gaps), this module fetches precise technical guidance from Perplexity SONAR-PRO for fixing the gap. Features caching, budget control, and structured JSON responses.

**Key Functions/Classes:**
- `PrecisionContextFetcher` class -- main engine with `resolve_gap(gap)` async method
- `GapProfile` dataclass -- describes what the parser missed
- `ActionableGuidance` dataclass -- structured output (regex, tree-sitter query, edge cases)
- `ResearchResult` dataclass -- wraps guidance with metadata
- `FetcherConfig` -- loads from `wave/config/aci_config.yaml`
- `BudgetController` -- monthly spend tracking ($5/month default)
- `fetch_guidance_for_gap()` / `fetch_guidance_sync()` -- convenience functions

**Internal Imports:** None.

**External APIs/Services:**
- **Perplexity API** (sonar-pro model, low temperature for precision)

**Dependencies:** `httpx`, `yaml`

**Data Files Read:** `wave/config/aci_config.yaml`

**Data Files Written:**
- `.agent/intelligence/external_cache/<hash>.json` (response cache, 1-week TTL)
- `.agent/intelligence/external_cache/usage_tracking.json` (budget tracking)

**Connection to Higher Systems:** Serves the **CCI** (Codome Completeness Index) pipeline. Config loaded from **ACI** config.

---

## 16. Test & Demo Files (Grouped)

### gemini_cache_demo.py
**Purpose:** Demo of Gemini analyzing codebase files directly from GCS without downloading. Shows Vertex AI context caching with GCS URIs.
**APIs:** Vertex AI Gemini, GCS, gcloud CLI.
**Reads:** `tools/archive/config.yaml`

### gemini_genai_test.py
**Purpose:** Test connectivity to Vertex AI Gemini across multiple regions using google-genai SDK. Probes for model availability.
**APIs:** Vertex AI Gemini (multi-region), gcloud CLI.

### gemini_test_simple.py
**Purpose:** Minimal Vertex AI SDK test (vertexai.init + GenerativeModel).
**APIs:** Vertex AI Gemini via vertexai SDK.

### test_vertex_sdk.py
**Purpose:** Tests multiple Gemini model versions via vertexai SDK to find a working one.
**APIs:** Vertex AI via vertexai SDK.

### debug_models.py (list_models.py)
**Purpose:** Lists available Gemini models in the Model Garden via Vertex AI low-level API.
**APIs:** Vertex AI Model Garden Service, gcloud CLI.

### setup_rag.py
**Purpose:** RAG infrastructure setup tool: bundles docs for NotebookLM, checks Discovery Engine API health, guides Agent Builder setup.
**APIs:** Google Cloud Discovery Engine, gcloud CLI.
**Reads:** `wave/tools/archive/config.yaml`
**Writes:** `wave/output/notebooklm_bundle_<timestamp>.zip`

### setup_agent_builder.sh
**Purpose:** Shell script guiding Vertex AI Agent Builder Data Store creation via Console.
**APIs:** gcloud CLI (instructions only).

---

## Utility Map: Which Tools Support Which Systems

```
HIGHER-LEVEL SYSTEM           SUPPORT TOOLS USED
=====================         ==========================================

analyze.py (Core Engine)      context_filters.py    -- file filtering
                              token_estimator.py    -- budget checks
                              industrial_ui.py      -- GeminiUI, ContextUI
                              intel.py              -- deck/session context
                              observe_session.py    -- session monitoring

ACI System                    context_filters.py    -- file filtering
                              token_estimator.py    -- budget pre-flight
                              industrial_ui.py      -- ContextUI transparency
                              precision_fetcher.py  -- gap resolution research
                              perplexity_research.py -- Perplexity tier

Collider (Particle)           insights_generator.py -- AI insights on output
                              laboratory_bridge.py  -- agent-side invocation
                              graph_engine.py       -- Neo4j graph queries

Decision Deck                 intel.py              -- reads deck state

Research Workflows            perplexity_research.py -- external research
                              loop.py               -- Gemini+Perplexity loop
                              precision_fetcher.py  -- CCI gap resolution

Boundary / Maintenance        boundary_analyzer.py  -- org validation

HuggingFace Access            hf_space.py           -- chat, image, spaces CLI
                              hf_spaces.py          -- multi-model generation

Gemini Diagnostics            gemini_status.py      -- quota/error monitoring
                              gemini_cache_demo.py  -- GCS caching demo
                              gemini_genai_test.py  -- connectivity testing
                              test_vertex_sdk.py    -- SDK version testing
                              debug_models.py       -- model discovery

GCP Infrastructure            setup_rag.py          -- RAG/Agent Builder setup
                              setup_agent_builder.sh -- Console guide
```

---

## Dependency Graph (Internal Imports & Subprocess Calls)

```
loop.py ----subprocess----> analyze.py
        ----subprocess----> perplexity_research.py

insights_generator.py ---subprocess----> analyze.py

observe_session.py ---subprocess/pty----> analyze.py

laboratory_bridge.py ---subprocess----> particle/tools/research/laboratory.py

perplexity_research.py ---optional import----> industrial_ui.py

analyze.py ---import----> context_filters.py
           ---import----> token_estimator.py
           ---import----> industrial_ui.py
           ---import----> intel.py

precision_fetcher.py ---reads----> wave/config/aci_config.yaml
```

---

## External Service Dependencies

| Service | Tools Using It |
|---------|---------------|
| **Perplexity API** | perplexity_research.py, precision_fetcher.py |
| **Google Gemini (AI Studio)** | analyze.py, graph_engine.py |
| **Google Vertex AI** | insights_generator.py, gemini_cache_demo.py, gemini_genai_test.py, test_vertex_sdk.py, debug_models.py, setup_rag.py |
| **Neo4j** | graph_engine.py |
| **HuggingFace** | hf_space.py, hf_spaces.py |
| **Doppler** | perplexity_research.py, gemini_status.py, hf_space.py, hf_spaces.py, precision_fetcher.py |
| **GCS (Cloud Storage)** | gemini_cache_demo.py, setup_rag.py |

---

## File Count Summary

| Category | Count | Files |
|----------|-------|-------|
| Core Utilities | 5 | intel, context_filters, token_estimator, industrial_ui, boundary_analyzer |
| Research Tools | 3 | perplexity_research, precision_fetcher, loop |
| Bridge/Integration | 2 | laboratory_bridge, insights_generator |
| Monitoring | 2 | gemini_status, observe_session |
| Graph/DB | 1 | graph_engine |
| HuggingFace | 2 | hf_space, hf_spaces |
| Test/Demo | 5 | gemini_cache_demo, gemini_genai_test, gemini_test_simple, test_vertex_sdk, debug_models |
| Setup/Infra | 2 | setup_rag, setup_agent_builder.sh |
| **Total** | **22** | |
