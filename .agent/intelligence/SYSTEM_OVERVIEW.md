# PROJECT_elements: System Overview (SPIRAL 0: ORBIT)

**Cartography Level:** SPIRAL 0 - ORBIT (Highest-level external view)
**Generated:** 2026-02-02
**Confidence:** HIGH (based on REPO_STRUCTURE.json, DOMAINS.yaml, ROADMAP.md, theory docs)

---

## 1. Identity

**Name:** PROJECT_elements (also known as "Standard Model of Code" or "SMC")

**One-Sentence Summary:**
A reference model and toolchain for AI-assisted code understanding that classifies software entities into structured coordinates, enabling AI agents to comprehend code as architecture rather than text.

---

## 2. Purpose & Value Proposition

### What It Is
PROJECT_elements is NOT a scientific discovery claiming universal laws about software. It is a **practical reference model** - a constrained invention that provides:

1. **Structured Vocabulary:** 167 atom types for classifying code entities (functions, classes, modules)
2. **8 Dimensional Coordinates:** Classification axes (Role, Layer, Ring, Purity, etc.)
3. **16 Scale Levels:** From Bit (L-3) to Universe (L12)
4. **Working Toolchain:** "Collider" - a 28-stage analysis pipeline

### Why It Exists
**The Problem:** AI agents consume code as unstructured text. They lack a shared vocabulary for discussing code architecture, leading to:
- Context window waste (verbose explanations of structure)
- Inconsistent understanding across sessions
- No interoperability between tools

**The Solution:** SMC provides machine-actionable structure that compresses context. Instead of explaining "this is a data access layer class that handles database operations," an AI can receive `{role: Repository, layer: Infrastructure, ring: Core}`.

### Success Metric
**UTILITY, not TRUTH.** Does the classification help AI agents work more effectively with code? If yes, the model succeeds.

---

## 3. Architecture (Trinity)

PROJECT_elements is organized into three layers that mirror its own theory:

```
┌─────────────────────────────────────────────────────────────┐
│                      OBSERVER                               │
│                (How we SEE the system)                      │
│         observer/ - Control Room UI, dashboards             │
├─────────────────────────────────────────────────────────────┤
│                        WAVE                                 │
│              (What the code MEANS)                          │
│    wave/ - AI tools, context refinement, intelligence       │
├─────────────────────────────────────────────────────────────┤
│                      PARTICLE                               │
│               (What the code IS)                            │
│  particle/ - Collider engine, schemas, type definitions     │
└─────────────────────────────────────────────────────────────┘
```

### PARTICLE Layer (`particle/`)
**Purpose:** Code structure analysis engine
**Key Components:**
- `cli.py` - Main entry point (Collider CLI)
- `src/core/full_analysis.py` - 28-stage analysis pipeline
- `src/patterns/*.yaml` - 167 atom type definitions (T0/T1/T2)
- `schema/` - Type constraints, crosswalks, ground truth
- `docs/theory/` - Theoretical foundations (axioms, definitions, principles)

**Output:** JSON graph of code entities with dimensional coordinates

### WAVE Layer (`wave/`)
**Purpose:** AI integration and context management
**Key Components:**
- `tools/ai/analyze.py` - Multi-model AI analysis (Gemini, Claude, Cerebras)
- `tools/ai/aci/refinery.py` - Context atomization pipeline
- `intelligence/` - AI-generated knowledge artifacts
- `data/` - Enriched outputs, repo maps, tags

**Output:** Refined context chunks for AI consumption

### OBSERVER Layer (`observer/`)
**Purpose:** Human interface and monitoring
**Key Components:**
- `merged/` - Combined File Explorer + Dashboard
- `frontend/` - React/Vite dashboard
- `backend/` - FastAPI server

**Output:** Visual exploration of Collider results

---

## 4. Key Artifacts

### Schemas & Definitions
| Artifact | Location | Purpose |
|----------|----------|---------|
| 167 Atom Types | `particle/src/patterns/ATOMS_*.yaml` | Entity classification |
| 8 Dimensions | `particle/schema/fixed/dimensions.json` | Classification axes |
| 16 Levels | `particle/schema/fixed/levels.json` | Scale hierarchy |
| Constraints | `particle/schema/constraints/` | Validation rules |

### Theory Documents
| Document | Location | Purpose |
|----------|----------|---------|
| L0 Axioms | `particle/docs/theory/L0_AXIOMS.md` | Foundational assumptions |
| L1 Definitions | `particle/docs/theory/L1_DEFINITIONS.md` | Core terms |
| L2 Principles | `particle/docs/theory/L2_PRINCIPLES.md` | Behavioral patterns |
| L3 Applications | `particle/docs/theory/L3_APPLICATIONS.md` | Practical usage |
| Predictions | `particle/docs/theory/PREDICTIONS.md` | 16 falsifiable claims |

### Governance
| Document | Location | Purpose |
|----------|----------|---------|
| ROADMAP | `governance/ROADMAP.md` | Path to v1.0.0 |
| DECISIONS | `governance/DECISIONS.md` | Architecture decisions |
| QUALITY_GATES | `governance/QUALITY_GATES.md` | G1-G10 checkpoints |

---

## 5. Statistics

| Metric | Value |
|--------|-------|
| Total files (estimated) | ~21,000 |
| Particle layer | ~13,092 files |
| Wave layer | ~7,629 files |
| Observer layer | ~89 files |
| Python code (sampled) | 35,000+ lines |
| Atom types | 167 |
| Dimensions | 8 |
| Scale levels | 16 |
| Pipeline stages | 28 |
| Tests passing | 406 |

---

## 6. Current State (2026-02-02)

### Maturity
- **Theory:** Complete (L0-L3 documented, 16 falsifiable predictions stated)
- **Implementation:** Working (Collider runs, 28 stages functional)
- **Validation:** Partial (5/16 predictions verified, empirical studies pending)
- **Documentation:** 25% toward v1.0.0 quality gates

### Active Work
- Documentation reframing: "scientific discovery" → "practical reference model"
- Quality gate fixes (count drift, broken links, placeholders)
- Verification tooling automation

### Known Issues
- 14 broken documentation links
- Count drift between indexes and registries
- 733/788 active docs have no internal links (orphans)

---

## 7. Who Built It & Why

**Creator:** Leonardo Lech
**Primary Tool:** Claude Code CLI (AI-assisted development)
**Supporting AI:** Gemini, Cerebras, Perplexity

**Motivation:** Enable AI agents to understand code architecturally, not just textually. The explosion of AI coding assistants revealed that they lack structural vocabulary - they can read code but can't efficiently discuss its architecture. SMC provides that vocabulary.

**Target Users:**
1. **AI Agents** - Primary consumers (machine-readable classification)
2. **Developers** - Secondary (clarity through structured thinking)
3. **Researchers** - Tertiary (testable framework for code structure)

---

## 8. How to Use It

### Quick Start
```bash
# Analyze a codebase with Collider
./collider full /path/to/repo --output /tmp/analysis

# View results
open /tmp/analysis/output.html

# AI-assisted analysis
python wave/tools/ai/analyze.py --set body "explain the architecture"
```

### Key Commands
```bash
./pe deck          # View task deck
./pe verify v1     # Run quality gates
pytest tests/ -q   # Run tests
```

---

## 9. SPIRAL 0 Gaps (To Investigate in Deeper Spirals)

### UNKNOWN: Implementation Details
- Exact atom classification algorithms
- Pipeline stage implementations
- Edge case handling

### UNKNOWN: Data Flow
- How Collider output feeds Wave tools
- Observer data consumption patterns
- Cross-layer interfaces

### UNKNOWN: Operational Aspects
- Deployment patterns
- Performance characteristics
- Error recovery

---

## Next Spiral: SPIRAL 1 (ATMOSPHERE)

The next investigation level will explore the three subsystems in more detail:
- PARTICLE_MAP.md - Collider deep dive
- WAVE_MAP.md - AI/Context layer
- OBSERVER_MAP.md - Control Room UI

---

*Part of the Cerebras Cartography Protocol. See `CEREBRAS_CARTOGRAPHY_PROTOCOL.md` for methodology.*
