# Collider Modular Architecture

> Token Management & Data Flow Design Documentation

---

## System Overview

```mermaid
flowchart TB
    subgraph INPUT["INPUT"]
        SOURCE[("Source Code")]
    end

    subgraph PARSING["STAGE 1: PARSING"]
        TSE["tree_sitter_engine.py"]
        PYE["python_extractor.py"]
        UC["universal_classifier.py"]

        TSE --> PYE
        TSE --> UC
    end

    subgraph UNIFIED["STAGE 2-6: UNIFIED ANALYSIS"]
        UA["unified_analysis.py"]

        subgraph STAGES["Pipeline Stages"]
            S1["1: AST Parse"]
            S2["2: RPBL Classification"]
            S3["3: Auto Pattern Discovery"]
            S4["4: Edge Extraction"]
            S5["5: Graph Inference"]
            S6["6: Unified Output"]
        end

        EE["edge_extractor.py"]

        S1 --> S2 --> S3 --> S4 --> S5 --> S6
        S4 -.-> EE
    end

    subgraph DM["DATA MANAGEMENT"]
        CS["CodebaseState"]

        subgraph INDEXES["O1 Indexes"]
            BY_FILE["_by_file"]
            BY_RING["_by_ring"]
            BY_KIND["_by_kind"]
            BY_ROLE["_by_role"]
        end
    end

    subgraph ENRICHMENT["SEMANTIC ENRICHMENT"]
        SME["standard_model_enricher"]
        PF["purpose_field"]
        EF["execution_flow"]
        PP["performance_predictor"]
        TR["topology_reasoning"]
        SC["semantic_cortex"]
    end

    subgraph FULL["FULL ANALYSIS"]
        FA["full_analysis.py"]

        subgraph COMPUTE["Computations"]
            MM["Markov Matrix"]
            KD["Knot Detection"]
            DF["Data Flow"]
            FI["File Index"]
        end
    end

    subgraph TOKENS["DESIGN TOKENS"]
        AT["appearance.tokens.json"]
        CT["controls.tokens.json"]
        TRSV["TokenResolver"]
    end

    subgraph VIZ["VISUALIZATION"]
        AE["AppearanceEngine"]
        CE["ControlsEngine"]
        PE["PhysicsEngine"]
    end

    subgraph OUTPUT["OUTPUT"]
        OG["output_generator"]
        NO["normalize_output"]
        BD["brain_download"]
        JSON[("JSON")]
        HTML[("HTML")]
    end

    SOURCE --> TSE
    TSE --> UA
    UA --> CS
    CS --> FA

    FA --> SME
    FA --> PF
    FA --> EF
    FA --> PP
    FA --> TR
    FA --> SC

    SME --> CS
    PF --> CS
    EF --> CS

    FA --> MM
    FA --> KD
    FA --> DF
    FA --> FI

    AT --> TRSV
    CT --> TRSV
    TRSV --> AE
    TRSV --> CE

    CS --> OG
    OG --> NO
    OG --> AE
    OG --> CE
    OG --> PE
    OG --> BD

    NO --> JSON
    AE --> HTML
    CE --> HTML
    PE --> HTML
    BD --> JSON
```

---

## Data Structures Flow

```mermaid
flowchart LR
    subgraph PARTICLES["Raw Particles"]
        P1["id, kind, file_path, params, return_type"]
    end

    subgraph UNIFIED_NODE["UnifiedNode"]
        UN["+ role, confidence, discovery_method, in/out_degree, layer"]
    end

    subgraph ENRICHED_NODE["Enriched Node"]
        EN["+ rpbl, atom, dimensions, ring, purpose"]
    end

    subgraph VIZ_NODE["Viz-Ready Node"]
        VN["+ color, size, opacity, fileIdx, x, y"]
    end

    P1 -->|unified_analysis| UN
    UN -->|enricher + purpose_field| EN
    EN -->|appearance + physics| VN
```

---

## Token Resolution Flow

```mermaid
flowchart TB
    subgraph SCHEMA["schema/viz/tokens/"]
        APP["appearance.tokens.json"]
        CTL["controls.tokens.json"]
    end

    subgraph RESOLVER["TokenResolver Singleton"]
        LOAD["Load JSON on init"]
        CACHE["Cache in memory"]
        DOT["Dot-notation lookup"]
    end

    subgraph ENGINES["Visualization Engines"]
        AE2["AppearanceEngine"]
        CE2["ControlsEngine"]
    end

    subgraph HTML_OUT["HTML Output"]
        STYLE["CSS: colors, sizes"]
        JS["JS: panels, buttons"]
        WEBGL["WebGL: nodes, edges"]
    end

    APP --> LOAD
    CTL --> LOAD
    LOAD --> CACHE
    CACHE --> DOT
    DOT --> AE2
    DOT --> CE2
    AE2 --> STYLE
    AE2 --> WEBGL
    CE2 --> JS
```

---

## 12-Stage Full Analysis Pipeline

```mermaid
flowchart TD
    subgraph STAGE_1_6["Unified Analysis"]
        S1["1: AST Parse"]
        S2["2: RPBL Classification"]
        S3["3: Auto Pattern Discovery"]
        S4["4: Edge Extraction"]
        S5["5: Graph Inference"]
        S6["6: Unified Output"]

        S1 --> S2 --> S3 --> S4 --> S5 --> S6
    end

    subgraph STAGE_7_12["Full Analysis"]
        S7["7: Standard Model Enrichment"]
        S8["8: Purpose Field"]
        S9["9: Execution Flow"]
        S10["10: Markov + Knots"]
        S11["11: Topology + Semantics"]
        S12["12: Output Generation"]

        S7 --> S8 --> S9 --> S10 --> S11 --> S12
    end

    S6 --> S7
```

---

## CodebaseState Data Management

```mermaid
classDiagram
    class CodebaseState {
        +Dict nodes
        +List edges
        +Dict metadata
        -Dict _by_file
        -Dict _by_ring
        -Dict _by_kind
        -Dict _by_role
        -Dict _edges_from
        -Dict _edges_to
        +load_initial_graph()
        +enrich_node()
        +get_node()
        +get_by_file()
        +get_by_ring()
        +get_edges_from()
        +validate()
        +export()
    }

    class UnifiedNode {
        +str id
        +str name
        +str kind
        +str file_path
        +int start_line
        +int end_line
        +str role
        +float role_confidence
        +str discovery_method
        +List params
        +str return_type
        +int complexity
        +int in_degree
        +int out_degree
        +str layer
        +Dict rpbl
        +str atom
        +Dict dimensions
    }

    class UnifiedEdge {
        +str source
        +str target
        +str edge_type
        +float weight
        +float confidence
        +str resolution
        +Dict metadata
    }

    CodebaseState "1" *-- "*" UnifiedNode
    CodebaseState "1" *-- "*" UnifiedEdge
```

---

## Visualization Token System

```mermaid
flowchart LR
    subgraph TOKENS["Design Tokens"]
        subgraph APPEARANCE["appearance.tokens.json"]
            COLOR["color: node, edge"]
            SIZE["size: small, medium, large"]
            OPACITY["opacity: active, inactive"]
        end

        subgraph CONTROLS["controls.tokens.json"]
            PANELS["panels: metrics, fileInfo, report"]
            BUTTONS["buttons: datamaps, modes"]
            SLIDERS["sliders: threshold, zoom"]
        end
    end

    subgraph RESOLVER["TokenResolver"]
        GET["get_resolver singleton"]
        APP_FN["appearance path default"]
        CTL_FN["controls path default"]
    end

    subgraph USAGE["Usage Examples"]
        EX1["color.edge.calls = #0066cc"]
        EX2["panels.metrics.visible = true"]
        EX3["size.node.large = 3.0"]
    end

    APPEARANCE --> GET
    CONTROLS --> GET
    GET --> APP_FN
    GET --> CTL_FN
    APP_FN --> EX1
    APP_FN --> EX3
    CTL_FN --> EX2
```

---

## Module Dependency Matrix

| Module | Depends On | Produces |
|--------|-----------|----------|
| `tree_sitter_engine.py` | `parser/*`, `classification/*` | Raw particles |
| `unified_analysis.py` | `tree_sitter_engine`, `edge_extractor` | `UnifiedAnalysisOutput` |
| `edge_extractor.py` | particles | edges with resolution |
| `data_management.py` | - | `CodebaseState` (indexed) |
| `standard_model_enricher.py` | `schema/fixed/*` | RPBL, atoms, dimensions |
| `purpose_field.py` | nodes, edges | layer assignments |
| `execution_flow.py` | nodes, edges | entry points, orphans |
| `full_analysis.py` | all enrichment modules | `full_output` dict |
| `token_resolver.py` | `schema/viz/tokens/*` | resolved token values |
| `appearance_engine.py` | `token_resolver` | colored nodes/edges |
| `controls_engine.py` | `token_resolver` | UI panel config |
| `output_generator.py` | all above | JSON + HTML files |

---

## Key File Paths

| Component | Path |
|-----------|------|
| **Entry Point** | `cli.py` |
| **Full Analysis** | `src/core/full_analysis.py` |
| **Unified Analysis** | `src/core/unified_analysis.py` |
| **Data Management** | `src/core/data_management.py` |
| **Edge Extractor** | `src/core/edge_extractor.py` |
| **Standard Model Enricher** | `src/core/standard_model_enricher.py` |
| **Purpose Field** | `src/core/purpose_field.py` |
| **Execution Flow** | `src/core/execution_flow.py` |
| **Topology Reasoning** | `src/core/topology_reasoning.py` |
| **Semantic Cortex** | `src/core/semantic_cortex.py` |
| **Token Resolver** | `src/core/viz/token_resolver.py` |
| **Appearance Engine** | `src/core/viz/appearance_engine.py` |
| **Controls Engine** | `src/core/viz/controls_engine.py` |
| **Output Generator** | `src/core/output_generator.py` |
| **Brain Download** | `src/core/brain_download.py` |
| **Appearance Tokens** | `schema/viz/tokens/appearance.tokens.json` |
| **Controls Tokens** | `schema/viz/tokens/controls.tokens.json` |

---

## Canonical Data Conventions

| Convention | Format | Example |
|------------|--------|---------|
| **Node ID** | `file_path::qualified_name` | `src/core/service.py::MyService.run` |
| **Confidence** | 0.0 - 1.0 (never 0-100) | `0.92` |
| **Atom** | `RING.SUB.TIER` | `LOG.SRV.A` |
| **Rings** | LOG, DAT, ORG, EXE, EXT | `LOG` |
| **Tiers** | T0, T1, T2, M, A, C, U | `A` |
| **Edge Types** | calls, imports, contains, inherits | `calls` |
| **Resolution** | resolved_internal, external, unresolved | `resolved_internal` |

---

## Design Patterns Used

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Facade** | `TreeSitterUniversalEngine` | Wraps parser + classifier |
| **Singleton** | `TokenResolver.get_resolver()` | Single token cache |
| **Strategy** | `AppearanceEngine` color modes | tier/ring/file coloring |
| **Pipeline** | `unified_analysis`, `full_analysis` | Sequential stages |
| **DTO** | `UnifiedNode`, `UnifiedEdge` | Fixed data contracts |
| **Index/Cache** | `CodebaseState._by_*` | O(1) lookups |

---

## Node Schema

```json
{
  "id": "src/core/file.py::ClassName.method_name",
  "name": "method_name",
  "kind": "method",
  "file_path": "/full/path/to/file.py",
  "start_line": 42,
  "end_line": 105,
  "role": "Service",
  "role_confidence": 0.92,
  "discovery_method": "pattern",
  "params": [{"name": "x", "type": "int"}],
  "return_type": "str",
  "complexity": 3,
  "in_degree": 5,
  "out_degree": 3,
  "layer": "application",
  "ring": "LOG",
  "atom": "LOG.SRV.A",
  "rpbl": {
    "responsibility": 7,
    "purity": 8,
    "boundary": 4,
    "lifecycle": 6
  },
  "dimensions": {
    "D1_WHAT": "LOG.SRV",
    "D1_ECOSYSTEM": "python",
    "D2_PURPOSE": "service"
  },
  "color": "#ff6b6b",
  "size": 2.4,
  "fileIdx": 3
}
```

---

## Edge Schema

```json
{
  "source": "src/core/file.py::Service.method",
  "target": "src/core/other.py::Repository.query",
  "edge_type": "calls",
  "weight": 1.0,
  "confidence": 0.95,
  "resolution": "resolved_internal",
  "file_path": "src/core/file.py",
  "line": 42,
  "markov_weight": 0.33
}
```

---

*Generated: 2026-01-18*
