# Research: Architectural topology question for SMC:

Does our theory have a concept for CONCENTRIC LAYERS with ...

> **Date:** 2026-01-31 07:36:21
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:32f63726a2130c18221de15ec4df68c194d04b4250f275e37d75a2b1d3b368ba`
> **Raw JSON:** `raw/20260131_073621_architectural_topology_question_for_smc___does_our.json`

---

## Query

Architectural topology question for SMC:

Does our theory have a concept for CONCENTRIC LAYERS with CENTRALITY?

Example: A tool where:
- CORE (center) = pure operations, no dependencies
- MIDDLE = business logic using core
- OUTER = interface using middle
- Dependencies flow INWARD only

This is like Clean Architecture / Onion Architecture / Hexagonal Architecture.

Questions:
1. Does SMC already have this concept? Where?
2. If not, should we add it?
3. What would we call it? (Not 'Ring' - that's OS terminology)
4. How does it relate to D2_LAYER which seems more horizontal (tiers) than concentric (layers around a core)?

Be specific with SMC terminology and cite theory documents.

---

## Response

As the Chief Architect, I have analyzed your request against the `COLLIDER_ARCHITECTURE.md` and `CODESPACE_ALGEBRA.md` frameworks.

Here is the architectural determination regarding **Concentric Layers (Centrality)** within the Standard Model of Code.

### 1. Does SMC already have this concept?

**Yes, but it is currently implicit, derived from the interaction of `RPBL` and `Atoms`.**

The Standard Model currently defines "Rings" (`LOG`, `DAT`, `ORG`, `EXE`, `EXT` in `COLLIDER_ARCHITECTURE.md`), but as you noted, these function more like **Vertical Functional Families** (e.g., Logic, Data, Execution) rather than **Concentric Dependency Shells**.

However, the concept of "Centrality" exists latently in the **RPBL** (Responsibility, Purity, Boundary, Lifecycle) classification system:

1.  **Purity (π in RPBL):** This is the primary proxy for "Core."
    *   High Purity atoms (e.g., Domain Entities, Value Objects) have *no* side effects and *no* I/O dependencies. They sit at the geometric center.
    *   Low Purity atoms (e.g., DB Adapters, API Controllers) rely on external state. They sit at the periphery.
2.  **Boundary (β in RPBL):** This defines the "Membrane."
    *   High Boundary scores indicate code that touches the "outside world" (Filesystem, Network, UI).

**Current Topology:**
Currently, the `UnifiedNode` contains `rpbl` scores. If we visualize the graph where $r = (1/Purity)$, we generate a concentric map where pure logic falls to the center and infrastructure flies to the edges.

### 2. Should we add it?

**YES. It must be formalized.**

While `D2_LAYER` handles N-Tier architecture (Presentation $\to$ Logic $\to$ Data), it often fails to represent **Hexagonal/Onion Architecture** where "Data" and "Presentation" are *both* external adapters surrounding a pure core.

Formalizing this allows us to enforce the **Centripetal Dependency Law**:
> *Dependencies must only point inward toward higher Purity.*

This prevents the specific architectural rot where "Core Business Logic" accidentally imports a "Database Driver," violating the `Atoms` isolation principle.

### 3. What would we call it?

Since "Ring" is claimed by the SMC for functional grouping (Log/Dat/Org) and "Layer" is claimed by `D2_LAYER` (vertical stack), we should align with the physics metaphor of the Standard Model:

**Proposal: The "SHELL" (or "Electron Shell")**

In atomic physics, electrons inhabit shells ($n=1, 2, 3$) around the nucleus.
In SMC, code inhabits Shells based on its distance from the Pure Core.

*   **Shell 0 (Nucleus):** Pure Domain Models (Zero dependencies).
*   **Shell 1 (S):** Domain Services (Depends only on Shell 0).
*   **Shell 2 (P):** Application Services / Use Cases (Orchestrates Shell 1).
*   **Shell 3 (D):** Interface Adapters (Controllers, Gateways).
*   **Shell 4 (F):** Frameworks & Drivers (DB, Web, Devices).

This fits the **Atom** metaphor perfectly: Unstable isotopes (High Shell #) decay/change frequently; the Nucleus (Shell 0) is stable.

### 4. Relation to D2_LAYER vs. SHELL

This highlights a critical topological distinction in our architecture:

| Feature | **D2_LAYER** (Horizontal/Stack) | **SHELL** (Concentric/Radial) |
| :--- | :--- | :--- |
| **Geometry** | Stack (Top-Down) | Sphere (Center-Out) |
| **Logic Flow** | Request flows *Down* | Request flows *In* then *Out* |
| **Data Access** | Often the "Bottom" layer | An "Outer" Shell (Adapter) |
| **Constraint** | "Presentation calls Logic" | "Outer wraps Inner" |
| **Dependency** | `A -> B -> C` | `A -> B <- C` (Inversion of Control) |

In the Standard Model, **D2_LAYER** describes *where* code lives in the deployment stack, while **SHELL** describes its *distance from the domain truth*.

### Implementation Strategy

To implement this without breaking the `COLLIDER_ARCHITECTURE` schema, we derive **Shell** from existing `RPBL` and `Atoms` data during the **Enrichment Stage** (Stage 7 of Full Analysis).

**Algorithm:**
```python
def calculate_shell(node: UnifiedNode) -> int:
    # SHELL 0: Pure definitions (Tier 0 Atoms)
    if node.rpbl.purity >= 9 and node.rpbl.boundary == 0:
        return 0

    # SHELL 4: Heavy Infrastructure (High Boundary)
    if node.rpbl.boundary >= 8:
        return 4

    # ... interpolation logic for Shells 1-3 based on dependency edges
```

**Topological Invariant (The Knot Check):**
If a Node in `Shell 1` imports a Node in `Shell 3`, the **Socratic Layer** (`analyze.py --verify`) must flag a **Centrifugal Violation** (dependency pointing outward).

### Executive Recommendation

1.  **Adopt "SHELL"** as the term for concentricity to avoid collision with "Ring".
2.  **Do not modify the `UnifiedNode` schema** yet; calculate `Shell` dynamically in `standard_model_enricher.py`.
3.  **Update `semantic_models.yaml`** (Antimatter Laws) to include a new law:
    *   `AM004: Centrifugal Dependency Violation` (Inner Shell cannot depend on Outer Shell).

---

## Citations

_No citations provided_
