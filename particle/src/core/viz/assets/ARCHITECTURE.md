# Collider Visualization Architecture

> Modularization of the 10,481-line `app.js` monolith into maintainable IIFE modules.

## Module Dependency Graph

```mermaid
graph TD
    subgraph "Phase 1: Foundation (No Dependencies)"
        CORE[core.js<br/>Constants & Utilities]
        NODE[node-accessors.js<br/>Node Property Access]
        COLOR[color-engine.js<br/>OKLCH Color System]
    end

    subgraph "Phase 2: Data Layer"
        DATA[data-manager.js<br/>Centralized Data Access]
        LEGEND[legend-manager.js<br/>Legend System]
    end

    subgraph "Phase 3: Animation System"
        REFRESH[refresh-throttle.js<br/>Throttled Updates]
        ANIM[animation.js<br/>Unified Controller]
    end

    subgraph "Phase 4: UI Components"
        SELECT[selection.js<br/>Node Selection]
        SIDEBAR[sidebar.js<br/>Sidebar Manager]
        PANELS[panels.js<br/>HUD Panels]
    end

    subgraph "Phase 5: Graph Core"
        GRAPH[graph-core.js<br/>Main Graph Ops]
        EDGE[edge-system.js<br/>Edge Coloring]
        FILE[file-viz.js<br/>File Visualization]
    end

    subgraph "Phase 6: Integration"
        MAIN[main.js<br/>Entry Point + Shims]
    end

    subgraph "Existing"
        PERF[performance.js<br/>Frame Budget & Quality]
    end

    %% Dependencies
    NODE --> DATA
    COLOR --> DATA
    COLOR --> LEGEND
    NODE --> LEGEND

    REFRESH --> ANIM
    PERF --> ANIM

    COLOR --> SELECT
    DATA --> SELECT

    DATA --> SIDEBAR
    COLOR --> SIDEBAR

    DATA --> PANELS

    DATA --> GRAPH
    COLOR --> GRAPH
    ANIM --> GRAPH
    SELECT --> GRAPH
    PERF --> GRAPH

    COLOR --> EDGE
    NODE --> EDGE

    COLOR --> FILE
    DATA --> FILE

    %% Main wires everything
    GRAPH --> MAIN
    EDGE --> MAIN
    FILE --> MAIN
    SIDEBAR --> MAIN
    PANELS --> MAIN
    SELECT --> MAIN
```

## Load Order (Concatenation Sequence)

```mermaid
flowchart LR
    subgraph "Build Time"
        PY[visualize_graph_webgl.py]
    end

    subgraph "Module Order"
        direction TB
        M1[1. performance.js]
        M2[2. core.js]
        M3[3. node-accessors.js]
        M4[4. color-engine.js]
        M5[5. data-manager.js]
        M6[6. legend-manager.js]
        M7[7. refresh-throttle.js]
        M8[8. animation.js]
        M9[9. selection.js]
        M10[10. sidebar.js]
        M11[11. panels.js]
        M12[12. edge-system.js]
        M13[13. file-viz.js]
        M14[14. graph-core.js]
        M15[15. main.js]
    end

    subgraph "Output"
        HTML[collider_report.html<br/>Single File]
    end

    PY --> M1 --> M2 --> M3 --> M4 --> M5 --> M6 --> M7 --> M8 --> M9 --> M10 --> M11 --> M12 --> M13 --> M14 --> M15 --> HTML
```

## Data Flow

```mermaid
flowchart TB
    subgraph "Python Pipeline"
        JSON[(unified_analysis.json)]
        TOKENS[(appearance.tokens.json<br/>controls.tokens.json<br/>physics.tokens.json)]
        TEMPLATE[template.html]
    end

    subgraph "HTML Generation"
        COMPRESS[gzip + base64<br/>Payload Encoding]
        INJECT[Token Injection<br/>CSS Variables]
        CONCAT[Module<br/>Concatenation]
    end

    subgraph "Browser Runtime"
        DECOMPRESS[pako.inflate<br/>Payload Decode]
        INIT[Module<br/>Initialization]
        GRAPH_RENDER[3D-Force-Graph<br/>WebGL Render]
    end

    JSON --> COMPRESS --> INJECT
    TOKENS --> INJECT
    TEMPLATE --> CONCAT
    INJECT --> CONCAT --> HTML_OUT[collider_report.html]

    HTML_OUT --> DECOMPRESS --> INIT --> GRAPH_RENDER
```

## Module Responsibilities

```mermaid
mindmap
    root((app.js<br/>Modules))
        Foundation
            CORE
                SELECTION_SIZE_MULT
                PENDULUM oscillator
                amplify utilities
            NODE
                getTier
                getFamily
                getRing
                getLayer
                getEffect
            COLOR
                OKLCH transforms
                Palette management
                Interval gradients
                Subscriptions
        Data
            DATA
                Graph indexes
                Node lookups
                Tier counts
                File groupings
            LEGEND
                Color legends
                Mode switching
                Label generation
        Animation
            REFRESH
                Throttled refresh
                Frame coalescing
                Statistics
            ANIM
                Layout transitions
                Flock simulation
                Motion loops
                Ownership mgmt
        UI
            SELECT
                Multi-select
                Visual feedback
                Modal display
            SIDEBAR
                Section collapse
                Button handlers
                Slider controls
            PANELS
                HUD positioning
                Info panels
                Stats display
        Graph
            GRAPH
                initGraph
                filterGraph
                refreshGraph
            EDGE
                Edge coloring
                Mode switching
            FILE
                File boundaries
                File colors
        Integration
            MAIN
                Window shims
                Event wiring
                Initialization
```

## IIFE Module Pattern

```mermaid
classDiagram
    class ModuleTemplate {
        +IIFE wrapper
        +use strict
        +private state
        +public API
        +backward compat shims
    }

    class CORE {
        +SELECTION_SIZE_MULT
        +PENDULUM
        +amplify(value, gamma)
        +amplifyContrast(value, strength)
    }

    class NODE {
        +getTier(node)
        +getFamily(node)
        +getRing(node)
        +getLayer(node)
        +getEffect(node)
        +normalizeTier(tier)
    }

    class COLOR {
        -palette
        -transform
        -subscribers
        +get(dimension, category)
        +getInterval(name, value)
        +setTransform(key, value)
        +subscribe(callback)
    }

    class REFRESH {
        -pending
        -lastRefresh
        -stats
        +throttled()
        +force()
        +cancel()
        +stats
    }

    class DATA {
        -graph
        -nodeIndex
        -fileIndex
        +init(graphData)
        +getNodes()
        +getLinks()
        +getNodeById(id)
        +getTierCounts()
    }

    class ANIM {
        -currentAnimation
        -ownership
        +applyLayout(preset)
        +startFlock(params)
        +stopAll()
    }

    class GRAPH {
        -Graph instance
        -filters
        +init(container, data)
        +filter(criteria)
        +refresh()
        +destroy()
    }

    ModuleTemplate <|-- CORE
    ModuleTemplate <|-- NODE
    ModuleTemplate <|-- COLOR
    ModuleTemplate <|-- REFRESH
    ModuleTemplate <|-- DATA
    ModuleTemplate <|-- ANIM
    ModuleTemplate <|-- GRAPH

    NODE --> DATA : provides accessors
    COLOR --> DATA : provides colors
    REFRESH --> GRAPH : throttles
    ANIM --> GRAPH : animates
    DATA --> GRAPH : supplies data
```

## Architecture Debt Resolution

```mermaid
flowchart LR
    subgraph "Before (Problems)"
        A1[ARCH-001<br/>No clear call structure]
        A2[ARCH-002<br/>O n² flock algorithm]
        A3[ARCH-003<br/>Unthrottled refresh]
        A4[ARCH-004<br/>Animation conflicts]
    end

    subgraph "After (Solutions)"
        B1[Module boundaries<br/>Clear dependencies]
        B2[Spatial hashing<br/>O n neighbors]
        B3[REFRESH module<br/>Frame coalescing]
        B4[ANIM ownership<br/>Single controller]
    end

    A1 --> B1
    A2 --> B2
    A3 --> B3
    A4 --> B4
```

## File Structure

```
src/core/viz/assets/
├── modules/
│   ├── core.js              # Constants, utilities
│   ├── node-accessors.js    # Node property access
│   ├── color-engine.js      # OKLCH color system
│   ├── data-manager.js      # Centralized data
│   ├── legend-manager.js    # Legend system
│   ├── refresh-throttle.js  # Throttled updates
│   ├── animation.js         # Unified animation
│   ├── selection.js         # Node selection
│   ├── sidebar.js           # Sidebar UI
│   ├── panels.js            # HUD panels
│   ├── graph-core.js        # Main graph ops
│   ├── edge-system.js       # Edge coloring
│   └── file-viz.js          # File visualization
├── performance.js           # Frame budget (existing)
├── main.js                  # Entry point + shims
├── app.js                   # DEPRECATED (delete after migration)
├── styles.css               # Component styles
└── template.html            # HTML shell
```

## Migration Strategy

```mermaid
gitGraph
    commit id: "Start"
    branch modularize
    commit id: "Phase 1: core.js"
    commit id: "Phase 1: node-accessors.js"
    commit id: "Phase 1: color-engine.js"
    commit id: "Phase 2: data-manager.js"
    commit id: "Phase 2: legend-manager.js"
    commit id: "Phase 3: refresh-throttle.js"
    commit id: "Phase 3: animation.js"
    commit id: "Phase 4: selection.js"
    commit id: "Phase 4: sidebar.js"
    commit id: "Phase 4: panels.js"
    commit id: "Phase 5: graph-core.js"
    commit id: "Phase 5: edge-system.js"
    commit id: "Phase 5: file-viz.js"
    commit id: "Phase 6: main.js"
    commit id: "Phase 6: Update Python"
    commit id: "Phase 6: Delete app.js"
    checkout main
    merge modularize id: "Complete"
```

## Verification Checklist

| Phase | Module | Test Command | Success Criteria |
|-------|--------|--------------|------------------|
| 1.1 | core.js | `./collider full . --output .collider` | No JS errors |
| 1.2 | node-accessors.js | Open HTML, check console | Tier colors work |
| 1.3 | color-engine.js | Click color mode buttons | Colors change |
| 2.1 | data-manager.js | Check node info panel | Data displays |
| 2.2 | legend-manager.js | Toggle legend | Legend updates |
| 3.1 | refresh-throttle.js | Rapid interactions | No freeze |
| 3.2 | animation.js | Apply layout presets | Smooth animation |
| 4.x | UI modules | All controls | Responsive |
| 5.x | Graph modules | Full interaction | Everything works |
| 6 | main.js | Complete test | Identical to original |

---

*Generated for Collider app.js modularization project*
