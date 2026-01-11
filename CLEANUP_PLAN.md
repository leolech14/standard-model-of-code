# Repository Cleanup & Reorganization Plan

> **Created**: 2026-01-07
> **Current Size**: ~10GB (145,000+ files)
> **Goal**: Crystal clear structure with obvious separation of concerns

---

## Current Problems

| Issue | Description | Impact |
|-------|-------------|--------|
| **Bloated directories** | `validation/` = 3.8GB, `output/` = 4.1GB, `github_analysis/` = 1.4GB | Hard to navigate |
| **Duplicate archives** | Multiple files already have `_ARCHIVED_` suffix but still in active folders | Confusing |
| **Mixed concerns** | Theory, code, outputs, test data all intermingled | Hard to understand |
| **28 root files** | Too many files at project root | No clear entry point |
| **Redundant copies** | `core/` duplicates files from `schema/`, `docs/` | Sync issues |

---

## Proposed Structure

```
standard-model-of-code/
│
├── README.md                    ← Main entry point
├── pyproject.toml               ← Package config
├── setup.py
│
├── schema/                      ← 🎯 FORMAL DEFINITIONS (keep)
│   ├── particle.schema.json    
│   ├── graph.schema.json       
│   ├── types.ts                
│   ├── types.py                
│   ├── antimatter_laws.yaml    
│   └── 200_ATOMS.md            
│
├── docs/                        ← 📚 DOCUMENTATION (keep, reorganize)
│   ├── theory/                 ← Core theory files
│   │   ├── FOUNDATIONAL_THEORIES.md
│   │   ├── ADDITIONAL_THEORIES.md
│   │   └── theory_v2.md (rename to THEORY.md)
│   ├── roadmaps/               ← Implementation plans
│   ├── prompts/                ← Visualization prompts
│   └── assets/                 ← Images
│
├── src/                         ← 🔧 SOURCE CODE (keep, is Collider)
│   ├── core/
│   ├── analytics/
│   ├── app/
│   └── tools/
│
├── tests/                       ← ✅ TESTS (keep)
│
├── scripts/                     ← 🛠 UTILITY SCRIPTS (keep)
│
├── .archive/                    ← 📦 ARCHIVED (move, gitignore)
│   ├── docs_archive/           ← Old theory versions
│   ├── audio/                  ← 400MB audio files
│   ├── legacy_orphans/         ← Current archive/ folder
│   └── html_reports/           ← Old HTML files from root
│
├── .data/                       ← 💾 LARGE DATA (move, gitignore)
│   ├── validation/             ← 3.8GB validation runs
│   ├── output/                 ← 4.1GB output files
│   ├── github_analysis/        ← 1.4GB repo clones
│   └── collider_output/        ← 17MB analysis outputs
│
└── .research/                   ← 🔬 RESEARCH (move to keep repo clean)
    └── extracted_nodes/
```

---

## Cleanup Actions

### Phase 1: Archive Large Data (Save ~9GB)

```bash
# Create hidden data directory (will be gitignored)
mkdir -p .data

# Move massive directories
mv validation .data/
mv output .data/
mv github_analysis .data/
mv collider_output .data/

# These are analysis outputs, not core repo
```

### Phase 2: Archive Legacy Files

```bash
# Create hidden archive directory
mkdir -p .archive/docs_archive

# Move all already-archived docs
mv docs/archive/* .archive/docs_archive/

# Move audio files (400MB)
mv audio .archive/

# Move legacy archive folder
mv archive .archive/legacy_orphans
```

### Phase 3: Clean Root Directory

```bash
# Move root HTML files to archive
mv *.html .archive/html_reports/

# Keep only essential root files:
# - README.md
# - ROADMAP_10_OF_10.md  
# - pyproject.toml
# - setup.py
# - pytest.ini

# Move other MD files to appropriate locations
mv STORAGE_ARCHITECTURE.md docs/
mv DEPENDENCIES.md docs/
mv GPU_SETUP.md docs/
```

### Phase 4: Remove core/ (It's a Copy)

```bash
# core/ is just a copy of files from schema/ and docs/
# The authoritative versions are in those folders
rm -rf core/
```

### Phase 5: Reorganize docs/

```bash
# Create clear subdirectories
mkdir -p docs/theory

# Move theory files
mv docs/FOUNDATIONAL_THEORIES.md docs/theory/
mv docs/ADDITIONAL_THEORIES.md docs/theory/
mv docs/SYNTHESIS_GAP_IMPLEMENTATION.md docs/theory/
mv docs/theory_v2.md docs/theory/THEORY.md
mv docs/theory.md docs/theory/THEORY_ORIGINAL.md
mv docs/VALUE_SCENARIOS.md docs/theory/
```

### Phase 6: Update .gitignore

```gitignore
# Large data directories (not tracked)
.data/
.archive/
.research/

# Keep schema and docs tracked
!schema/
!docs/
```

---

## Files to Keep at Root (8 max)

| File | Purpose |
|------|---------|
| `README.md` | Main entry point |
| `ROADMAP_10_OF_10.md` | Current roadmap |
| `pyproject.toml` | Package config |
| `setup.py` | Install script |
| `pytest.ini` | Test config |
| `.gitignore` | Git ignore |
| `.pre-commit-config.yaml` | If exists |
| `LICENSE` | If exists |

---

## Directory Summary After Cleanup

| Directory | Purpose | Tracked? |
|-----------|---------|----------|
| `schema/` | Formal schemas (JSON, TS, Python) | ✅ Yes |
| `docs/` | Documentation, theory, prompts | ✅ Yes |
| `src/` | Collider source code | ✅ Yes |
| `tests/` | Test suite | ✅ Yes |
| `scripts/` | Utility scripts | ✅ Yes |
| `.data/` | Large analysis data | ❌ No |
| `.archive/` | Archived legacy files | ❌ No |
| `.research/` | Research outputs | ❌ No |

---

## Expected Result

- **Tracked files**: ~600 (down from 145,000+)
- **Repo size**: ~100MB (down from 10GB)
- **Root files**: 8 (down from 28)
- **Crystal clear**: Schema → Docs → Code → Tests

---

## Commands to Execute

```bash
# Run from standard-model-of-code/

# Phase 1: Create directories
mkdir -p .data .archive/docs_archive .archive/html_reports

# Phase 2: Move large data
mv validation .data/
mv output .data/
mv github_analysis .data/
mv collider_output .data/

# Phase 3: Move archives
mv docs/archive/* .archive/docs_archive/
mv audio .archive/
mv archive .archive/legacy_orphans

# Phase 4: Clean root
mv *.html .archive/html_reports/ 2>/dev/null

# Phase 5: Remove duplicate core/
rm -rf core/

# Phase 6: Reorganize docs
mkdir -p docs/theory
mv docs/FOUNDATIONAL_THEORIES.md docs/theory/
mv docs/ADDITIONAL_THEORIES.md docs/theory/
mv docs/SYNTHESIS_GAP_IMPLEMENTATION.md docs/theory/
mv docs/theory_v2.md docs/theory/THEORY.md

# Phase 7: Move root MD files
mv STORAGE_ARCHITECTURE.md docs/ 2>/dev/null
mv DEPENDENCIES.md docs/ 2>/dev/null
mv GPU_SETUP.md docs/ 2>/dev/null

# Phase 8: Update .gitignore
echo -e "\n# Large untracked directories\n.data/\n.archive/\n.research/" >> .gitignore
```

---

## Verification After Cleanup

```bash
# Check final structure
find . -maxdepth 2 -type d ! -path './.git*' ! -path './.data*' ! -path './.archive*' | sort

# Count tracked files
find . -type f ! -path './.git/*' ! -path './.data/*' ! -path './.archive/*' ! -path './.venv/*' | wc -l

# Check repo size
du -sh . --exclude='.data' --exclude='.archive' --exclude='.git' --exclude='.venv'
```
