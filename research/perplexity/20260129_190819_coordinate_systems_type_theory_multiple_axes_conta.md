# Research: coordinate systems type theory multiple axes containment vs abstraction orthogonal dimensions softwa...

> **Date:** 2026-01-29 19:08:19
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:33c95a2be3b6733f1ff2c166d1291e9bdfdb737eda79ebe1003f5599eceafc0f`
> **Raw JSON:** `raw/20260129_190819_coordinate_systems_type_theory_multiple_axes_conta.json`

---

## Query

coordinate systems type theory multiple axes containment vs abstraction orthogonal dimensions software architecture

---

## Response

**Orthogonality in software architecture** refers to designing systems with independent dimensions or axes—such as abstraction levels, aggregation scales, and property types—that can vary without unintended side effects, much like perpendicular coordinates in geometry or type theory where types are disjoint and composable.[1][2][3]

This approach contrasts **containment** (hierarchical nesting, e.g., modules encapsulating subcomponents within fixed boundaries) with **abstraction** (generalizing across levels without embedding details).[1][4] In the **TOPSA framework**, architectures are modeled along **three orthogonal dimensions**:

- **Abstraction level**: From concrete implementation details to high-level conceptual views; raising it does not force changes in other dimensions.[1]
- **Aggregation level**: Scaling from individual elements (e.g., code lines) to system-wide structures; independent of abstraction.[1]
- **Property types**: Qualities like performance or modularity, combinable arbitrarily due to orthogonality.[1]

These dimensions enable precise descriptions, process-independent analysis (forward/reverse engineering), and representation flexibility.[1]

| Concept | Containment (Hierarchical) | Abstraction (Layered/Independent) |
|---------|----------------------------|-----------------------------------|
| **Structure** | Nested scopes (e.g., classes containing subclasses); changes propagate inward.[2] | Independent layers (e.g., data flow from OLTP to OLAP cubes); bridges impedance mismatches.[4] |
| **Change Impact** | Affects enclosed elements; tight coupling risks ripple effects.[2] | Isolated changes; loose coupling preserves orthogonality.[2][3] |
| **Example** | Arrays inside structures in C (non-orthogonal exceptions).[3] | Multiple axes like region/product/period for sales analysis; views remain independent.[4] |

**Benefits in software architecture** include easier debugging (isolate one axis), simpler APIs (few primitives combine orthogonally), and compact designs without side effects—strong cohesion within components and loose coupling between them.[2][3] In data architecture, orthogonal perspectives (e.g., admin/user/requirements views) form multi-dimensional "cubes" for analysis, extensible beyond three axes visually.[4]

Limitations: Pure orthogonality can complicate systems (e.g., CISC vs. successful RISC CPUs), and real-world combinations may correlate despite theoretical independence.[1][3] This draws from type theory's orthogonal types (no overlap, safe composition) applied to architectural axes.[1][3]

---

## Citations

1. https://fileadmin.cs.lth.se/serg/old-serg-dok/docs-serg/194_nosa_99_final_2.pdf
2. https://www.freecodecamp.org/news/orthogonality-in-software-engineering/
3. https://en.wikipedia.org/wiki/Orthogonality_(programming)
4. https://tdan.com/dimensions-of-data-architecture/10849

---

## Usage Stats

- Prompt tokens: 13
- Completion tokens: 515
- Total tokens: 528
