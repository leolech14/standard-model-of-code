# CONTAINMENT TOPOLOGY - The Structure of Code Organization

**Theory Layer:** L1 (Definitions) + L3 (Measurements)
**Status:** FORMALIZED (2026-01-28)
**Source:** User's insights on filesystem architecture and subdivision stability

---

## 1. DEFINITIONS

### Filesystem Containers and Unknown Cardinality

A filesystem can be modeled as a **rooted hierarchy of containers**. A **directory** contains a finite set of entries, each entry being either a **subdirectory** or a **file**. When I "open" a directory (e.g., in a file explorer), I initially see **only its immediate children**. I cannot know the number of children *a priori* from the name alone; it can be **any non-negative integer**, subject to filesystem and OS limits, and I only learn it by enumerating the directory.

**Formal:**
```
Directory d contains:
  children(d) = subdirs(d) ∪ files(d)

  |children(d)| ∈ ℕ ∪ {0}
  |children(d)| is unknown until enumerated
```

---

### Two Simultaneous Views of Code: Container Topology and Atom Topology

Code can be represented in **two topologies at the same time**:

1. **Container topology** (directories → files), which is a tree-like containment structure.
2. **Atom topology** (functions/classes/methods/etc.), which is a graph of fine-grained entities connected by structural relations (calls, imports, references, inheritance, reads/writes, etc.).

These two views should be **toggleable** independently and also **overlayable** in one visualization. In the overlay, every **file node** should have explicit **containment edges** to the **atom nodes** it contains. Node and edge types must be visually distinguishable (e.g., different colors/shapes/line styles) so that containment is never confused with dependency.

**Formal:**
```
Graph G = (V, E_contains, E_depends)

V = Directories ∪ Files ∪ Atoms

E_contains:
  Directory --CONTAINS--> Directory
  Directory --CONTAINS--> File
  File --CONTAINS--> Atom

E_depends:
  Atom --DEPENDS--> Atom
  (subtype: calls, imports, inherits, references, etc.)

Views:
  V_container: Show only Directories ∪ Files, E_contains
  V_atom: Show only Atoms, E_depends
  V_overlay: Show all V, all E (typed visualization)
```

---

### Boundary of What is Visible vs. What Exists

A directory listing (or an "open folder" view) is a **viewport boundary**: it reveals only the immediate contents of that directory. Deeper descendants exist, but they remain hidden until I traverse into subdirectories (expand / open / recursively enumerate). So visibility is bounded by the chosen view, even though the underlying structure is larger.

**Formal:**
```
Visibility from context c (directory):
  visible(c) = immediate_children(c)
  hidden(c) = descendants(c) \ immediate_children(c)

Properties:
  |visible(c)| is measurable (enumeration)
  |hidden(c)| is unknown until descent

Information Hiding Principle:
  ∀ level L:
    observer_at(L) sees only children(L)
    observer_at(L) cannot_see(descendants(children(L)))

Topological Space:
  Open sets = {children(d) | d ∈ Directories}
  Boundary = directory_interface
  Interior = nested_contents (hidden from parent)
```

---

### Visual Encoding Rule (Corrected)

> "They must not connect in the color aspect... they will connect in the structural sense."

**Corrected interpretation:**

Use **different visual encodings** for different node/edge types so users never confuse them.

- **Containment edges:** One style (thin/grey/dashed)
- **Dependency edges:** Another style (solid/colored)
- **Node types:** Distinct shapes or colors (Dir vs File vs Atom)

**Goal:** Not "preventing connections," but **preventing semantic confusion**.

---

## 2. MODEL

### Typed Multigraph

**G = (V, E_contains, E_depends)**

**Node Types:**
```
V_dir: Directories
V_file: Files
V_atom: Atoms (functions, classes, methods, variables)

V = V_dir ∪ V_file ∪ V_atom
```

**Edge Types:**
```
E_contains:
  V_dir → V_dir  (directory contains subdirectory)
  V_dir → V_file (directory contains file)
  V_file → V_atom (file contains atom)

E_depends:
  V_atom → V_atom (atom depends on atom)
  Subtype: {calls, imports, inherits, references}
```

**Derived Edges (for coarse view):**
```
E_file_depends (derived):
  File₁ → File₂  iff ∃ atom_a ∈ File₁, atom_b ∈ File₂:
    (atom_a → atom_b) ∈ E_depends

Purpose: View coupling at file level without drawing every atom
```

---

## 3. VIEWS

### View 1: Container-Only (Tree)
```
Show: V_dir ∪ V_file
Show: E_contains (directory structure)
Hide: V_atom, E_depends

Use case: Navigate filesystem, understand organization
```

### View 2: Atom-Only (Graph)
```
Show: V_atom
Show: E_depends (code dependencies)
Hide: V_dir, V_file, E_contains

Use case: Analyze code coupling, find dependencies
```

### View 3: Overlay (Typed Multigraph)
```
Show: ALL (V_dir ∪ V_file ∪ V_atom)
Show: ALL (E_contains ∪ E_depends)
Distinguish: Color/shape by type

Use case: See how filesystem organization relates to code structure
```

### View 4: Animated Transition
```
State A: Container-only view
  ↓ (750ms crossfade)
State B: Atom-only view

Implementation: Already built (unified graph + crossfade)
```

---

## 4. MEASUREMENTS

### Root Fan-Out

**Definition:** Number of immediate children of root R

```
fanout(R) = |immediate_children(R)|

Can measure:
  fanout_dirs(R) = |subdirectories(R)|
  fanout_files(R) = |files(R)|
  fanout_total(R) = fanout_dirs(R) + fanout_files(R)
```

**Observed in our repo:**
- Root fan-out (total): 23 items
- Core directories: 4 (.agent, context-management, standard-model-of-code, archive)
- Auxiliary: 19 (governance docs, configs, outputs)

---

### Cross-Boundary Dependency Ratio

**Definition:** How much coupling crosses top-level boundaries?

```
top(R, atom) = immediate child of R that contains atom

cross_boundary_edges(R) = {
  (a, b) ∈ E_depends | top(R, a) ≠ top(R, b)
}

cross_ratio(R) = |cross_boundary_edges(R)| / |E_depends|

Optimal: Low cross_ratio = good modular isolation
```

---

### Stability Over Time

**Definition:** How stable is the subdivision structure?

```
Measure across commits t₁, t₂, ..., tₙ:

fanout_stability(R) = stdev([fanout(R, t₁), ..., fanout(R, tₙ)])

membership_churn(R, t₁, t₂) =
  |children(R, t₁) △ children(R, t₂)| / |children(R, t₁) ∪ children(R, t₂)|

boundary_drift(R, t₁, t₂) =
  |cross_ratio(R, t₁) - cross_ratio(R, t₂)|
```

---

## 5. DESIGN HYPOTHESIS

**Healthy decompositions keep fan-out manageable while minimizing cross-boundary coupling and churn.**

**Measurable criteria:**

1. **Fan-out in optimal range:**
   ```
   4 ≤ fanout(R) ≤ 9  (Miller's 7±2)
   ```

2. **Low cross-boundary coupling:**
   ```
   cross_ratio(R) < 0.3  (30% of edges cross boundaries)
   ```

3. **Stable over time:**
   ```
   fanout_stability(R) < 2  (low variance)
   boundary_drift(R) < 0.1  (coupling doesn't degrade)
   ```

---

## 6. EMPIRICAL RESULTS (Our Repo - 2026-01-28)

**Measurement executed:** `measure_subdivision_stability.py`

**Results:**
- Total directories analyzed: 4,963
- **Median fan-out: 4** (below optimal 5-9)
- Mode: 1 (many singleton directories)
- Mean: 12.01 (skewed by outliers)

**Interpretation:**
- ⚠️ Median = 4 is just below optimal range
- ✅ 42.8% of directories in optimal range (4-9)
- ❌ Many shallow trees (mode = 1, singleton directories)
- ❌ Some extreme outliers (>100 children)

**Outliers (>100 children):**
- Research dumps: 302 Gemini docs in flat directory
- Archive images: 2,697 files in single directory
- Vendor code: 7,494 PyTorch headers in flat directory

**Conclusion:** Repo is MOSTLY well-organized (median near optimal), but has pockets of flat structure that could benefit from subdivision.

---

## 7. TERMINOLOGY CLARIFICATION

### Module (Overloaded Term)

**To avoid confusion, use:**

**Container** = Directory/file containment unit (filesystem topology)

**Component** = Architectural unit with:
- Intended boundary
- Published interface
- Clear ownership
- Cohesive purpose

**Module** = Language-specific construct:
- Python: .py file or package with __init__.py
- JavaScript: .js file or npm package
- Go: package directory
- Level: Typically L6 (Package) in 16-level scale

**In this theory:**
- "Subdivision" = immediate children count (filesystem)
- "Component" = architectural boundary (design)
- "Module" = code unit at L6 (implementation)

---

## 8. INTEGRATION WITH EXISTING THEORY

**Connects to:**

**L0_AXIOMS (Duality):**
- Codome files contain executable atoms
- Contextome files contain documentation atoms
- Both use same containment topology

**L1_DEFINITIONS (16-Level Scale):**
- L5 (FILE) contains L4 (CONTAINER) contains L3 (NODE)
- Containment defines the scale hierarchy
- Each level is a "container" for the next

**L2_LAWS (Holarchic Structure):**
- "Turtles all the way down" = infinite holarchic nesting
- Each holon contains holons
- Subdivision at each level follows same principles

**L3_APPLICATIONS (Measurement):**
- Fan-out, cross-ratio, stability are measurable
- Empirical testing validates hypotheses
- Observed median = 4 (close to predicted optimal)

---

## 9. VISUALIZATION REQUIREMENTS (From User)

**Must support:**

1. **Toggle views:**
   - Container-only (directories + files)
   - Atom-only (functions + dependencies)
   - Both (overlay)

2. **Animated transitions:**
   - Crossfade between views (750ms)
   - Atoms fade in/out
   - Files remain visible

3. **Typed edges with distinct encoding:**
   - Containment: Visual style A (thin, dashed, grey)
   - Dependency: Visual style B (solid, colored)
   - Never ambiguous

4. **File→Atom edges:**
   - Each file connects to all atoms it contains
   - Progressive disclosure (expand on demand)
   - Prevent visual explosion

**Implementation:** Unified graph (already built, needs testing)

---

## 10. THEORETICAL CONTRIBUTION

**New L2 Law (Proposed):**

**Law of Optimal Subdivision**

> Systems decompose into 4-9 immediate subsystems at each level.
> Deviation indicates either under-organization (too few) or over-complexity (too many).

**Evidence:**
- Cognitive science: Miller's 7±2
- Our repo: Median = 4 (close)
- SUBSYSTEMS.yaml: 5 (optimal)
- Common patterns: 5-7

**To validate:**
- Measure across many repos
- Correlate with maintainability metrics
- Test if refactoring toward 5-7 improves outcomes

---

**Status:** Formalized using user's corrected language
**Next:** Integrate into canonical theory (L1 + L3)
