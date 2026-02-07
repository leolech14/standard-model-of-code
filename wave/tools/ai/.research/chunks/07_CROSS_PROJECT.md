# Cross-Project Map: wave/tools/ai/ Connections

**Date:** 2026-02-07
**Scope:** How the AI toolkit in PROJECT_elements connects to every other project in ~/PROJECTS_all/
**Method:** Full-text search across projects + code-level analysis of imports, paths, and data flows

---

## Connection Summary

```
                         PROJECT_elements (Host)
                               |
                    wave/tools/ai/ (AI Toolkit)
                    /      |       |       \
                   /       |       |        \
    PROJECT_openclaw  PROJECT_atman  PROJECT_sentinel  PROJECT_central-mcp
    (Runtime Engine)  (Data Viz)     (Automations)     (Archaeological Source)
```

**Active connections:** 4 projects
**Direct code imports:** 0 (all connections are via data exchange, CLI invocation, or config references)
**Shared data format:** unified_analysis.json (Collider output)
**Planned but not built:** MCP server wrapping (3-server architecture)

---

## 1. PROJECT_elements (Host Project) -- DEEP INTEGRATION

The AI toolkit lives inside PROJECT_elements and has the deepest integration with its sibling directories.

### 1.1 Collider (particle/ + standard-model-of-code/)

The Collider is the primary data producer that feeds the AI toolkit. The connection is one-directional: Collider produces `unified_analysis.json`, and multiple AI tools consume it.

**Data flow:**
```
Collider (./collider full /repo --output .collider)
    |
    v
unified_analysis.json
    |
    +---> cerebras_enricher.py    (adds semantic layer)
    +---> insights_generator.py   (AI-powered insights)
    +---> laboratory_bridge.py    (experiment runner)
    +---> analyze.py --mode insights  (legacy path)
    +---> CARD-ANA-001.yaml       (Deck card for analysis)
```

**Key files consuming Collider output:**
- `cerebras_enricher.py` -- loads `unified_analysis.json`, enriches nodes with semantic data via Cerebras API. Reads atoms, imports, exports from Collider data. Outputs `enriched_analysis.json`.
- `insights_generator.py` -- reads `unified_analysis.json`, calls Gemini to generate AI insights report.
- `laboratory_bridge.py` -- Wave-to-Particle bridge. Locates the `particle/` directory, calls its Laboratory facade, passes `unified_analysis.json` for coverage analysis and hypothesis generation.

### 1.2 particle/ Directory

Several AI tools read/write to the `particle/` directory tree:

| Tool | particle/ Path | Purpose |
|------|---------------|---------|
| `perplexity_research.py` | `particle/docs/research/perplexity/` | Auto-saves research results |
| `gemini_status.py` | `particle/docs/research/gemini/sessions` | Tracks Gemini sessions |
| `cerebras_zoo_compare.py` | `particle/docs/theory/` | Reads theory docs for validation |
| `cerebras_rapid_intel.py` | `particle/` (root) | Context scanning target |
| `cerebras_doc_validator.py` | `particle/docs/theory/` | Validates theory documents |
| `cerebras_tagger.py` | `particle/src/` | Tags source files semantically |
| `analyze.py` | `particle/docs/MODEL.md`, `particle/src/core/` | Context sets for analysis |

### 1.3 ACI/Semantic Finder and Particle Schema

The `aci/semantic_finder.py` module deeply integrates with the Standard Model of Code:
- Reads `particle.schema.json` role definitions (lines 65, 110)
- Implements `compute_semantic_distance()` operating on particle dimensions (D1-D8)
- `get_upstream_context()` and `get_downstream_context()` traverse particle dependency graphs
- Maps particle roles to semantic categories (167 atom types)

### 1.4 Refinery Platform (wave/experiments/refinery-platform/)

The Refinery Platform is a Next.js dashboard that visualizes chunks produced by `aci/refinery.py`:
- Location: `wave/experiments/refinery-platform/`
- Stack: Next.js 15 with API routes
- Pages: Overview, Projects, Chunks, Search, Activity, Settings
- Data source: chunks from `aci/refinery.py` output directory (`intelligence/chunks/`)

The `aci/refinery.py` module (`CHUNK_REGISTRY_DIR`) points to `PROJECT_elements/intelligence/chunks/` for chunk persistence.

### 1.5 Decision Deck

The deck subsystem (`deck/`) uses Collider operations as card actions:
- `CARD-ANA-001.yaml` -- "Execute full Collider analysis pipeline." Steps include reviewing `unified_analysis.json`.
- `CARD-OPP-076.yaml` -- "Implement collider mcafee CLI command"
- `deck_router.py` -- Routes intent pattern `r"run.*collider"` to `CARD-ANA-001`
- `fabric_bridge.py` -- Classifies "collider" actions alongside "analyze" and "scan"

---

## 2. PROJECT_openclaw (Runtime Engine) -- PLANNED INTEGRATION

OpenClaw is the VPS-based runtime that would consume the AI toolkit as services. The connection is currently at the planning/documentation stage, not code-level.

### 2.1 MCP Server Wrapping (Research Complete, Not Implemented)

The most significant planned connection is wrapping `wave/tools/ai/` as MCP servers consumable by OpenClaw. Research completed on 2026-02-07:

**File:** `PROJECT_openclaw/skills-security/spec/MCP_WRAPPING_RESEARCH_2026-02-07.md`

Proposed 3-server architecture:
```
cerebras-intelligence-mcp     (12-15 tools)
  cerebras_rapid_intel, cerebras_spiral_intel, cerebras_tagger,
  cerebras_enricher, cerebras_queue, perplexity_research

adaptive-context-intelligence-mcp  (10-12 tools)
  analyze.py --aci, aci/refinery.py, intel.py,
  insights_generator.py, boundary_analyzer.py

decision-automation-mcp        (10-12 tools)
  play_card.py + 26 CARD-*.yaml, token_estimator.py,
  gemini_status.py
```

Framework chosen: FastMCP 2.14+ (stdio transport locally, Streamable HTTP for VPS).

### 2.2 Integration Playbook (Recipes Documented)

**File:** `PROJECT_openclaw/docs/guides/INTEGRATION_PLAYBOOK.md`

Defines how OpenClaw would consume:
- `run_collider` skill -- SSH to Mac, run `./collider full` on target repo
- `query_refinery` skill -- SSH to Mac, query refinery-platform via npm
- `open_projectome` skill -- SSH to Mac, launch visualization dashboard

These are OpenClaw custom skills (JavaScript) that SSH to the Mac and invoke the AI toolkit.

### 2.3 Cerebras Model Configuration

**File:** `PROJECT_openclaw/config/openclaw.json`

OpenClaw's model mapper includes Cerebras models (`cerebras/gpt-oss-120b`, `cerebras/qwen-3-235b-a22b-instruct-2507`, `cerebras/zai-glm-4.7`) as fallback providers, matching the same Cerebras API used by the AI toolkit's `cerebras_*.py` tools.

### 2.4 Development Backlog Reference

**File:** `PROJECT_openclaw/docs/DEVELOPMENT_BACKLOG.md`

Top priority item: "Enable Fast Inference (Cerebras)" -- update `openclaw.json` to use `cerebras/*` models, matching the toolkit's Cerebras integration.

### 2.5 Agent Onboarding

**File:** `PROJECT_openclaw/docs/guides/00-start/AGENT_ONBOARDING.md`

Documents `wave/tools/ai/` as the toolkit location for agents, with commands:
```bash
cd ~/PROJECTS_all/PROJECT_elements/wave/tools/ai
python3 cerebras_rapid_intel.py "quick query"
```

---

## 3. PROJECT_atman (Data Viz + Orchestration) -- SHARED CODEBASE

Atman has the most concrete code-level connection to the AI toolkit because it shares the same `analyze.py` codebase (forked/copied).

### 3.1 Shared analyze.py

**File:** `PROJECT_atman/analyze.py`

Atman has its own copy of `analyze.py` that:
- References `collider-pipeline` store names
- Points to `context-management/config/analysis_sets.yaml` and `prompts.yaml`
- Uses the same `--index`, `--search`, `--set`, `--mode` interface
- References `context-management/docs/COLLIDER_ARCHITECTURE.md`
- Stores output at `gs://elements-archive-2026/intelligence` (same GCS bucket)

### 3.2 Registry Cross-References

**File:** `PROJECT_atman/context-management/registry/REGISTRY.json`

The Atman registry explicitly maps to PROJECT_elements source files:
```json
"context-management/tools/ai/analyze.py": {
  "local_path": ".../PROJECT_elements/context-management/tools/ai/analyze.py",
  "cloud_uri": "gs://elements-archive-2026/repository_mirror/latest/context-management/tools/ai/analyze.py"
}
```

This confirms Atman treats Elements' `analyze.py` as canonical source.

### 3.3 Collider AI Insights Proposal

**File:** `PROJECT_atman/context-management/docs/proposals/COLLIDER_AI_INSIGHTS_PROPOSAL.md`

Documented and implemented integration plan for adding `--mode insights` to `analyze.py`, reading `unified_analysis.json` from Collider. Status: IMPLEMENTED. This is a bidirectional connection -- the proposal lives in Atman but modifies the Elements codebase.

### 3.4 Standard Model References

Atman's `_external/standard-model-for-computer-language/` directory contains validation code that works with particles, semantic IDs, and the 8-dimensional classification system -- the same theoretical framework that `aci/semantic_finder.py` uses.

---

## 4. PROJECT_sentinel (Automations) -- OPERATIONAL INTEGRATION

Sentinel manages LaunchAgents that automate AI toolkit execution on file changes.

### 4.1 LaunchAgent: com.elements.refinery-local

**File:** `PROJECT_sentinel/agents/com.elements.refinery-local.plist`

Runs `hsl_daemon.py` from PROJECT_elements with:
- Python: `PROJECT_elements/.tools_venv/bin/python`
- Trigger: WatchPaths on `semantic_models.yaml` and `standard-model-of-code/src/core`
- Working directory: PROJECT_elements root
- PYTHONPATH: standard-model-of-code

This is the "local refinery" -- when Collider source code changes, the daemon processes new chunks.

### 4.2 LaunchAgent: com.elements.socratic-audit

**File:** `PROJECT_sentinel/agents/com.elements.socratic-audit.plist`

Directly invokes `analyze.py` from the AI toolkit:
```
doppler run --project ai-tools --config dev -- python
  .../wave/tools/ai/analyze.py --verify pipeline
  --output .../reports/socratic_audit_latest.md
```

This is a cron-like job that runs architectural validation using the AI toolkit's verify mode.

### 4.3 LaunchAgent: com.elements.hsl-daemon

**File:** `PROJECT_sentinel/agents/com.elements.hsl-daemon.plist`

Runs `hsl_daemon.py --once` with Doppler secrets injection. Watches:
- `context-management/config/semantic_models.yaml`
- `standard-model-of-code/src/core`

### 4.4 Chunk Data in Sentinel

**File:** `PROJECT_sentinel/context-management/intelligence/chunks/logistics_demo.json`

Contains refinery-produced chunks with `"agent": "refinery.py"` attribution -- 45+ chunks demonstrating the data format that flows from the AI toolkit's refinery into Sentinel's intelligence layer.

---

## 5. PROJECT_central-mcp (Archaeological Source) -- PATTERN ANCESTRY

Central-MCP is abandoned as a product but contains ancestral patterns that evolved into the AI toolkit.

### 5.1 Intelligence Module

**Directory:** `PROJECT_central-mcp/src/intelligence/`

Contains TypeScript equivalents of concepts now in the AI toolkit:
- `PatternDetector.ts` -- Agent performance patterns, bottleneck detection (ancestor of `aci/semantic_finder.py` pattern matching)
- `PredictionEngine.ts` -- Prediction based on patterns (ancestor of ACI tier routing)
- `OptimizationSuggestor.ts` -- Optimization suggestions (ancestor of `insights_generator.py`)
- `EventAnalyzer.ts` -- Event analysis (ancestor of `aci/feedback_store.py`)
- `SessionManager.ts` -- Session state management (ancestor of `analyze/session.py`)

### 5.2 MCP Tool Patterns

**Directory:** `PROJECT_central-mcp/src/tools/intelligence/`

Contains 8 tool files including `connectToMCP.ts`, `visualMCPCall.ts`, `uploadProjectContext.ts` -- these are the patterns being adapted for the MCP wrapping plan in PROJECT_openclaw.

### 5.3 Key Differences

| Aspect | Central-MCP (old) | wave/tools/ai/ (current) |
|--------|-------------------|--------------------------|
| Language | TypeScript | Python |
| Architecture | Monolithic 259K files | Modular 60 files |
| Intelligence | Event-based + AI client | Tiered ACI + Cerebras |
| Persistence | SQLite + better-sqlite3 | JSON chunks + YAML |
| State | Database-backed sessions | File-based + cache |

The evolution shows a deliberate move from TypeScript monolith to Python toolkit with domain-specific tools.

---

## 6. Cross-Project Data Flow Diagram

```
                    COLLIDER (particle/)
                         |
                  unified_analysis.json
                         |
        +--------+-------+--------+--------+
        |        |       |        |        |
   enricher  insights  lab_bridge  refinery  deck
   (Cerebras) (Gemini)  (Science)  (Chunks)  (Cards)
        |        |       |        |        |
        v        v       v        v        v
   enriched   ai_insights  experiment  chunk     play
   _analysis  .json      results    registry  log
   .json                                       |
        |                          |           |
        +----------+---------------+    deck_router
                   |                    (intent->card)
            SENTINEL watches
            (LaunchAgents)
                   |
            socratic audit
            refinery daemon
            hsl daemon
                   |
            OPENCLAW (planned)
            (MCP servers via SSH)
                   |
            WhatsApp/Telegram
            (user interface)
```

---

## 7. Shared Infrastructure

### 7.1 Google Cloud

Both the AI toolkit and Atman share:
- GCS bucket: `gs://elements-archive-2026`
- Vertex AI for Gemini calls
- Doppler for secrets (`ai-tools` project)

### 7.2 Cerebras API

Used by:
- `wave/tools/ai/cerebras_*.py` (6 tools) -- direct API calls
- `PROJECT_openclaw/config/openclaw.json` -- model configuration
- Planned: MCP server wrapping for remote access

### 7.3 Virtual Environment

All Python tools share `.tools_venv` at PROJECT_elements root:
- Sentinel LaunchAgents invoke via `.tools_venv/bin/python`
- `analyze.py` auto-detects and bootstraps into this venv

---

## 8. Gaps and Opportunities

### Currently Missing Connections

| Connection | Status | Effort |
|-----------|--------|--------|
| AI toolkit -> PROJECT_ytpipe | No references found | Low (both use Pydantic + FastMCP) |
| AI toolkit -> PROJECT_lechworld | No references found | N/A (different domain) |
| AI toolkit -> PROJECT_orchestra | No direct references | Medium (orchestration overlap) |
| MCP server wrapping | Research done, not built | High (3 servers, 35+ tools) |
| OpenClaw live integration | Recipes documented | Medium (SSH + skill creation) |

### Strongest Connections (by evidence count)

1. **PROJECT_elements internal** -- 50+ cross-references to particle/, collider, unified_analysis
2. **PROJECT_sentinel** -- 3 LaunchAgents directly invoking AI toolkit scripts
3. **PROJECT_atman** -- Shared analyze.py + registry cross-references + implemented proposals
4. **PROJECT_openclaw** -- MCP wrapping research + integration playbook + cerebras config
5. **PROJECT_central-mcp** -- Pattern ancestry (intelligence module, MCP tools)

---

## 9. Architecture Principle

The AI toolkit follows a **hub-and-spoke** model:
- **Hub:** `wave/tools/ai/` in PROJECT_elements
- **Spokes:** Other projects connect via data exchange (JSON), CLI invocation (subprocess/SSH), or LaunchAgent automation
- **No direct imports:** No project does `from wave.tools.ai import X` -- all integration is through file I/O, CLI, or planned MCP

This is intentional. The toolkit's independence means it can be wrapped as MCP servers (OpenClaw plan) or consumed by any future project without coupling.

---

**Last Updated:** 2026-02-07
**Analysis Method:** ripgrep across ~/PROJECTS_all/ + targeted file reads
**Files Analyzed:** 60+ Python source files, 24 CARD YAMLs, 3 LaunchAgent plists, multiple MD docs
