# PROJECT_elements

Foundation repo for the ecosystem: Standard Model of Code (SMC) + Collider engine + Wave AI tooling.

## Start Here

- Project map + commands: `CLAUDE.md`
- Governance index (roadmap, decisions, quality gates): `governance/README.md`
- Safe AI querying (context budgeting): `governance/QUICK_START.md`
- Scale + active surface + consolidation targets: `reports/audits/MISSION_CONTROL.md`
- Documentation index: `docs/README.md`

## Mental Model (2 Hemispheres)

- `particle/` = "body" (Collider engine: parses code into atoms/layers/dimensions)
- `wave/` = "brain" (AI tools, context management, MCP servers)

## Practical Rule

This repo is large and includes many artifacts; prefer using the built-in filtered query tooling:

- `wave/tools/ai/analyze.py` (see `governance/QUICK_START.md`)

## Operational Truth (2026-02-25)

- Unified CLI `./pe` resolves tool roots from `wave/tools/` first, with legacy fallback to `context-management/tools/`.
- Collider root is `particle/` (legacy fallback: `standard-model-of-code/`).
- Root shim `./collider` forwards to `particle/collider`.
- `./pe collider --full` and `./pe test collider --full` run full analysis on the current repo.
- `./pe test --help` shows usage without running pytest.
- `collider health` is wired to `src/core/newman_suite.py` probes.
- `collider audit` executes Newman probes + a minimal full analysis run.
- React TSX extraction path is Tree-sitter-first again (no fallback-only regression when optional grammars are partially installed).

Known environment-dependent outcomes:
- `collider health` reports FAIL when Ollama is offline.
- Stage 14 vectorization reports warning/failure if `lancedb` is not installed.
