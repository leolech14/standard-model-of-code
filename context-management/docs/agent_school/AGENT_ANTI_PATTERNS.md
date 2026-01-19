# Liabilities of AI-Driven Software Development & Guardrails
*Incorporating the Standard Model of Code*

> **The "Agent-Only" Paradox**: Agents are excellent at *creating* code but terrible at *remembering* code they cannot see. When you strictly use AI agents to code, you are effectively running a project with a team of brilliant developers who have **amnesia** and **tunnel vision**.

This document details the failure modes of AI coding agents, supports them with industry research, and provides actionable guardrails rooted in the **Standard Model of Code**.

---

## 1. Documented AI Failure Modes (Anti-Patterns)
*Validation & Refinement of Known Issues*

AI coding agents exhibit several failure modes that differ from typical human mistakes. Below we validate 8 known anti-patterns with technical evidence and case studies.

### Context Myopia
*Creating a plug without a socket.*
AI agents often lack a holistic project view due to limited context windows, leading to code that doesn’t integrate well beyond the snippet at hand.
*   **The Findings**: Tenable researchers note that an LLM may suggest changes oblivious to other files. Kodus emphasizes that an AI “doesn’t have [the] contextual understanding” of your specific system.
*   **Manifestation**: Creates architecture misalignment (violating layering) or redundant Helper functions because the AI did not "see" the existing utility.
*   **Industry Term**: "Lost in the Middle Phenomenon".

### Refactoring Abandonment
*Building a new bridge but keeping the old one "just in case".*
AI agents may initiate refactors but fail to propagate them throughout the codebase, leaving partial, broken transitions.
*   **The Findings**: A "vibe coding" security blog warns that AI often misses several places in a codebase during refactors. Nolan Lawson notes that coding agents love making "subtle fixes" that break original intent.
*   **Manifestation**: `particle_classifier.py` (V1) coexists with `UniversalClassifier.py` (V2). The system rot increases as V1 is never deleted.
*   **Standard Model**: Causes **Semiotic Misalignment** between D1_WHAT (Structure) and D3_ROLE (Intent).

### Hallucinated Dependencies
*The Supply Chain Liability.*
Generative AI may invent or suggest libraries, APIs, or modules that do not actually exist.
*   **The Findings**: Endor Labs highlights "hallucinated dependencies" as a risk for "slopsquatting" attacks.
*   **Manifestation**: Importing a package that *sounds* real but isn't. Humans rarely type imports for non-existent libs; AI does it confidently.

### Security Blind Spots
*The Silent Vulnerability.*
AI-generated code frequently omits essential security steps or introduces subtle vulnerabilities.
*   **The Findings**: Over 40% of AI-generated solutions in a survey contained security flaws.
*   **Manifestation**: Dropping authentication checks or using outdated APIs. Endor Labs calls this "architectural drift"—breaking a security invariant without breaking syntax.
*   **Standard Model**: Requires analysis of D6_EFFECT (Side Effects) and D4_BOUNDARY (I/O).

### Architectural & Layer Drift
*The Law of Physics Violation.*
AI agents lack higher-level understanding of design principles and often optimize for the local goal, violating layering or modularity.
*   **The Findings**: AlterSquare reports AI tools struggle with system architecture, treating features as standalone.
*   **Manifestation**: A Controller (Application Layer) calling a Repository (Infrastructure) directly.
*   **Standard Model**: Detectable via D2_LAYER violations (e.g., AM001 Layer Skip Violation).

### Duplication and Redundancy
*The DRY Amnesia.*
AI agents copy-paste logic in multiple places rather than refactoring or reusing.
*   **The Findings**: "AI tools frequently generate redundant code," leading to maintenance bloat.
*   **Manifestation**: Dozens of similar "helper" files.
*   **Standard Model**: Erodes R4_COMPOSITION and R5_RELATIONSHIPS integrity.

### Semantic Drift & Documentation Mismatch
*The Meaning Shift.*
AI produces changes that drift away from original intent or fail to update documentation.
*   **The Findings**: AI "fixes" might strip important warning comments (Nolan Lawson) or add side-effects not requested (Kodus).
*   **Manifestation**: Function logic changes but docstring remains static.
*   **Standard Model**: Conflict between D1_WHAT (Code) and D3_ROLE (Docs/Intent).

### Testing Gaps (Happy-Path Focus)
*The False Confidence.*
AI-written tests often focus on "sunny day" scenarios, ignoring edge cases.
*   **The Findings**: High coverage but bugs slip through.
*   **Manifestation**: Tests checks `add(1,1)` but not `add(NULL, 1)`.
*   **Standard Model**: Failure in D7_LIFECYCLE (Create/Use/Destroy) coverage.

---

## 2. Additional Failure Modes Unique to AI-First Development

### Over-reliance & Skill Atrophy
*   **The Risk**: Devs trust AI outputs without review, leading to "rusting" of deep debugging skills.
*   **Result**: The team loses the ability to understand or evolve the system's innards.

### Non-Deterministic Changes (Heisenbug Code)
*   **The Risk**: AI introduces stochastic variations. Running the same refactor prompt twice yields different results.
*   **Result**: Unpredictable builds and "flickering" logic.

### Excessive Dependency Introduction
*   **The Risk**: AI pulls in heavy libraries for simple tasks because it saw them in training.
*   **Result**: Bloat and increased attack surface.

### Rapid Decay of Intent Traceability
*   **The Risk**: AI code lacks the "why" (rationale). Unlike humans who leave specific breadcrumbs, AI writes generic code.
*   **Result**: Maintainers struggle to discern original thought process during bugs.

### Cascade of Small Errors
*   **The Risk**: AI builds on its own previous small mistakes, creating a tower of bugs.
*   **Result**: A convoluted design that must be scrapped rather than fixed.

---

## 3. Detection Signals & Forensics

To catch these issues, we look for specific signals in the codebase.

### 3.1 Timestamp Forensics: The Hidden Signal
*Project-Specific Timestamp Analysis*

The file system meta-data (Creation Time vs Modification Time) is the single most powerful tool for detecting these patterns.

| Anti-Pattern | Timestamp Signature | Forensic Query (using `query_timestamps.py`) |
| :--- | :--- | :--- |
| **Refactoring Abandonment** | **The V1/V2 Gap**: A file stops changing exactly when a new file starts existing. | `Analyze files where LastModified < (Today - 30 days) AND is_in_active_directory` |
| **Context Window Myopia** | **Noise Ratio**: Agent context is filled with files untouched for years. | `Filter context: exclude files where Age > 90 days UNLESS dependencies > 0` |
| **Hollow Generator** | **Interactive Void**: File `birthtime` is effectively equal to `mtime`. It was dumped and never refined. | `Select files where (mtime - birthtime) < 1 minute AND LOC > 50` |
| **Path of Least Resistance** | **Hotspot Friction**: A single utility file has `mtime` updated 50x more than core logic. | `Sort by ModificationCount (if tracked) or check frequency of recent mtime updates` |
| **Colocation Confusion** | **Temporal Strata**: Active directory contains mixed "Geological Layers" (e.g., 2023 files next to 2026 files). | `Group files by CreationMonth; flag directories with High Variance using` |

> [!TIP]
> **Agent Rule**: "If you find a file that hasn't been touched in 6 months in a directory that is edited daily... ask permission to archive it."

### 3.2 Detection Signals Beyond Timestamps
*   **Duplicate Code Fragments**: Spike in clone similarity > 30%. (R4 Composition issue).
*   **Unreferenced Code**: New functions with in-degree 0. (D7 Lifecycle issue).
*   **Cyclomatic Complexity Spike**: Simple tasks implemented with high complexity (Hallucination/Over-engineering).
*   **Layer Violation Edges**: Infrastructure calling Application. (D2 Layer issue).
*   **Unapproved Dependencies**: New imports not in allow-list. (D4 Boundary issue).
*   **Security Scan Delta**: New high-severity SAST warnings. (D6 Effect issue).
*   **Runtime Telemetry**: Performance regression after AI deploy.

---

## 4. Mitigation Strategies and Best Practices

### Strategy A: Linter Laws (AI Guardrails)
*   **Concept**: Treat coding standards as inviolable laws.
*   **Implementation**: `antimatter_laws.yaml` fed to the Agent.
*   **Rule**: "Controllers must not directly import Repositories."
*   **Effect**: Turns "Architectural Drift" into a hard syntax error.

### Strategy B: Contracts-First Development
*   **Concept**: Write the Interface (Contract) before the Implementation.
*   **Implementation**: Prompt AI to design `IClassifier` before `UniversalClassifier`.
*   **Effect**: Solves "Writing Problem" (Context Myopia) by creating a "socket" first.

### Strategy C: The Socratic Supervisor
*   **Concept**: Separate "Coder Agent" from "Auditor Agent".
*   **Implementation**: A secondary agent reads the diff and asks: "Why is this unused?"
*   **Effect**: Breaks tunnel vision. The Auditor is focused on *connections*, not creation.

### Strategy D: Test-Driven AI Development
*   **Concept**: AI must write tests that fail *before* writing code that passes.
*   **Implementation**: CI gate enforcing new tests for new functions.
*   **Effect**: Prevents "Happy Path" bias.

### Strategy E: Continuous Quality Monitors
*   **Concept**: Automated dashboards (using Collider) to track drift.
*   **Implementation**: Alert if `duplicated_code` > 5% or `god_class_count` increases.

---

## 5. Integration into the 8D Model and Collider Schema

We map these failure modes to the Standard Model to systematize detection.

| Failure Mode | Primary Dimensions | Lenses |
| :--- | :--- | :--- |
| **Context Myopia** | D2 (Layer), D5 (State) | R7 (Hermeneutics) |
| **Refactoring Abandonment** | D7 (Lifecycle), D1 vs D3 | R8 (Epistemology) |
| **Hallucinated Dependency** | D4 (Boundary) | R5 (Relationships) |
| **Security Risk** | D6 (Effect), D4 (Boundary) | R6 (Transformation) |
| **Architectural Drift** | D2 (Layer), D3 (Role) | R4 (Composition) |

### Antimatter Laws Extension
We extend `antimatter_laws.yaml` with:
*   **AM004 Duplicate Logic**: >80% similarity.
*   **AM005 Orphan Code**: No incoming calls.
*   **AM006 Hallucinated Dependency**: Import unknown.

---

## 6. Manager Playbook
*How to steer the swarm.*

1.  **Define "Do's and Don'ts" Upfront**: Explicit policy (e.g., "No new dependencies without approval").
2.  **Quality Gates in CI**: Fail build on AI anti-patterns.
3.  **Mandate Contracts/Tests**: "Think before you code."
4.  **Visualize**: Use Collider maps in standups to spot "Spiderweb" clusters.
5.  **Two-Strikes Rule**: If AI breaks production twice, pause and review process.

---

## 7. Audit Log (Jan 18, 2026)
*Automated Scan using `tools/query_timestamps.py`*

Applied **Strategy C (Socratic Supervisor)** using timestamp analysis to find "Stale Code" (potential Refactoring Abandonment or Dead Code).

**Findings (Files untouched > 30 days):**
*   `src/core/particle_classifier.py` (Dec 4) - Likely superseded by `UniversalClassifier`.
*   `src/core/dependency_analyzer.py` (Dec 14) - Investigating if this is the "Old Bridge" left behind.
*   `src/core/language_loader.py` (Dec 14) - Potential relic of an earlier parsing strategy.

**Action**: These files are now flagged for manual review or deletion. This proves that *time* is a valid proxy for *relevance* in an AI-generated codebase.
