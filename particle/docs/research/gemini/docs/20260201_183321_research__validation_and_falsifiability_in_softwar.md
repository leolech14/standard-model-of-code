# Research: RESEARCH: Validation and Falsifiability in Software Metrics

1. POPPER'S CRITERION: How does falsifi...

> **Date:** 2026-02-01 18:33:21
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:cfdab85f272d3d03df43914220da069ad63ca2a4c01862db33cfe231ff2e8ae3`
> **Raw JSON:** `raw/20260201_183321_research__validation_and_falsifiability_in_softwar.json`

---

## Query

RESEARCH: Validation and Falsifiability in Software Metrics

1. POPPER'S CRITERION: How does falsifiability apply to software engineering claims? Can we falsify 'coupling causes bugs'?

2. OBJECTIVE vs SUBJECTIVE METRICS: What makes a metric like cyclomatic complexity 'objective'? Is 'code quality' measurable or subjective?

3. GRAPH-THEORETIC METRICS: Dependency graphs, Betti numbers, centrality - are these discoveries about code structure or invented measures?

4. LEHMAN'S LAWS VALIDATION: How were Lehman's Laws empirically validated? What studies support or challenge them?

5. CONWAY'S LAW: Is Conway's Law falsifiable? How has it been tested?

6. BROOKS'S LAW: 'Adding people to a late project makes it later' - is this a law or heuristic? How validated?

7. METRIC VALIDATION: How do researchers validate that a metric (coupling, cohesion) actually predicts outcomes (bugs, maintenance cost)?

8. FRAMEWORK VALIDATION: How would one validate an entire theoretical framework (like SMC) rather than individual metrics?

Provide methodology, key studies, and limitations.

---

## Response

This is a foundational research analysis for the **Standard Model of Code (SMC)**. To treat code as physics (the core mission of `PROJECT_elements`), we must move beyond heuristics into falsifiable theories.

Here is the analysis of validation and falsifiability in software metrics, integrated with the `particle` (Collider) and `wave` (Context) architectures found in your codebase.

---

### 1. Popper’s Criterion & Falsifiability in Software Engineering

**The Core Question:** Can software engineering claims be proven false?

*   **Popper's Criterion:** A theory is scientific only if it is falsifiable—i.e., there exists a logical observation that could contradict it.
*   **Application to "Coupling Causes Bugs":**
    *   **Is it falsifiable?** Yes. If we consistently observe high-coupling systems (High $CBO$) with zero defect density over long periods in controlled environments, the strict causal claim is falsified.
    *   **Nuance:** Software Engineering is probabilistic, not deterministic. The claim is better stated as "High coupling increases the probability of defects." This is tested via statistical hypothesis testing ($H_0$: Correlation = 0).
*   **Methodology:**
    *   **Longitudinal Mining:** Extract git history.
    *   **metric:** Calculate Chidamber & Kemerer (CK) metrics (Coupling Between Objects) at $t_0$.
    *   **outcome:** Count bug-fix commits (using heuristics like "fix" in messages) involving those files at $t_1$.
    *   **Falsification:** If $Correlation(CBO, Defects) \le 0$, the hypothesis is falsified for that context.

### 2. Objective vs. Subjective Metrics

**The Core Question:** What defines metric objectivity?

*   **Objective Metrics (Cyclomatic Complexity - CC):**
    *   **Definition:** A metric is objective if it is algorithmic and observer-independent.
    *   **Why CC is objective:** Given Source Code $S$, $CC(S) = E - N + 2P$. Any two agents (human or machine) following this algorithm will yield the exact same number.
    *   **SMC Context:** Your `Collider` pipeline (specifically `particle/src/core/control_flow_analyzer.py`) produces objective metrics. The "Particle" layer is designed to be purely objective.
*   **Subjective Metrics (Code Quality/Readability):**
    *   **Definition:** "Quality" is a latent construct, not a direct observable. It depends on the cognitive model of the reader.
    *   **Is it measurable?** Directly? No. We measure **proxies** (e.g., Maintainability Index, Halstead Complexity) and correlate them with human ratings (Likert scales).
*   **SMC Context:** The `wave` layer deals with subjectivity. The `Holographic-Socratic Layer (HSL)` attempts to stabilize subjective interpretations by comparing them against objective particle data.

### 3. Graph-Theoretic Metrics: Discovery or Invention?

**The Core Question:** Are we finding structures or making them up?

*   **Realism (Discovery):** The dependency graph (nodes = functions, edges = calls) is a *real* structure existing in the code's topology.
    *   **Betti Numbers:** In Topological Data Analysis (TDA), Betti-0 is the number of connected components; Betti-1 is the number of "holes" or cycles. These are mathematical facts about the code structure, discovered, not invented.
*   **Constructivism (Invention):** The *semantic meaning* assigned to these numbers is invented.
    *   **Centrality:** claiming Eigenvector Centrality = "Module Importance" is an invented mapping.
*   **Validation:** We validate the "Invention" by checking if high-centrality nodes are indeed the ones that break the system when modified (Change Propagation Analysis).

### 4. Lehman’s Laws of Software Evolution

**The Core Question:** How do we know software "rots"?

*   **The Laws:** (e.g., Law I: Continuing Change, Law II: Increasing Complexity/Entropy).
*   **Methodology of Validation:**
    *   **Time Series Analysis:** Lehman and Belady (1974) studied OS/360 release data. They plotted module count and change logs over years.
    *   **Key Findings:** Without active refactoring work (anti-regressive work), entropy (disorder) invariably increases.
*   **SMC Context:** Your `drift_detected` section in `DOMAINS.yaml` and the `orphans` logic in `particle` are direct validators of Lehman's II Law. The `refinery` pipeline specifically combats this.
*   **Key Study:** *Herraiz et al. (2013)* validated Lehman’s laws on thousands of Open Source projects, finding mostly support but noting that "Law of Conservation of Familiarity" is often violated in rapid-release cycles.

### 5. Conway’s Law

**The Core Question:** Does the Org Chart dictate the Architecture?

*   **Hypothesis:** "Organizations which design systems are constrained to produce designs which are copies of the communication structures of these organizations."
*   **Falsifiability:** Highly falsifiable. Find a distributed, loose-knit open-source team that produces a tightly coupled monolithic kernel (Linux is a counter-example often debated; it is monolithic code but modular governance).
*   **Validation Strategy (The Mirroring Hypothesis):**
    *   Construct the **Technical Dependency Graph**.
    *   Construct the **Social Communication Graph** (who talks to whom/Slack/Email).
    *   **Test:** Compare the modularity ($Q$) of both graphs.
*   **Key Study:** *MacCormack, Rusnak, & Baldwin (Harvard, 2012).* They compared commercial software (tight teams) vs. open source (loose teams) and found commercial code was more coupled, validating Conway.

### 6. Brooks’s Law

**The Core Question:** Does adding manpower to a late project make it later?

*   **Status:** It is a **Heuristic/Observation**, not a physical law.
*   **Mechanism:** $Communication Cost = \frac{n(n-1)}{2}$. As $n$ grows, communication grows quadratically, while work capacity grows linearly.
*   **Validation:** Validated via **System Dynamics Modeling** (Abdel-Hamid & Madnick, 1991).
*   **Falsification:** It is falsifiable under conditions of perfect partitionability. If a task is perfectly parallel (painting a fence), the law fails. In software (debugging), the law usually holds.

### 7. Metric Validation Frameworks

**The Core Question:** How do we trust a metric?

**IEEE 1061 Methodology:**
1.  **Correlation:** Does Metric $M$ correlate with external attribute $A$ (e.g., Bugs)?
2.  **Consistency:** If $A$ increases, does $M$ strictly increase?
3.  **Predictability:** Can $M$ at time $t$ predict $A$ at time $t+1$?

**Weyuker’s Properties (Theoretical Validation):**
Elaine Weyuker (1988) proposed axioms for complexity metrics. E.g.,
*   *Non-coarseness:* Not all programs have the same complexity.
*   *Monotonicity:* Adding code should not decrease complexity.
*   *Interaction:* Complexity of ($P+Q$) can be greater than Complexity($P$) + Complexity($Q$).

**Key Study:** *Basili, Briand, & Melo (1996)* validates the CK Metrics suite. They proved Object-Oriented metrics (coupling, inheritance depth) were better predictors of fault-proneness than standard LOC (Lines of Code).

### 8. Framework Validation (Validating the SMC)

**The Core Question:** How do you validate an entire theory (PROJECT_elements)?

You cannot validate a framework with a single correlation. You need **Structural Equation Modeling (SEM)** or a **Nomological Network**.

**Methodology for SMC:**
1.  **Internal Consistency (Symmetry):**
    *   *Hypothesis:* The Code (Particle) and Context (Wave) must mirror each other.
    *   *Test:* Your `DOMAINS.yaml` drift detection. If `Code` exists without `Context` (Phantoms) or vice versa, the model detects "Symmetry Breaking."
2.  **Construct Validity:**
    *   Does "Atom T0" actually represent a fundamental unit?
    *   *Test:* Use the `Laboratory Bridge` (`wave/tools/ai/laboratory_bridge.py`). Can we reconstruct the `Code` behavior using only the `Atoms`? If yes, the Atoms are valid constructs.
3.  **Predictive Validity (The "Collider" Test):**
    *   *Hypothesis:* The `unified_analysis.json` graph topology predicts "God Class" risks.
    *   *Test:* Run `particle/src/core/god_class_detector_lite.py`. Compare identified classes against git churn history. If high-churn files are *not* detected, the framework is invalid (low recall).

**SMC Specifics (From your codebase):**
*   **Falsifiability Mechanism:** The `Holographic-Socratic Layer` (HSL) is your built-in falsification engine. It constantly asks: "Does the code disprove the documentation?"
*   **Experiment:** `wave/tools/ai/analyze.py --verify` is the implementation of Popper's Criterion for your project.

### Summary Table

| Concept | Nature | Falsifiable? | Key Validation Method | Project Component |
| :--- | :--- | :--- | :--- | :--- |
| **Coupling** | Empirical | Yes | Correlation w/ Defects | `particle/src/core/graph_metrics.py` |
| **Complexity** | Algorithmic | N/A (Definition) | Weyuker's Axioms | `particle/src/core/control_flow_analyzer.py` |
| **Lehman's Laws** | Evolutionary | Yes | Time-Series Mining | `wave/tools/ai/repo_archaeologist.py` |
| **Conway's Law** | Sociotechnical | Yes | Mirroring Hypothesis | `DOMAINS.yaml` (Symmetry) |
| **SMC Theory** | Theoretical | Yes | Structural Eq. Modeling | `Holographic-Socratic Layer` |

---

## Citations

_No citations provided_
