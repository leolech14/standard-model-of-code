# Research Directions: Standard Model of Code as Systems of Systems

> **Created:** 2026-01-21
> **Purpose:** Capture theoretical foundations and research directions for extending the Standard Model of Code
> **Status:** Living document - questions, not declarations

---

## 1. Core Theoretical Alignments Discovered

### 1.1 Normalized Systems Theory
**Key Finding:** Direct theoretical predecessor for software evolvability.

> "The theory of Normalized Systems addresses the problem of developing information systems that can evolve over time, by guaranteeing that each new feature can be implemented with a limited number of changes that does not depend on the actual size of the system."

**Relevance to SMC:**
- Addresses Lehman's Law (evolvability decreases over time)
- Provides architectural patterns for maintainable change
- Five distinct elements for application logic

**Source:** [Normalized Systems Theory - ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S2590118425000322)

---

### 1.2 Category Theory for Software Architecture
**Key Finding:** Formal mathematical framework for component composition.

> "Categories that are considered primarily have formal models of programs as objects and formal descriptions of various activities of their integration as morphisms. Assembling systems is described by colimits of configurations."

**Relevance to SMC:**
- Morphisms = our edges (transformations between components)
- Colimits = system composition from parts
- Functors = mappings between different views of same system

**Open Questions:**
- Can we formalize `topology_role` as a functor?
- Are interface surfaces natural transformations?
- What are the limits/colimits in dependency graphs?

**Source:** [Category-Theoretic Approach to Software Systems Design](https://www.researchgate.net/publication/286295228_Category-Theoretic_Approach_to_Software_Systems_Design)

---

### 1.3 Network Centrality in Microservices
**Key Finding:** Centrality metrics correlate with architectural quality.

> "Central services tend to have low ratios of private-to-public and protected-to-public methods... centrality metrics can provide new insights into MSA quality and facilitate the detection of architectural anti-patterns."

**Network Science Metrics We're Missing:**

| Metric | Definition | SMC Application |
|--------|------------|-----------------|
| **Betweenness Centrality** | Nodes on shortest paths between others | Bridge detection, criticality |
| **Closeness Centrality** | Average distance to all other nodes | Communication efficiency |
| **Eigenvector Centrality** | Connected to important nodes | Influence propagation |
| **PageRank** | Recursive importance | Code significance ranking |
| **Clustering Coefficient** | Local interconnectedness | Module cohesion |

**Open Questions:**
- Does high betweenness predict change fragility?
- Can we detect anti-patterns (nano/mega/hub services) from centrality?
- How does centrality evolve over time (temporal network analysis)?

**Sources:**
- [Network Centrality as a New Perspective on Microservice Architecture (arXiv 2501.13520)](https://arxiv.org/abs/2501.13520)
- [Neo4j Betweenness Centrality](https://neo4j.com/docs/graph-data-science/current/algorithms/betweenness-centrality/)

---

### 1.4 Biological Evolvability (Wagner, Kirschner, Gerhart)
**Key Finding:** Robustness and evolvability are NOT opposites - they enable each other through modularity.

> "Modularity—defined as the clustering of epistatic interactions—is an important form of robustness because it limits the number of system components that are affected by a given perturbation."

**Kirschner & Gerhart's Evolvability Enablers:**
1. Versatile elements (reusable components)
2. Weak linkage (loose coupling)
3. Compartmentation (bulkheads)
4. Redundancy (fault tolerance)
5. Exploratory behavior (adaptive discovery)

**Wagner's Key Insight:**
> "The more robust a system is, the more mutations in it are neutral... Wagner argued that such neutral change – and thus robustness – can be a key to future evolutionary innovation."

**Translation to Code:**

| Biology | Code Equivalent | SMC Concept |
|---------|-----------------|-------------|
| Neutral mutation | Refactoring without behavior change | Safe evolution zone |
| Epistatic interaction | Dependency coupling | Edge weight |
| Phenotype | Observable behavior | API contract |
| Genotype | Source code | Implementation |
| Neutral network | Equivalent implementations | Substitutability |

**Open Questions:**
- Can we measure "neutral network size" for code components?
- Is there a "fitness landscape" for software architectures?
- How do we quantify weak linkage vs tight coupling?

**Sources:**
- [Wagner - Robustness and Evolvability in Living Systems (Princeton, 2005)](https://www.researchgate.net/publication/237132986_Robustness_and_Evolvability_in_Living_Systems)
- [Kirschner & Gerhart - Evolvability (PNAS, 1998)](https://pubmed.ncbi.nlm.nih.gov/9671692/)
- [Protein Structural Modularity and Robustness](https://academic.oup.com/gbe/article/doi/10.1093/gbe/evr046/583684)

---

### 1.5 Software Architecture Evolvability Analysis (AREA)
**Key Finding:** Evolvability can be systematically assessed.

> "Software evolvability is a multifaceted quality attribute that describes a software system's ability to easily accommodate future changes... The software architecture evolvability analysis process (AREA) provides quality attribute subcharacteristics values and identifies weak parts of the system architecture."

**AREA Process Goals:**
1. Quality attribute subcharacteristics values
2. Identification of weak architectural parts
3. Evolvability scoring

**Open Questions:**
- Can we automate AREA using our graph analysis?
- What are the subcharacteristics of evolvability?
- How do we identify "weak parts" from topology?

**Source:** [Software Architecture Evolution Through Evolvability Analysis](https://www.sciencedirect.com/science/article/abs/pii/S016412121200163X)

---

## 2. Systems of Systems Complexity Framework

From SEBoK (Systems Engineering Body of Knowledge):

> "In a changing context, with an evolving system, where elements are densely interconnected, problems and opportunities will continually emerge. Moreover, they will emerge in surprising ways, due to phase transitions, cascading failures, fat tailed distributions, and black swan events."

**SoS Characteristics:**
1. Operational independence of elements
2. Managerial independence of elements
3. Evolutionary development
4. Emergent behavior
5. Geographic distribution

**Lehman's Laws of Software Evolution:**
1. Continuing Change
2. Increasing Complexity
3. Self-Regulation
4. Conservation of Organizational Stability
5. Conservation of Familiarity
6. Continuing Growth
7. Declining Quality
8. Feedback System

**Open Questions:**
- Can we detect phase transitions in code evolution?
- What are the "black swan" events in software architecture?
- How do we measure emergent properties vs designed ones?

**Source:** [SEBoK - System of Systems and Complexity](https://sebokwiki.org/wiki/System_of_Systems_and_Complexity)

---

## 3. Mathematical Formalisms to Explore

### 3.1 Sheaf Theory
**Status:** Not yet found in software architecture literature.

**Potential Application:**
- Local-to-global properties (module behavior → system behavior)
- Consistency of interfaces across boundaries
- Information fusion from different views

**Research Direction:** Look for applications in distributed systems, concurrency theory.

---

### 3.2 Topological Data Analysis (TDA)
**Potential Application:**
- Persistent homology of dependency graphs
- Detecting "holes" in architecture (missing connections)
- Shape analysis of code structure over time

**Research Direction:** Apply TDA tools (GUDHI, Ripser) to dependency graphs.

---

### 3.3 Information Geometry
**Potential Application:**
- Measuring "distance" between architectures
- Optimization on manifold of possible designs
- Curvature as measure of architectural stress

---

## 4. Concrete Next Steps

### 4.1 Implement Missing Network Metrics
```python
# Proposed additions to full_analysis.py
node['betweenness_centrality'] = nx.betweenness_centrality(G).get(node_id, 0)
node['closeness_centrality'] = nx.closeness_centrality(G).get(node_id, 0)
node['clustering_coefficient'] = nx.clustering(G.to_undirected()).get(node_id, 0)
node['pagerank'] = nx.pagerank(G).get(node_id, 0)
```

### 4.2 Add Evolvability Score
Based on Wagner/Kirschner/Gerhart, evolvability correlates with:
- Modularity (clustering coefficient)
- Weak linkage (low coupling)
- Redundancy (similar components exist)
- Neutral network size (refactoring freedom)

### 4.3 Detect Architectural Anti-Patterns
Using centrality metrics:
- **Hub Service:** High degree + high betweenness
- **Mega Service:** High PageRank + many methods
- **Nano Service:** Very low degree (isolated)
- **Circular Dependency:** Strongly connected components

### 4.4 Temporal Analysis
Track metrics over git history to detect:
- Centrality drift (becoming more hub-like)
- Evolvability decay (Lehman's Law)
- Phase transitions (architectural shifts)

---

## 5. Key Researchers to Follow

| Researcher | Area | Key Contribution |
|------------|------|------------------|
| **Andreas Wagner** | Biology/Evolvability | Robustness enables evolvability |
| **Marc Kirschner & John Gerhart** | Biology | Facilitated variation theory |
| **Adrian Bejan** | Physics | Constructal Law |
| **Stafford Beer** | Cybernetics | Viable System Model |
| **Hermann Haken** | Physics | Synergetics, slaving principle |
| **Manny Lehman** | Software Engineering | Laws of software evolution |
| **José Fiadeiro** | Software Architecture | Category theory for SE |
| **Neo4j Team** | Graph Analysis | Centrality algorithms |

---

## 6. Open Questions Registry

### Fundamental
- [ ] What is the mathematical object that best represents a software system?
- [ ] Is there a universal "fitness function" for architecture?
- [ ] Can evolvability be predicted from structure alone?

### Practical
- [ ] How do we measure interface quality automatically?
- [ ] What thresholds define "hub" vs "normal" centrality?
- [ ] Can we detect impending architectural decay?

### Theoretical
- [ ] Is there a category of software architectures?
- [ ] What are the morphisms between architectures?
- [ ] Does sheaf cohomology have meaning for code?

---

## 7. References

### Primary Sources
1. Wagner, A. (2005). *Robustness and Evolvability in Living Systems*. Princeton University Press.
2. Kirschner, M., & Gerhart, J. (1998). Evolvability. *PNAS*, 95(15), 8420-8427.
3. Bejan, A. (1997). Constructal-theory network of conducting paths for cooling a heat generating volume. *Int. J. Heat Mass Transfer*, 40, 799-816.
4. Beer, S. (1972). *Brain of the Firm*. Allen Lane.
5. Lehman, M.M. (1980). Programs, Life Cycles, and Laws of Software Evolution. *Proc. IEEE*, 68(9).

### Software Architecture
6. Breivold, H.P., et al. (2012). Software architecture evolution through evolvability analysis. *JSS*, 85(11).
7. Fiadeiro, J. (2007). Category theory for software engineering. *Summer School on Generative and Transformational Techniques*.
8. Network Centrality as a New Perspective on Microservice Architecture. *arXiv:2501.13520* (2025).

### Systems Engineering
9. SEBoK Wiki. System of Systems and Complexity. https://sebokwiki.org/
10. Normalized Systems Theory. https://normalizedsystems.org/
