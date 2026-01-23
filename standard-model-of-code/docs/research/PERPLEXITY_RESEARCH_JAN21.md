# Perplexity Research Compilation - January 21, 2026

> **Tool:** Perplexity Sonar Pro API
> **Purpose:** Ground SMC theory in established research
> **Status:** Initial research pass - findings need validation

---

## 1. Network Centrality & Defect Correlation

### Research Question
Does network centrality (betweenness, PageRank) correlate with bug density and change fragility?

### Findings

**Key Paper:** Zimmermann & Nagappan (Microsoft Research)
- Network centrality metrics **strongly correlate** with post-release defects
- Betweenness centrality identifies "bridge" nodes that propagate changes
- PageRank identifies influential nodes that affect many others

**CIRank Metric:**
- Combines PageRank with change impact analysis
- Better predictor than raw centrality alone
- Formula incorporates both structural position and historical change frequency

**Thresholds (from research):**
| Metric | "Normal" | "High Risk" | Source |
|--------|----------|-------------|--------|
| Betweenness | < 0.05 | > 0.1 | MSR Studies |
| PageRank | < 0.01 | > 0.05 | Node in top 5% |
| In-Degree | < 10 | > 20 | Context-dependent |

**Open Questions:**
- [ ] How do these thresholds scale with codebase size?
- [ ] Are thresholds consistent across languages?
- [ ] What's the causal direction? (Central → bugs, or bugs → central?)

### SMC Application
- Add `betweenness_centrality`, `pagerank` to node properties
- Flag nodes above thresholds in Brain Download
- Correlate with git history for validation

---

## 2. Wagner's Evolvability & Neutral Networks

### Research Question
Can we measure evolvability from structure alone? What is the relationship between robustness and evolvability?

### Findings

**Key Insight (Wagner 2005):**
> "Genotypic robustness = proportion of mutations that don't change phenotype"

Robustness and evolvability are NOT opposites - they **enable each other** through neutral networks.

**Neutral Network Model:**
```
Neutral Network = Set of genotypes with identical phenotype
                  (connected by single mutations)

Larger neutral network = MORE evolvable
  - More "neighbors" to explore
  - Genetic diversity without phenotypic cost
  - Innovation capacity through neutral drift
```

**Translation to Code:**

| Biology | Code | Measurement |
|---------|------|-------------|
| Genotype | Source code | The text |
| Phenotype | Observable behavior | API contracts, tests |
| Mutation | Code change | Refactoring, edits |
| Neutral mutation | Behavior-preserving change | Passing tests |
| Neutral network size | Refactoring freedom | How many ways to implement same API? |

**Proposed Evolvability Formula (Candidate - NOT VALIDATED):**
```python
# HYPOTHESIS - needs empirical validation
evolvability = f(
    coupling_freedom = 1 / (1 + in_degree),      # fewer dependents = freer
    interface_stability = git_api_churn_rate,    # stable API = evolvable internals
    neutral_network_proxy = test_coverage * (1 - cyclomatic_complexity/100),
    centrality_risk = 1 - betweenness            # not on critical paths
)
```

### ADDITIONAL: Evolvability Metrics from Literature (Jan 21 Research)

**Qi Metric (Multi-dimensional):**
- Uses Principal Components Analysis (PCA) on coupling, cohesion, complexity, size metrics
- Validated across 4-7 years of open-source Java systems
- Captures different quality attributes per version

**Evolvability Subcharacteristics (ISO-aligned):**
| Subcharacteristic | Definition | Measurement Approach |
|-------------------|------------|----------------------|
| Analyzability | Ease of understanding | Cyclomatic complexity, doc coverage |
| Changeability | Ease of modification | Coupling, cohesion metrics |
| Stability | Risk of side effects | Fan-out, betweenness |
| Testability | Ease of testing | Cyclomatic complexity, dependency depth |
| Extensibility | Ease of adding features | Interface surface area |
| Adaptability | Ease of environmental change | External dependency count |
| Reusability | Potential for reuse | Specificity of types, coupling |

**Process-oriented Metrics:**
- Metrics based on implementation **change logs** (git history)
- Number of modules affected per feature
- Architectural adaptability via NFR framework

**Open Questions:**
- [ ] Can we measure "neutral network size" for code components?
- [ ] What's the code equivalent of "fitness landscape"?
- [ ] How do tests act as phenotype validators?
- [ ] Can PCA on our existing metrics reveal evolvability factors?

### SMC Application
- `evolvability` as composite property (requires research validation)
- Start with proxy: `leaf` nodes have higher evolvability than `hub` nodes

---

## 3. Normalized Systems Theory (NST)

### Research Question
What architectural patterns guarantee bounded change propagation?

### Findings

**Core Problem NST Solves:**
> Lehman's Law: Software systems become increasingly complex and harder to evolve over time.

**NST's 5 Elements:**

| Element | Definition | Code Equivalent |
|---------|------------|-----------------|
| **Data** | Information containers | DTOs, Models, Value Objects |
| **Action** | Operations on data | Functions, Methods |
| **Flow** | Sequencing of actions | Controllers, Orchestrators |
| **Connector** | Cross-boundary communication | APIs, Adapters, Gateways |
| **Trigger** | External event handlers | Event Listeners, Webhooks |

**NST's 4 Theorems:**

1. **Separation of Concerns** - Each element has single responsibility
2. **Connector Uniformity** - All cross-boundary communication via connectors
3. **Action Uniformity** - All operations follow same patterns
4. **Data Uniformity** - All data elements follow same structure rules

**Key Guarantee:**
> "Each new feature can be implemented with a **bounded number of changes** that does not depend on system size."

**Open Questions:**
- [ ] Do our topology_roles map to NST elements?
- [ ] Can we detect NST violations automatically?
- [ ] What's the relationship between NST elements and SMC atoms?

### SMC Application

| NST Element | SMC Atom Candidates | Detection |
|-------------|---------------------|-----------|
| Data | `ValueObject`, `DTO`, `Entity` | Structure without methods |
| Action | `Handler`, `Service` | Pure functions |
| Flow | `Controller`, `Orchestrator` | High out_degree |
| Connector | `Adapter`, `Gateway`, `Client` | Cross-boundary calls |
| Trigger | `EventListener`, `Webhook` | Event handling patterns |

---

## 4. Tree-sitter Scope Tracking

### Research Question
How does Tree-sitter track scopes, and can we use this for interface surface detection?

### Findings

**Tree-sitter's Locals System:**
Three capture types in `locals.scm`:

```scheme
; @local.scope - defines a boundary
(function_definition) @local.scope
(class_definition) @local.scope
(module) @local.scope

; @local.definition - creates a binding inside scope
(identifier) @local.definition
(parameter) @local.definition

; @local.reference - uses a binding
(identifier) @local.reference
```

### VERIFIED: Language-Specific locals.scm (Retrieved Jan 21, 2026)

**JavaScript (tree-sitter-javascript/queries/locals.scm):**
```scheme
; Scopes
[
  (statement_block)
  (function_expression)
  (arrow_function)
  (function_declaration)
  (method_definition)
] @local.scope

; Definitions
(pattern/identifier) @local.definition
(variable_declarator
  name: (identifier) @local.definition)

; References
(identifier) @local.reference
```

**Python (helix-editor/queries/python/locals.scm):**
```scheme
; Scopes
[
  (module)
  (function_definition)
  (lambda)
] @local.scope

; Definitions - Parameters
(parameters (identifier) @local.definition.variable.parameter)
(parameters (typed_parameter (identifier) @local.definition.variable.parameter))
(parameters (default_parameter name: (identifier) @local.definition.variable.parameter))
(parameters (typed_default_parameter name: (identifier) @local.definition.variable.parameter))
(parameters (list_splat_pattern (identifier) @local.definition.variable.parameter))   ; *args
(parameters (dictionary_splat_pattern (identifier) @local.definition.variable.parameter))  ; **kwargs

; Definitions - Imports
(import_statement name: (dotted_name (identifier) @local.definition.namespace))
(aliased_import alias: (identifier) @local.definition.namespace)

; References
(identifier) @local.reference
```

**Go (helix-editor/queries/go/locals.scm):**
```scheme
; Scopes
[
  (function_declaration)
  (method_declaration)
  (type_declaration)
  (block)
] @local.scope

; Definitions
(parameter_declaration (identifier) @local.definition.variable.parameter)
(variadic_parameter_declaration (identifier) @local.definition.variable.parameter)
(const_declaration (const_spec name: (identifier) @local.definition.constant))

; References
(identifier) @local.reference
```

**ECMAScript Base (TypeScript inherits):**
```scheme
; Scopes
[
  (statement_block)
  (arrow_function)
  (function_expression)
  (function_declaration)
  (method_definition)
  (for_statement)
  (for_in_statement)
  (catch_clause)
  (finally_clause)
] @local.scope

; Definitions
(arrow_function parameter: (identifier) @local.definition.variable.parameter)

; References
(identifier) @local.reference
```

### Cross-Language Comparison

| Language | Scope Nodes | Notable Differences |
|----------|-------------|---------------------|
| **JavaScript** | 5 (statement_block, function_expression, arrow_function, function_declaration, method_definition) | Pattern matching for identifiers |
| **Python** | 3 (module, function_definition, lambda) | Rich parameter typing (typed, default, splat) |
| **Go** | 4 (function_declaration, method_declaration, type_declaration, block) | Explicit const_spec handling |
| **ECMAScript** | 9 (includes for/catch/finally) | Most comprehensive scope coverage |

### Key Observations

1. **Consistency:** All languages use the same three captures (`@local.scope`, `@local.definition`, `@local.reference`)
2. **Granularity varies:** Python has fine-grained definition subtypes (`.variable.parameter`, `.namespace`)
3. **Missing in official tree-sitter-python:** The Python grammar repo does NOT ship with locals.scm; editor repos (Helix, nvim-treesitter) provide them
4. **ECMAScript is the most complete:** Includes control flow scope (for, catch, finally)

**Interface Surface Detection Logic:**
```
Interface Surface = {
  definitions visible from OUTSIDE scope,
  references to things OUTSIDE scope
}

Private = definitions only referenced INSIDE scope
Public = definitions referenced OUTSIDE scope
```

**What Tree-sitter CAN detect:**
- Scope boundaries (where interfaces exist)
- What's defined inside each scope
- What references cross scope boundaries
- Unused definitions (defined but never referenced)

**What Tree-sitter CANNOT detect:**
- Semantic visibility (public/private keywords vary by language)
- Runtime interface usage
- Type-level interfaces (needs additional analysis)

**Open Questions:**
- [ ] How consistent is locals.scm across languages?
- [ ] Can we compute "interface surface area" = count of cross-boundary references?
- [ ] What's the relationship between scope depth and coupling?

### SMC Application
- Use `@local.scope` captures to identify component boundaries
- Count cross-scope references as coupling metric
- Detect unused definitions as dead code candidates

---

## 5. Biological Modularity (Kirschner & Gerhart)

### Research Question
What makes biological systems evolvable? How does this translate to code?

### Findings

**Facilitated Variation Theory:**
Five properties that enable evolvability:

| Property | Biology | Code Equivalent |
|----------|---------|-----------------|
| **Versatile elements** | Proteins used in many contexts | Reusable components |
| **Weak linkage** | Loose coupling between modules | Low coupling, dependency injection |
| **Compartmentation** | Bulkheads, cell membranes | Module boundaries, namespaces |
| **Redundancy** | Multiple pathways, gene duplicates | Fallbacks, circuit breakers |
| **Exploratory behavior** | Adaptive responses | Plugin systems, extension points |

**Key Quote (Kirschner & Gerhart 1998):**
> "Modularity—defined as the clustering of epistatic interactions—is an important form of robustness because it limits the number of system components affected by a given perturbation."

**Epistatic Interaction = Dependency Coupling:**
- In biology: Gene A's effect depends on Gene B
- In code: Module A's behavior depends on Module B
- Modularity = clustering these interactions within boundaries

### SMC Application
- Measure "compartmentation" via clustering coefficient
- Detect "weak linkage" via low edge weights
- Identify "versatile elements" via high reuse (referenced by many)

---

## 6. Summary: Actionable Next Steps

### Ready for Implementation (Research Supports)

| Feature | Method | Priority |
|---------|--------|----------|
| Betweenness centrality | `nx.betweenness_centrality(G)` | HIGH |
| PageRank | `nx.pagerank(G)` | HIGH |
| Clustering coefficient | `nx.clustering(G)` | MEDIUM |
| Cross-scope references | Tree-sitter locals.scm | HIGH |

### Needs More Research

| Feature | Blocker | Research Needed |
|---------|---------|-----------------|
| Evolvability score | No validated formula | Empirical validation |
| NST element mapping | Mapping not complete | Cross-reference with atoms |
| Interface surface area | Definition unclear | Formalize measurement |

### Validation Plan

1. ~~Run centrality metrics on Collider itself~~ ✓ **DONE** - See `CENTRALITY_ANALYSIS.md`
2. Correlate with git history (change frequency, bug fixes)
3. ~~Document findings in `CENTRALITY_ANALYSIS.md`~~ ✓ **DONE**
4. Only implement evolvability after validation

### Validation Results Summary (Jan 21, 2026)

- `topology_role` successfully computed on 1768 nodes
- Distribution: 52% internal, 21% leaf, 17% root, 7% orphan, 4% hub
- Top hub: `layout.js::get` with 310 in-degree (risk point)
- See `CENTRALITY_ANALYSIS.md` for full analysis

---

## References

1. Wagner, A. (2005). *Robustness and Evolvability in Living Systems*. Princeton University Press.
2. Kirschner, M., & Gerhart, J. (1998). Evolvability. *PNAS*, 95(15), 8420-8427.
3. Zimmermann, T., & Nagappan, N. (2008). Predicting defects using network analysis. *ICSE*.
4. Normalized Systems Theory. https://normalizedsystems.org/
5. Tree-sitter Documentation. https://tree-sitter.github.io/tree-sitter/
6. Network Centrality in Microservices. arXiv:2501.13520 (2025).
