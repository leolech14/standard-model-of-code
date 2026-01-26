# PARTICLE COLLIDER - EMERGENCY MAP

> **Status:** DEGRADED - Core parsing broken
> **Created:** 2026-01-26
> **Author:** Claude Opus 4.5 (system crystallization)
> **Realm:** PARTICLE (Deterministic Analysis)

---

## EXECUTIVE SUMMARY

Collider is the **heartbeat** of PROJECT_elements. It transforms source code into semantic graphs. When Collider doesn't run, everything downstream starves.

```
SEVERITY: CRITICAL
IMPACT:   No fresh analysis → all consumers get stale/empty data
ROOT:     tree-sitter Python bindings not installed/broken
CASCADE:  Collider → unified_analysis.json → Purpose Field → POM → ACI → AI answers
```

---

## 1. WHAT COLLIDER IS

### Identity

| Attribute | Value |
|-----------|-------|
| **Subsystem ID** | S1 |
| **Realm** | PARTICLE (deterministic) |
| **Role** | The Analysis Engine |
| **Location** | `standard-model-of-code/` |
| **Entry Point** | `./pe collider full <path> --output <dir>` |
| **CLI** | `cli.py` (1063+ lines) |

### The 28-Stage Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         COLLIDER PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STAGE 1: Base Analysis                                                 │
│  ├── AST parsing (tree-sitter)  ◄── BROKEN HERE                        │
│  ├── Token extraction                                                   │
│  └── Basic node/edge creation                                           │
│                                                                         │
│  STAGE 2: Standard Model Classification                                 │
│  ├── Atom detection (167 types)                                         │
│  ├── Role assignment (33 canonical)                                     │
│  └── 8-dimensional coordinates                                          │
│                                                                         │
│  STAGE 3: Purpose Field                                                 │
│  ├── 3.0: Auto Pattern Discovery                                        │
│  ├── 3.5: Organelle Purpose (π₃)                                        │
│  ├── 3.6: File Purpose (π₄)                                             │
│  └── 3.7: Purpose Coherence (NEW - never executed)                      │
│                                                                         │
│  STAGE 4: Execution Flow                                                │
│  └── Reachability analysis                                              │
│                                                                         │
│  STAGE 5: Markov Transitions                                            │
│  └── State transition matrix                                            │
│                                                                         │
│  STAGES 6-7: Graph Analytics                                            │
│  ├── Centrality measures                                                │
│  └── Cycle detection                                                    │
│                                                                         │
│  STAGES 8-8.6: Purpose Intelligence                                     │
│  ├── Q-scores (quality metrics)                                         │
│  ├── Architecture profile validation                                    │
│  └── God class detection                                                │
│                                                                         │
│  STAGES 9-12: Output Generation                                         │
│  ├── Roadmap evaluation                                                 │
│  ├── Visual reasoning                                                   │
│  ├── Semantic cortex                                                    │
│  └── Consolidated outputs                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Outputs

| File | Purpose | Consumers |
|------|---------|-----------|
| `unified_analysis.json` | Complete semantic graph | POM, ACI, Laboratory, Charts |
| `collider_report.html` | Interactive 3D viz | Human inspection |
| `output.md` | "Brain download" report | Documentation |

---

## 2. WHAT'S BROKEN

### The tree-sitter Problem

```
DESIGNED:
  Source Code → tree-sitter → AST → Collider stages → unified_analysis.json

ACTUAL:
  Source Code → tree-sitter → ERROR/EMPTY → Nothing downstream
```

**Error Pattern:**
```python
import tree_sitter  # ModuleNotFoundError or ImportError
# OR
parser.parse(code)  # Returns empty/malformed tree
```

### Evidence

```bash
$ ./pe collider full . --output .collider
# Output shows 0 nodes parsed, or errors about tree-sitter
```

---

## 3. DEPENDENCY MAP

### What Collider Needs (Upstream)

```
┌─────────────────┐
│   tree-sitter   │ ◄── Python bindings
│   (parser)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ tree-sitter-    │ ◄── Language grammars
│ python/js/ts/go │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Collider     │
│    cli.py       │
└─────────────────┘
```

### What Depends on Collider (Downstream)

```
                    ┌─────────────────┐
                    │    Collider     │
                    │      (S1)       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ unified_analysis│
                    │     .json       │
                    └────────┬────────┘
                             │
       ┌─────────────┬───────┴───────┬─────────────┐
       │             │               │             │
       ▼             ▼               ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ Purpose   │ │ POM       │ │Laboratory │ │ Continuous│
│ Field     │ │ (S14?)    │ │ Bridge    │ │Cartograph │
│ Stage 3.7 │ │           │ │ (S9b)     │ │ er        │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
      │             │             │             │
      │             ▼             │             ▼
      │      ┌───────────┐        │      ┌───────────┐
      │      │ coherence │        │      │repo_truths│
      │      │ = 0.0     │        │      │  .yaml    │
      │      │ (BROKEN)  │        │      │  (STALE)  │
      │      └───────────┘        │      └─────┬─────┘
      │                           │            │
      └───────────────────────────┴────────────┘
                                  │
                                  ▼
                           ┌───────────┐
                           │    ACI    │
                           │(stale data│
                           └───────────┘
```

---

## 4. THE STANDARD MODEL (What Collider Implements)

### Atom Classification

```
ATOM: The fundamental unit of code structure

167 Total Atom Types:
├── 94 Implemented (core)
├── 33 Canonical Roles
└── 3,534 T2 Ecosystem (framework-specific)

Examples:
  Entity, Repository, Service, Controller, Factory,
  Validator, Transformer, Handler, Listener, Provider...
```

### 8-Dimensional Coordinates

Every code element gets classified in 8 dimensions:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  D1: Scale (16 levels)     │  Bit → Byte → ... → System → Universe     │
│  D2: Layer                 │  Infrastructure → Domain → Application    │
│  D3: Role                  │  33 canonical roles                       │
│  D4: Type                  │  Class, Function, Module, etc.            │
│  D5: Pattern               │  36 architectural patterns                │
│  D6: Visibility            │  Public, Private, Protected, Internal     │
│  D7: Lifecycle             │  Static, Instance, Singleton, Transient   │
│  D8: Purpose               │  Query, Command, Event, etc.              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Purpose Hierarchy (π₁ → π₄)

```
π₄: System Purpose    ← Gradient across entire codebase
     ↑
π₃: Layer Purpose     ← Shared across architectural layer
     ↑
π₂: Composite Purpose ← Emergent from grouped components
     ↑
π₁: Atomic Purpose    ← Individual function role
```

---

## 5. KEY FILES

| File | Purpose | Lines |
|------|---------|-------|
| `cli.py` | Main entry point | 1063+ |
| `src/core/full_analysis.py` | Pipeline orchestration | 1600+ |
| `src/core/purpose_field.py` | Purpose computation | 400+ |
| `src/core/purpose_intelligence.py` | Q-scores | 500+ |
| `src/core/atom_classifier.py` | Standard Model | 300+ |
| `src/core/registry/atom_registry.py` | Atom definitions | 200+ |

---

## 6. CONFIGURATION

### pyproject.toml Dependencies

```toml
[project]
dependencies = [
    "tree-sitter>=0.20.0",      # Core parser
    "tree-sitter-python",        # Python grammar
    "tree-sitter-javascript",    # JS grammar
    "tree-sitter-typescript",    # TS grammar
    # ... other languages
]
```

### Supported Languages

| Language | Grammar Package | Status |
|----------|-----------------|--------|
| Python | tree-sitter-python | Required |
| JavaScript | tree-sitter-javascript | Required |
| TypeScript | tree-sitter-typescript | Required |
| Go | tree-sitter-go | Optional |
| Rust | tree-sitter-rust | Optional |
| Java | tree-sitter-java | Optional |

---

## 7. RECOVERY PROCEDURE

### Step 1: Verify Current State

```bash
cd ~/PROJECTS_all/PROJECT_elements/standard-model-of-code

# Check if tree-sitter importable
uv run python -c "import tree_sitter; print('tree-sitter OK')"

# Check language grammars
uv run python -c "import tree_sitter_python; print('python grammar OK')"
```

### Step 2: Install Dependencies

```bash
cd ~/PROJECTS_all/PROJECT_elements/standard-model-of-code

# Option A: Using uv (preferred)
uv pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript

# Option B: Using pip in venv
source .venv/bin/activate
pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript
```

### Step 3: Test Parsing

```bash
# Run on a small file first
uv run python cli.py full src/core/purpose_field.py --output /tmp/test_collider

# Check output
cat /tmp/test_collider/unified_analysis.json | python -m json.tool | head -50
```

### Step 4: Full Analysis

```bash
cd ~/PROJECTS_all/PROJECT_elements

# Run full analysis
./pe collider full . --output .collider

# Verify
python3 -c "
import json
with open('.collider/unified_analysis.json') as f:
    d = json.load(f)
print(f'Nodes: {len(d.get(\"nodes\", []))}')
print(f'Edges: {len(d.get(\"edges\", []))}')
"
```

### Step 5: Verify Stage 3.7 Executed

```bash
python3 -c "
import json
with open('.collider/unified_analysis.json') as f:
    d = json.load(f)
nodes_with_coherence = sum(1 for n in d['nodes'] if 'coherence_score' in n)
print(f'Nodes with coherence_score: {nodes_with_coherence}')
"
```

---

## 8. SUCCESS CRITERIA

| Metric | Current | Target |
|--------|---------|--------|
| tree-sitter imports | ERROR | OK |
| Nodes parsed | 0 | >2000 |
| Edges extracted | 0 | >5000 |
| coherence_score populated | NO | YES |
| purpose_entropy populated | NO | YES |
| collider_report.html renders | NO | YES |

---

## 9. INTEGRATION POINTS

### Collider → Wave (ACI)

```
unified_analysis.json
       │
       ├──► laboratory_bridge.py (calls Laboratory facade)
       │
       ├──► continuous_cartographer.py (updates repo_truths)
       │
       └──► POM (projectome_omniscience.py)
                │
                └──► coherence metric for AI queries
```

### Collider → Observer (Tasks)

```
Collider analysis can identify:
  - Dead code (archive candidates)
  - God classes (refactor tasks)
  - Missing tests (coverage gaps)
  - Architecture violations (tech debt)

These feed into Task Registry (S5) as opportunities.
```

---

## 10. RELATED EMERGENCY MAPS

| Map | Relationship |
|-----|--------------|
| `WAVE-AI-SUBSYSTEM-EMERGENCY-MAP.md` | Downstream consumer (starving) |
| `OBSERVER-BARE-EMERGENCY-MAP.md` | Integration gap (S5→S6) |

---

*Collider is the foundation. Fix this first.*
