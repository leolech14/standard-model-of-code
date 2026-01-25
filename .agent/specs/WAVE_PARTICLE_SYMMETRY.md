# Wave-Particle Symmetry Achievement

> The gold standard for repository documentation. When Wave (documentation) perfectly mirrors Particle (implementation).

---

## The Principle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     WAVE-PARTICLE SYMMETRY                              │
│                                                                         │
│   Every PARTICLE (code construct) has a corresponding WAVE (doc)        │
│   Every WAVE (doc claim) has a corresponding PARTICLE (code proof)      │
│                                                                         │
│   PARTICLE ←──────────── SYMMETRY ──────────────→ WAVE                  │
│   (What IS)                                       (What's DESCRIBED)    │
│                                                                         │
│   When these are identical: ACHIEVEMENT UNLOCKED                        │
└─────────────────────────────────────────────────────────────────────────┘
```

**Symmetry means:**
- No undocumented public APIs
- No documented features that don't exist
- No stale examples
- No broken links
- No orphan docs
- No orphan code

---

## Achievement Tiers

| Tier | Name | Score | Description |
|:----:|------|:-----:|-------------|
| 🥉 | **Bronze** | 60-74% | Basic README, some API docs |
| 🥈 | **Silver** | 75-89% | Complete API docs, architecture diagram |
| 🥇 | **Gold** | 90-97% | Full symmetry, examples work, cross-refs |
| 💎 | **Diamond** | 98-100% | Perfect symmetry, auto-validated |

---

## Scoring Rubric (100 points)

### 1. Structural Symmetry (25 points)

| Criterion | Points | Validation |
|-----------|:------:|------------|
| Every public module has a doc section | 10 | `modules.count == doc_sections.count` |
| Every public class has docstring | 5 | AST check: `class.docstring != None` |
| Every public function has docstring | 5 | AST check: `func.docstring != None` |
| Directory structure documented | 5 | `ls -R` matches architecture doc |

### 2. Behavioral Symmetry (25 points)

| Criterion | Points | Validation |
|-----------|:------:|------------|
| All CLI commands documented | 10 | `--help` output matches docs |
| All config options documented | 5 | Config schema == doc table |
| All environment variables listed | 5 | `grep -r "os.environ"` == doc list |
| Error messages explained | 5 | Error codes in docs |

### 3. Example Symmetry (20 points)

| Criterion | Points | Validation |
|-----------|:------:|------------|
| README examples run without error | 10 | `bash -x examples.sh` passes |
| Code snippets are tested | 5 | doctest or equivalent |
| Example outputs match actual outputs | 5 | Snapshot testing |

### 4. Reference Symmetry (15 points)

| Criterion | Points | Validation |
|-----------|:------:|------------|
| All internal links resolve | 5 | Link checker passes |
| All external links live | 5 | HTTP 200 on all URLs |
| Cross-references bidirectional | 5 | A→B implies B→A |

### 5. Freshness Symmetry (15 points)

| Criterion | Points | Validation |
|-----------|:------:|------------|
| Docs updated with code changes | 10 | `git log` correlation |
| No TODOs older than 30 days | 3 | `grep -r "TODO"` audit |
| Version numbers match | 2 | `__version__` == docs |

---

## Required Documents (Diamond Tier)

```
repo/
├── README.md                    # Entry point (required)
├── ARCHITECTURE.md              # System overview (required)
├── CHANGELOG.md                 # Version history (required)
├── docs/
│   ├── getting-started.md       # Onboarding
│   ├── api/                     # API reference (auto-generated OK)
│   │   └── [module].md
│   ├── guides/                  # How-to guides
│   │   └── [task].md
│   ├── concepts/                # Explanations
│   │   └── [concept].md
│   └── reference/               # Technical reference
│       ├── config.md            # All config options
│       ├── cli.md               # All CLI commands
│       └── errors.md            # All error codes
└── examples/                    # Working examples
    └── [example]/
        ├── README.md
        └── [code]
```

---

## Validation Tool

The actual validation tool is implemented at `.agent/tools/symmetry_check.py`:

```bash
# Full check with details
python .agent/tools/symmetry_check.py

# JSON output for CI pipelines
python .agent/tools/symmetry_check.py --json

# Brief one-liner for status
python .agent/tools/symmetry_check.py --brief
# Output: 🥈 SILVER (86/100)
```

### Example Output

```
============================================================
WAVE-PARTICLE SYMMETRY CHECK
============================================================

Category           Score    Max Evidence
------------------------------------------------------------
STRUCTURAL            22     25   96% class, 78% func docstrings
BEHAVIORAL            22     25   CLI works, 4/4 key docs
EXAMPLES              15     20   78 code blocks in key docs
REFERENCES            15     15   0 broken links, 0 total
FRESHNESS             12     15   18 TODOs, 15 FIXMEs
------------------------------------------------------------
TOTAL                 86    100

TIER: 🥈 SILVER

Gap to Gold: 4 points
```

### Quick Commands for Each Category

```bash
# Check STRUCTURAL (docstring coverage)
python3 -c "
import ast
from pathlib import Path
total = documented = 0
for f in Path('standard-model-of-code/src').rglob('*.py'):
    try:
        for n in ast.walk(ast.parse(f.read_text())):
            if isinstance(n, ast.FunctionDef) and not n.name.startswith('_'):
                total += 1
                if ast.get_docstring(n): documented += 1
    except: pass
print(f'{documented}/{total} = {100*documented//total}%')
"

# Check REFERENCES (broken links)
grep -o '\[.*\]([^)]*\.md)' CLAUDE.md | while read link; do
  path=$(echo "$link" | sed 's/.*](//' | sed 's/)$//')
  [ ! -f "$path" ] && echo "BROKEN: $path"
done

# Check FRESHNESS (TODO count)
grep -r "TODO\|FIXME" standard-model-of-code/src --include="*.py" | wc -l
```

---

## Automated Symmetry Enforcement

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: symmetry-check
        name: Wave-Particle Symmetry
        entry: ./scripts/symmetry_check.py
        language: python
        pass_filenames: false
        stages: [commit]
```

### CI Integration

```yaml
# .github/workflows/symmetry.yml
name: Documentation Symmetry
on: [push, pull_request]
jobs:
  symmetry:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check symmetry
        run: |
          pip install symmetry-checker  # hypothetical
          symmetry-check --min-score 90
```

---

## PROJECT_elements Symmetry Status

### Current Score: **85/100** (Silver 🥈) — Validated 2026-01-23

| Category | Score | Max | Evidence |
|----------|:-----:|:---:|----------|
| Structural | 22 | 25 | 96% class, 77% func docstrings |
| Behavioral | 22 | 25 | CLI works, 4/4 key docs exist |
| Examples | 14 | 20 | 74 code blocks in key docs |
| References | 15 | 15 | 0 broken links |
| Freshness | 12 | 15 | 19 TODOs, 15 FIXMEs |
| **TOTAL** | **85** | **100** | **Gap to Gold: 5 pts** |

### Validation Tool

```bash
# Run the automated symmetry check
python .agent/tools/symmetry_check.py

# JSON output for CI
python .agent/tools/symmetry_check.py --json

# Brief one-liner
python .agent/tools/symmetry_check.py --brief
```

### Path to Gold (90+)

| Action | Points | Priority |
|--------|:------:|:--------:|
| Add docstrings to core functions | +3 | P1 |
| Add more code examples | +3 | P1 |
| Clear remaining TODOs | +3 | P2 |
| **TOTAL GAIN** | **+11** | |

### Path to Diamond (98+)

After Gold:
- Implement automated symmetry check in CI
- Add doctest to all code examples
- Implement bidirectional cross-reference validation
- Auto-generate API docs from source

---

## The Symmetry Mantra

```
     "If it's in the code, it's in the docs.
      If it's in the docs, it's in the code.
      If they disagree, one of them is wrong."
```

---

## Tools That Help

| Tool | Purpose | Symmetry Aspect |
|------|---------|-----------------|
| **Collider** | Code structure extraction | Particle → data |
| **mkdocs** | Doc site generation | Wave → HTML |
| **doctest** | Example validation | Example symmetry |
| **markdown-link-check** | Link validation | Reference symmetry |
| **interrogate** | Docstring coverage | Structural symmetry |
| **git-cliff** | Changelog generation | Freshness symmetry |

---

## Measuring Symmetry with Collider

```bash
# 1. Analyze codebase (extract Particle)
./collider full /path/to/repo --output /tmp/analysis

# 2. Analyze docs (extract Wave)
./collider full /path/to/repo/docs --output /tmp/docs_analysis

# 3. Compare coverage
python -c "
import json
particle = json.load(open('/tmp/analysis/unified_analysis.json'))
wave = json.load(open('/tmp/docs_analysis/unified_analysis.json'))

particle_exports = {n['id'] for n in particle['nodes'] if n.get('visibility') == 'public'}
wave_mentions = {n['id'] for n in wave['nodes']}

documented = particle_exports & wave_mentions
undocumented = particle_exports - wave_mentions
orphan_docs = wave_mentions - particle_exports

print(f'Documented: {len(documented)}')
print(f'Undocumented: {len(undocumented)}')
print(f'Orphan docs: {len(orphan_docs)}')
print(f'Symmetry: {len(documented) / len(particle_exports) * 100:.1f}%')
"
```

---

## Achievement Badge

When a repo achieves Diamond tier:

```markdown
[![Wave-Particle Symmetry](https://img.shields.io/badge/docs-diamond-blue?style=flat-square&logo=data:image/svg+xml;base64,...)](./docs/SYMMETRY.md)
```

---

*Symmetry is not a destination. It's a continuous practice.*
