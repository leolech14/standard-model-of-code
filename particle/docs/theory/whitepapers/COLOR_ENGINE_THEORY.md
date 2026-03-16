**THE COLOR ENGINE**

*A Visual Query Engine for Deterministic Code Comprehension*

Theory, Combinatorial Analysis, and Semantic Architecture

────────────────────────────────────────

Collider Project --- Particle Visualization System

LBL Integracao e Sistemas

March 2026

**TECHNICAL SPECIFICATION --- DRAFT v0.1**

**Table of Contents**

**1. Abstract**

This document presents the theoretical foundations, combinatorial analysis, and architectural design of the Color Engine: a deterministic visual query system that transforms multi-dimensional code analysis data into perceptually meaningful color encodings using the OKLCH color space.

The Collider static analysis pipeline produces 72+ data fields per code node, spanning categorical classifications (architectural tier, topology role, semantic function) and continuous metrics (complexity, coherence, purity, graph centrality). The Color Engine addresses a fundamental question: of the 24,336 possible ways to map three data fields to three color channels (Hue, Lightness, Chroma), how many produce visually distinct, analytically coherent, information-carrying encodings?

Through a five-stage filtering pipeline combining structural validity checks, information-theoretic analysis (joint entropy), perceptual capacity constraints (Bertin 1967, Munzner 2014), and domain coherence rules, we demonstrate that approximately 33 node-level presets across 8 analytical domains survive as meaningful visual queries. Combined with 6-8 edge presets, the system yields roughly 40 scientifically grounded color encodings from the raw combinatorial space.

When composed with the four orthogonal visualization axes (2 layouts, 5 themes, 2 appearance modes, 60 color sources), the full system produces 1,200 distinct diagram-systems, each functioning as a unique analytical instrument for code comprehension.

Critically, every encoding carries a deterministic Semantic Signature: a machine-generated, natural-language interpretation that requires no LLM inference. The signature comprises a frozen question, a reading grammar, a 2x2 pattern-meaning matrix, and statistically-derived findings, enabling the visualization to narrate its own analytical story.

**2. Introduction: The Visual Query Paradigm**

Traditional code visualization systems treat color as decoration: fixed palettes assigned to categories (blue for classes, green for functions, red for errors). The Color Engine inverts this relationship. Color is not a visual property of nodes; color is a query language. Each color configuration is a question posed to the codebase, and the resulting visual pattern is the answer.

**2.1 The Problem Statement**

Modern static analysis tools produce rich, multi-dimensional data about codebases. The Collider pipeline, for example, annotates every code symbol with over 72 fields: architectural classification, graph topology metrics, complexity measures, purity scores, lifecycle assessments, and convergence signals. The challenge is not data scarcity but data overwhelm. No human can simultaneously reason about 72 dimensions.

Color provides a solution through parallel visual processing. The human visual system can process color pre-attentively: differences in hue, brightness, and saturation are perceived instantaneously, without conscious effort. By mapping data fields to color channels, we transform abstract metrics into spatial patterns that exploit the brain\'s most powerful pattern-recognition system.

**2.2 The OKLCH Advantage**

The Color Engine uses OKLCH (Oklab Lightness, Chroma, Hue) rather than HSL, HSV, or RGB. OKLCH is perceptually uniform: equal numerical distances produce equal perceived differences. This is critical for data encoding because it means that a 0.1 increase in the Lightness channel always looks like the same amount of brightening, regardless of the hue. In HSL, the same numerical change produces wildly different perceived effects at different hues (yellow appears much lighter than blue at the same L value).

The three OKLCH channels map naturally to three independent data dimensions: Hue encodes categorical identity (what group does this node belong to?), Lightness encodes a continuous metric (how much of quality A?), and Chroma encodes a second continuous metric (how much of quality B?). This decomposition is the foundation of the entire system.

![fig2_oklch_encoding.png](media/7d60927f15a377f904a521f1dfd60dd0bc61c582.png "fig2_oklch_encoding.png"){width="6.041666666666667in" height="2.1354166666666665in"}

*Figure 2: The three OKLCH channels and their semantic roles in the encoding model.*

**3. The Data Ontology: Field Inventory**

The first requirement for a Color Engine is a complete inventory of available data fields, classified by their type (categorical vs. continuous) and their semantic domain. This inventory defines the raw input space for the combinatorial analysis.

**3.1 Categorical Fields (Hue Sources)**

Categorical fields have discrete, named values. They are the natural candidates for the Hue channel, which encodes identity: what kind of thing is this node? The Collider pipeline produces 16 categorical fields, grouped into five semantic clusters.

  -------- ---------------------- ------------ --------------------------------------------------------
  **\#**   **Field**              **Values**   **Semantic Domain**

  1        atom (tier prefix)     4            CORE / ARCH / EXT / EXT.DISCOVERED

  2        atom_family            5            LOG / DAT / ORG / EXE / EXT

  3        ring                   8            Clean Architecture layers

  4        topology_role          5            hub / authority / bridge / leaf / isolate

  5        file (golden-angle)    N            Per-file identity via golden-angle hue distribution

  6        level                  16           Holarchy scale L0--L15

  7        kind                   \~12         function / class / method / module / interface / \...

  8        role_cat               \~6          Orchestration / Storage / Ingress / Utility / \...

  9        D2_LAYER               \~6          Architectural layer dimension

  10       D4_BOUNDARY            2            Internal / External

  11       D5_STATE               2            Stateful / Stateless

  12       convergence_severity   3            moderate / high / critical

  13       codome_source          6            test_entry / entry_point / framework_managed / \...

  14       semantic_role          \~8          orchestrator / transformer / validator / \...

  15       level_zone             \~4          SEMANTIC / STRUCTURAL / \...

  16       edge_type (dominant)   6            calls / imports / contains / uses / inherits / default
  -------- ---------------------- ------------ --------------------------------------------------------

*Table 1: The 16 categorical fields available as Hue sources.*

**3.2 Continuous Fields (Lightness and Chroma Sources)**

Continuous fields have numeric values along a range. They are the natural candidates for the Lightness and Chroma channels, which encode quantitative information: how much of a particular quality does this node have? The pipeline produces 19 continuous metrics.

  -------- ------------------------ ----------- ---------------------------------------------
  **\#**   **Field**                **Range**   **What It Measures**

  1        coherence_score          0--1        Semantic cohesion of the code unit

  2        D6_pure_score            0--1        Functional purity (absence of side effects)

  3        cyclomatic_complexity    1--200+     Control flow complexity (branches, loops)

  4        pagerank                 0--1        Graph importance (recursive authority)

  5        betweenness_centrality   0--1        Bridge importance (shortest-path frequency)

  6        in_degree                0--N        Incoming connections (dependents)

  7        out_degree               0--N        Outgoing connections (dependencies)

  8        loc (lines of code)      1--N        Physical size of the code unit

  9        trust / confidence       0--1        Classification confidence score

  10       rpbl.responsibility      1--9        Single Responsibility adherence

  11       rpbl.purity              1--9        Functional purity score

  12       rpbl.boundary            1--9        Boundary clarity score

  13       rpbl.lifecycle           1--9        Lifecycle management score

  14       convergence_count        0--N        Number of converging analysis signals

  15       depth / call_depth       0--N        Position in the call tree

  16       rank                     0--1        Generic ranking metric

  17       churn                    0--N        Change frequency over time

  18       age                      0--N        Time since creation

  19       fileIdx                  0--N        File position ordinal
  -------- ------------------------ ----------- ---------------------------------------------

*Table 2: The 19 continuous fields available as Lightness/Chroma sources. Each can be used with invert: true/false.*

![fig10_field_taxonomy.png](media/c609cd57298039747a0bbe5278f8667fdafd60aa.png "fig10_field_taxonomy.png"){width="6.041666666666667in" height="3.6458333333333335in"}

*Figure 10: Data Ontology field classification taxonomy showing the grouping structure of all 35 data fields.*

**4. Combinatorial Analysis**

A ViewSpec is a triple (hue_source, lightness_metric, chroma_metric) that defines one complete color encoding. The combinatorial analysis determines how many ViewSpecs are structurally valid, informationally non-redundant, and semantically coherent.

**4.1 The Raw Permutation Space**

The raw count is a straightforward product of the options for each channel:

**H options: 16 categorical fields**

**L options: 19 continuous metrics × 2 (invert flag) + 1 (none) = 39**

**C options: 19 continuous metrics × 2 (invert flag) + 1 (none) = 39**

**Raw permutations: 16 × 39 × 39 = 24,336**

**4.2 The Five-Stage Filtering Pipeline**

Most of the 24,336 raw permutations are noise. The filtering pipeline applies five successive constraints, each eliminating a class of meaningless or redundant encodings.

**Stage 1: Structural Validity**

Eliminate degenerate assignments where L and C encode the exact same field with the same inversion direction. This produces identical information on both channels, wasting one. There are 19 fields times 2 directions = 38 such degenerate pairs, yielding 24,336 minus (16 times 38) = 23,728 structurally valid mappings.

**Stage 2: Information-Theoretic Filtering**

Two fields that are highly correlated in the actual data (e.g., pagerank and in_degree, often with Pearson r \> 0.8) carry redundant information when co-mapped. The mutual information between L and C approaches zero as their correlation approaches 1. For each codebase, we compute the 19-by-19 correlation matrix of continuous fields and eliminate pairs where the absolute correlation exceeds a threshold (typically 0.5). This is the first codebase-dependent filter.

![fig5_correlation_matrix.png](media/2b7847e2c4ccac49b1ebeedd5394807153028b93.png "fig5_correlation_matrix.png"){width="5.0in" height="4.375in"}

*Figure 5: Simulated cross-correlation matrix of the 19 continuous fields. Red zones indicate redundant pairs (\|r\| \> 0.6) that waste a channel when co-mapped. White/blue zones indicate high-information pairs.*

**Stage 3: Joint Entropy Threshold**

For each surviving ViewSpec, compute the joint entropy H(hue_field, L_field, C_field) over the actual node population. This measures how many distinguishable visual states the encoding actually produces. Low joint entropy means most nodes end up looking the same (clustered in color space). The perceptual threshold is derived from human visual channel capacity research.

![fig9_entropy_spectrum.png](media/de41e2955849a1d2438d0a728438f56ec19220ce.png "fig9_entropy_spectrum.png"){width="5.625in" height="2.8125in"}

*Figure 9: Joint entropy spectrum across ViewSpecs sorted by information content. The perceptual threshold separates meaningful encodings (green) from redundant ones (red).*

**Stage 4: Perceptual Capacity Constraint**

Human perception imposes hard limits on the number of distinguishable values per channel. Research by Bertin (1967), Cleveland and McGill (1984), and Munzner (2014) establishes that humans can reliably distinguish approximately 8 to 12 hues simultaneously, 4 to 5 lightness levels within a single hue, and 3 to 4 chroma levels. This gives approximately 200 distinguishable visual states per ViewSpec. Beyond about 40 presets, new presets become perceptually too similar to existing ones to justify inclusion.

![fig11_perceptual_capacity.png](media/921dc9db3abdd466abb0487ac3b539872f49c1b3.png "fig11_perceptual_capacity.png"){width="5.0in" height="2.8125in"}

*Figure 11: Human perceptual channel capacity and the resulting information-carrying capacity of the encoding system.*

**Stage 5: Domain Coherence**

The final filter is semantic: the three channels must answer a coherent analytical question together. Hue says \'what group,\' Lightness says \'how much of quality A,\' Chroma says \'how much of quality B.\' When A and B are from the same analytical domain and relate to each other (complexity and coherence both measure code health), the view becomes an instrument. When they are from unrelated domains, it is noise. The Relationship Matrix (Section 5) formalizes this constraint.

![fig1_combinatorial_funnel.png](media/1931739ba522de965ab02c4929ce60fe0a95c85a.png "fig1_combinatorial_funnel.png"){width="5.625in" height="3.5416666666666665in"}

*Figure 1: The combinatorial funnel showing the five-stage reduction from 24,336 raw permutations to approximately 33 meaningful presets.*

**5. The Relationship Matrix**

The Relationship Matrix is the core intelligence of the Color Engine. It encodes which field combinations form coherent analytical questions, organized by domain. Each domain groups ViewSpecs that answer the same category of question about the codebase.

**5.1 Domain Structure**

The 33 meaningful presets distribute across 8 analytical domains. Each domain has a characteristic question it answers and a set of field combinations that address that question from different angles.

![fig4_domain_distribution.png](media/b680f0b2488ed82e6edf336f1969f2596affe53b.png "fig4_domain_distribution.png"){width="5.833333333333333in" height="2.7604166666666665in"}

*Figure 4: Distribution of the 33 meaningful presets across 8 analytical domains.*

**5.2 Domain 1: Architecture Quality (6 presets)**

*Question: How well-structured is this code?*

  --------------------- ------------- ---------------- -------------- ----------------------------
  **View Name**         **H**         **L**            **C**          **Story**

  Arch-Coherence        tier          coherence        purity         Tier identity + quality

  Arch-Responsibility   tier          responsibility   boundary       Tier + RPBL profile

  Ring-Purity           ring          purity           coherence      Layer + functional purity

  Layer-Lifecycle       D2_LAYER      lifecycle        purity         Layer depth + maturity

  Family-Cohesion       atom_family   coherence        complexity⁻¹   Family + simplicity

  Kind-Size             kind          loc              complexity     Symbol type + size profile
  --------------------- ------------- ---------------- -------------- ----------------------------

*Table 3: Architecture Quality domain --- 6 presets measuring structural design quality.*

**5.3 Domain 2: Code Health (5 presets)**

*Question: Where are the problems?*

  -------------------- --------------- -------------- ------------------ -----------------------------
  **View Name**        **H**           **L**          **C**              **Story**

  Health-Complexity    tier            complexity⁻¹   coherence          Dark = complex + incoherent

  Health-Convergence   conv_severity   conv_count     trust⁻¹            Multi-signal danger zones

  Health-Trust         tier            trust          complexity⁻¹       Low-confidence + complex

  Health-Purity        ring            purity⁻¹       responsibility⁻¹   Impure + irresponsible

  Health-Churn         tier            churn          complexity         Hot + complex = fragile
  -------------------- --------------- -------------- ------------------ -----------------------------

*Table 4: Code Health domain --- 5 presets revealing problem areas.*

**5.4 Domain 3: Topology and Flow (5 presets)**

*Question: How does information flow through this system?*

  --------------- --------------- ------------- ------------- ---------------------------
  **View Name**   **H**           **L**         **C**         **Story**

  Topo-Rank       topology_role   pagerank      betweenness   Role + importance

  Topo-Fanout     topology_role   out_degree    in_degree     Role + coupling direction

  Topo-Depth      ring            depth         out_degree    Layer + call depth

  Flow-Bridge     topology_role   betweenness   trust         Bridges + confidence

  Flow-Hub        tier            in_degree     out_degree    Tier + coupling profile
  --------------- --------------- ------------- ------------- ---------------------------

*Table 5: Topology & Flow domain --- 5 presets mapping information flow and graph structure.*

**5.5 Domains 4--8: Remaining Domains**

The remaining five domains follow the same pattern: Organization & Files (4 presets), RPBL DNA Profile (4 presets), Scale & Holarchy (3 presets), Semantic Purpose (3 presets), and Evolution & Risk (3 presets). Each domain targets a specific analytical concern with field combinations drawn from the same semantic cluster.

The complete domain summary table:

  ----------------------- ------------- -----------------------------------------------
  **Domain**              **Presets**   **Core Question**

  Architecture Quality    6             How well-structured is this code?

  Code Health             5             Where are the problems?

  Topology & Flow         5             How does information flow?

  Organization & Files    4             How is the code organized?

  RPBL DNA Profile        4             What is the behavioral DNA of each component?

  Scale & Holarchy        3             At what scale does this component operate?

  Semantic Purpose        3             What does this component DO?

  Evolution & Risk        3             What is changing and what is at risk?

  **TOTAL**               **33**        **8 distinct analytical lenses**
  ----------------------- ------------- -----------------------------------------------

*Table 6: Complete domain summary --- 33 meaningful presets across 8 analytical domains.*

**6. The Semantic Signature**

Every ViewSpec has an inherent, deterministic meaning expressible in natural language. The Semantic Signature is a data structure that captures this meaning at three layers, each computed without LLM inference.

**6.1 The Three Layers of Deterministic Meaning**

Layer 1 (The Question) is static, derived from the domain tag alone. Layer 2 (The Reading Grammar) is static, derived from field metadata and inversion flags. Layer 3 (The Findings) is dynamic, derived from actual data distributions combined with natural-language templates. Together, they enable the visualization to narrate its own analytical story.

![fig7_semantic_signature.png](media/48a43734d464d98c92d232f1255f5fd87de20212.png "fig7_semantic_signature.png"){width="5.625in" height="4.375in"}

*Figure 7: The three layers of deterministic meaning, each requiring no LLM inference.*

**6.2 The 2×2 Pattern-Meaning Matrix**

Every ViewSpec with both L and C channels mapped generates a 2×2 matrix from the poles of the two continuous axes. This matrix is the reading key: it tells the human what each visual quadrant means before they even look at the graph.

For the Health-Complexity ViewSpec (L = complexity inverted, C = coherence), the four quadrants are: bright+vivid = simple and coherent (healthy), bright+gray = simple but scattered (needs refactoring), dim+vivid = complex but coherent (intentional complexity), dim+gray = complex and scattered (danger zone).

![fig3_pattern_matrix.png](media/08841f1c54b9a44a530099f6fb4d6b9d9a7c6162.png "fig3_pattern_matrix.png"){width="4.479166666666667in" height="3.1770833333333335in"}

*Figure 3: The 2×2 Visual Pattern Meaning Matrix for a Health-Complexity ViewSpec. Each quadrant maps deterministically to an analytical interpretation.*

**6.3 Deterministic Finding Generation**

Layer 3 operates by applying statistical pattern detectors to the actual node data under a given ViewSpec, then filling natural-language templates with the results. Examples of pattern detectors include: cluster detection (a group of dim+gray nodes in one hue category indicates systematic debt), outlier detection (a node significantly dimmer than its group mean indicates a localized problem), and distribution analysis (a bimodal distribution in the L channel indicates two distinct populations within a single category).

The template system requires no machine learning. It is analogous to a clinical decision support system: predefined rules map data patterns to interpretive statements.

**7. The Diagram-System Product Space**

The Color Engine produces ViewSpecs, but a ViewSpec is only one of four independent axes that define a complete visualization. The full diagram-system is the Cartesian product of four orthogonal perceptual knobs, each controlling a different dimension of the visual experience.

**7.1 The Four Orthogonal Axes**

Layout controls where nodes sit in space (force-directed graph vs. holarchy 3D layering). Theme controls the visual environment (dark, light, aquarela, high-contrast, scientific-paper). Appearance Mode controls how nodes render (filled solid vs. wireframe outline). Color Source controls what data the colors encode (28 single-dimension color modes plus 32 three-channel encoding views).

These axes are truly independent because each controls a different perceptual layer. Layout encodes spatial proximity (what is near what?). Theme encodes reading context (exploration vs. publication). Appearance encodes rendering style (painting vs. blueprint). Color encodes data semantics (what does this color mean?). Changing any one axis produces a genuinely different analytical instrument.

![fig6_diagram_systems.png](media/7f384b21d20abe31e201f0e5f7fc46cc673485f1.png "fig6_diagram_systems.png"){width="5.729166666666667in" height="3.5416666666666665in"}

*Figure 6: The Diagram-System Product Space --- four orthogonal axes producing 1,200 distinct analytical instruments.*

**7.2 Why the Color Source Axis is a Sum, Not a Product**

The 28 color modes and the 32 encoding views are mutually exclusive: selecting an encoding view overrides the color mode selector entirely. The encoding view takes over all three color channels. It would be semantically contradictory to simultaneously assign hue by tier (color mode) and hue by topology_role (encoding view). Therefore, the Color Source axis has 28 + 32 = 60 options, not 28 times 32 = 896.

**7.3 Concrete Example Configurations**

To illustrate the diversity: a force-graph with dark theme, filled appearance, and tier color mode produces a glowing starfield of colored particles. The same graph with scientific-paper theme and wireframe appearance produces a publication-ready technical diagram with colored outlines on white. Switching to holarchy layout places nodes on architectural planes. Switching to Health encoding changes every color meaning from identity to quality. Each combination answers a fundamentally different question.

**8. Proposed Architecture**

The Color Engine is composed of four major components. The DataOntology stores the complete field inventory with metadata (type, range, semantic domain, human-readable descriptions for template generation). The RelationshipMatrix encodes valid field combinations, redundancy rules, and inversion semantics. The ViewSpecGenerator produces valid ViewSpecs from the matrix, ranks them by information content, and validates user-defined custom combinations. The SemanticSignature module computes the three-layer interpretation for each ViewSpec.

![fig8_architecture.png](media/ad6f8b8c0c1a9f55663a83a8bc8a935ed399068b.png "fig8_architecture.png"){width="5.9375in" height="4.166666666666667in"}

*Figure 8: Color Engine architecture showing the four major components and their data flow.*

**8.1 Integration with Existing Code**

The current codebase has the bottom layer (ViewSpec dataclass and ChannelMapping in color_encoding.py) and the color science functions (gamut mapping, OKLCH-to-sRGB conversion in color_science.py). The Color Engine adds the top two layers: the ontology and the relationship matrix. This is an additive change: existing code remains untouched.

**8.2 Data Chemistry Layer Dependency**

The Color Engine depends on the Data Chemistry Layer for its field inventory. The ontology must be derived from whatever the actual enrichment pipeline produces, not from assumptions about field availability. The current analysis in this document is based on the Claude Code session inventory of 72+ fields and requires validation against the actual data_chemistry module exports.

*Note: At time of writing, the exact interface of the data chemistry layer has not been verified against the current codebase. The field inventory in Tables 1 and 2 should be treated as provisional until cross-referenced with the actual pipeline output schema.*

**9. Information-Theoretic Foundations**

**9.1 Joint Entropy as Quality Metric**

The quality of a ViewSpec is measured by the joint entropy H(H_field, L_field, C_field) over the node population. Joint entropy quantifies how many distinguishable visual states the encoding actually produces for a given codebase. The formula is: H(X, Y, Z) = negative sum over all (x, y, z) of P(x, y, z) times log2 of P(x, y, z).

High joint entropy means the three channels partition the node space into many distinct groups, each visually distinguishable. Low joint entropy means most nodes cluster into a few visual states, and the encoding fails to reveal structure.

**9.2 Codebase Dependence**

A critical insight is that the number of meaningful presets is not fixed. It is a function of the codebase. In a codebase with many independent metrics (low cross-correlation), more ViewSpecs carry sufficient entropy. In a small codebase where metrics are tightly correlated, fewer ViewSpecs are informative.

This means the Color Engine should compute the meaningful set dynamically for each analyzed codebase, rather than relying on a fixed preset list. The 33-preset estimate is a typical value for medium-to-large codebases with diverse architectural patterns.

**9.3 The Signal-to-Noise Ratio**

Approximately 33 meaningful presets from 24,336 raw permutations yields a signal-to-noise ratio of 0.14 percent. This extreme selectivity is the core value proposition of the Relationship Matrix: it eliminates combinations where the channels do not tell a coherent story. Mapping file to hue while also mapping fileIdx to lightness is redundant (same axis twice). Mapping convergence_severity to hue while using pagerank for lightness mixes unrelated domains and answers no coherent question.

**10. Theoretical References**

The Color Engine draws on established research in visual encoding theory and information visualization:

Bertin, J. (1967). Semiology of Graphics. University of Wisconsin Press. The foundational taxonomy of visual variables (position, size, shape, value, color, orientation, texture) and their suitability for encoding data types.

Cleveland, W. S. and McGill, R. (1984). Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods. Journal of the American Statistical Association, 79(387), 531-554. Empirical ranking of visual encoding effectiveness.

Munzner, T. (2014). Visualization Analysis and Design. CRC Press. Modern synthesis of the effectiveness of visual encoding channels, including quantitative estimates of distinguishable levels per channel.

Oklab color space: Ottosson, B. (2020). A perceptual color space for image processing. The OKLCH color model used by the Color Engine for perceptually uniform encoding.

Shannon, C. E. (1948). A Mathematical Theory of Communication. Bell System Technical Journal, 27(3), 379-423. The entropy metric used for ViewSpec quality assessment.

**Appendix A: Glossary**

  ---------------------- -----------------------------------------------------------------------------------------------------------------
  **Term**               **Definition**

  ViewSpec               A frozen triple (hue_source, L_metric, C_metric) defining one complete 3-channel color encoding.

  Semantic Signature     The deterministic, machine-generated natural-language interpretation of a ViewSpec.

  Diagram-System         The full Cartesian product of Layout, Theme, Appearance, and Color Source.

  Relationship Matrix    The lookup structure encoding which field combinations form coherent analytical questions.

  DataOntology           The complete inventory of available fields with type, range, and domain metadata.

  Joint Entropy          H(H,L,C): the information content of a ViewSpec applied to a specific codebase.

  Perceptual Threshold   The minimum joint entropy for a ViewSpec to produce humanly distinguishable visual patterns.

  Channel Mapping        The function that converts a field value to an OKLCH channel value (with normalization and optional inversion).

  2×2 Pattern Key        The four-quadrant interpretation grid derived from the poles of the L and C axes.

  Color Mode             A single-dimension color assignment (one field to hue) used in the default encoding view.

  Encoding View          A three-channel OKLCH encoding using a full ViewSpec from the Relationship Matrix.

  RPBL                   Responsibility, Purity, Boundary, Lifecycle --- the four behavioral DNA dimensions.
  ---------------------- -----------------------------------------------------------------------------------------------------------------

*Table A1: Glossary of key terms used throughout this document.*
