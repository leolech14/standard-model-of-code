# Research: Research academic and industry prior art for these software architecture concepts:

1. CARDINALITY U...

> **Date:** 2026-02-01 02:19:32
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:3926e2f20294e27e059569a8556ba3ea83df9192fc3d62fa7ca4bcc19280dd7a`
> **Raw JSON:** `raw/20260201_021932_research_academic_and_industry_prior_art_for_these.json`

---

## Query

Research academic and industry prior art for these software architecture concepts:

1. CARDINALITY UNCERTAINTY in file systems - literature on 'cost to know' what's inside a container, epistemic vs ontological uncertainty in data structures

2. MILLER'S LAW (7±2) applied to software architecture - directory structure, module organization, package design, API surface limits

3. ONTOLOGICAL HIDING vs Information Hiding (Parnas 1972) - is there a 'stronger' form of hiding? Object-Oriented Ontology (Harman) applied to software?

4. RECURSIVE HOLARCHY in software - Arthur Koestler's holons (1967) applied to code organization, PROSA architecture, holonic systems

5. BOUNDARY THEOREM - 'a module acquires meaning only when integrated into its parent system' - Mereology (part-whole theory), Teleological emergence, contextual meaning

Provide: Author names, paper/book titles, years, key concepts. We need proper citations.

---

## Response

### 1. CARDINALITY UNCERTAINTY in file systems - literature on 'cost to know' what's inside a container, epistemic vs ontological uncertainty in data structures

No direct prior art was found on **cardinality uncertainty** specifically in file systems or the 'cost to know' metric for container contents. Related concepts appear in systems engineering and uncertainty modeling, distinguishing **epistemic uncertainty** (lack of knowledge about model parameters, reducible via observation) from **ontological uncertainty** (complete ignorance of system aspects, unknown-unknowns).[1] These are applied to system models, e.g., perception chains in safety analysis, but not file systems or data structures.[1][3] Aleatory uncertainty (irreducible randomness) is also differentiated.[1][3]

### 2. MILLER'S LAW (7±2) applied to software architecture - directory structure, module organization, package design, API surface limits

No academic or industry prior art directly applies **Miller's Law** (cognitive limit of 7±2 items in working memory, from George A. Miller's 1956 paper "The Magical Number Seven, Plus or Minus Two") to software architecture elements like directories, modules, packages, or APIs. Search results lack references to this intersection; general software organization principles (e.g., information hiding) exist separately but unlinked.

### 3. ONTOLOGICAL HIDING vs Information Hiding (Parnas 1972) - is there a 'stronger' form of hiding? Object-Oriented Ontology (Harman) applied to software?

**Information Hiding** originates in David Parnas's 1972 paper "On the Criteria to Be Used in Decomposing Systems into Modules," emphasizing hiding design decisions to reduce complexity. No direct literature contrasts it with **ontological hiding** or posits a 'stronger' form. **Ontological uncertainty** (model incompleteness) is discussed in system models but not as a hiding mechanism.[1] Graham Harman's **Object-Oriented Ontology** (e.g., 2002 book *Tool-Being*) applies to philosophy, withdrawing objects from relations; no applications to software found.[5] Ontologies in systems engineering represent knowledge but do not address hiding.[2][4]

### 4. RECURSIVE HOLARCHY in software - Arthur Koestler's holons (1967) applied to code organization, PROSA architecture, holonic systems

**Arthur Koestler's holons** (from 1967 book *The Ghost in the Machine*) describe hierarchical systems where parts are wholes (holarchy), but no direct applications to software code organization in results. **PROSA architecture** (not mentioned) refers to holonic manufacturing systems (e.g., Van Brussel et al., 1998 "Reference Architecture for Holonic Manufacturing Systems"), involving recursive agents, but absent here. Holonic systems appear indirectly in ontology extensions for uncertainty, without recursion focus.[3]

### 5. BOUNDARY THEOREM - 'a module acquires meaning only when integrated into its parent system' - Mereology (part-whole theory), Teleological emergence, contextual meaning

No **Boundary Theorem** or exact match found; concept echoes mereology (part-whole relations, e.g., in ontology engineering).[2][4] Contextual module meaning aligns with systems engineering ontologies, where entities gain semantics via integration (e.g., TIDO ontology extends PROV for threat intelligence, emphasizing relationships).[3] Ontologies formalize part-whole via classes/slots for knowledge representation.[2][4] Teleological emergence unaddressed.

---

## Citations

1. https://arxiv.org/pdf/2303.04042
2. https://research.fit.edu/media/site-specific/researchfitedu/systems-realization-lab/documents/Ontology-based-Uncertainty-Management-Approach-in-Designing-of-Robust-Decision-Workflows.pdf
3. https://ceur-ws.org/Vol-4083/paper57.pdf
4. https://web.mst.edu/lib-circ/files/Special%20Collections/INCOSE2010/An%20introduction%20to%20knowledge%20representation%20and%20ontology%20development%20for%20systems%20engineers.pdf
5. https://plato.stanford.edu/archives/sum2019/entries/information/

---

## Usage Stats

- Prompt tokens: 220
- Completion tokens: 756
- Total tokens: 976
