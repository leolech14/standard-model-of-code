# Cross-Domain Parallel Strength (CDPS) Methodology

**Layer:** Meta-theory (applies to all borrowed terminology)
**Status:** ACTIVE | Gemini-validated 2026-02-01
**Version:** 1.0.0
**Depends on:** Structure Mapping Theory (Gentner 1983), Category Theory

---

## Purpose

This methodology defines how to calculate **Cross-Domain Parallel Strength (CDPS)** - a rigorous, reproducible metric for evaluating mappings between domains (e.g., Genetics → Software Engineering).

Replaces intuitive "this feels like 70%" assessments with quantifiable scores.

---

## 1. Theoretical Basis

### Structure Mapping Theory (SMT)
**Source:** Gentner, D. (1983). *Structure-mapping: A theoretical framework for analogy.* Cognitive Science.

**Principle:** Strong analogies rely on *systematicity* - mapping deep relational structures rather than superficial object attributes.

### Category Theory (Functoriality)
**Source:** Mac Lane, S. (1971). *Categories for the Working Mathematician.*

**Principle:** A true parallel is a *functor* between Category A and Category B. It must:
- Map objects to objects
- Map morphisms (relationships) to morphisms
- Preserve composition

---

## 2. The Five Dimensions of Isomorphism

| Dimension | Code | Weight | Question |
|-----------|------|--------|----------|
| Topological Isomorphism | D1 | 20% | Does the graph structure map 1:1? |
| Causal Fidelity | D2 | 25% | Do cause-effect chains map correctly? |
| Predictive Power | D3 | 30% | Can we predict unknowns in Target from Source? |
| Failure Mode Symmetry | D4 | 15% | Do systems fail the same way? |
| Scale Invariance | D5 | 10% | Does mapping hold across abstraction levels? |

### D1: Topological Isomorphism (Structure) - 20%

Does the graph structure of Domain A map 1:1 to Domain B?

| Score | Description | Example |
|-------|-------------|---------|
| 0 | Discordant | Tree vs Mesh - fundamentally different |
| 2 | Vague resemblance | "Both have nodes" |
| 5 | Homologous | High-level matches, low-level diverges |
| 8 | Isomorphic subset | Most nodes/edges map |
| 10 | Bijective | Every node and edge has exactly one correspondent |

### D2: Causal Fidelity (Mechanism) - 25%

If A → B in Source domain, does A' → B' in Target domain?

| Score | Description | Example |
|-------|-------------|---------|
| 0 | Unrelated | Probabilistic vs deterministic |
| 2 | Metaphorical only | "Sort of like..." |
| 5 | Analogous | Outcome similar, "physics" differs |
| 8 | Strict causal map | Chain maps directly |
| 10 | Law-equivalent | DNA→RNA→Protein = Source→Bytecode→Runtime |

### D3: Predictive Power (Inference) - 30%

**Highest weight** - the ultimate test of a parallel.

| Score | Description | Example |
|-------|-------------|---------|
| 0 | Descriptive only | Explains known facts |
| 2 | Hindsight | "Oh yes, that makes sense now" |
| 5 | Hypothesis generating | Suggests things to investigate |
| 8 | Accurate predictions | Most predictions validated |
| 10 | Deterministic | Laws in A derive unknown laws in B |

### D4: Failure Mode Symmetry (Entropy) - 15%

Do systems degrade/fail the same way?

| Score | Description | Example |
|-------|-------------|---------|
| 0 | Divergent | A degrades gracefully, B explodes |
| 2 | Superficially similar | "Both can break" |
| 5 | Symptom match | Technical debt ≈ genetic load |
| 8 | Root cause match | Same underlying mechanism |
| 10 | Identical physics | Cancer ≈ infinite recursion |

### D5: Scale Invariance (Fractal Nature) - 10%

Does the mapping hold when zooming in/out?

| Score | Description | Example |
|-------|-------------|---------|
| 0 | Brittle | Works at exactly one abstraction level |
| 2 | Breaks easily | Works at 1-2 levels, fails elsewhere |
| 5 | Multi-level | Robust across 2-3 layers |
| 8 | Most levels | Holds from function to system |
| 10 | Universal | Bit/nucleotide to ecosystem/population |

---

## 3. Aggregation Formula

### Raw Score Calculation

```
P_raw = (0.20 × S_D1) + (0.25 × S_D2) + (0.30 × S_D3) + (0.15 × S_D4) + (0.10 × S_D5)

CDPS = P_raw × 10
```

Where S_Dn is the score (0-10) for dimension n.

### The Structural Veto

**If S_D1 < 3 OR S_D2 < 3:**

The mapping is declared **Poetic (Metaphor)** rather than **Isomorphic (Parallel)**, and CDPS is **capped at 30%** regardless of other dimensions.

Rationale: Without structural or causal fidelity, high scores in other dimensions are misleading.

---

## 4. Classification Tiers

| CDPS Range | Classification | Definition | Use Case |
|------------|----------------|------------|----------|
| **90-100%** | Isomorphism | Mathematical equivalence | Direct algorithm porting |
| **75-89%** | Strong Parallel | High predictive fidelity | Architecture design |
| **50-74%** | Homology | Shared logic, divergent specifics | Heuristics, rules of thumb |
| **30-49%** | Metaphor | Useful for teaching, dangerous for engineering | Documentation only |
| **0-29%** | False Cognate | Superficially similar, deeply different | **AVOID** |

---

## 5. Worked Examples

### Example 1: Genotype → Source Code

**Mapping:** Genotype : Phenotype :: Source Code : Runtime Behavior

| Dimension | Score | Justification |
|-----------|-------|---------------|
| D1 Structure | 9 | DNA = sequence of instructions; Code = sequence of tokens |
| D2 Mechanism | 10 | Central Dogma = Compilation Pipeline (DNA→RNA→Protein = Source→Bytecode→Runtime) |
| D3 Prediction | 8 | Knowing genotype predicts phenotype (mostly); knowing source predicts runtime (mostly) |
| D4 Failure | 7 | Mutation→disease; Bug→crash |
| D5 Scale | 8 | Holds at gene/function, chromosome/module, genome/system |

```
P_raw = (0.20 × 9) + (0.25 × 10) + (0.30 × 8) + (0.15 × 7) + (0.10 × 8)
      = 1.8 + 2.5 + 2.4 + 1.05 + 0.8
      = 8.55

CDPS = 85.5% → Strong Parallel
```

### Example 2: Mutation → Code Change

**Mapping:** Random Mutation : Genetic Change :: Code Edit : Software Change

| Dimension | Score | Justification |
|-----------|-------|---------------|
| D1 Structure | 6 | Both modify sequences, but mutation is point-wise; refactoring is structural |
| D2 Mechanism | 3 | CRITICAL: Biology = random; Code = intentional (teleological) |
| D3 Prediction | 4 | Can't predict code changes from mutation theory |
| D4 Failure | 6 | Both can cause dysfunction |
| D5 Scale | 5 | Works at statement/nucleotide level, less at higher levels |

```
P_raw = (0.20 × 6) + (0.25 × 3) + (0.30 × 4) + (0.15 × 6) + (0.10 × 5)
      = 1.2 + 0.75 + 1.2 + 0.9 + 0.5
      = 4.55

CDPS = 45.5% → Metaphor (useful for teaching, not engineering)
```

### Example 3: Epigenetics → Configuration

**Mapping:** Epigenetic Marks : Gene Expression :: Config Files : Code Behavior

| Dimension | Score | Justification |
|-----------|-------|---------------|
| D1 Structure | 8 | Both are "overlay" systems modifying expression without changing core |
| D2 Mechanism | 9 | Both turn genes/functions on/off without modifying sequence |
| D3 Prediction | 8 | Studying epigenetics suggests config-driven architecture patterns |
| D4 Failure | 7 | Epigenetic errors cause disease; misconfig causes outages |
| D5 Scale | 7 | Works at gene/function and pathway/module levels |

```
P_raw = (0.20 × 8) + (0.25 × 9) + (0.30 × 8) + (0.15 × 7) + (0.10 × 7)
      = 1.6 + 2.25 + 2.4 + 1.05 + 0.7
      = 8.0

CDPS = 80% → Strong Parallel
```

---

## 6. Application to Genetic Parallel

Using this methodology, we recalculate the genetic metaphor strengths:

| Concept | D1 | D2 | D3 | D4 | D5 | CDPS | Tier |
|---------|----|----|----|----|----|----|------|
| Genotype/Phenotype | 9 | 10 | 8 | 7 | 8 | **85.5%** | Strong Parallel |
| Epigenetics/Config | 8 | 9 | 8 | 7 | 7 | **80.0%** | Strong Parallel |
| HGT/Dependencies | 9 | 9 | 7 | 6 | 8 | **78.5%** | Strong Parallel |
| Genetic Load/Tech Debt | 7 | 8 | 8 | 8 | 6 | **76.0%** | Strong Parallel |
| Pleiotropy/Fan-out | 8 | 8 | 7 | 7 | 7 | **74.5%** | Homology |
| Linkage/Coupling | 7 | 7 | 7 | 6 | 7 | **69.5%** | Homology |
| Epistasis/Shadowing | 6 | 6 | 6 | 5 | 6 | **59.0%** | Homology |
| Mutation/Code Change | 6 | 3 | 4 | 6 | 5 | **45.5%** | Metaphor |

---

## 7. Prior Art & References

1. **Gentner, D. (1983).** *Structure-mapping: A theoretical framework for analogy.* Cognitive Science, 7(2), 155-170.
   - Definitive work on structural vs attribute mapping

2. **Mac Lane, S. (1971).** *Categories for the Working Mathematician.* Springer.
   - Functors preserving structure between categories

3. **Bejan, A. (1996).** *The Constructal Law.*
   - Flow systems in nature and engineering evolve towards similar configurations

4. **Holland, J. H. (1975).** *Adaptation in Natural and Artificial Systems.* University of Michigan Press.
   - Foundational work mapping genetics to computational search

5. **Hofstadter, D. & Sander, E. (2013).** *Surfaces and Essences: Analogy as the Fuel and Fire of Thinking.* Basic Books.
   - Modern treatment of analogy in cognition

---

## Usage Notes

1. **Always score all 5 dimensions** before calculating CDPS
2. **Apply the Structural Veto** - don't trust high D3/D4/D5 if D1/D2 are weak
3. **Document justifications** - scores without reasoning are worthless
4. **Use the tier classification** to guide how you apply the parallel
5. **Re-score when new evidence emerges** - parallels can strengthen or weaken

---

*This methodology applies to all borrowed terminology in GLOSSARY.yaml.*
*For the genetic parallel specifically, see L1_DEFINITIONS.md §5.8.1.*
