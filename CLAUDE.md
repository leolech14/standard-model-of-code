# PROJECT_elements

Standard Model of Code -- the theoretical framework + implementation for treating code as architecture.

## Architecture

Two hemispheres (like a brain):

| Hemisphere | Purpose | Location |
|-----------|---------|----------|
| **Particle** (Body) | Collider engine -- parses code into atoms, layers, dimensions | `particle/` |
| **Wave** (Brain) | AI tools -- 40+ intelligence tools, context management, MCP servers | `wave/` |

**Projectome** = Codome (executable code) + Contextome (docs/config/data). MECE partition.

### Key Directories

```
particle/           Collider engine (Python, v2.3.0)
wave/tools/ai/      AI intelligence toolkit (Cerebras, ACI, Perplexity, Decision Deck)
wave/tools/ai/mcp_servers/  MCP server wrappers (3 servers)
wave/config/        Analysis sets, model config
.agent/             Governance, decision deck cards, task registry
context-management/ Refinery + visualization dashboards
governance/         Roadmap, decisions, quality gates
docs/               AI model reference, diagrams
standard-model-of-code/  Theory package (pip installable)
```

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

# AI Tools (all via doppler for secrets)
doppler run -- .venv/bin/python3 wave/tools/ai/cerebras_rapid_intel.py sweep
doppler run -- .venv/bin/python3 wave/tools/ai/analyze.py --aci "query"
doppler run -- .venv/bin/python3 wave/tools/ai/cerebras_tagger.py tag --pattern "**/*.py"
doppler run -- .venv/bin/python3 wave/tools/ai/perplexity_research.py "topic"

# Testing
cd particle && pytest tests/ -q    # 406 tests

# Dashboards
cd context-management/viz/unified-dashboard && npm run dev   # Projectome viewer :3000
cd context-management/experiments/refinery-platform && npm run dev  # Refinery :3001
```

## Key Paths

| Task | Location |
|------|----------|
| Analyze a repo | `particle/cli.py` (entry), `particle/full_analysis.py` |
| AI query (fast) | `wave/tools/ai/cerebras_rapid_intel.py` |
| AI query (smart routing) | `wave/tools/ai/analyze.py --aci` |
| MCP servers | `wave/tools/ai/mcp_servers/` (3 servers) |
| Decision deck cards | `.agent/deck/` + `wave/tools/ai/deck/` |
| Atom taxonomy | `particle/data/atoms/` (3,610 atoms) |
| Analysis config | `wave/config/analysis_sets.yaml` |
| Subsystem map | `SUBSYSTEMS.yaml` (8 subsystems) |
| Domain map | `DOMAINS.yaml` (6 domains) |
| Architecture deep dive | `wave/tools/ai/.research/ARCHITECTURE_MAP.md` |

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
