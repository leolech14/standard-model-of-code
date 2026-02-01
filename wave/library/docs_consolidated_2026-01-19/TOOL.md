# TOOL.md - Collider Reference

> **Layer:** 1 (Bible) | **Parent:** [CLAUDE.md](../CLAUDE.md) | **Index:** [INDEX.md](INDEX.md)
> **Children:** [ARCHITECTURE.md](ARCHITECTURE.md), [COMMANDS.md](COMMANDS.md)
> **Purpose:** Complete reference for the Collider implementation

---

## What Is Collider?

Collider is the tool that applies the Standard Model of Code to real codebases. It transforms invisible code structure into visible, actionable knowledge.

**Name Origin:** Like a particle collider reveals fundamental particles, Collider reveals the "atoms" of code.

**Previous Name:** Spectrometer (renamed 2026-01-11)

---

## The One Command

```bash
./collider full <path> --output <dir>
```

**Example:**
```bash
./collider full /path/to/repo --output /tmp/analysis
```

**With AI Insights:**
```bash
./collider full /path/to/repo --output /tmp/analysis --ai-insights
```

---

## Output Files

| File | Purpose | Format |
|------|---------|--------|
| `unified_analysis.json` | Structured graph data | JSON |
| `output.md` | Brain Download report | Markdown |
| `collider_report.html` | Interactive 3D visualization | HTML |

---

## Complete Command Reference

### Primary Commands

| Command | Purpose |
|---------|---------|
| `./collider full <path>` | Complete 12-stage analysis |
| `./collider full <path> --output <dir>` | Analysis with custom output |
| `./collider full <path> --ai-insights` | Analysis with LLM enrichment |
| `./collider analyze <path>` | Canonical analysis (alias) |

### Graph Commands

| Command | Purpose |
|---------|---------|
| `./collider graph <json>` | Analyze existing graph |
| `./collider graph <json> --bottlenecks` | Bottleneck analysis |
| `./collider graph <json> --shortest-path <a:b>` | Path between nodes |

### Visualization Commands

| Command | Purpose |
|---------|---------|
| `./collider viz <json>` | Generate HTML visualization |
| `./collider viz <json> --3d` | 3D visualization |

### Diagnostic Commands

| Command | Purpose |
|---------|---------|
| `./collider doctor <path>` | Pipeline + output validation |

### All Flags

| Flag | Description |
|------|-------------|
| `--output`, `-o` | Output directory |
| `--ai-insights` | Enable LLM layer |
| `--verbose`, `-v` | Detailed logging |
| `--timing` | Pipeline timing |
| `--verbose-timing` | Per-stage timing |
| `--bottlenecks` | Bottleneck analysis only |
| `--3d` | 3D visualization |
| `--help`, `-h` | Show help |

---

## Architecture

### Two-Layer System

```
+-----------------------------------------------------+
|  LAYER 1: DETERMINISTIC CORE (The Intelligence)     |
|  - Atomic Theory: 94 atoms, 4 phases, 16 families   |
|  - Role Theory: 29 canonical roles                  |
|  - Layer Theory: Domain, Application, Infra, UI    |
|  - Antimatter Laws: Violation detection             |
|  - RPBL Scoring, Topology Classification            |
|  - Dead Code Detection, Coupling Analysis           |
|  STATUS: FULLY IMPLEMENTED                          |
+-----------------------------------------------------+
|  LAYER 2: LLM ENRICHMENT (Optional)                 |
|  - Pattern narratives                               |
|  - Refactoring suggestions                          |
|  - Risk explanations                                |
|  PROVIDERS: Vertex AI Gemini, Ollama                |
|  STATUS: IMPLEMENTED (--ai-insights)                |
+-----------------------------------------------------+
```

**Key Insight:** The deterministic layer IS the intelligence. LLM is optional amplification.

### The 12-Stage Pipeline

| Stage | Name | Produces |
|-------|------|----------|
| 1 | Classification | atoms |
| 2 | Role Detection | roles |
| 3 | Antimatter Detection | violations |
| 4 | Predictions | missing components |
| 5 | Insights Engine | recommendations |
| 6 | Purpose Field | layers |
| 7 | Execution Flow | reachable_set, orphans |
| 8 | Performance Analysis | hotspots |
| 9 | Visualization | HTML report |
| 10 | Export | unified_analysis.json |
| 11 | Brain Download | output.md |
| 12 | Topology | shape classification |

---

## Output Sections (Brain Download)

| Section | What It Contains |
|---------|------------------|
| IDENTITY | Node count, edge count, dead code % |
| CHARACTER (RPBL) | 4-dimensional behavioral profile |
| ARCHITECTURE | Type distribution, layer breakdown |
| HEALTH STATUS | Traffic-light indicators |
| ACTIONABLE IMPROVEMENTS | Prescriptive recipes |
| VISUAL REASONING | Topology shape |
| DOMAIN CONTEXT | Inferred business domain |
| AI INSIGHTS | LLM analysis (if enabled) |

---

## Key Source Files

| File | Purpose |
|------|---------|
| `cli.py` | CLI entry point |
| `src/core/full_analysis.py` | 12-stage pipeline orchestrator |
| `src/core/unified_analysis.py` | Core graph generation |
| `src/core/brain_download.py` | Markdown report generation |
| `src/core/atom_loader.py` | Unified atom taxonomy loader |
| `src/core/atom_classifier.py` | Code entity classifier |
| `src/core/heuristic_classifier.py` | Role assignment |
| `src/core/topology_reasoning.py` | Shape classification |
| `tools/visualize_graph_webgl.py` | HTML visualization |

### Configuration Files

| File | Purpose |
|------|---------|
| `src/patterns/atoms.json` | 14 base atom definitions |
| `src/patterns/ATOMS_TIER0_CORE.yaml` | 42 T0 atoms |
| `src/patterns/ATOMS_TIER1_STDLIB.yaml` | 21 T1 atoms |
| `src/patterns/ATOMS_TIER2_ECOSYSTEM.yaml` | 17 T2 atoms |
| `src/patterns/canonical_types.json` | Type definitions |
| `schema/fixed/roles.json` | 33 role definitions |

### Visualization Assets

| File | Purpose |
|------|---------|
| `src/core/viz/assets/template.html` | HTML template |
| `src/core/viz/assets/styles.css` | Styles |
| `src/core/viz/assets/app.js` | Interactive logic |

---

## Development

### Setup

```bash
# Install in dev mode
pip install -e .

# Run tests
pytest tests/ -q

# Self-check
./collider full . --output .collider
```

### Testing HTML Changes

**CRITICAL:** Always regenerate after modifying visualization files:

```bash
./collider full . --output .collider
```

Never trust old `.html` outputs - they are stale.

### LLM Integration

```bash
# Authenticate
gcloud auth application-default login

# Run with AI insights
./collider full . --ai-insights --output .collider
```

**What LLM Receives:** Structured metrics (node counts, topology shape, hub names)

**What LLM Does NOT Receive:** Actual source code

---

## Data Structures

### Node Schema

```json
{
  "id": "UserService.validate",
  "name": "validate",
  "kind": "method",
  "role": "Validator",
  "layer": "Application",
  "file_path": "src/services/user.py",
  "start_line": 45,
  "end_line": 67,
  "body_source": "def validate(self, data):\n    ...",
  "complexity": 8
}
```

### Edge Schema

```json
{
  "source": "UserController.create",
  "target": "UserService.validate",
  "edge_type": "calls"
}
```

### Canonical Schema (Minimal)

**Nodes:** `id, name, kind, role, layer`

**Edges:** `source, target, edge_type`

---

## The Bidirectionality Vision

### Current: Analysis Only

```
Codebase  ======>  Collider  ======>  Codespace (graph)
```

### Target: Full Bidirectionality

```
Codebase  <=====>  Collider  <=====>  Codespace (graph)
                                            |
                                       MANIPULATE
                                       (move, merge,
                                        extract, rewire)
```

**The Vision:** Manipulate the graph, then deterministically reconstruct the codebase.

**Status:** Synthesis layer NOT YET IMPLEMENTED.

**Node Body Coverage:** Currently ~36%, target 90%+

---

## Common Workflows

### Quick Analysis
```bash
./collider full . --output .collider
open .collider/collider_report.html
```

### Find Bottlenecks
```bash
./collider full . --output analysis
./collider graph analysis/unified_analysis.json --bottlenecks
```

### Find Path Between Functions
```bash
./collider graph analysis/unified_analysis.json --shortest-path main:validate
```

### Self-Check (Debugging)
```bash
./collider full src/core --output /tmp/self_check
```

---

## Metrics Reference

### RPBL Dimensions

| Dimension | Low (1) | High (9) |
|-----------|---------|----------|
| Responsibility | Single purpose | Omnibus |
| Purity | No side effects | Heavy I/O |
| Boundary | Internal only | External APIs |
| Lifecycle | Ephemeral | Singleton |

### Topology Shapes

| Shape | Description |
|-------|-------------|
| Star | Central hub with spokes |
| Hierarchical | Tree-like structure |
| Mesh | Highly interconnected |
| Islands | Disconnected clusters |
| Layered | Clear architectural layers |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| HTML shows wrong data | Regenerate: `./collider full . --output .collider` |
| LLM not working | Run `gcloud auth application-default login` |
| Import errors | Install: `pip install -e .` |
| Test failures | Check Python version (3.10+) |

---

## Version History

| Date | Event |
|------|-------|
| 2025-12-14 | Initial commit (Spectrometer v12) |
| 2025-12-23 | THE PIVOT: AI → Deterministic |
| 2026-01-11 | Rebrand: Spectrometer → Collider |
| 2026-01-19 | Atom integration (94 atoms unified) |

---

## See Also

- `docs/THEORY.md` - Standard Model theory reference
- `docs/ARCHITECTURE.md` - Detailed architecture docs
- `docs/registry/HISTORY.md` - Full project timeline
