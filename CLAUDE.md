# PROJECT_elements

Standard Model of Code -- the theoretical framework + implementation for treating code as architecture.

## Architecture

Two hemispheres (like a brain):

| Hemisphere | Purpose | Location |
|-----------|---------|----------|
| **Particle** (Body) | Collider engine -- parses code into atoms, layers, dimensions | `particle/` |
| **Wave** (Brain) | AI tools -- 40+ intelligence tools, context management, MCP servers | `wave/` |

**Projectome** = Codome (executable code) + Contextome (docs/config/data). MECE partition.

### 4-Zone Repository Architecture

| Zone | Tracked | What belongs here | Examples |
|------|---------|-------------------|----------|
| **1: Source Code** | Yes | Executable code, tests, configs, CI | `particle/src/`, `wave/tools/`, `tests/` |
| **2: Reference Data** | Yes | Taxonomies, schemas, specs | `particle/data/atoms/`, `wave/config/` |
| **3: Generated Output** | No | Regenerable analysis, reports, research | `research/`, `reports/`, `.collider/` |
| **4: Ephemeral State** | No | Agent state, logs, caches | `.agent/state/`, `wave/library/` |

Zone 3 backed up via `scripts/archive-to-gcs.sh`. Zone 4 is transient (Syncthing-only).

### Key Directories

```
particle/           Collider engine (Python, v2.3.0)
wave/tools/ai/      AI intelligence toolkit (Cerebras, ACI, Perplexity, Decision Deck)
wave/tools/ai/mcp_servers/  MCP server wrappers (see MCP Servers section)
wave/config/        Analysis sets, model config
wave/experiments/refinery-platform/  Ecosystem dashboard (Next.js 15, has own .claude/CLAUDE.md)
.agent/             Governance, decision deck cards, task registry
context-management/ Refinery + visualization dashboards
governance/         Roadmap, decisions, quality gates
docs/               AI model reference, diagrams
standard-model-of-code/  Theory package (pip installable)
```

### Refinery Platform (Ecosystem Dashboard)

Full-scope ecosystem dashboard: Next.js 15 / React 19 / Tailwind 4. Surfaces 200+ OpenClaw API endpoints across 12 domains (system, voice, LLM, comms, trading, finance, memory, tools, etc.) as a unified frontend.

- **Location:** `wave/experiments/refinery-platform/`
- **Port:** 3001 (dev + prod)
- **Deploy:** `dashboard.centralmcp.ai` (behind Authelia)
- **Design system:** Algebra-UI -- parametric OKLCH engine (hard tokens / soft tokens / coefficients). Lineage from PROJECT_vector-ui research.
- **Agent context:** `.ecoroot/common_knowledge.md` (shared SSOT) + thin wrappers: `.claude/CLAUDE.md`, `GEMINI.md`, `AGENTS.md`
- **Plan:** `~/.claude/plans/keen-wondering-puddle.md` (master implementation spec, 474 lines)

When working on the Refinery Platform, the project-level agent files have the full context. All three agents (Claude, Gemini, Codex) share `.ecoroot/common_knowledge.md` as their single source of truth.

## Commands

```bash
# Unified CLI
./pe status              # System health
./pe deck deal           # Available certified moves
./pe collider full .     # Run Collider on current repo
./pe collider --full     # Alias: full analysis on current repo
./pe test collider --full  # Test-style alias to collider full
./pe test --help         # Show test command usage

# Collider directly
./collider full /path/to/repo --output /tmp/analysis
.venv/bin/python3 -m collider full /path/to/repo --output /tmp/analysis
./collider-hub full --repo /path/to/repo            # Canonical full run + feedback bundle
./collider-hub smoke --repo /path/to/repo           # Reliability run + feedback bundle
./collider-hub feedback --repo /path/to/repo        # Feedback-only from existing artifacts
./collider-hub manual-feedback --repo /path/to/repo --problem "..." --evidence "..."

# REH (Repository Evolution History) — git-powered codebase archaeology
# MCP server with 5 tools: timeline, pickaxe, file history, capability changes, directory activity
uv run python wave/tools/mcp/mcp_history_server.py                      # Start MCP server (stdio)
uv run python wave/tools/mcp/mcp_history_server.py --test /path/to/repo # Quick smoke test

# AI Tools (all via doppler for secrets)
doppler run -- .venv/bin/python3 wave/tools/ai/cerebras_rapid_intel.py sweep
doppler run -- .venv/bin/python3 wave/tools/ai/analyze.py --aci "query"
doppler run -- .venv/bin/python3 wave/tools/ai/cerebras_tagger.py tag --pattern "**/*.py"
doppler run -- .venv/bin/python3 wave/tools/ai/perplexity_research.py "topic"

# Testing
cd particle && pytest tests/ -q    # 1,211 tests

# Archive Zone 3 to GCS
bash scripts/archive-to-gcs.sh             # Dry-run
bash scripts/archive-to-gcs.sh --execute   # Real sync

# Dashboards
cd context-management/viz/unified-dashboard && npm run dev   # Projectome viewer :3000
cd wave/experiments/refinery-platform && npm run dev  # Refinery :3001
```

## Key Paths

| Task | Location |
|------|----------|
| Analyze a repo | `particle/cli.py` (entry), `particle/full_analysis.py` |
| AI query (fast) | `wave/tools/ai/cerebras_rapid_intel.py` |
| AI query (smart routing) | `wave/tools/ai/analyze.py --aci` |
| MCP servers | `wave/tools/ai/mcp_servers/` + `wave/tools/mcp/` (see MCP Servers section) |
| REH (temporal) | `particle/src/core/reh_core.py` (core), `temporal_analysis.py` (engine), `wave/tools/mcp/mcp_history_server.py` (MCP) |
| Decision deck cards | `.agent/deck/` + `wave/tools/ai/deck/` |
| Atom taxonomy | `particle/data/atoms/` (3,610 atoms) |
| Analysis config | `wave/config/analysis_sets.yaml` |
| Subsystem map | `SUBSYSTEMS.yaml` (8 subsystems) |
| Domain map | `DOMAINS.yaml` (6 domains) |
| Architecture deep dive | `wave/tools/ai/.research/ARCHITECTURE_MAP.md` |
| Refinery Platform (dashboard) | `wave/experiments/refinery-platform/` (has own `.claude/CLAUDE.md`) |
| Refinery design system | `wave/experiments/refinery-platform/app/globals.css` (parametric OKLCH engine) |
| Refinery master plan | `~/.claude/plans/keen-wondering-puddle.md` (474-line implementation spec) |

## MCP Servers

3+ activated MCP servers registered in `~/.claude.json`. Full inventory in `.ecoroot/TOOLS_REGISTRY.yaml` (SSOT).

| Server | ECO-ID | Tools | Secrets | Key Capability |
|--------|--------|-------|---------|----------------|
| **cerebras-intelligence** | ECO-047 | 10 | Doppler (CEREBRAS_API_KEY) | Fast LLM queries, Perplexity research, token estimation |
| **reh** | ECO-051 | 11 | None | Git archaeology, session history, evolution reports |
| **reddit-intelligence** | ECO-059 | 6 | None | Community search, post threads, subreddit stats |

Additional servers implemented but not yet activated: `aci_system_mcp` (8 tools), `decision_deck_mcp` (6 tools).

**Locations:** `wave/tools/ai/mcp_servers/` (AI servers) + `wave/tools/mcp/` (REH, Perplexity)
**Transport:** All stdio (JSON-RPC). Registered per-project in `~/.claude.json`.
**Pattern:** `doppler run -- .venv/bin/python3 <server>.py` (if secrets needed) or direct `.venv/bin/python3 <server>.py`

## Rules

- Always run `doppler run --` before any AI tool (secrets are in Doppler, not .env)
- Collider output goes to `.collider/` or explicit `--output` path
- Collider Hub always writes post-run feedback to `.collider/feedback/`:
  - `latest_auto_feedback.json`
  - `latest_ai_user_audit.md`
  - `collider_feedback_report_latest.json`
- Feedback ingestion sink is single and centralized:
  - `/Users/lech/PROJECTS_all/PROJECT_elements/collider_feedback/`
- Use `--set brain` for Wave analysis, `--set body` for Particle analysis
- Decision Deck: check `./pe deck deal` before improvising
- MCP server directory is `mcp_servers/` (NOT `mcp/` -- avoids shadowing pip package)
- GCS archive bucket: `gs://elements-archive-2026/`
- Two venvs: `.venv` (main, AI tools) and `.tools_venv` (pe CLI, docling)
