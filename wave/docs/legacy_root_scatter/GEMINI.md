# PROJECT_elements

> The effort to find the basic constituents of computer programs.

## Architecture

| Hemisphere | Path | Purpose |
|------------|------|---------|
| **Body** | `particle/` | Collider engine - parses code |
| **Brain** | `wave/` | AI tools, cloud mirror |
| **Logistics** | `wave/tools/refinery/` | Ingestion, Provenance, Physics |

## Commands

```bash
# Primary: Analyze a codebase
cd particle && ./collider full /path/to/repo --output /tmp/out

# AI query (this project uses Gemini)
python wave/tools/ai/analyze.py "query" --set brain

# Socratic Verification (Antimatter Law Check)
python wave/tools/ai/analyze.py --verify pipeline

# Tests
cd particle && pytest tests/ -q

# Logistics Pipeline
python3 wave/tools/refinery/pipeline.py /path/to/repo
```

## Coding Style

- Python 3.10+ required
- 4-space indentation
- Type hints for public functions
- Docstrings for modules and classes
- No `print()` in production code - use logging

## Key Paths

| Task | Location |
|------|----------|
| Collider engine | `particle/src/core/` |
| Atom schemas | `particle/schema/*.yaml` |
| AI tools | `wave/tools/ai/` |
| Theory docs | `particle/docs/` |
| Logistics Theory | `wave/intelligence/concepts/THEORY_DATA_LOGISTICS.md` |

## Rules

- Regenerate before debugging HTML: `./collider full . --output .collider`
- Run tests before commit
- Archive is read-only (large files in GCS)
- Know your hemisphere before editing

## Holographic-Socratic Layer

24/7 AI guardian detecting documentation/implementation drift.
- **Command**: `python wave/tools/ai/analyze.py --verify pipeline`
- **Config**: `wave/config/semantic_models.yaml`
- **Output**: `gs://elements-archive-2026/intelligence/`


## GCP

- Project: `elements-archive-2026`
- Model: `gemini-2.0-flash-001` (1M tokens)
- Bucket: `gs://elements-archive-2026/`

## Extended Context

@.gemini/context/body.md
@.gemini/context/brain.md
