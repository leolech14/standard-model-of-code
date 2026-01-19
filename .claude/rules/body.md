---
paths:
  - "standard-model-of-code/**"
---

# Body (Collider) Rules

## Before Making Changes
- Read `standard-model-of-code/CLAUDE.md` first
- Run existing tests: `pytest tests/ -q`

## Code Style
- Python 3.10+ features allowed
- Type hints required for public functions
- Docstrings for modules and classes

## Testing
- Add tests for new functionality in `tests/`
- Verify with: `pytest tests/ -v --tb=short`

## HTML/Visualization
- Never trust old `.html` outputs
- Always regenerate: `./collider full . --output .collider`
- Assets in `src/core/viz/assets/`

## Key Files
- Entry: `cli.py`
- Pipeline: `src/core/full_analysis.py`
- Output: `src/core/brain_download.py`
