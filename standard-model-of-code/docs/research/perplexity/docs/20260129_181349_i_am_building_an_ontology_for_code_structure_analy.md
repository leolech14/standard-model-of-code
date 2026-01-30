# Research: I am building an ontology for CODE STRUCTURE ANALYSIS that models software repositories as typed mul...

> **Date:** 2026-01-29 18:13:49
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:0781a24f0f261422dfb4bd9bbc8f1ceafab6c0a9dbfbe757f2c8543c6bd6d4f3`
> **Raw JSON:** `raw/20260129_181349_i_am_building_an_ontology_for_code_structure_analy.json`

---

## Query

I am building an ontology for CODE STRUCTURE ANALYSIS that models software repositories as typed multigraphs with spatial/topological relationships. I need to ground my inventory in established standards.

## CURRENT INVENTORY

### Node Types (Containers)
- Directory, File, Atom (functions, classes, methods, variables)

### Edge Types - Containment (E_contains)
- Directory → Directory (subdirectory)
- Directory → File
- File → Atom

### Edge Types - Dependencies (E_depends)
- calls, imports, inherits, references

### Spatial Concepts We Use
- contains, within, crosses (boundary), adjacent, overlaps
- visible vs hidden (viewport boundary)
- interior vs boundary

### Measurements
- fan-out (branching factor)
- cross-boundary coupling ratio
- Betti numbers (connected components, cycles)
- Euler characteristic

## RESEARCH TASKS

### Task 1: Identify Canonical Inventories
What are the definitive, peer-reviewed taxonomies for:

a) **Spatial Relations** (topological, directional, metric)
   - OGC Simple Features / DE-9IM matrix
   - RCC-8 (Region Connection Calculus)
   - GeoSPARQL ontology
   - ISO 19107 (Spatial Schema)
   - Allen's temporal intervals (for applicability to code regions)

b) **Graph Relations** (for dependency graphs)
   - Is there a canonical taxonomy of edge types in program analysis?
   - Call graphs, data flow, control flow - standard vocabulary?

c) **Topological Invariants** (for code structure)
   - Beyond Betti numbers: persistent homology, Euler characteristic
   - What invariants are used in software complexity analysis?

d) **Error/Anomaly Types** (geometric/topological)
   - OGC geometry validation errors
   - What's the canonical list? (self-intersection, polygon gaps, dangles, pseudo-nodes, spikes)

### Task 2: Gap Analysis
Compare my inventory to the canonical sources:
- What spatial relation types am I MISSING?
- What error types should I add?
- What measurement invariants should I consider?

### Task 3: Unknown Unknowns
Beyond obvious sources, search for:
- Mereotopology (part-whole + topology combined)
- Qualitative spatial reasoning (QSR) in AI
- Graph grammar / graph transformation systems
- Applied algebraic topology in software engineering
- Network motifs and structural patterns

### Task 4: Ontology Architecture
How should I structure an incremental ontology?
- What are the minimum primitives (atomic relations)?
- Which relations are derivable from primitives?
- RCC-8 composition tables - how do they work?
- Should I use OWL/SKOS, or something lighter?

## DELIVERABLES REQUESTED

1. **Canonical Inventory Table**: Map my terms to standard terms with citations
2. **Gap List**: Relations/errors I'm missing with definitions
3. **Unknown Unknowns List**: Concepts from adjacent fields I should investigate
4. **Primitive Set**: Recommended minimal set of atomic relations
5. **Architecture Recommendation**: OWL vs SKOS vs custom, with rationale
6. **Key Papers**: 5-10 foundational papers I should read, with URLs

Provide citations with URLs where possible. Prefer ISO/OGC specs, peer-reviewed papers, and authoritative sources.

---

## Response

# Formal Ontological Grounding for Code Structure Analysis: A Spatial-Topological Framework Based on ISO/OGC Standards and Foundational Theories

This comprehensive research report addresses the integration of established spatial-topological standards with code structure analysis by systematically examining canonical inventories from the Open Geospatial Consortium, the International Organization for Standardization, foundational ontology research, and qualitative spatial reasoning. The analysis identifies that while geospatial standards provide robust formalisms for spatial relations (particularly the Dimensionally Extended 9-Intersection Model and Region Connection Calculus), software structure analysis requires augmentation with mereotopological primitives, graph-theoretic relations, and novel error taxonomies adapted from geometric validation. The minimal primitive set should comprise six foundational relations—parthood, connection, dependence, location, interior-part, and boundary—from which both spatial and graph-theoretic relations can be derived through formal composition rules. The recommended ontology architecture employs OWL 2 with a lightweight core conforming to the SEMIC semantic conventions, supplemented by a mereotopological module following Barry Smith's foundational work, and implements spatial relation queries through GeoSPARQL-inspired SPARQL extensions adapted for directed acyclic graph structures.

## Canonical Spatial Relations Frameworks: The Definitive Standards

### The Dimensionally Extended 9-Intersection Model (DE-9IM)

The most fundamental standard for capturing spatial topological relations is the Dimensionally Extended 9-Intersection Model, which has been standardized by the Open Geospatial Consortium and is implemented across all major spatial databases and geographic information systems[1][4][19]. The DE-9IM provides a mathematical foundation for reasoning about spatial relationships by decomposing any two geometric objects into their interior, boundary, and exterior components and then examining all nine possible intersections between these components[1]. Formally, given two geometric objects *a* and *b*, the model constructs a matrix where each cell contains the dimension of the intersection result, with dimensions represented as -1 (empty), 0 (point), 1 (line), or 2 (area)[4][19]. This approach yields 512 theoretically possible topological relations, from which approximately 8 base relations between simple two-dimensional regions can be realized, and from these base relations derive the common named predicates such as Equals, Disjoint, Intersects, Touches, Crosses, Overlaps, Within, and Contains[1][4][19].

The mathematical elegance of DE-9IM lies in its invariance properties: the spatial relations expressed by the model are invariant to rotation, translation, and scaling transformations, meaning the topological relationship between two geometries depends solely on the structure of their boundaries and interiors, not on their position, orientation, or size[4][19]. The OGC standardization documents specify that the matrix is formally expressed as \( \dim(I(a) \cap I(b)), \dim(I(a) \cap B(b)), \dim(I(a) \cap E(b)), \dim(B(a) \cap I(b)), \dim(B(a) \cap B(b)), \dim(B(a) \cap E(b)), \dim(E(a) \cap I(b)), \dim(E(a) \cap B(b)), \dim(E(a) \cap E(b)) \)[1][4], where \( I \) denotes interior, \( B \) denotes boundary, and \( E \) denotes exterior. This formalism enables not only the definition of named predicates (which are implementations of DE-9IM pattern matrices) but also enables complete descriptive queries: rather than asking "does geometry *a* touch geometry *b*?", one can ask "what is the complete topological relationship between *a* and *b*?" and receive a 9-character string encoding all intersection dimensions[4][19].

Critically for your software ontology, the DE-9IM standard accommodates objects of different dimensionality and different dimensions of embedding space[22][38][41]. For example, a line intersecting a polygon produces different DE-9IM matrices than a point intersecting a line, and the 9-intersection provides finer granularity than the earlier 4-intersection model (which only considered interior and boundary) for distinguishing these cases[22][38]. This dimensionality-aware approach maps directly to your code structure problem: a function (1-dimensional flow graph) may cross a module boundary in topologically distinct ways than a class (2-dimensional containment) crosses the same boundary.

### Region Connection Calculus (RCC-8)

While DE-9IM focuses on dimensional intersection details, the Region Connection Calculus (RCC) provides an alternative formalism grounded in qualitative spatial reasoning that may be more appropriate for certain code structure queries[2][5][27][30]. RCC-8 defines exactly eight mutually exclusive and collectively exhaustive relations between spatial regions: Disconnected (DC), Externally Connected (EC), Partially Overlapping (PO), Tangential Proper Part (TPP), Non-Tangential Proper Part (NTPP), Tangential Proper Part Inverse (TPPi), Non-Tangential Proper Part Inverse (NTTPi), and Equal (EQ)[2][5][30]. The formalism is based on a primitive connection relation \( C(x,y) \) read as "x is connected to y," meaning the closures of the two regions have a non-empty intersection[2][5].

The RCC framework differs fundamentally from DE-9IM in its epistemic grounding: RCC-8 relations are *qualitatively* exhaustive, meaning given no additional constraints, any two regions must stand in exactly one of these eight relations[2][5]. This property makes RCC-8 ideal for scenarios where precise metric information is unavailable but qualitative spatial knowledge is reliable—a condition that often applies to code structure analysis where exact call counts matter less than relationship topology[20]. The formal semantics of RCC-8 in a typical interpretation require that for any region pair, the relations can be axiomatically characterized in terms of the connection predicate and standard mereological operations (part-of, overlap)[2][5][30].

GeoSPARQL, the OGC standard for geospatial linked data querying, implements both DE-9IM through the Simple Features relation family and RCC-8 through dedicated spatial functions[3][6]. The specification provides a crucial bridge to semantic web technologies: spatial relations can be expressed as RDF properties or as SPARQL filter functions, enabling integration with ontological reasoning[3][6]. For your code structure ontology, this suggests that spatial relations should be representable both as object properties in OWL and as queryable SPARQL functions.

### ISO 19107 and the Spatial Schema Standard

ISO 19107:2019 (Geographic information — Spatial schema) provides the authoritative specification for conceptual schemas describing spatial characteristics and spatial operations[7][10]. This standard defines geometric objects as organized into a class hierarchy including Point, Curve, Surface, GeometryCollection and their variants, each associated with a spatial reference system[1][7]. Importantly, ISO 19107 distinguishes between geometric primitives (non-decomposed, single-connected objects) and geometric aggregates (collections of primitives), a distinction that maps directly to your File-Atom and Directory-File hierarchies[1].

The spatial schema also formalizes the concept of boundaries: a boundary is defined as the set of limit points of a geometric object, and a fundamental axiom (implicit in topological definitions) holds that boundaries have lower dimension than their parent objects[7]. This becomes critical when reasoning about code structure: the boundary between modules (a fiat boundary in geographic ontology terms) or the interface between components forms a topological entity that may participate in topological relations independently of the components themselves.

## Graph-Based Relations for Software Dependency Analysis

### Formal Structure of Software Dependency Graphs

While the OGC spatial standards provide powerful formalisms for modeling containment and adjacency, software structure involves explicit semantic relationships that lack direct analogs in geometric space. Your dependency edge types (calls, imports, inherits, references) require their own formal framework. A control flow graph (CFG) is typically formalized as a directed graph \( G = (V, E) \) where vertices represent program statements or basic blocks and edges represent possible execution flows, while a data flow graph (DFG) adds edges representing variable definition-use relationships[16]. In the context of your ontology, these should be distinguished as separate edge relation types with distinct semantics and transitivity properties.

The formalization of call graphs presents an additional layer of structure: a call graph typically forms a directed acyclic graph (DAG) or contains strongly connected components (SCCs) representing mutually recursive function sets[37][58]. This graph structure admits cycle detection, reachability analysis, and transitive dependency computation—all operations that have no direct equivalent in spatial topologies but are critical for understanding code structure[37][58]. Program dependence graphs (PDGs) further extend this by combining control and data dependencies into a single formal structure[13].

A crucial distinction emerges when comparing graph structures to spatial topologies: cycles in dependency graphs represent mutual dependence, which corresponds to semantic circularity rather than spatial containment. Your current inventory does not explicitly address cycles, yet they are topologically and ontologically distinct from acyclic dependency patterns. This suggests the need for a graph-theoretic primitive encoding cyclicity or mutual dependence, separate from spatial relation primitives.

### Network Motifs and Structural Patterns

Network motifs—recurring patterns of interconnections appearing more frequently in real networks than in randomized graphs—provide a language for describing characteristic structures in dependency graphs[21][24]. Common motifs in software dependency networks include feed-forward loops (one component controls another which controls a third, without feedback), bifan patterns (one component feeding multiple targets while receiving from multiple sources), and clustering triangles (three mutually dependent components)[21][24]. These motifs have no direct representation in your current inventory and represent a category of higher-order structural properties distinct from pairwise relations.

The significance of network motifs lies in their ontological implications: they are not reducible to sets of binary relations, but rather represent irreducible combinatorial patterns that encode functional and causal structure[21][24]. For code structure analysis, a feed-forward loop in the dependency graph carries information about layering and abstraction hierarchy, while a clustering triangle indicates potential circular coupling or shared responsibility. These patterns should be explicitly representable in your ontology as composite structures or constraint patterns rather than primitive relations.

## Topological Invariants and Software Complexity Measurement

### Betti Numbers and Homological Structure

You identify Betti numbers and Euler characteristic as measurements of code structure. Betti numbers, the ranks of homology groups, quantify topological features at different dimensions: the zeroth Betti number counts connected components, the first Betti number counts independent cycles (genus), and the second Betti number counts voids or cavities[15]. In the context of directed acyclic graphs representing code structure, the first Betti number—representing the cyclomatic complexity—directly corresponds to the number of linearly independent cycles in the control flow graph[32][35].

The Euler characteristic \( \chi = V - E + F \) for a planar graph provides a topological invariant that, combined with Betti numbers, fully characterizes the graph's gross topological structure[15]. For a directed acyclic graph (DAG) with \( n \) vertices and \( m \) edges, if the graph is embedded as a planar structure, the Euler characteristic equals 2 minus twice the first Betti number, providing a consistency check on topological complexity measurements[15].

Topological data analysis (TDA) and persistent homology extend these concepts by examining how topological features persist across different scales or resolutions[15][18][25]. While not yet widely applied to software analysis, persistent homology could detect code structure properties that remain invariant across different levels of granularity (e.g., module, file, function levels). The birth and death times of topological features (captured as persistence diagrams) would encode at what architectural scale certain structural patterns emerge.

### Coupling and Cohesion Metrics

Coupling metrics quantify inter-component dependencies: Coupling Between Objects (CBO) measures the number of other classes a class depends on, while Coupling Through Message Passing (CTM) measures message counts[32][35]. Cohesion metrics measure intra-component relationships: Lack of Cohesion in Methods (LCOM) assesses whether methods within a class operate on shared state[32][35]. These metrics lack explicit topological grounding in your current inventory but represent measurable consequences of the spatial relations you model.

Critically, cyclomatic complexity—a classical software metric—is formally equivalent to the first Betti number of the control flow graph, meaning your topological framework can subsume existing complexity measurements[32][35]. This suggests that a unified topological-graph-theoretic framework can replace fragmented metrics with a coherent formal system.

## Error and Anomaly Classification: Geometric Validation Applied to Code Structure

### OGC Topology Validation Rules

The OGC and GIS standards specify a comprehensive set of topology validation rules for geometric data, including polygon self-intersection, boundary gaps, dangling line endpoints, pseudo-nodes (line endpoints touching line interiors), and duplicate geometry[31][34]. These rules emerge from the requirement that geographic data maintain spatial integrity: a polygon must have a non-self-intersecting boundary, must enclose a well-defined area, and must participate in valid topological relationships with adjacent features[31][34].

Your code structure ontology should incorporate an isomorphic set of validation rules:

**Containment Integrity**: Files must not circularly contain themselves (analogy: polygon self-intersection). Directory hierarchies must form directed acyclic graphs (analogy: polygon boundaries must not self-intersect).

**Boundary Consistency**: Atoms within a file must have non-overlapping scopes (analogy: non-overlapping polygon interiors). Module boundaries must be well-defined (analogy: polygon boundaries must be closed curves).

**Dependency Validity**: Dependency edges must respect containment boundaries—a file dependency must be routable through directory interfaces (analogy: line endpoints must touch polygon vertices or edges, not float within interiors).

**Interface Completeness**: All external dependencies from a component must be declared (analogy: no dangling line endpoints floating outside of polygon boundaries).

**Topological Consistency**: Circular dependencies must not occur in acyclic dependency layers (analogy: polygon ring orientation consistency).

### Geometric Anomalies Translated to Code Structure

The comprehensive list of geometric validation errors from GIS standards[31][34] maps onto code structure anomalies as follows:

| Geometric Anomaly | GIS Meaning | Code Structure Analog | Ontological Type |
|---|---|---|---|
| Polygon self-intersection | Boundary crosses itself | Cyclic containment | Boundary integrity violation |
| Gaps between polygons | Uncovered regions | Missing dependencies or incomplete coverage | Coverage completeness violation |
| Dangling line endpoints | Line terminates without connection | Unresolved symbol references | Boundary connectivity violation |
| Pseudo-nodes | Line endpoint touches line interior | Scope overlap at wrong level | Granularity/boundary mismatch |
| Duplicate geometry | Same feature stored twice | Duplicated function definitions | Identity violation |
| Overlapping polygon interiors | Two regions occupy same space | Name collision or shadowed scope | Exclusivity violation |
| Unclosed polygon rings | Boundary not continuous | Incomplete module interface | Boundary closure violation |

This taxonomy suggests that your error model should be grounded in the topological invariants and boundary conditions of your formal system rather than being an ad hoc list.

## Mereotopology: Integrating Part-Whole and Spatial Relations

### Foundational Theory of Parts and Boundaries

Mereotopology, the combined theory of parts (mereology) and spatial topology, provides the rigorous foundation that geospatial standards implicitly assume[9][12][36][43]. Mereology axiomatically defines the part-of relation (≤) as reflexive (everything is a part of itself), antisymmetric (if x is a part of y and y is a part of x, then x equals y), and transitive (if x is part of y and y is part of z, then x is part of z)[12][36][43]. From the primitive parthood relation, additional relations can be derived: proper parthood (PP), overlap (O), and disjointness (DR)[12][36][43].

Topology adds a primitives connection relation (C) or interior-part relation (IP), enabling distinction between tangential connections (where parts touch at boundaries) and non-tangential containment (where contained parts lie strictly in the interior)[9][12][36]. The critical axiom governing boundaries in mereotopology is Brentano's thesis: a boundary of an object can exist only as part of a higher-dimensional whole[9][12]. Formally, if B(x,y) reads "x is a bona fide boundary of y," then the dimension of x must be strictly less than the dimension of y[12][36].

For your code structure ontology, Brentano's thesis translates to: a module boundary (1-dimensional interface) can exist only as part of a 2-dimensional (or higher) component structure; an atom's visibility boundary (0-dimensional scope) can exist only within a 1-dimensional context (function, class). This provides rigorous justification for hierarchical structure and prevents incoherent ontological combinations.

### Fiat Boundaries Versus Bona Fide Boundaries

Mereotopology distinguishes between bona fide boundaries (naturally occurring limits intrinsic to an object, such as a mountain range's edges) and fiat boundaries (humanly imposed divisions, such as national borders)[12][36][43]. This distinction is crucial for code structure: containment imposed by file system directories represents fiat boundaries (the same set of atoms could be organized differently), while function scope boundaries represent something closer to bona fide boundaries (determined by language syntax and semantics).

The axiomatization of fiat boundaries (denoted B* rather than B) differs significantly: fiat boundaries are transitive (if x is a fiat boundary of y, and y is a fiat boundary of z, then x is a fiat boundary of z), whereas bona fide boundaries are not[12][36][43]. This suggests that your ontology should distinguish between structural hierarchy (bona fide) and organizational structure (fiat), with different composition rules for each.

### Connection via Fiat Boundary

Two discrete (non-overlapping) entities can be fiat-boundary-connected only if one of them is not closed (does not include all its bona fide boundaries as parts)[12][36][43]. For code structure, this axiom prevents incoherent scenarios where a complete module (including all its internal structure) is connected to external code through a fiat boundary without any actual interface. Connection must occur through an explicitly defined interface—a partially bounded or open structure.

## Qualitative Spatial Reasoning and Conceptual Neighborhoods

### QSR Frameworks Beyond Metrics

Qualitative spatial reasoning (QSR), a subdiscipline of artificial intelligence, develops calculi for spatial relations without requiring metric information[20][23][27]. Beyond topological relations (RCC-8, DE-9IM), QSR formalisms include directional relations (north, south, left, right), ordinal relations (before, after, between), and distance relations (near, far, comparable)[20][23]. While directional reasoning has limited applicability to code structure, the formalism of compositional reasoning through relation algebras is highly relevant.

QSR systems specify that any spatial calculus must satisfy the property of being jointly exhaustive and pairwise disjoint (JEPD): for any two entities, exactly one relation from the set must hold, and no two relations can simultaneously apply[20][23]. Your current inventory violates this property: an atom might simultaneously satisfy "within" and "crosses" (boundary), which are logically incompatible. Ensuring JEPD consistency would eliminate ambiguity in your spatial queries.

### Conceptual Neighborhoods and Transitional Relations

A crucial concept from QSR is the conceptual neighborhood graph, which organizes relations such that topological transformations correspond to transitions between neighboring relations[20][23]. For example, two regions that are tangentially adjacent can transform continuously into two regions that overlap, but cannot transform directly into two regions that are disjoint without passing through an intermediate state[20][23]. This topology of relation space—the structure of possible transitions—encodes constraints on how spatial configurations can evolve.

For code structure, this suggests that certain refactorings (moving a function from one class to another) trace paths through a space of topological relations, and understanding these paths enables intelligent refactoring assistance. A function cannot transition directly from "contains" to "disjoint" without passing through "crosses" or "touches."

## Ontology Formalization: Architecture and Implementation

### Minimal Primitive Set

Based on the analysis of canonical standards and foundational theories, the minimal set of primitive relations from which others can be derived comprises:

1. **Parthood (P)**: Fundamental mereological relation; x P y reads "x is a part of y" (includes identity as improper part). Axiomatically reflexive, antisymmetric, and transitive[12][36][43].

2. **Connection (C)**: Fundamental topological relation; C(x,y) reads "the closures of x and y have non-empty intersection." Enables distinction between discrete and overlapping entities[2][5][12].

3. **Dependence (D)**: Ontological relation; D(x,y) reads "the existence of x is dependent on the existence of y." Reflexive, transitive, and non-symmetric[43]. Encodes call dependencies and semantic coupling.

4. **Interior-Part (IP)**: Topological refinement of parthood; IP(x,y) reads "x is a part of y that lies in the interior of y (not touching the boundary)." Derives from P and C[9][12].

5. **Location (L)**: Spatial location relation; L(x,y) reads "x is exactly located at region y." Functional (each entity locates at exactly one region at a given time). Bridges mereology to spatial embedding[36][43].

6. **Boundary (B)**: Topological relation; B(x,y) reads "x is a bona fide boundary of y." Axiomatically constrained by Brentano's thesis: dimension(x) < dimension(y)[12][36][43].

From these six primitives, all OGC spatial predicates, RCC-8 relations, and code-structure-specific relations can be formally derived. For instance:

- **Equals (EQ)**: \( EQ(x, y) \equiv P(x, y) \wedge P(y, x) \)
- **Proper Part (PP)**: \( PP(x, y) \equiv P(x, y) \wedge \neg P(y, x) \)
- **Overlap (O)**: \( O(x, y) \equiv \exists z(P(z, x) \wedge P(z, y)) \)
- **Disjoint (DR)**: \( DR(x, y) \equiv \neg O(x, y) \)
- **Tangential Proper Part (TPP)**: \( TPP(x, y) \equiv PP(x, y) \wedge C(x, y) \)
- **Touches**: \( \text{Touches}(x, y) \equiv C(x, y) \wedge \neg O(x, y) \)

### OWL 2 Implementation with Lightweight Semantics

The recommended ontology implementation uses OWL 2 with semantic constraints ensuring lightweight decidability, following the SEMIC semantic conventions[29][44][47]. The architecture comprises three layers:

**Core Layer (OWL 2 DL)**: Defines the six primitive relations as object properties with cardinality constraints and domain/range restrictions. Primitive relations are declared as disjoint where appropriate (e.g., Disjoint and Overlap are mutually exclusive). The core layer remains minimal and decidable, supporting efficient reasoning.

**Derived Relations Layer**: Defines all OGC predicates (DE-9IM, RCC-8), graph-theoretic relations, and code-structure-specific relations as restrictions or compositions of primitives. These are declared as object properties with formal definitions expressed as OWL class restrictions or SWRL rules.

**Domain-Specific Extension Layer**: Specialized rules for code structure validation, including topology validation rules, error classifications, and metric computations. This layer uses SHACL (Shapes Constraint Language) for constraint specification and SPARQL for query and inference patterns.

The implementation follows the principle of **no automated reasoning assumption**: the ontology is designed such that SPARQL queries and explicit derivation rules provide reasoning capability, rather than relying on full first-order logic inference[29]. This choice balances expressivity with practical tractability.

### SPARQL Integration and Spatial Queries

GeoSPARQL provides a blueprint for integrating spatial relations with linked data queries[3][6]. Spatial relations are expressed both as RDF properties (for basic triple patterns) and as SPARQL extension functions (for complex spatial conditions). The architecture recommends:

1. **Primitive relations as OWL object properties**: Core relations (Parthood, Connection, Dependence) are directly queryable via SPARQL triple patterns.

2. **Derived relations as SPARQL filter functions**: Complex relations like "transitively contains" or "crosses boundary" are implemented as SPARQL functions that accept geometry or structural parameters and return boolean results.

3. **Composition rules as SPARQL path expressions**: Allen's interval algebra-inspired composition tables (e.g., "If A calls B and B calls C, then A transitively calls C") are expressed using SPARQL property paths (?x calledBy* ?y).

Example query pattern:
```sparql
PREFIX code: <http://example.org/code-structure#>
PREFIX rcc: <http://example.org/rcc8#>

SELECT ?function ?module
WHERE {
  ?function code:dependsOn ?target .
  ?module code:contains ?boundary .
  ?target code:crossesBoundary ?boundary .
  FILTER(rcc:crosses(code:geometry(?target), code:geometry(?boundary)))
}
```

This query retrieves functions with external dependencies that topologically cross module boundaries, combining structural properties (dependsOn, contains) with topological predicates (crossesBoundary, rcc:crosses).

## Gap Analysis: Inventory Enhancements

### Missing Spatial Relation Types

Comparing your current inventory against canonical sources reveals several important gaps:

**Directional Relations** (not in inventory): While directional reasoning (above, below, left, right) has limited application to abstract code structure, the formalism of ordinal relations (precedes, follows, between) applies to sequential dependency analysis. If code execution or compilation order carries semantic significance, these relations should be represented.

**Distance Relations** (mentioned as "metric" only): QSR distinguishes among far, near, similar-distance relations independent of absolute metric values[20][23]. For code structure, metric-independent distance concepts like "few intermediate dependencies" versus "many intermediate dependencies" or "tightly coupled" versus "loosely coupled" enable qualitative reasoning without precise measurements.

**Composition Results** (not systematically enumerated): Your inventory lists relations but does not capture composition semantics. From RCC-8 theory, we know that "A is tangentially part of B" combined with "B non-tangentially contains C" yields a specific set of possible relations between A and C, formalized in composition tables[2][5]. Systematically enumerating composition results enables transitive queries and consistency checking.

**Higher-Dimensional Objects** (implicit in inventory): Your mention of "crosses (boundary)" suggests awareness of dimensional distinctions, but the ontology does not explicitly represent dimensionality. Extending your primitives to include explicit dimension tags (or using typed containment with dimension constraints) would enable dimensional type checking and automatic detection of invalid combinations.

**Cyclic Versus Acyclic Structures** (missing**: While RCC-8 and DE-9IM describe topological relations, neither explicitly addresses cycles. Your ontology should include a primitive or derived relation encoding mutual dependence or cyclicity, distinct from topological relations. In directed graphs, this corresponds to strong connectivity; in undirected structures, this corresponds to the existence of cycles.

### Missing Error and Anomaly Types

Extending the error taxonomy from GIS validation rules:

**Boundary Discontinuity Errors**: File scope boundaries that are not properly closed or aligned with language syntax (analogy: non-closed polygon rings). Examples: inconsistent visibility modifiers across method signatures, partially implemented abstract interfaces.

**Scope Shadowing Errors**: Inner scope variables with identical names to outer scope variables, creating name collision at the boundary between scopes (analogy: overlapping polygon interiors). This violates the exclusivity principle for identity.

**Coupling Discontinuity Errors**: Dependencies that skip abstraction layers without documented justification, violating expected hierarchical structure (analogy: dangling line endpoints floating to wrong level). Examples: direct access to private members of unrelated classes, architectural layer violations.

**Circular Import Chains**: Cyclical dependencies among files or modules that violate acyclic dependency assumptions (analogy: non-planar graph with hidden cycles). More specific than general cycles, these represent specific classes of semantic inconsistency.

**Interface Incompleteness Errors**: Required external dependencies that are not declared through interfaces but accessed through side effects or reflective mechanisms (analogy: implicit connections without topological registration).

### Unknown Unknowns: Adjacent Theoretical Frameworks

**Qualitative Temporal Reasoning**: Allen's interval algebra (1983) defines 13 base temporal relations (precedes, meets, overlaps, starts, during, ends, etc.) with formal composition tables[8][11]. While your ontology addresses spatial relations, temporal aspects of code structure (compilation order, execution order, development history) admit isomorphic temporal calculi. A unified spatiotemporal framework could model temporal evolution of code structure.

**Graph Transformation Systems and Graph Grammars**: Graph grammars formalize rule-based mechanisms for generating or transforming graphs, with application to natural language processing and formal language theory[14][17]. Code refactoring can be formally specified as graph transformation rules: a rule matches a subgraph pattern in the code dependency structure and replaces it with a transformed version. This framework enables systematic formalization of refactoring correctness and composability.

**Topological Data Analysis and Persistent Homology**: TDA employs persistent homology to track topological features across different scales of resolution[15][18][25]. Applied to code structure at different levels of granularity (module, file, function, statement), persistent homology could identify robust structural patterns that remain invariant across granularities. Birth and death times of cycles reveal at what architectural scale circular dependencies emerge.

**Abstract Syntax Trees and Program Semantics**: Abstract syntax trees (ASTs) provide formal tree representations of program structure that differ from dependency graphs[50][53]. While your ontology focuses on spatial relations among components, AST-based approaches offer precise syntactic structure. Integration with AST theory enables formal specification of scope rules, visibility constraints, and syntactic validity.

**Network Motifs and Modular Structure**: Network motifs provide a language for hierarchical and modular structure detection in complex networks[21][24]. Software architectures exhibit characteristic motifs (layered architectures, microservices patterns, plugin architectures) that could be formally specified as motif patterns and used for architectural validation and understanding.

**Foundational Ontologies: BFO, DOLCE, UFO**: Beyond the mereotopological primitives, comprehensive foundational ontologies like Basic Formal Ontology (BFO), Descriptive Ontology for Linguistic and Cognitive Engineering (DOLCE), and Unified Foundational Ontology (UFO) provide established frameworks for representing entities, events, roles, and qualities[49][52]. DOLCE's distinction between endurants (continuants: objects) and perdurants (occurrents: events), and its formalization of constitution and quality relations, could enrich your ontology with temporal and qualitative dimensions.

**Formal Concept Analysis**: Formal Concept Analysis (FCA) provides a mathematical framework for analyzing structures of data through partially ordered sets and lattices. Applied to code structure, FCA could identify hierarchical concept lattices representing abstraction levels, design patterns, and architectural constraints.

## Canonical Inventory Table: Mapping Your Terms to Standards

| Your Term | OGC/ISO Standard | Formal Definition | Primitive Roots | Notes |
|---|---|---|---|---|
| contains | DE-9IM Contains / RCC-8 NTTPi | \( I(a) \cap I(b) \neq \emptyset \) AND \( E(a) \cap B(b) = \emptyset \) AND \( E(a) \cap I(b) = \emptyset \) | Connection, Interior-Part | Requires non-tangential containment; tangential variant uses Touches predicate |
| within | DE-9IM Within / RCC-8 NTPP | \( I(a) \cap I(b) \neq \emptyset \) AND \( a \cap E(b) = \emptyset \) AND \( B(a) \cap E(b) = \emptyset \) | Parthood, Interior-Part | Inverse of Contains; within-or-touching variant is Covers |
| crosses | DE-9IM Crosses | \( \dim(I(a) \cap I(b)) = 1 \) AND \( a \notin b \) AND \( b \notin a \) | Connection, Interior-Part | Strictly requires shared interior with parts outside |
| adjacent | RCC-8 EC | \( C(x,y) \wedge \neg O(x,y) \) | Connection, Parthood | Externally connected; boundaries touch but interiors disjoint |
| overlaps | DE-9IM Overlaps / RCC-8 PO | \( I(a) \cap I(b) \neq \emptyset \) AND \( a \not\subseteq b \) AND \( b \not\subseteq a \) | Overlap (derived) | Requires same dimension and partial mutual containment |
| equal | DE-9IM Equals / RCC-8 EQ | \( a \subseteq b \wedge b \subseteq a \) | Parthood | Identity under topological equivalence |
| disjoint | RCC-8 DC | \( \neg C(x,y) \) | Connection (negation) | Disconnected; no contact or overlap |
| touches | DE-9IM Touches / RCC-8 EC | \( C(x,y) \wedge \neg O(x,y) \) | Connection, Parthood | Boundaries intersect; interiors disjoint |
| visible | (non-standard) | \( IP(x, \text{scope}) \) | Interior-Part | Scope boundary inclusion determines visibility; requires language-specific rules |
| hidden | (non-standard) | \( \neg IP(x, \text{scope}) \) | Interior-Part (negation) | Inverse of visible; outside current scope |
| calls | (program analysis standard) | \( \text{Dependence}(\text{func}_a, \text{func}_b) \in \text{CallType} \) | Dependence | Directed semantic dependency; not symmetric |
| imports | (program analysis standard) | \( \text{Dependence}(\text{module}_a, \text{module}_b) \in \text{ImportType} \) | Dependence | Structural dependency on external module |
| inherits | (program analysis standard) | \( \text{Dependence}(\text{class}_a, \text{class}_b) \in \text{InheritanceType} \) | Dependence | Semantic subtyping relationship; affects scope and method resolution |
| references | (program analysis standard) | \( \text{Dependence}(\text{entity}_a, \text{entity}_b) \in \text{ReferenceType} \) | Dependence | Generic reference; subsumes calls, imports, inherits |

## Primitive Set Formal Specification

The six primitive relations are formally axiomatized as follows:

**Parthood (P)**:
- Reflexivity: \( \forall x: P(x, x) \)
- Antisymmetry: \( P(x, y) \wedge P(y, x) \rightarrow x = y \)
- Transitivity: \( P(x, y) \wedge P(y, z) \rightarrow P(x, z) \)
- Extensionality: \( \forall z[P(z, x) \leftrightarrow P(z, y)] \rightarrow x = y \)

**Connection (C)**:
- Symmetry: \( C(x, y) \leftrightarrow C(y, x) \)
- Closure property: Enables definition of closure, interior, and boundary

**Dependence (D)**:
- Reflexivity: \( \forall x: D(x, x) \)
- Transitivity: \( D(x, y) \wedge D(y, z) \rightarrow D(x, z) \)
- Semantic constraint: \( \text{exists}(y) \rightarrow \text{exists}(x) \) where \( D(x, y) \)

**Interior-Part (IP)**:
- Definition: \( IP(x, y) \equiv P(x, y) \wedge \exists r[C(r, x) \wedge \neg C(r, y)] \)
- Consequence: IP objects lie strictly interior to their container

**Location (L)**:
- Functionality: \( L(x, r_1) \wedge L(x, r_2) \rightarrow r_1 = r_2 \)
- Bridge axiom: \( L(x, y) \rightarrow \exists z[P(z, y) \wedge C(x, z)] \)

**Boundary (B)**:
- Brentano's Thesis: \( B(x, y) \rightarrow \text{dimension}(x) < \text{dimension}(y) \)
- Closure property: \( B(x, y) \rightarrow P(x, \text{closure}(y)) \)

## Architecture Recommendation: OWL 2 with SHACL Validation

The recommended ontology architecture employs three integrated but distinct semantic layers:

**Layer 1 - OWL 2 DL Core** (Decidable, Lightweight):
- Classes: Object (mereological primitive), SpatialRegion (topological dimension-aware), Atom, Container, Boundary
- Object Properties: partOf, connectedTo, dependsOn, locatedAt, boundaryOf (six primitive relations)
- Cardinality constraints on Location (functional) and limited composition rules to maintain decidability
- Rationale: OWL 2 DL provides decidable, tractable reasoning; widely supported by tools (Protégé, Hermit, Pellet); integrates with RDF/SPARQL infrastructure

**Layer 2 - SPARQL/SWRL Derivation** (Extensible, Implementable):
- Derived relations (Contains, Within, Touches, Overlaps, Calls, etc.) as named SPARQL queries or SWRL rules
- Composition tables encoding RCC-8 and DE-9IM composition rules
- Path expressions for transitive closure (e.g., transitiveCalls = calls+ using SPARQL property paths)
- Rationale: SPARQL functions provide expressivity beyond OWL restrictions; implementable in any triple store without heavyweight reasoning; supports full RCC-8 and DE-9IM semantics

**Layer 3 - SHACL Constraints and Validation** (Domain-specific, Non-semantic):
- Topology validation rules (no circular containment, boundary consistency, etc.)
- Type coercion rules (fiat boundaries vs. bona fide boundaries)
- Error and anomaly detection rules
- Domain-specific metric computations
- Rationale: SHACL provides constraint-checking independent of OWL reasoning; enables validation without polluting the semantic core; separates ontological consistency from domain-specific correctness

This three-layer architecture balances semantic rigor (OWL layer), practical expressivity (SPARQL layer), and domain-specific validation (SHACL layer), following the principle of separation of concerns and the SEMIC recommendation for lightweight semantic artifacts[29].

## Key Foundational Papers and Resources

1. **Dimensionally Extended 9-Intersection Model**: Egenhofer, M.J., and Herring, J.R. (1991). "Categorizing Binary Topological Relations Between Regions, Lines, and Points in Geographic Databases." Available as OGC Technical Report through the Open Geospatial Consortium. This paper formalizes DE-9IM and provides the definitive categorization of topological relations; foundational for all subsequent OGC spatial standards.

2. **Region Connection Calculus**: Randell, D.A., Cohn, A.G., and Cui, Z. (1992). "A Spatial Logic based on Regions and Connection." In: Proceedings, Third International Conference on Knowledge Representation and Reasoning. Morgan Kaufmann Publishers. Formalizes RCC-8 with complete axiomatization and provides composition tables; introduces the connection primitive as foundational.

3. **Mereotopology Theory**: Smith, B. (1996). "Mereotopology: A Theory of Parts and Boundaries." Data & Knowledge Engineering, 20(3), 287-303. Available at: http://ontology.buffalo.edu/smith/articles/Mereotopology1.pdf Provides rigorous axiomatization combining mereology with topology; introduces Brentano's thesis formalization; foundational for ontological grounding.

4. **Allen's Interval Algebra**: Allen, J.F. (1983). "Maintaining Knowledge about Temporal Intervals." Communications of the ACM, 26(11), 832-843. Formalizes 13 base temporal relations with composition table; while temporal, the algebra structure applies directly to spatial relation reasoning.

5. **GeoSPARQL Standard**: OGC Standard (2021). "GeoSPARQL - A Geographic Query Language for RDF Data." OGC 11-052r5. Available at: https://www.ogc.org/standards/geosparql. Specification for integrating spatial relations with RDF/SPARQL; provides concrete implementation patterns for ontology-based spatial reasoning.

6. **ISO 19107 Spatial Schema**: International Organization for Standardization (2019). "Geographic information — Spatial schema." ISO 19107:2019. Available through ISO: https://www.iso.org/standard/66175.html. Authoritative specification for geometric objects, spatial reference systems, and operations; normative reference for GIS standards.

7. **Foundational Ontologies Survey**: Borgo, S., and Masolo, C. (2010). "Foundational Choices in DOLCE." In: Frontiers in Artificial Intelligence and Applications, Vol. 218. IOS Press. Available at: http://www.loa.istc.cnr.it/wp-content/uploads/2020/02/FoundationalChoicesBorgoMasoloPUB.pdf. Comprehensive analysis of foundational ontological choices with comparison of BFO, DOLCE, and alternatives; essential for understanding design trade-offs.

8. **Qualitative Spatial Reasoning**: Cohn, A.G., and Renz, J. (2008). "Qualitative Spatial Representation and Reasoning." In: Handbook of Knowledge Representation. Elsevier. Comprehensive survey of QSR formalisms including RCC, cardinal directions, and distance relations; establishes JEPD principle and composition table methodology.

9. **Topological Data Analysis**: Otter, N., Porter, M.A., Tillmann, U., and Grindrod, P. (2017). "A roadmap for the computation of persistent homology." EPJ Data Science, 6, 17. https://doi.org/10.1140/epjds/s13688-017-0109-5. Provides computational framework for persistent homology; discusses application of algebraic topology to data analysis at multiple scales.

10. **Ontological Tools for Geographic Representation**: Smith, B. (2001). "Ontological Tools for Geographic Representation." In: Proceedings, FOIS Conference. Available at: http://ontology.buffalo.edu/smith/articles/fois(csv).pdf. Applies mereotopology to geographic information, particularly bona fide versus fiat boundaries; directly applicable to software structure representation.

## Conclusion and Implementation Roadmap

Your ontology for code structure analysis can achieve rigorous formal grounding by integrating established standards from geospatial information science with foundational ontology research and graph-theoretic analysis. The integration of the Dimensionally Extended 9-Intersection Model for spatial-topological relations, Region Connection Calculus for qualitative reasoning, mereotopology for part-whole relations, and program analysis standards for dependency semantics creates a unified framework more powerful and more coherent than any single tradition alone.

The minimal primitive set of six foundational relations (Parthood, Connection, Dependence, Interior-Part, Location, Boundary) provides sufficient expressive power to derive all OGC spatial predicates, all RCC-8 relations, and all necessary code-structure-specific relations through formal composition and derivation rules. The recommended three-layer ontology architecture (OWL 2 DL core, SPARQL/SWRL derivation, SHACL validation) balances formal rigor with practical implementability and enables integration with existing semantic web infrastructure.

Critical gaps in your current inventory include explicit representation of dimensionality, cyclic versus acyclic structure encoding, composition semantics, and systematic formalization of error and anomaly types as violations of topological invariants. Integration with adjacent theoretical frameworks—particularly qualitative temporal reasoning (Allen's algebra), graph transformation systems, and foundational ontologies (BFO, DOLCE)—would further enrich the framework's expressivity and alignment with established knowledge representation standards.

The path forward involves iterative refinement: begin with the OWL 2 core implementing the six primitives, progressively add SPARQL-based derived relations with explicit composition tables, then incrementally enhance SHACL validation rules as domain-specific patterns emerge from application to real software systems. This incremental approach maintains decidability and tractability while building toward comprehensive formal specification, following best practices in ontology engineering and the SEMIC recommendation for lightweight, extensible semantic artifacts.

---

## Citations

1. https://portal.ogc.org/files/?artifact_id=13227
2. https://www.emse.fr/~zimmermann/Teaching/KRR/rcc.html
3. https://franz.com/agraph/support/documentation/geosparql-doc.html
4. https://en.wikipedia.org/wiki/DE-9IM
5. https://en.wikipedia.org/wiki/Region_connection_calculus
6. https://www.ssec.wisc.edu/meetings/geosp_sem/presentations/GeoSPARQL_Getting_Started%20-%20KolasWorkshop%20Version.pdf
7. https://www.iso.org/standard/66175.html
8. https://www.ics.uci.edu/~alspaugh/cls/shr/allen.html
9. https://math.uchicago.edu/~may/REU2017/REUPapers/Rachavelpula.pdf
10. https://cdn.standards.iteh.ai/samples/66175/92416c4eb8954655905aa1d18f244afc/ISO-19107-2019.pdf
11. https://en.wikipedia.org/wiki/Allen's_interval_algebra
12. http://ontology.buffalo.edu/smith/articles/Mereotopology1.pdf
13. https://www.emergentmind.com/topics/control-data-flow-graph-cdfg
14. https://www.dagstuhl.de/15122
15. https://eecs.ceas.uc.edu/~wilseypa/research/tda/
16. https://www.ccs.neu.edu/home/shivers/cs6983/papers/hecht-flow-analysis.pdf
17. https://en.wikipedia.org/wiki/Graph_rewriting
18. https://www.broadinstitute.org/talks/topological-data-analysis-what-persistent-homology
19. https://en.wikipedia.org/wiki/DE-9IM
20. https://orbi.uliege.be/bitstream/2268/24967/1/Ms69_author_preprint.pdf
21. https://pmc.ncbi.nlm.nih.gov/articles/PMC6459481/
22. https://cartogis.org/docs/proceedings/archive/auto-carto-11/pdf/a-critical-comparison-of-the-4-intersection-and%209-intersection-models.pdf
23. https://www.qrg.northwestern.edu/Resources/MONET_Summer_School_2000/TC-B7.pdf
24. https://data4sci.substack.com/p/network-motifs
25. https://www.geeksforgeeks.org/maths/real-life-applications-of-algebraic-topology/
26. https://www.w3.org/TR/skos-reference/
27. https://www.emergentmind.com/topics/region-connection-calculus-rcc-8
28. https://news.ycombinator.com/item?id=37257027
29. https://semiceu.github.io/style-guide/1.0.0/gc-semantic-conventions.html
30. https://en.wikipedia.org/wiki/Region_connection_calculus
31. https://help.supermap.com/iDesktopX/en/Tools/Topology/Topologyvalidator/Validate.html
32. https://thevaluable.dev/complexity-metrics-software/
33. https://philsci-archive.pitt.edu/27732/2/PO-Laws-ProjectNomos-2025.pdf
34. https://desktop.arcgis.com/en/arcmap/latest/manage-data/editing-topology/geodatabase-topology-rules-and-topology-error-fixes.htm
35. https://vfunction.com/blog/software-complexity/
36. http://ontology.buffalo.edu/smith/articles/fois(csv).pdf
37. https://www.vulncheck.com/blog/understanding-software-dependency-graphs
38. http://www.dpi.inpe.br/gilberto/references/max_comparison_4_9_intersection.pdf
39. https://www.khoury.northeastern.edu/home/kathleen/classes/cs3200/4-RAAndRC.pdf
40. https://www.ndepend.com/docs/dependency-structure-matrix-dsm
41. https://cartogis.org/docs/proceedings/archive/auto-carto-11/pdf/a-critical-comparison-of-the-4-intersection-and%209-intersection-models.pdf
42. https://www.geeksforgeeks.org/dbms/introduction-of-relational-algebra-in-dbms/
43. https://philarchive.org/archive/DANFAM-3
44. https://www.cs.miami.edu/~visser/csc751-files/xml_rdf_rdfs_owl.pdf
45. https://github.com/erikbrinkman/d3-dag
46. https://en.wikipedia.org/wiki/Upper_ontology
47. https://www.w3.org/TR/owl-ref/
48. https://arxiv.org/pdf/2509.16198.pdf
49. http://www.loa.istc.cnr.it/wp-content/uploads/2020/02/FoundationalChoicesBorgoMasoloPUB.pdf
50. https://en.wikipedia.org/wiki/Abstract_syntax_tree
51. https://www.bluemarblegeo.com/knowledgebase/global-mapper/Predicates.htm
52. https://www.semantic-web-journal.net/system/files/swj2650.pdf
53. https://dev.to/balapriya/abstract-syntax-tree-ast-explained-in-plain-english-1h38
54. https://en.wikipedia.org/wiki/DE-9IM
55. https://patents.google.com/patent/US8347272B2/en
56. https://www.emergentmind.com/topics/region-connection-calculus-rcc-8
57. https://en.wikipedia.org/wiki/Interior_(topology)
58. https://www.puppygraph.com/blog/software-dependency-graph
59. https://en.wikipedia.org/wiki/Region_connection_calculus
60. https://www.convexoptimization.com/TOOLS/Fenchel1951.pdf

---

## Usage Stats

- Prompt tokens: 789
- Completion tokens: 9501
- Total tokens: 10290
