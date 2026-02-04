# Perplexity Research: Validation and falsifiability in software engineering metrics. Popper's falsifiability applied to so...

> **Date:** 2026-02-01 18:43:07
> **Model:** sonar-pro
> **Query Length:** 520 chars

---

## Query

Validation and falsifiability in software engineering metrics. Popper's falsifiability applied to software claims. Objective vs subjective metrics (cyclomatic complexity, coupling, cohesion). Graph-theoretic metrics in code analysis (Betti numbers, centrality). Validating Lehman's Laws, Conway's Law, Brooks's Law empirically. IEEE 1061 metric validation framework. Weyuker's properties for complexity metrics. How to validate entire theoretical frameworks in software engineering. Academic methodology and key studies.

---

## Response

**Falsifiability**, per Karl Popper, requires scientific claims in software engineering to be testable and potentially disprovable by empirical evidence, such as experiments rejecting universal theories via counterexamples.[1][5] This principle critiques unfalsifiable software claims, like those assuming metrics universally predict defects or multi-version programming ensures independence, by demanding rigorous experiments that could refute them.[1][3]

### Popper's Falsifiability Applied to Software Claims
Popper's criterion demands theories be empirically testable: a single counterexample falsifies universal claims, while surviving tests provisionally supports them without proof.[1][5] In software engineering:
- **Multi-version programming theory** (independent versions reduce errors) was falsified by Knight and Leveson's experiment on a launch interceptor: 1,255 coincident failures across versions rejected independence at 99% confidence, using a gold program and 1 million tests.[1]
- **Software metrics predicting defects** (e.g., complexity metrics) failed cross-project validation in Nagappan et al.'s study of five Microsoft projects (>1M LOC): predictors worked within projects via regression and principal component analysis but not across dissimilar ones.[1]
- **UML models reducing defects** showed inconclusive results; surrogate measures like acceptance test runs were unreliable, questioning modeling benefits.[1]
These cases illustrate falsification reorienting research away from debunked ideas.[1][4]

### Objective vs. Subjective Metrics
**Objective metrics** like **cyclomatic complexity** (control flow branches), **coupling** (module interdependencies), and **cohesion** (intra-module relatedness) are graph-derived and quantifiable but often fail Popperian tests for universal defect prediction across projects.[1] Subjective metrics lack such formalization. Search results emphasize their limitations: while intra-project predictors exist, cross-project falsification reveals context-dependence, undermining generality.[1]

### Graph-Theoretic Metrics in Code Analysis
Graph theory underpins code metrics:
- **Cyclomatic complexity**, **coupling**, and **cohesion** model code as graphs (nodes: modules/functions; edges: dependencies/calls).[1]
- Advanced ones include **Betti numbers** (persistent homology for topological code structure) and **centrality** (node influence in dependency graphs), but results lack direct falsification studies here; they extend traditional metrics yet face similar cross-context validation issues.[1]

### Validating Specific Software Laws Empirically
Empirical tests apply falsification:
- **Lehman's Laws** (e.g., software evolves or dies): Limited direct refutations in results, but metric studies indirectly challenge growth predictions via defect non-predictability.[1]
- **Conway's Law** (system structure mirrors organization): Anecdotal support; falsification requires organizational-code mismatch experiments (none cited).[1]
- **Brooks's Law** ("adding manpower late delays"): Untested here, but Popper demands controlled project experiments.[1][3]
Validation uses large datasets, statistical models (e.g., regression), and cross-validation, rejecting claims if predictions fail.[1]

### IEEE 1061 Metric Validation Framework
IEEE 1061 provides a structured process for software quality metrics: define attributes (e.g., predictability, discriminability), correlate with quality factors, and test via experiments. It aligns with falsifiability by requiring empirical refutation thresholds, though not directly cited in results.[1]

### Weyuker's Properties for Complexity Metrics
Weyuker's 9 properties (e.g., non-coarseness, monotonicity, distribution) test if complexity measures behave axiomatically like true complexity. Violations falsify metric suitability; e.g., some fail merging/disjunction properties, questioning objectivity.[1]

### Validating Entire Theoretical Frameworks
Frameworks (e.g., Lehman's, metric suites) are harder due to Duhem-Quine issues (auxiliary assumptions confound tests).[5] Approach:
- Decompose into falsifiable hypotheses (e.g., "Law X holds in context Y").[2][3]
- Use experiments: A/B tests, shadow mode (e.g., Tesla), cross-project data.[1][2]
- Compete models (e.g., ML hypotheses discarded via unseen data).[2]
Academic methodology: Hypothetico-deductive cycles—predict, test adversarially, reject if falsified; prioritize logical consistency first.[1][5] Key studies: Knight-Leveson (multi-version), Nagappan (metrics).[1]

### Key Studies and Academic Methodology
- **Nagappan et al. (2006)**: Cross-project metric failure on Microsoft data.[1]
- **Knight-Leveson**: Single experiment falsifying independence.[1]
- Broader: Popperian testing in ML (DeepMind AlphaFold, Spotify A/B).[2]
Methodology favors quantitative experiments over induction, with humility: tests disconfirm, not confirm.[3][4] Limitations: Results focus on metrics/multi-version; broader laws need more data.[1]

---

## Citations

1. https://ubiquity.acm.org/article.cfm?id=3512338
2. https://crowintelligence.org/2025/02/25/falsifiable-hypotheses-how-poppers-philosophy-transformed-my-data-science-practice/
3. http://blog.ezyang.com/2011/06/philosophy-of-software-engineering/
4. https://russmiles.substack.com/p/software-engineering-is-the-scientific
5. https://en.wikipedia.org/wiki/Falsifiability
6. https://www.theseedsofscience.pub/p/is-a-qualitative-metric-of-falsifiability
7. https://arxiv.org/pdf/1704.08111
8. https://muuktest.com/blog/falsifiability-in-software-testing

---

## Usage Stats

- Input tokens: 101
- Output tokens: 1048
