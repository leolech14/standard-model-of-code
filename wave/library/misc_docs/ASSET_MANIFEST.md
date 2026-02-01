# Asset Manifest (KEEP vs ARCHIVE)

Goal: treat everything in this folder as an asset, but keep a small “active core” and safely archive the rest (move to `ARCHIVE/` — no deletions).

## Tiers

- **CORE (keep active)**: source-of-truth canon + current runnable engines.
- **OPTIONAL (keep if you use it weekly)**: tools/visualizers that aren’t required for the canon.
- **REGENERATABLE (archive immediately)**: caches, virtualenvs, `node_modules`, generated outputs.
- **HISTORICAL (archive)**: old prototypes, one-off scripts, transcripts, intermediate reports, unused canvases.
- **MEDIA (archive unless referenced)**: screenshots/PNGs not used by the core docs.

## CORE (recommended active set)

Canon / datasets:
- `STANDARD_MODEL_OF_CODE_HONEST_GUIDE.md`
- `STANDARD-MODEL.md`
- `STANDARD_MODEL_STRUCTURE.md`
- `STANDARD_MODEL_ARCHITECTURE_AUDIT.md`
- `STANDARD_MODEL_COMPARATIVE_AUDIT_REPORT.md`
- `STANDARD_MODEL_AUDIT_RESPONSES.md`
- `GAP_ANALYSIS_MATRIX.md`
- `HADRONS_96_FULL.md`
- `HADRONS_96_MERMAID.md`
- `HADRONS_MERMAID_DIAGRAM.md`
- `HADRONS_96_MERMAID.png`
- `1440_csv.csv`
- `THEORY_COMPLETE.canvas`
- `spectrometer_v12_minimal/LAW_11_CANONICAL.md`
- `spectrometer_v12_minimal/LAW_11_CANONICAL.json`
- `spectrometer_v12_minimal/IMPOSSIBLE_42_CANONICAL.md`
- `spectrometer_v12_minimal/IMPOSSIBLE_42_CANONICAL.csv`
- `spectrometer_v12_minimal/1440_summary.json`

Current engines:
- `spectrometer_v12_minimal/core/`
- `spectrometer_v12_minimal/patterns/`
- Benchmark suite (golden truth + scoring):
  - `spectrometer_v12_minimal/validation/benchmarks/`
  - `spectrometer_v12_minimal/validation/run_benchmark_suite.py`
- Repo truth-source scanner (helps pick benchmark repos with embedded architecture truth):
  - `tools/scan_repo_truth_sources.py`

Entrypoints / how-to-run:
- `README.md`
- `CODEX.md`

If you are using the API + dashboard stack:
- `spectrometer_api_rest.py`
- `spectrometer_v9_raw_haiku.py`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `dashboard_web/`

## OPTIONAL (keep or archive depending on usage)

- `MermaidFlow/` (3D Mermaid visualizer)
- `chrome-mcp/` (keep source; archive `chrome-mcp/node_modules/`)
- `spectrometer-os_-standard-model-v5/` (React/Vite app)
- `.obsidian/` (only if this folder is an Obsidian vault you actively use)

## REGENERATABLE (safe to archive now)

- `chrome-mcp/node_modules/` (142MB; reinstallable)
- `spectrometer-env/`, `venv_ts/`, `venv_treesitter/` (local Python envs)
- `**/__pycache__/`, `**/*.pyc`, `**/.pytest_cache/`
- `**/.DS_Store`
- Generated outputs you can reproduce:
  - `spectrometer_v12_minimal/output/`
  - `spectrometer_v12_minimal/validation/validation_output/`
  - `spectrometer_v12_minimal/validation/benchmarks/runs/`

## HISTORICAL (high-confidence archive candidates)

- Older/experimental engines: most `spectrometer_v*_*.py`, `parser_*.py`, `haiku_omega_*.py`, `*_framework*.py`, `*validator*.py`
- Transcripts/context dumps: `000*.md`, `00*-grok*.md`, `2025-*.txt`
- Most canvas variants: keep your chosen canonical ones (at minimum `THEORY_COMPLETE.canvas`)
- Old generated reports: `*validation*results*.json`, `*report*.md`, `*summary*.json` (when reproducible)
- `spectrometer_v7_final.zip` (archive as a snapshot)

## MEDIA (archive most of it)

Keep only what is referenced by the canon docs (currently the obvious one is `HADRONS_96_MERMAID.png`). Archive the rest of root-level UUID PNGs and “Untitled design” screenshots.

## Do the archiving (dry-run first)

This repo is not a git checkout, so do moves via a reversible manifest.

- Dry run: `python3 tools/archive_assets.py --dry-run`
- Current dry-run snapshot (2025-12-14): selects 113 items / 15,828 files / ~336.7 MB (mostly `chrome-mcp/node_modules/` + local `venv*` + root PNGs).
- Apply: `python3 tools/archive_assets.py --apply`
- Skip rules (example, keep your virtualenvs): `python3 tools/archive_assets.py --apply --skip-rule python_virtualenvs`
- Undo (restores exact paths): `python3 tools/archive_assets.py --undo ARCHIVE/<date>/manifest.json`

The default rules live in `tools/archive_plan.json` and are meant to be edited.
