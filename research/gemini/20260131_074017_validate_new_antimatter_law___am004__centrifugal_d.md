# Research: VALIDATE NEW ANTIMATTER LAW:

AM004: Centrifugal Dependency Violation
Rule: Inner Ring cannot depend...

> **Date:** 2026-01-31 07:40:17
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:4c09c12184dd2f4ef38fbe557354d2876dfa6460c5eec9f10c824cb8d936becf`
> **Raw JSON:** `raw/20260131_074017_validate_new_antimatter_law___am004__centrifugal_d.json`

---

## Query

VALIDATE NEW ANTIMATTER LAW:

AM004: Centrifugal Dependency Violation
Rule: Inner Ring cannot depend on Outer Ring
Enforcement: Dependencies must flow INWARD only (toward higher purity)

Ring Architecture (ADOPTED TERMINOLOGY):
- Ring 0 (Nucleus): Pure Domain Models - zero dependencies
- Ring 1: Domain Services - depends only on Ring 0
- Ring 2: Application Services / Use Cases - orchestrates Ring 1
- Ring 3: Interface Adapters - Controllers, Gateways
- Ring 4: Frameworks & Drivers - DB, Web, UI, Devices

Questions:
1. Is AM004 logically consistent with existing AM001-AM003?
2. Does Ring terminology conflict with existing SMC 'Ring' usage (LOG/DAT/ORG/EXE)?
3. How to disambiguate? Suggest: 'Functional Ring' vs 'Dependency Ring'?
4. Provide formal definition for GLOSSARY.md

Validate against existing Antimatter Laws in semantic_models.yaml

---

## Response

This is the **CHIEF ARCHITECT**. I have analyzed your proposal for **AM004 (Centrifugal Dependency Violation)** against the `PROJECT_elements` Standard Model of Code.

Here is the architectural determination.

### 1. Verdict: **APPROVED WITH MODIFICATION**

**AM004 is logically valid and necessary**, but your terminology introduces a **CRITICAL NAMESPACE COLLISION** with the Standard Model's existing topology.

In the Standard Model of Code (SMC):
1.  **RINGS** are **Vertical/Categorical** (LOG, DAT, ORG). They describe *Category*.
2.  **SHELLS** (Proposed) are **Concentric/Hierarchical**. They describe *Depth*.

You cannot use "Ring" for dependency depth because `unified_analysis.json` already defines `ring` as the Functional Family (Logos, Data, Organelle).

---

### 2. The Conflict Analysis

#### Existing Structure (The "Functional Ring")
Defined in `COLLIDER_ARCHITECTURE.md` and `UnifiedNode` schema.
*   **LOG (Logos):** Pure Logic (Algorithms)
*   **DAT (Data):** State schemas, DTOs
*   **ORG (Organelle):** Systems, controllers
*   **EXE (Execution):** Entry points, scripts
*   **EXT (External):** Libraries (Tier 2)

#### Proposed Structure (The "Dependency Ring")
*   **Level 0:** Domain Model
*   **Level 4:** Infrastructure/Frameworks

**The Clash:** A `DAT` node (Data Ring) can exist at *any* dependency level (e.g., a Core DTO vs. an API Response DTO). If we overload "Ring", the `semantic_finder.py` will fail to distinguish between *Kind* and *Position*.

---

### 3. The Architectural Solution: **ELECTRON SHELLS**

To maintain the "Atom/Physics" metaphor of the Standard Model, we will map Dependency Levels to **Electron Shells ($n$)**.

*   **Nucleus (Shell 0):** Pure Domain (High Stability)
*   **Valence Shell (Shell 4):** Interface/Interaction (High Reactivity)

**The Force Rule:**
*   **Centripetal Force:** Dependencies must "fall" toward the nucleus.
*   **AM004 Violation:** A node in an inner shell "reaching out" to an outer shell (Centrifugal).

---

### 4. Revised Definition (For GLOSSARY.md & semantic_models.yaml)

#### A. New Terminology (Add to `GLOSSARY.md`)

```markdown
### Topology: Shells (Dependency Depth)

| Shell | ID | Analogy | Component Type | Dependencies Allowed |
|-------|----|---------|----------------|----------------------|
| **S0** | **Nucleus** | Protons/Neutrons | Pure Domain Entities, Constants, Types | None (Self-contained) |
| **S1** | **Core** | Inner Orbitals | Domain Services, Business Rules | Depends on S0 only |
| **S2** | **Application** | Middle Orbitals | Use Cases, Orchestration | Depends on S1, S0 |
| **S3** | **Adapter** | Outer Orbitals | Controllers, Gateways, Presenters | Depends on S2, S1, S0 |
| **S4** | **Valence** | Interaction | Frameworks, DB Drivers, UI, CLI | Depends on S3+ (and External T2) |

**The Centripetal Law:**
Dependencies $d(A \to B)$ are valid iff $Shell(A) \ge Shell(B)$.
Gravity pulls inward. Logic relying on "outer" volatile elements causes topological instability.
```

#### B. The Antimatter Law (Add to `semantic_models.yaml`)

```yaml
AM004:
  name: "Centrifugal Dependency Violation"
  severity: "CRITICAL"
  description: "Inner Shells must not depend on Outer Shells. Dependencies must flow inward (Centripetal)."
  logic: |
    Let S(n) be the Shell index of node n.
    For every edge e(source -> target):
      IF S(source) < S(target) THEN VIOLATION
  exceptions:
    - "Dependency Injection Interfaces (Inversion of Control patterns)"
    - "Observability Hooks (if implemented as non-blocking side effects)"
  remediation: "Apply Dependency Inversion Principle (DIP). Define interface in Inner Shell, implement in Outer Shell."
```

---

### 5. Implementation Strategy (The Architect's Code)

To enforce this, we must map your existing "Rings" (LOG, DAT...) to the new **Shells** or calculate Shells dynamically based on `RPBL.Boundary`.

**In `standard_model_enricher.py`:**

We need to calculate the **Shell Index ($n$)** during the enrichment phase.

```python
def calculate_shell(node: UnifiedNode) -> int:
    """
    Determines the Gravitational Shell (0-4) based on Atom and RPBL.
    """
    # 1. Nucleus: Pure Types and Data Definitions
    if node.atom.startswith("DAT") and node.rpbl.purity >= 9:
        return 0 # S0: Nucleus
        
    # 2. Core: Pure Logic (Algorithms)
    if node.atom.startswith("LOG") and node.rpbl.boundary <= 2:
        return 1 # S1: Core
        
    # 3. Application: Orchestration of Logic
    if node.atom.startswith("ORG") or node.role == "Service":
        return 2 # S2: Application
        
    # 4. Adapters: Controllers, Interfaces
    if node.atom.startswith("INT") or node.role in ["Controller", "Gateway"]:
        return 3 # S3: Adapter
        
    # 5. Valence: Execution, Scripts, Framework Bindings
    if node.atom.startswith("EXE") or node.atom.startswith("EXT"):
        return 4 # S4: Valence
        
    return 4 # Default to volatile outer shell if unknown
```

**In `analyze.py` (The Validator):**

```python
def check_am004_centrifugal_force(graph):
    violations = []
    for edge in graph.edges:
        source_shell = edge.source.shell
        target_shell = edge.target.shell
        
        # Allow same shell or inward flow
        if source_shell < target_shell:
            # EXCEPTION CHECK: Is target an Interface defined in inner shell?
            # (Requires deeper AST analysis, but strictly strict node position checks:)
            violations.append({
                "code": "AM004",
                "message": f"Centrifugal Force Detected: {edge.source.id} (S{source_shell}) -> {edge.target.id} (S{target_shell})",
                "severity": "CRITICAL"
            })
    return violations
```

### 6. Summary for the Record

1.  **Consistency:** AM004 is consistent. It mathematically formalizes "Architecture Drift" (AM002).
2.  **Terminology:** "Ring" is rejected for this concept. We adopt **"Shells"** (S0-S4).
3.  **Disambiguation:**
    *   **Ring** = Functional Category (Vertical).
    *   **Shell** = Dependency Depth (Radial).
4.  **Action:** Update `GLOSSARY.md` with the Shell definition and implement the `calculate_shell` logic in the `standard_model_enricher`.

*Signed,*
**CHIEF ARCHITECT**

---

## Citations

_No citations provided_
