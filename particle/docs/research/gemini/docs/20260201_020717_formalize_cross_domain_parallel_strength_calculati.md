# Research: FORMALIZE CROSS-DOMAIN PARALLEL STRENGTH CALCULATION

We have documented a genetic locus parallel fo...

> **Date:** 2026-02-01 02:07:17
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:57cb37885f8edf04559a89fe0ab99b21114c0ee0971e05ca5752b1e952bcecb7`
> **Raw JSON:** `raw/20260201_020717_formalize_cross_domain_parallel_strength_calculati.json`

---

## Query

FORMALIZE CROSS-DOMAIN PARALLEL STRENGTH CALCULATION

We have documented a genetic locus parallel for the Standard Model of Code with strength scores (40%-98%) but these are qualitative/intuitive assessments.

TASK: Define a rigorous, reproducible methodology for calculating parallel strength between two domains.

REQUIREMENTS:
1. What dimensions should be measured? (structural, behavioral, predictive, etc.)
2. What weights should each dimension have?
3. How do you score each dimension (0-100)?
4. What's the aggregation formula?
5. What literature/prior art exists for cross-domain mapping evaluation?

CONTEXT: We're mapping genetics concepts (locus, allele, genotype, phenotype, epistasis, pleiotropy, etc.) to software engineering concepts. We need a defensible methodology, not just intuition.

OUTPUT: A formal scoring rubric we can add to the theory documentation.

---

## Response

This analysis defines a formal methodology for calculating the **Cross-Domain Parallel Strength (CDPS)**. This framework moves beyond intuition to a quantifiable metric based on **Structure Mapping Theory** and **Category Theory**.

This should be added to `particle/docs/theory/CROSS_DOMAIN_METHODOLOGY.md`.

---

# Methodology: Cross-Domain Parallel Strength (CDPS) Calculation

## 1. Theoretical Basis
This methodology derives from **Dedre Gentner’s Structure-Mapping Theory (SMT)** and mathematical **Category Theory**.

*   **SMT Principle:** Strong analogies rely on *systematicity*—mapping deep relational structures rather than superficial object attributes.
*   **Functoriality:** A true parallel is a *functor* between Category A (Genetics) and Category B (Software). It must map objects to objects and morphisms (relationships) to morphisms, preserving composition.

## 2. The Five Dimensions of Isomorphism

To calculate the CDPS, we evaluate the mapping on five orthogonal dimensions.

### D1: Topological Isomorphism (Structure)
**Weight: 20%**
Does the graph structure of Domain A map 1:1 to Domain B?
*   **0 (Discordant):** Structures are fundamentally different (e.g., Tree vs. Mesh).
*   **5 (Partial):** High-level structures align, but low-level nodes disappear or merge.
*   **10 (Bijective):** Mathematical bijection exists. Every node and edge in A has exactly one correspondent in B.

### D2: Causal Fidelity (Mechanism)
**Weight: 25%**
Do cause-and-effect chains map correctly? If $A \to B$ in Genetics, does $A' \to B'$ in Code?
*   **0 (Unrelated):** Mechanisms differ entirely (e.g., probabilistic vs. deterministic).
*   **5 (Analogous):** The outcome is similar, but the "physics" of how it happens differs.
*   **10 (Homomorphic):** The causal chain is identical (e.g., Central Dogma: DNA $\to$ RNA $\to$ Protein matches Source $\to$ Bytecode $\to$ Runtime).

### D3: Predictive Power (Inference)
**Weight: 30%**
Can we predict unknown properties of the Target Domain by observing the Source Domain?
*   **0 (Descriptive):** Useful only for describing what we already know.
*   **5 (Weakly Predictive):** Suggests hypotheses, but requires significant modification.
*   **10 (Strongly Predictive):** A law in Domain A allows us to derive a previously unknown law in Domain B (e.g., discovering "Code Epistasis" by looking for non-additive gene interactions).

### D4: Failure Mode Symmetry (Entropy)
**Weight: 15%**
Do systems fail in the same way?
*   **0 (Divergent):** Domain A degrades gracefully; Domain B explodes.
*   **5 (Similar):** "Sickness" looks similar (e.g., technical debt $\approx$ genetic load).
*   **10 (Symmetric):** Specific pathologies map 1:1 (e.g., Cancer $\approx$ Infinite Recursion/Resource Exhaustion).

### D5: Scale Invariance (Fractal Nature)
**Weight: 10%**
Does the mapping hold when zooming in (micro) or out (macro)?
*   **0 (Brittle):** Works only at one specific level of abstraction.
*   **5 (Robust):** Works across 2-3 layers of abstraction.
*   **10 (Invariant):** Holds from bit/nucleotide to ecosystem/population.

---

## 3. The Scoring Rubric

Assign a score ($S$) of 0-10 for each dimension ($d$) based on the criteria below.

| Score | D1 Structure | D2 Mechanism | D3 Prediction | D4 Failure | D5 Scale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0** | No graph match | Mechanics orthogonal | Hindsight only | Failures unrelated | One level only |
| **2** | Vague resemblance | Metaphorical only | Lucky guesses | Superficially similar | Breaks easily |
| **5** | **Homologous** | **Process matches** | **Generating Hypotheses** | **Symptom match** | **Multi-level** |
| **8** | Isomorphic subset | Strict causal map | High accuracy | Root cause match | Most levels |
| **10** | **Bijective** | **Law-equivalent** | **Deterministic** | **Identical Physics** | **Universal** |

---

## 4. Aggregation Formula

The Total Parallel Strength ($P_{total}$) is the weighted sum of dimensions, subject to a **Structural Veto**.

$$P_{raw} = (0.2 \cdot S_{D1}) + (0.25 \cdot S_{D2}) + (0.3 \cdot S_{D3}) + (0.15 \cdot S_{D4}) + (0.1 \cdot S_{D5})$$

$$CDPS = P_{raw} \times 10$$

**The Structural Veto:**
If $S_{D1} < 3$ (Structural mismatch) OR $S_{D2} < 3$ (Causal mismatch), the mapping is declared **Poetic (Metaphor)** rather than **Isomorphic (Parallel)**, and the score is capped at **30%**, regardless of other dimensions.

---

## 5. Classification Tiers

| Range | Classification | Definition | Use Case |
| :--- | :--- | :--- | :--- |
| **90-100%** | **Isomorphism** | Mathematical equivalence. | Direct Algorithm Porting |
| **75-89%** | **Strong Parallel** | High predictive fidelity. | Architecture Design |
| **50-74%** | **Homology** | Shared ancestry/logic, divergent specifics. | Heuristics / Rules of Thumb |
| **30-49%** | **Metaphor** | Useful for teaching, dangerous for engineering. | Documentation / Explainer |
| **0-29%** | **False Cognate** | Superficially similar, deeply different. | **AVOID** |

---

## 6. Worked Example: "Genotype vs. Source Code"

Let us evaluate the parallel: **Genotype : Phenotype :: Source Code : Runtime Behavior**.

1.  **D1 Structure (9/10):** DNA is a sequence of instructions (nucleotides); Code is a sequence of instructions (tokens). Both define the total potentiality of the organism/program.
2.  **D2 Mechanism (10/10):** DNA is transcribed/translated to protein; Source is compiled/interpreted to machine code. The Central Dogma maps perfectly to the Compilation Pipeline.
3.  **D3 Prediction (8/10):** Knowing the genotype predicts the phenotype (mostly). Knowing source predicts runtime (mostly). Both suffer from "environmental" interference (epigenetics / OS state), but the prediction is strong.
4.  **D4 Failure (7/10):** Mutation in DNA $\to$ disease/death. Bug in source $\to$ crash/error.
5.  **D5 Scale (8/10):** Holds at function (gene), module (chromosome), and system (genome) levels.

**Calculation:**
$$P_{raw} = (0.2 \cdot 9) + (0.25 \cdot 10) + (0.3 \cdot 8) + (0.15 \cdot 7) + (0.1 \cdot 8)$$
$$P_{raw} = 1.8 + 2.5 + 2.4 + 1.05 + 0.8 = 8.55$$

**CDPS = 85.5% (Strong Parallel / Isomorphism)**

---

## 7. Prior Art & References

1.  **Gentner, D. (1983).** *Structure-mapping: A theoretical framework for analogy.* Cognitive Science. (The definitive work on structural vs. attribute mapping).
2.  **Mac Lane, S. (1971).** *Categories for the Working Mathematician.* (Functors preserving structure between categories).
3.  **Bejan, A. (1996).** *The Constructal Law.* (Flow systems in nature and engineering evolve towards similar configurations).
4.  **Holland, J. H. (1975).** *Adaptation in Natural and Artificial Systems.* (Foundational work mapping genetics to computational search).

---

## Citations

_No citations provided_
