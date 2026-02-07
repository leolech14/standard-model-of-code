# 01 - Cerebras Tools: Architecture & Dependency Map

**Scope:** 8 files in `wave/tools/ai/cerebras_*.py`
**Date:** 2026-02-07
**Model:** Claude Opus 4.6

---

## Overview

The Cerebras toolkit is a suite of 8 standalone Python scripts that leverage the Cerebras inference API (3000 tokens/sec via `llama-3.3-70b`) for fast codebase intelligence operations. They share no common base module -- each file independently implements its own Cerebras client, rate limiter, and API key retrieval. This is an explicit architectural debt acknowledged in `CONSOLIDATION_2026.yaml` (task: "Extract Cerebras client from cerebras_enricher.py for reuse").

All files share the same structural pattern:
- `PROJECT_ROOT = Path(__file__).parent.parent.parent.parent` (resolves to repo root)
- Direct `requests.post()` to `https://api.cerebras.ai/v1/chat/completions`
- API key from `CEREBRAS_API_KEY` env var, fallback to Doppler secrets
- Default model: `llama-3.3-70b` (overridable via `CEREBRAS_MODEL` env var)
- CLI via `argparse` subcommands
- JSON/dataclass output to `wave/data/` subdirectories

---

## File-by-File Analysis

### 1. cerebras_rapid_intel.py (920 lines)

**Purpose:** Full-codebase intelligence sweep -- scans all files, analyzes each with Cerebras, detects gaps, generates reports, and exports a semantic index.

**Key Functions/Classes:**
| Name | Type | Description |
|------|------|-------------|
| `FileIntel` | dataclass | Per-file intelligence record (purpose, summary, concepts, deps, gaps, quality) |
| `GapReport` | dataclass | Detected gap with type, severity, suggested fix |
| `IntelReport` | dataclass | Aggregate report with findings and metrics |
| `cerebras_query()` | function | Single API call with rate limiting (0.15s interval) |
| `cerebras_batch()` | function | Parallel prompt execution via ThreadPoolExecutor |
| `scan_files()` | function | Recursive file scanner with extension/directory filters |
| `analyze_file()` | function | Analyze one file, parse JSON response |
| `analyze_batch()` | function | Analyze many files with MD5 hash-based caching |
| `detect_gaps()` | function | Heuristic gap detection from intel data |
| `integrate_with_enriched()` | function | Merge rapid intel with enricher output |
| `export_for_semantic_finder()` | function | Export index for `aci/semantic_finder.py` |

**CLI Commands:** `sweep`, `gaps`, `context <path>`, `stats`, `integrate`

**Data Written:**
- `wave/data/intel/file_intel_cache.json` -- per-file analysis cache
- `wave/data/intel/reports/gaps_*.md` -- gap reports
- `wave/data/intel/reports/summary_*.json` -- summary reports
- `wave/data/intel/unified_intel.json` -- merged with enricher data
- `wave/data/intel/semantic_index.json` -- exported for semantic_finder

**Internal Dependencies:** None (standalone)

**Exported To:**
- `analyze.py` imports `cerebras_query`, `cerebras_batch` for Tier 0.5 fast queries
- `aci/semantic_finder.py` reads `semantic_index.json` output file
- `aci/tier_orchestrator.py` routes queries to Cerebras tier based on triggers

**Refinery Connection:** `integrate_with_enriched()` merges with `wave/data/enriched/enriched_latest.json` (from cerebras_enricher). The unified output feeds into the Refinery pipeline via the semantic index.

---

### 2. cerebras_spiral_intel.py (1081 lines)

**Purpose:** Multi-pass iterative refinement engine -- runs 5 successive passes (P1-P5) each building on previous results, spiraling upward in confidence. Registered as TOOL-SPIRAL-001 (REG-014).

**Key Functions/Classes:**
| Name | Type | Description |
|------|------|-------------|
| `PassLevel` | Enum | P1_SURFACE through P5_UNIFIED |
| `Confidence4D` | dataclass | 4-axis confidence: factual, alignment, current, onwards |
| `FileIntel` | dataclass | Extended version with `pass_history`, `dependents`, `confidence` dict |
| `SubsystemIntel` | dataclass | Group-level intelligence (P4+) |
| `LapStats` | dataclass | Per-pass metrics: duration, rate, confidence delta, gaps closed |
| `SpiralState` | dataclass | Overall state tracking with lap history |
| `SpiralEngine` | class | Main engine: manages state, cache, and pass execution |
| `run_pass_1()` | method | Sequential surface scan |
| `run_pass_1_parallel()` | method | Parallel surface scan (up to 20 workers) |
| `run_pass_2()` | method | Gap filling with neighbor context |
| `run_pass_3()` | method | Dependency graph validation |

**CLI Commands:** `spiral [--parallel -w N]`, `pass --level N`, `status`, `laps`, `export`

**Data Written:**
- `wave/data/intel/spiral/file_intel.json` -- per-file intelligence
- `wave/data/intel/spiral/spiral_state.json` -- state + lap statistics
- `wave/data/intel/spiral/unified_model.json` -- export output

**Internal Dependencies:** None (standalone, but overlaps significantly with rapid_intel)

**Exported To:** Referenced in `REGISTRY_OF_REGISTRIES.yaml` (REG-014), `TOOLS_REGISTRY.yaml`

**Key Differences from rapid_intel:** Spiral has the `Confidence4D` model, multi-pass architecture, `LapStats` telemetry, and `SpiralEngine` class. Rapid intel is flat single-pass with integration hooks.

---

### 3. cerebras_tagger.py (456 lines)

**Purpose:** Batch D1-D8 dimension classification of code files using the Standard Model taxonomy. Tags every file with 8 structural dimensions (WHAT, LAYER, ROLE, BOUNDARY, STATE, EFFECT, LIFECYCLE, TRUST).

**Key Functions/Classes:**
| Name | Type | Description |
|------|------|-------------|
| `DIMENSIONS` | dict | Complete D1-D8 enumeration with all valid values |
| `FileTag` | dataclass | Classification result with all 8 dimensions + confidence |
| `classify_file_cerebras()` | function | Classify one file with retry logic (up to 5 retries, exponential backoff) |
| `collect_files()` | function | Glob-based file collector with exclusions |
| `cmd_tag()` | function | Batch tagging with progress and cost estimation |
| `cmd_validate()` | function | Generate Claude validation prompt for sampled tags |
| `cmd_stats()` | function | Distribution statistics per dimension |

**CLI Commands:** `tag [--pattern --path --limit]`, `validate [--sample]`, `stats`, `pipeline`

**Data Written:**
- `wave/data/tags/tags_*.json` -- timestamped tag results
- `wave/data/tags/tags_latest.json` -- latest run
- `wave/data/tags/validation_prompt.txt` -- prompt for Claude cross-validation

**Internal Dependencies:** None (standalone)

**Exported To:** Referenced in `repo_mapper.py` (TODO: integrate execution), `TOOLS_REGISTRY.yaml`

**Notable:** Validation step generates a prompt for Claude (manual paste) rather than calling Claude API directly. This is a deliberate Cerebras-first, Claude-second workflow.

---

### 4. cerebras_enricher.py (520 lines)

**Purpose:** Semantic enrichment layer on top of Collider AST output. Collider provides structure (atoms, edges, dimensions); the enricher adds meaning (purpose, tags, complexity, quality hints, relationships).

**Key Functions/Classes:**
| Name | Type | Description |
|------|------|-------------|
| `MODELS` | dict | 6 available Cerebras models with RPM limits and quality ratings |
| `EnrichedNode` | dataclass | Combined Collider structure + Cerebras semantics |
| `call_cerebras()` | function | API call with 5-retry exponential backoff |
| `build_combined_prompt()` | function | Single comprehensive prompt extracting 7 attributes per file |
| `enrich_node()` | function | Enrich one Collider node (1 API call per file) |
| `load_collider_output()` | function | Load `unified_analysis.json` from Collider |
| `get_file_nodes()` | function | Extract file-level nodes from Collider graph |
| `cmd_enrich()` | function | Full enrichment pipeline with ETA tracking |
| `cmd_quick()` | function | Quick single-file enrichment |

**CLI Commands:** `enrich <collider_output> [--source --limit --model]`, `quick <path>`

**Data Written:**
- `wave/data/enriched/enriched_*.json` -- timestamped enrichment
- `wave/data/enriched/enriched_latest.json` -- latest run

**Data Read:**
- Collider output: `.collider/unified_analysis.json` (input)

**Internal Dependencies:** None (standalone)

**Exported To:**
- `cerebras_rapid_intel.py` reads `enriched_latest.json` in `integrate_with_enriched()`
- Referenced in `TOOLS_REGISTRY.yaml`, `CONSOLIDATION_2026.yaml`

**Refinery Connection:** Enriched output is the primary bridge between Collider (particle) and the AI intelligence layer (wave). The enriched nodes feed into the Refinery pipeline.

---

### 5. cerebras_queue.py (407 lines)

**Purpose:** Centralized file-based request queue to prevent rate limit chaos when multiple agents hit Cerebras simultaneously. Uses file locking (`fcntl`) for coordination.

**Key Functions/Classes:**
| Name | Type | Description |
|------|------|-------------|
| `QueueItem` | dataclass | Request with id, prompt, status, result |
| `QueueLock` | class | Context manager using `fcntl.LOCK_EX` for exclusive file lock |
| `submit_request()` | function | Add request to queue, return ID |
| `get_result()` | function | Poll for result (blocking or non-blocking) |
| `cerebras_call()` | function | Actual API call (used by worker) |
| `process_queue()` | function | Worker loop: dequeue, process, save results |
| `query_sync()` | function | Submit-and-wait synchronous API |
| `get_queue_status()` | function | Queue metrics |

**CLI Commands:** `submit <prompt>`, `get <id>`, `worker`, `status`, `query <prompt>`

**Data Written:**
- `wave/data/cerebras_queue/queue.json` -- pending/processing items
- `wave/data/cerebras_queue/results/*.json` -- per-request results
- `wave/data/cerebras_queue/.queue.lock` -- file lock

**Internal Dependencies:** None (standalone)

**Exported To:** Designed for programmatic import (`from cerebras_queue import query_sync`), but no actual imports found in the codebase.

**Platform Note:** Uses `fcntl` which is Unix-only (macOS/Linux). Will not work on Windows.

---

### 6. cerebras_hire.py (343 lines)

**Purpose:** Exclusive access control (mutex) for the Cerebras API. Ensures only one agent/consumer uses Cerebras at a time. Uses file-based state with PID tracking and auto-expiry.

**Key Functions/Classes:**
| Name | Type | Description |
|------|------|-------------|
| `HireState` | dataclass | Lock state: consumer, timestamps, PID |
| `try_hire()` | function | Non-blocking hire attempt |
| `do_hire()` | function | Blocking hire with poll interval |
| `do_release()` | function | Release with ownership check |
| `force_release()` | function | Emergency override |
| `is_expired()` | function | TTL check on hire |
| `is_process_alive()` | function | PID liveness check via `os.kill(pid, 0)` |
| `hire_cerebras()` | context manager | `with hire_cerebras("agent", 600): ...` |
| `get_status()` | function | Current hire status |

**CLI Commands:** `status`, `hire --consumer <name> --duration <sec>`, `release`, `force-release`

**Data Written:**
- `wave/data/cerebras_hire/hire_state.json` -- current lock state
- `wave/data/cerebras_hire/cerebras.lock` -- file lock

**Internal Dependencies:** None (standalone)

**Exported To:** Designed for import (`from cerebras_hire import hire_cerebras`). Referenced in `cerebras_rapid_intel.py` error message ("Consider using hire mechanism").

**Design:** Complementary to `cerebras_queue.py` -- hire is coarse-grained (one agent at a time), queue is fine-grained (request-level coordination). Both address the same problem (7 req/sec shared limit) with different granularity.

---

### 7. cerebras_zoo_compare.py (476 lines)

**Purpose:** Compare external knowledge documents (SWEBOK, etc.) against the CODE_ZOO taxonomy (167 atoms, 33 roles, 16 levels). Identifies matches, gaps, enhancements, and conflicts.

**Key Functions/Classes:**
| Name | Type | Description |
|------|------|-------------|
| `CODE_ZOO_SYSTEM_PROMPT` | str | Expert persona prompt with full taxonomy context |
| `ComparisonResult` | dataclass | Per-chunk: matches, gaps, enhancements, conflicts |
| `cerebras_complete()` | function | API call with system/user messages |
| `chunk_text()` | function | Split documents by chapter/word count |
| `compare_chunk_to_zoo()` | function | Compare one chunk, parse YAML response |
| `run_comparison()` | function | Full document comparison pipeline |
| `cmd_swebok()` | function | SWEBOK-specific comparison preset |
| `cmd_interactive()` | function | Interactive comparison mode |

**CLI Commands:** `swebok`, `compare <file>`, `interactive`

**Data Read:**
- `particle/docs/theory/CODE_ZOO.md` -- the taxonomy definition
- `wave/archive/references/swebok/swebok-v4-clean.txt` -- SWEBOK V4 text

**Data Written:**
- `wave/data/intel/zoo_comparisons/swebok_comparison.json`
- `wave/data/intel/zoo_comparisons/swebok_comparison.yaml`

**External Dependency:** `pyyaml` (for YAML parsing/output)

**Internal Dependencies:** None (standalone)

**Exported To:** Referenced in TASK-101 and batch consolidation plans.

---

### 8. cerebras_doc_validator.py (211 lines)

**Purpose:** Validates documentation for overclaiming language (e.g., "we discovered", "universal law", "PROOF"). Enforces the shift from "scientific discovery" framing to "practical reference model" framing.

**Key Functions/Classes:**
| Name | Type | Description |
|------|------|-------------|
| `VALIDATION_PROMPT` | str | Detailed overclaiming detection prompt with categories |
| `get_api_key()` | function | Key retrieval (env + Doppler fallback) |
| `call_cerebras()` | function | Simple API call |
| `validate_file()` | function | Validate one .md file, parse JSON result |
| `main()` | function | CLI: validate files/directories |

**CLI Commands:** `validate <path> [--output]`

**Data Read:** Any `.md` files in specified path

**Data Written:**
- `.agent/intelligence/OVERCLAIMING_AUDIT_REPORT.json` (default output)

**Internal Dependencies:** None (standalone)

**Exported To:** Not imported elsewhere. Used as standalone audit tool.

---

## Dependency Graph

```
EXTERNAL CONSUMERS                    CEREBRAS TOOLS                    DATA LAYER
==================                    ==============                    ==========

analyze.py ----imports----> cerebras_rapid_intel.py ----writes---> wave/data/intel/
  (cerebras_query,            |                                     file_intel_cache.json
   cerebras_batch)            |                                     semantic_index.json
                              |---reads-------> enriched_latest.json  unified_intel.json
                              |                 (from enricher)       reports/gaps_*.md
                              |                                       reports/summary_*.json
                              v
aci/semantic_finder.py       (reads semantic_index.json at runtime)
  (file-based coupling)

aci/tier_orchestrator.py     (routes queries to Cerebras tier -- no direct import)


                             cerebras_spiral_intel.py --writes---> wave/data/intel/spiral/
                              (standalone, parallel to rapid_intel)   file_intel.json
                                                                     spiral_state.json
                                                                     unified_model.json

                             cerebras_enricher.py ------writes---> wave/data/enriched/
                              |                                     enriched_latest.json
                              |---reads-------> .collider/unified_analysis.json
                              |                 (Collider output)
                              v
                             (enriched output consumed by rapid_intel.integrate)

                             cerebras_tagger.py --------writes---> wave/data/tags/
                              (standalone)                          tags_latest.json

repo_mapper.py               (references tagger, no import -- TODO)

                             cerebras_queue.py ---------writes---> wave/data/cerebras_queue/
                              (standalone worker)                   queue.json
                                                                    results/*.json

                             cerebras_hire.py ----------writes---> wave/data/cerebras_hire/
                              (standalone mutex)                    hire_state.json

                             cerebras_zoo_compare.py ---writes---> wave/data/intel/zoo_comparisons/
                              |                                     swebok_comparison.json
                              |---reads-------> particle/docs/theory/CODE_ZOO.md
                              |---reads-------> wave/archive/references/swebok/

                             cerebras_doc_validator.py --writes---> .agent/intelligence/
                              (standalone audit)                    OVERCLAIMING_AUDIT_REPORT.json
```

### Simplified Dependency Flow

```
Collider (particle)
    |
    v
cerebras_enricher.py  -----> enriched_latest.json
    |                              |
    |                              v
    |                  cerebras_rapid_intel.py  -----> semantic_index.json
    |                       |         |                      |
    |                       |         v                      v
    |                       |    analyze.py          aci/semantic_finder.py
    |                       |    (imports funcs)     (reads file)
    |                       v
    |              aci/tier_orchestrator.py
    |              (routes to Cerebras tier)
    |
    |--- cerebras_spiral_intel.py (parallel intelligence path)
    |
    |--- cerebras_tagger.py (D1-D8 classification)
    |
    |--- cerebras_zoo_compare.py (CODE_ZOO validation)
    |
    |--- cerebras_doc_validator.py (documentation audit)
    |
    +--- cerebras_queue.py + cerebras_hire.py (coordination layer)
```

---

## Configuration Dependencies

| Config | Used By | Notes |
|--------|---------|-------|
| `CEREBRAS_API_KEY` env var | ALL 8 files | Fallback: Doppler secrets |
| `CEREBRAS_MODEL` env var | ALL 8 files | Default: `llama-3.3-70b` |
| Doppler project `ai-tools` | tagger only | Explicit `--project ai-tools --config dev` |
| `wave/config/analysis_sets.yaml` | analyze.py (consumer) | Not Cerebras-specific |
| `particle/docs/theory/CODE_ZOO.md` | zoo_compare only | Taxonomy source |

---

## API Details

| Parameter | Value |
|-----------|-------|
| Endpoint | `https://api.cerebras.ai/v1/chat/completions` |
| Default Model | `llama-3.3-70b` |
| Available Models | `llama-3.3-70b`, `llama3.1-8b`, `qwen-3-32b`, `gpt-oss-120b`, `zai-glm-4.7`, `qwen-3-235b-a22b-instruct-2507` |
| Rate Limit (safe) | ~7 req/sec (0.15s interval) |
| Rate Limit (paid) | ~50 req/sec (0.02s in spiral_intel) |
| Burst Limit | 3,000 RPM / 4M tokens/min |
| Auth | Bearer token via `Authorization` header |
| Temperature | 0.1-0.3 (low for deterministic output) |

---

## Architectural Observations

1. **No shared client.** Every file reimplements `get_cerebras_key()`, rate limiting, and HTTP calls. This is the #1 consolidation target.

2. **Two intelligence paths.** `rapid_intel` (flat, integration-focused) and `spiral_intel` (multi-pass, confidence-focused) do similar work with different strategies. They write to different directories and do not interact.

3. **File-based coupling.** The main integration pattern is file I/O: enricher writes JSON, rapid_intel reads it. No Python imports between Cerebras tools (except self-references in docstrings). The only real import chain is `analyze.py -> cerebras_rapid_intel.py`.

4. **Queue and Hire are unused.** Neither `cerebras_queue.py` nor `cerebras_hire.py` is actually imported by any other file. They solve a real problem (multi-agent rate limit coordination) but are not wired into the toolkit.

5. **Refinery bridge.** The path from raw code to Refinery is: `Collider -> enricher -> rapid_intel.integrate -> semantic_index -> semantic_finder -> analyze.py`. The enricher is the critical bridge between particle (structure) and wave (intelligence).

6. **Registry presence.** All tools are registered in `TOOLS_REGISTRY.yaml` and `REGISTRY_OF_REGISTRIES.yaml`. Spiral intel has a formal tool ID (TOOL-SPIRAL-001, REG-014).

---

## Data Directory Summary

```
wave/data/
  intel/
    file_intel_cache.json       (rapid_intel)
    semantic_index.json         (rapid_intel export)
    unified_intel.json          (rapid_intel + enricher merge)
    reports/                    (rapid_intel)
      gaps_*.md
      summary_*.json
    spiral/                     (spiral_intel)
      file_intel.json
      spiral_state.json
      unified_model.json
    zoo_comparisons/            (zoo_compare)
      swebok_comparison.json
      swebok_comparison.yaml
  enriched/                     (enricher)
    enriched_latest.json
    enriched_*.json
  tags/                         (tagger)
    tags_latest.json
    tags_*.json
    validation_prompt.txt
  cerebras_queue/               (queue)
    queue.json
    results/*.json
  cerebras_hire/                (hire)
    hire_state.json
    cerebras.lock
```
