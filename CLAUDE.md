# CLAUDE.md - Agent Instructions

> Quick reference for AI agents working on this codebase.

---

## 🌌 The Big Picture

**PROJECT_elements** is the effort to find the **basic constituents of computer programs**.

It relies on a **theoretical model** — a map — that aims to consolidate, in a **topological continuum**, all basic components of the software engineering space.

This is an **open model**: not in the sense of being freely available, but in the sense that it is **always growing and reframing its assumptions**.

### The Codespace

We call this hyper-complex, high-dimensional space the **codespace** — where all software artifacts exist and relate.

### Canonical Order (Most → Least Fundamental)

| Level | Concept | Status |
|-------|---------|--------|
| **0** | **Three Parallel Layers** (Physical, Virtual, Semantic) | 🟢 Always Green |
| **1** | **16-Level Scale** (Bit → Universe) | Backbone |
| **2** | Atoms, Dimensions, Roles | Active |
| **3** | Patterns, Violations, Predictions | Active |

---

## The Dichotomy

| | Theory | Practice |
|---|--------|----------|
| **Name** | Standard Model of Code | Collider |
| **Purpose** | The map | The tool that uses the map |
| **Question** | *What are the atoms of software?* | *How do we detect them?* |
| **Location** | `docs/`, `schema/` | `src/core/`, `cli.py` |

This is the most distinctive aspect: **theory and application live together, informing each other**.

---

## What Is Collider?

**Collider** is the implementation that applies this theory to real codebases. It generates `output.md` — a structured report optimized for LLM consumption.

## The One Command

```bash
./collider full <path> [--output <dir>]
```

**Example:**
```bash
./collider full /path/to/repo --output /tmp/analysis
```

**Output:** `<output_dir>/output.md` - The "Brain Download"

---

## What The Output Contains

| Section | What It Tells You |
|---------|-------------------|
| **IDENTITY** | Node count, edge count, dead code % |
| **CHARACTER (RPBL)** | 4-dimensional profile (Responsibility, Purity, Boundary, Lifecycle) |
| **ARCHITECTURE** | Type distribution, layer breakdown |
| **HEALTH STATUS** | Traffic-light indicators (✅⚠️❌) |
| **ACTIONABLE IMPROVEMENTS** | Prescriptive recipes with steps |
| **VISUAL REASONING** | Topology shape (Star, Mesh, Islands) |
| **DOMAIN CONTEXT** | Inferred business domain |

---

## Key Files

| File | Purpose |
|------|---------|
| `cli.py` | CLI entry point |
| `src/core/full_analysis.py` | Main pipeline orchestrator |
| `src/core/brain_download.py` | Generates `output.md` |
| `src/core/metaphor_primer.md` | LLM persona instructions |
| `src/core/topology_reasoning.py` | Shape classification |
| `src/core/semantic_cortex.py` | Domain inference |

---

## Critical Rules

### HTML Visualization Testing

**ALWAYS run the full pipeline when testing HTML output.**

```bash
./collider full . --output .collider
```

Old outputs are **stale** and will show phantom bugs. The HTML is generated from:
- `src/core/viz/assets/template.html`
- `src/core/viz/assets/styles.css`
- `src/core/viz/assets/app.js`

If you modify any of these, **regenerate** - never inspect old `.html` files.

---

## Development

```bash
# Install
pip install -e .

# Run tests
pytest tests/

# Self-check (ALWAYS use this when debugging HTML)
./collider full src/core --output /tmp/self_check
```

---

## The Philosophy

> "Collider is the architecture that allows us to see architecture."

The tool transforms invisible code structure into visible, actionable knowledge.
