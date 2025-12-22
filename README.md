# ⚛️ Standard Model of Code

**The Periodic Table of Software Architecture**

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![Particles](https://img.shields.io/badge/particles-33-purple)

Transform any codebase into a **computable graph** with **lossless bidirectional transformation**. 
Code → Graph → Code. Zero information loss.

---

## 🎯 Single Entry Point

```python
from core.unified_analysis import analyze

# Analyze any codebase
result = analyze("/path/to/repo")

# Output: unified_analysis.json with consistent schema
print(f"Nodes: {result.stats['total_nodes']}")
print(f"Coverage: {result.stats['coverage_percentage']}%")
```

---

## ⚛️ The 33 Particles

Every code element maps to one of 33 fundamental types:

```
╔══════════════════════════════════════════════════════════════════╗
║                    STANDARD MODEL OF CODE                        ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  BEHAVIOR (How things act)                                       ║
║  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐                    ║
║  │ CMD │ QRY │ UCE │ EVH │ OBS │ EVP │ POL │                    ║
║  │Cmnd │Query│UseCs│EvHnd│Obsrv│EvPrc│Polcy│                    ║
║  └─────┴─────┴─────┴─────┴─────┴─────┴─────┘                    ║
║                                                                  ║
║  STRUCTURE (How things are organized)                            ║
║  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐              ║
║  │ SVC │ DSV │ ASV │ CTL │ FAC │ BLD │ PRV │ UTL │              ║
║  │Servc│DomSv│AppSv│Cntrl│Factry│Buildr│Provd│Util│              ║
║  └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘              ║
║                                                                  ║
║  DATA (What things hold)                                         ║
║  ┌─────┬─────┬─────┬─────┐                                      ║
║  │ ENT │ VO  │ DTO │ CFG │                                      ║
║  │Entty│ValObj│DTO │Confg│                                      ║
║  └─────┴─────┴─────┴─────┘                                      ║
║                                                                  ║
║  INTEGRATION (How things connect)                                ║
║  ┌─────┬─────┬─────┬─────┬─────┬─────┐                          ║
║  │ REP │ GWY │ CLI │ ADP │ ISV │ MAP │                          ║
║  │Repo │Gatwy│Clint│Adptr│IntSv│Mappr│                          ║
║  └─────┴─────┴─────┴─────┴─────┴─────┘                          ║
║                                                                  ║
║  QUALITY (What ensures correctness)                              ║
║  ┌─────┬─────┬─────┬─────┬─────┐                                ║
║  │ SPC │ VAL │ TST │ SUT │ EXC │                                ║
║  │Spec │Valid│Test │SubUT│Excpt│                                ║
║  └─────┴─────┴─────┴─────┴─────┘                                ║
║                                                                  ║
║  LIFECYCLE                                                       ║
║  ┌─────┬─────┬─────┐                                            ║
║  │ LFC │ ITR │ INT │                                            ║
║  │Lifecy│Itertr│Intrnl│                                            ║
║  └─────┴─────┴─────┘                                            ║
╚══════════════════════════════════════════════════════════════════╝
```

See [`STANDARD_MODEL_SCHEMA.json`](STANDARD_MODEL_SCHEMA.json) for complete schema.

---

## 🔬 The 6-Stage Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│  📂 Stage 1: AST PARSE                                           │
│     → Extract particles with body_source, params, decorators     │
├──────────────────────────────────────────────────────────────────┤
│  🏷️  Stage 2: RPBL CLASSIFICATION                                │
│     → Assign roles based on inheritance, decorators, paths       │
├──────────────────────────────────────────────────────────────────┤
│  🔍 Stage 3: AUTO PATTERN DISCOVERY                              │
│     → test_* → Test, get_* → Query, _private → Internal         │
├──────────────────────────────────────────────────────────────────┤
│  🔗 Stage 4: EDGE EXTRACTION                                     │
│     → imports, calls, contains, inherits                         │
├──────────────────────────────────────────────────────────────────┤
│  🧠 Stage 5: GRAPH INFERENCE                                     │
│     → "calls Repository" → Service (deterministic, no LLM)       │
│     → Parent inheritance: nested functions get parent's role     │
├──────────────────────────────────────────────────────────────────┤
│  📊 Stage 6: UNIFIED OUTPUT                                      │
│     → Consistent schema for ALL codebases                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Output Schema

Every analysis produces a consistent `unified_analysis.json`:

```json
{
  "schema_version": "1.0.0",
  "nodes": [...],           // All code particles
  "edges": [...],           // Relationships
  "stats": {
    "total_nodes": 1616,
    "total_edges": 4273,
    "coverage_percentage": 94.9
  },
  "classification": {
    "by_role": {"Test": 464, "Service": 23, ...},
    "by_kind": {"function": 1009, "class": 160, ...}
  },
  "auto_discovery": {...},
  "architecture": {...},     // "not_applied" if skipped
  "dependencies": {...},
  "antimatter": {...}
}
```

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/leolech14/standard-model-of-code.git
cd standard-model-of-code

# Install
pip install -r requirements.txt

# Analyze any repo
python3 core/unified_analysis.py /path/to/repo

# Or via CLI
python3 cli.py analyze /path/to/repo
```

---

## 📈 Coverage Results

| Repository | Particles | Coverage |
|------------|----------:|:--------:|
| Pydantic   | 14,539    | **95.2%** |
| Flask      | 1,616     | **94.9%** |
| Pytest     | 6,622     | **92.7%** |
| Requests   | 755       | **87.3%** |
| Click      | 1,552     | **84.2%** |

---

## 🗂️ Project Structure

```
core/
├── unified_analysis.py       # 🎯 Single entry point
├── tree_sitter_engine.py     # AST parsing with lossless capture
├── auto_pattern_discovery.py # Deterministic pattern matching
├── graph_type_inference.py   # Graph-based role inference
└── stats_generator.py        # Coverage & metrics

patterns/
├── particle_defs.json        # 33 particle definitions
└── canonical_types.json      # Type mappings

STANDARD_MODEL_SCHEMA.json    # ⚛️ The Periodic Table
```

---

## 🧬 Philosophy

> **"Purpose emerges from structure"**

We don't need LLMs to classify code. By analyzing:
- **What a function calls** → infer its role
- **Who calls the function** → infer its purpose
- **Its naming patterns** → confirm the classification

The architecture reveals itself through graph analysis.

---

## License

MIT
