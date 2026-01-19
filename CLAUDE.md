# PROJECT_elements

> The effort to find the basic constituents of computer programs.

## Architecture

Two-hemisphere system:

| Hemisphere | Path | Purpose |
|------------|------|---------|
| **Body** | `standard-model-of-code/` | Collider engine - parses code |
| **Brain** | `context-management/` | AI tools, theory, cloud mirror |

## Common Commands

```bash
# Analyze a codebase (primary tool)
cd standard-model-of-code && ./collider full /path/to/repo --output /tmp/out

# AI analysis (requires gcloud auth)
python context-management/tools/ai/analyze.py "query" --set brain_core

# Run tests
cd standard-model-of-code && pytest tests/ -q

# Sync to cloud
python context-management/tools/archive/archive.py mirror
```

## Key Paths

| Task | Location |
|------|----------|
| Collider code | `standard-model-of-code/src/core/` |
| Atom definitions | `standard-model-of-code/schema/` |
| AI analysis tool | `context-management/tools/ai/analyze.py` |
| Theory docs | `standard-model-of-code/docs/` |

## Hemisphere Instructions

@standard-model-of-code/CLAUDE.md

## GCP Config

- Project: `elements-archive-2026`
- Model: `gemini-2.0-flash-001`
- Bucket: `gs://elements-archive-2026/`

## Rules

- Always regenerate before debugging HTML: `./collider full . --output .collider`
- Run tests before commit
- Archive directory is read-only (large files in GCS)
- Know which hemisphere you're in before editing
