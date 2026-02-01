# Research: HOW SHOULD RING INTEGRATE WITH ATOM SCHEMA?

Current Atom ID format: PHASE.FAMILY.TIER
Example: LOG....

> **Date:** 2026-01-31 07:57:30
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:f5c8911d6d5efc64c600db80d836cde973fcfdca134f447d20387a3110b3a00b`
> **Raw JSON:** `raw/20260131_075730_how_should_ring_integrate_with_atom_schema___curre.json`

---

## Query

HOW SHOULD RING INTEGRATE WITH ATOM SCHEMA?

Current Atom ID format: PHASE.FAMILY.TIER
Example: LOG.FNC.M (Logic Function Molecule)

Structure:
- 4 PHASES: DAT, LOG, ORG, EXE
- 22 FAMILIES: Bits, Functions, Aggregates, etc.
- 3 TIERS: A(tom), M(olecule), O(rganism)
- 200 total atoms

NEW CONCEPT - RING (dependency depth):
- Ring 0: Pure Core (no dependencies)
- Ring 1: Domain Services
- Ring 2: Application/Use Cases
- Ring 3: Adapters/Controllers
- Ring 4: Frameworks/Drivers/UI

QUESTION: How should Ring integrate?

Option A: Add to ID → LOG.FNC.M.R2
Option B: Separate dimension (not in ID, calculated per instance)
Option C: New row in periodic table
Option D: Something else?

Consider:
1. Is Ring intrinsic to atom TYPE or contextual to INSTANCE?
2. Can the same atom type appear at multiple rings?
3. How does this affect the periodic table visualization?
4. How does Collider calculate/assign Ring?

Reference: particle/schema/fixed/200_ATOMS.md

---

## Response

As CHIEF ARCHITECT, I have analyzed the topological implications of integrating "Ring" (Dependency Depth) into the Atom Schema.

**DECISION:** **OPTION B (Separate Dimension)**
**VERDICT:** Ring is **Topological (Contextual)**, not **Ontological (Intrinsic)**.

We must strictly separate **Identity** (Atom) from **Location** (Ring).

---

### 1. The Architectural Proof

In the Standard Model of Code, we distinguish between the **Particle** and its **Position**.

*   **The Atom (`LOG.FNC.M`)** defines the *fundamental nature* of the code. A logic function is a logic function whether it calculates a hash (Core) or formats a UI string (Frontend). Its internal structure (Carbon) does not change based on where it sits.
*   **The Ring (0-4)** defines the *gravitational depth* within the dependency graph. It is a property of the **System**, not the **Node**.

**If we chose Option A (`LOG.FNC.M.R2`), we would commit a category error:**
1.  **Explosion of State:** We would multiply 200 atoms by 5 rings, creating 1,000 distinct types, diluting the periodic table.
2.  **Refactoring Fragility:** Moving a utility function from the Application layer to the Core layer should not change its *chemical identity* (Atom type), only its *orbital* (Ring).

### 2. Integration into the Collider Architecture

We will implement this using the **8-Dimensional Space** defined in `ACI_DATASET_MANAGEMENT.md` and `UnifiedNode` schema.

#### The Data Structure
In `UnifiedNode` (Stage 6 of `unified_analysis.py`), the integration looks like this:

```python
class UnifiedNode:
    # 1. Identity (D1: WHAT) - The Atom
    # Fixed via UniversalClassifier
    atom: str  # "LOG.FNC.M"

    # 2. Topology (D2: LAYER) - The Ring
    # Calculated via GraphInference (Dependency Depth)
    ring: int  # 0, 1, 2, 3, 4

    # 3. Purpose (RPBL) - The Role
    # Calculated via PurposeField
    rpbl: RPBLScore  # {responsibility, purity, ...}
```

### 3. Implementation Strategy (The Orbital Calculation)

The `Collider` must calculate the Ring *after* Edge Extraction (Stage 4), as the Ring is defined by inbound/outbound dependencies.

**The Ring Definitions:**

| Ring | Name | Definition | Edge Rules |
|:---:|---|---|---|
| **0** | **CORE** | Pure Logic / Entities | No imports (or only stdlib). **LAMINAR FLOW.** |
| **1** | **DOMAIN** | Business Rules | Imports Ring 0. |
| **2** | **APP** | Use Cases / Orchestration | Imports Ring 0, 1. |
| **3** | **ADAPTER** | Interfaces / Controllers | Imports Ring 0, 1, 2. |
| **4** | **FRAMEWORK** | Infrastructure / UI / IO | Imports Ring 0-3 + External Libs. **TURBULENT FLOW.** |

### 4. Visualization & Analysis Implications

This separation allows for powerful 2D visualizations in the `visualize_graph_webgl.py` engine:

1.  **X-Axis (Complexity):** Driven by Atom Tier (M → A → O).
2.  **Y-Axis (Depth):** Driven by Ring (0 → 4).
3.  **Color:** Driven by Atom Family (LOG/DAT/ORG).

**The "Electron Shell" Metaphor:**
Instead of a periodic table row, visualize the Codebase as an atom itself.
*   **Nucleus (Ring 0):** Dense, high-gravity `DAT.ENT.A` (Data Entities) and `LOG.ALG.M` (Algorithms).
*   **Outer Shells (Ring 4):** Volatile, reactive `EXE.UI.O` (User Interfaces) and `EXT.API.M` (External Connectors).

### 5. Immediate Action Items

1.  **Update `UnifiedNode`:** Ensure `ring` is a top-level field, separate from `atom`.
2.  **Update `GraphInference`:** Implement a topological sort or "onion peel" algorithm in the Collider to assign Ring numbers based on import depth.
    *   *Heuristic:* If Node A imports Node B, `Ring(A) >= Ring(B)`.
    *   *Anchor:* Files with 0 internal imports are Ring 0.
3.  **Update `200_ATOMS.md`:** Add a note explicitly stating that Atoms are Ring-agnostic.

**Summary:** The Atom is the **Matter**. The Ring is the **Gravity**. Do not mix them.

---

## Citations

_No citations provided_
