# Frontend Subsystem Registry: System of Systems (SOS)

> **Role:** Functional Anatomy (Physiology/Role)
> **Holarchy Position:** Part of **S1 (Collider)** in [LOL](file://.agent/intelligence/LOL.yaml).
> **Status:** ACTIVE
> **Updated:** 2026-01-27
> **Context:** Collider Frontend Architecture
> **Theory:** "Systems of Systems" (SoS) - Biological Analogy

This registry maps the frontend modules of the Collider tool, organized by their physiological role within the "Social Organism" of code. It serves as the **Functional Anatomy** view of the Projectome.

---

## Summary of Systems

| System | Role | Count | Key Modules |
|----------|------|-------|-------------|
| **1. Information Fabric** | Signaling & State | 6 | `event-bus.js`, `vis-state.js` |
| **2. Sensory & Interface** | UX & Interaction | 12 | `sidebar.js`, `control-bar.js` |
| **3. Metabolic Heart** | Data & Safety | 5 | `data-manager.js`, `circuit-breaker.js` |
| **4. Visual Anatomy** | Rendering & Form | 10 | `color-engine.js`, `file-viz.js` |
| **5. Kinetic Engine** | Physics & Layout | 5 | `animation.js`, `physics.js` |
| **6. The UPB Nervous System** | Property Binding | 7 | `upb/`, `property-query.js` |
| **7. Ontological Foundation** | Core & Metadata | 8 | `core.js`, `node-accessors.js` |
| **8. Flow Substances** | Aesthetics & Dynamics | 2 | `AquarelaBackground`, `AquarelaButton` |
| **TOTAL** | | **55** | |

---

## 1. Information Fabric (Communications & State)
*The signaling network that coordinates behavior across systems.*

| Module | Purpose | Notes |
|--------|---------|-------|
| `event-bus.js` | Global pub/sub messaging | Legacy bus |
| `event-bus-v2.js` | Typed, high-performance signaling | Modern bus |
| `refresh-throttle.js` | Throttled graph update orchestration | Prevents layout thrashing |
| `vis-state.js` | Master visualization state (zoom, filters) | Source of truth for UI |
| `filter-state.js` | Persistent filter configurations | Syncs with localStorage |
| `visibility.js` | Global visibility management | Toggles node/group groups |

---

## 2. Sensory & Interface (UX & Input)
*The boundary layer where the user interacts with the projectome.*

| Module | Purpose | Notes |
|--------|---------|-------|
| `sidebar.js` | Main control panel container | "The Command Center" |
| `panels.js` | Floating information windows | Details on nodes/clusters |
| `panel-system.js` | Modular Gridstack-based panel manager | Docking/Resizing logic |
| `panel-handlers.js` | Event listeners for dynamic panels | Logic for specific panel types |
| `control-bar.js` | Centered floating visual mapper | Floating glassmorphic component |
| `ui-manager.js` | Orchestrator for complex UI transitions | "The Stage Manager" |
| `ui-builders.js` | Reusable DOM fragment generators | HTML templates for buttons/swatches |
| `legend-manager.js` | Map legend UI & interactive filtering | Cross-references data colors |
| `tooltips.js` | Contextual hover metadata | Light-weight info display |
| `hover.js` | Hover interaction logic | Highlighting & ripple triggering |
| `hud.js` | "Heads-Up Display" overlays | Non-intrusive status info |
| `report.js` | Integrated Markdown report renderer | Shows summary.md in-app |

---

## 3. Metabolic Heart (Data & Homeostasis)
*The internal maintenance systems ensuring flow and safety.*

| Module | Purpose | Notes |
|--------|---------|-------|
| `data-manager.js` | Master data ingestion & indexing | Handles unified_analysis.json |
| `datamap.js` | Fast-lookup map of node/edge pointers | O(1) access to entities |
| `circuit-breaker.js` | Fault tolerance & error isolation | Prevents UI crashes from bad data |
| `perf-monitor.js` | Real-time FPS & memory tracking | Homeostatic feedback loop |
| `perf-telemetry.js` | (Inferred) Performance logging | |

---

## 4. Visual Anatomy (Rendering & Form)
*The morphological systems that turn data into physical form.*

| Module | Purpose | Notes |
|--------|---------|-------|
| `color-engine.js` | OKLCH-based perceptual color system | Master of "Semantic Pixels" |
| `color-helpers.js` | Conversions & palette generators | Linear/Discrete mixing logic |
| `color-contract-test.js`| Verification of color uniformity | Ensures ΔE consistency |
| `file-color-model.js` | Maps tiers/roles to hues | Semantic color defaults |
| `edge-system.js` | Logic for edge rendering & modes | Flow, containment, calls |
| `file-viz.js` | High-level file visualization modes | Switches between map/graph |
| `hull-visualizer.js` | Organic membrane rendering | Uses SDF shaders for hulls |
| `spatial.js` | Coordinate systems & bounding boxes | 3D space management |
| `groups.js` | Cluster & Group logic | Spatial partitioning |
| `theme.js` | Visual theme definitions | (Muted/Functional direction) |

---

## 5. Kinetic Engine (Simulation & Forces)
*The physiological systems of movement and tension.*

| Module | Purpose | Notes |
|--------|---------|-------|
| `animation.js` | Layout transition controller | Smooth camera/node movement |
| `layout.js` | High-level layout mode manager | Grid, Force, Radial, Axial |
| `layout-forces.js` | D3 Force-directed logic | Tension & repulsion params |
| `layout-helpers.js` | Math for 3D positioning | Plane fitting & centering |
| `physics.js` | Low-level physics engine hooks | Interface to 3d-force-graph |

---

## 6. The UPB Nervous System (Property Binding)
*The intelligence layer connecting attributes to visual channels.*

| Module | Purpose | Notes |
|--------|---------|-------|
| `upb/index.js` | UPB Central Orchestrator | Wires sources to targets |
| `upb/bindings.js` | Active binding ledger | Tracks "What drives What" |
| `upb/scales.js` | Normalization functions | Linear, Log, Sqrt, Inverse |
| `upb/endpoints.js` | Data adapters & Visual targets | Definition of I/O ports |
| `upb/blenders.js` | Conflict resolution (Max/Min/Avg) | Multi-source blending |
| `property-query.js` | Declarative data fetching engine | Safe access to nested attrs |
| `property-query-init.js`| Default mappings & discovery | Auto-population of mapper |

---

## 7. Ontological Foundation (Core & Metadata)
*The "DNA" and fundamental building blocks of the frontend.*

| Module | Purpose | Notes |
|--------|---------|-------|
| `main.js` | Central module integration entry | Wires everything together |
| `core.js` | Universal constants & configuration | Architectural axioms |
| `utils.js` | Low-level JS/DOM utilities | String/Number formatting |
| `node-accessors.js` | Functional property getters | Standardized node access |
| `node-helpers.js` | Semantic classification logic | Role/Tier detection helpers |
| `vis-schema.js` | Interface & Type definitions | Documentation of data shapes |
| `registry.js` | Base class for system registries | Generic "List of Lists" tracker |
| `theory.js` | Runtime theory validation | Checks implementation against MD |

---

## System of Systems (SoS) Insights

### 1. The Strange Loop
The `registry.js` and `registry/` sub-subsystems (e.g., `ControlRegistry.js`) manage themselves using the same patterns defined in the `REGISTRY_OF_REGISTRIES.md`. This represents a closed-loop architectural integrity.

### 2. The DTE (Data Trade Exchange)
As defined in `UI_REFACTOR_VISION.md`, the `UPB` and `Color Engine` are trending towards full integration into a **DTE** clearinghouse, where `upb/endpoints.js` acts as the "Market Maker" for data values.

### 3. Holographic Socratic Layer (HSL)
The `theory.js` module performs real-time drift detection, ensuring the running JavaScript "knows" and respects the theoretical constraints defined in the Contextome (`docs/`).

---

## 8. Flow Substances (Aesthetics & Dynamics)
*The expressive layer that provides movement and biological feel.*

| Module | Purpose | Notes |
|--------|---------|-------|
| `aquarela.js` | Global watercolor/ink background | Procedural fluid dynamics (Vanilla JS) |

---

## Nested Sub-Subsystems (System of Systems)

Many modules are themselves "Systems" containing specialized sub-components.

### A. Sidebar Controller (`sidebar.js`)
*   **Color Preset Engine**: Manages 10+ architectural/metric presets.
*   **Scheme Navigator**: Handles switching between 33 high-precision color ramps.
*   **View Mode Switcher**: Manages the transitions between "Atom" (Syntactic) and "Map" (Structural) modes.
*   **Layer/Tier Controller**: Toggles visibility and force-bias of hierarchical levels.

### B. Panel Handler System (`panel-handlers.js`)
*   **Camera Tracking System**: Manages position bookmarks and auto-fit logic.
*   **Accessibility Subsystem**: Controls visual adaptations (High Contrast, Greyscale).
*   **Export Engine**: Handles SVG screenshots and JSON state dumping.
*   **Intelligence Feedback Hub**: Real-time updates of graph statistics and node metadata.

### C. UPB Intelligence Layer (`upb/`)
*   **Scale Transform Bank**: A registry of 7+ mathematical scaling functions (Linear, Log, etc.).
*   **Endpoint Resolver**: Adapts variety of data sources to visual targets.
*   **Conflict Resolver**: Logic for blending overlapping bindings (Blenders).

### D. Rendering Stack (`file-viz.js`)
*   **Hull Geometry Engine**: Procedural generation of organic membranes around clusters.
*   **Shader Manager**: Controls WebGL GLSL materials for nodes/edges/hulls.

### E. Leaf Components & UI Builders (`ui-builders.js`)
*   **Checkbox/Toggle Subsystem**: Standardized interactive Boolean state controls.
*   **Filter/Chip Group System**: Multi-select tag engines with "Select All" logic.
*   **Datamap Toggle Subsystem**: Specialized controls for data-aware visibility.
*   **Exclusive Option (Radio) Subsystem**: Mutually exclusive selection groups.
*   **Aquarela Interaction Subsystem**: Fluid-responsive buttons using the `AquarelaButton` component.

---

*Part of the PROJECT_elements Frontend Registry*
