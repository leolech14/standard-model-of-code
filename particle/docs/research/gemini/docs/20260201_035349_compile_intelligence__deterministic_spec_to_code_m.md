# Research: COMPILE INTELLIGENCE: Deterministic Spec-to-Code Methods

We need comprehensive research on DETERMIN...

> **Date:** 2026-02-01 03:53:49
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:60627f5061dacbf678769ab159bb3be417d24d0c5db1c1ae7f4c89e97f9f18c4`
> **Raw JSON:** `raw/20260201_035349_compile_intelligence__deterministic_spec_to_code_m.json`

---

## Query

COMPILE INTELLIGENCE: Deterministic Spec-to-Code Methods

We need comprehensive research on DETERMINISTIC (provably correct) methods for generating code from specifications.

CATEGORIES TO COVER:

1. REFINEMENT CALCULUS
   - What is refinement? (spec → implementation via correctness-preserving steps)
   - Morgan's refinement calculus
   - Back's refinement algebra

2. PROOF ASSISTANTS / THEOREM PROVERS
   - Coq (Gallina extraction)
   - Lean (code extraction)
   - Isabelle/HOL (code generation)
   - Agda (dependent types)
   - F* (proof-oriented programming)

3. INDUSTRIAL FORMAL METHODS
   - B-Method (used in Paris Metro, aviation)
   - SPARK Ada (safety-critical)
   - Z notation
   - VDM (Vienna Development Method)
   - Event-B

4. LIGHTWEIGHT FORMAL METHODS
   - Alloy (model checking)
   - TLA+ (temporal logic)
   - Dafny (verification-aware language)
   - Liquid Haskell (refinement types)

5. THE EXTRACTION PROBLEM
   - How do you get RUNNABLE code from proofs?
   - Certified compilers (CompCert)
   - Proof-carrying code

6. AI + FORMAL METHODS
   - Can LLMs generate formally verifiable specs?
   - Neurosymbolic approaches
   - Current research (2024-2025)

For each method: History, how it works, industrial use cases, limitations.

---

## Response

Here is a comprehensive compilation of intelligence regarding **Deterministic Spec-to-Code Methods**.

This research covers the spectrum from mathematical refinement algebras to modern industrial application and the emerging neurosymbolic frontier.

---

# INTELLIGENCE REPORT: Deterministic Spec-to-Code Methods

> **Objective:** Identify methods to derive executable code from specifications such that the resulting code is mathematically guaranteed to satisfy the specification.
> **Constraint:** Methods must be deterministic (provably correct), avoiding probabilistic generation.

---

## 1. REFINEMENT CALCULUS
**Theory:** The transformation of a specification into executable code through a series of correctness-preserving steps.

### Core Concept
In classical programming, we write code ($C$) and hope it satisfies a specification ($S$). In Refinement Calculus, we start with $S$ and mathematically transform it into $C$.
$$S \sqsubseteq C \quad (\text{Implementation } C \text{ refines Specification } S)$$

### Morgan’s Refinement Calculus
Developed by Carroll Morgan, this extends Dijkstra’s **Weakest Precondition (wp)** calculus. It introduces a "Wide Spectrum Language" that mixes specification statements and executable code.
*   **Specification Statement:** `w :[pre, post]` (change variables $w$ such that if $pre$ holds, $post$ is established).
*   **Process:** You apply laws (e.g., "Assignment Law", "Sequential Composition Law") to break the abstract specification statement into smaller pieces, eventually reaching standard imperative constructs (assignment, `if`, `while`).
*   **Guarantee:** If every step follows a refinement law, the final code is correct by construction.

### Back’s Refinement Algebra
Ralph-Johan Back (and Joakim von Wright) formalized this using lattice theory.
*   **Lattice Structure:** Specifications and programs form a lattice.
*   **Monotonicity:** Program constructs are monotonic functions over this lattice.
*   **Data Refinement:** The crucial step of replacing abstract mathematical data types (sets, bags) with concrete implementation types (arrays, pointers) while proving the concrete operations simulate the abstract ones.

**Status:** Foundational theory. Rarely used manually today, but underpins tools like Event-B.

---

## 2. PROOF ASSISTANTS / THEOREM PROVERS
**Theory:** Code is a side-effect of a constructive proof.

### Coq (The Gallina Extraction)
*   **Mechanism:** Coq uses the Calculus of Inductive Constructions (CIC). You write a function in **Gallina** (Coq's functional language) and prove properties about it.
*   **Extraction:** Once proven, Coq’s extraction mechanism erases the "proof" parts (which have no runtime value) and compiles the "computational" parts into OCaml, Haskell, or Scheme.
*   **Key Achievement:** **CompCert**, a C compiler written and proved in Coq. It guarantees that the assembly output is semantically equivalent to the C input.

### Lean (The Modern Standard)
*   **Mechanism:** Lean is both a theorem prover and a programming language. Unlike Coq, there is less friction between the "proving" language and the "programming" language.
*   **Code Generation:** Lean compiles to C, which is then compiled to machine code.
*   **Status:** Rapidly growing ecosystem (Mathlib). Used heavily in modern formalization efforts.

### Isabelle/HOL
*   **Mechanism:** Uses Higher Order Logic (HOL). Adheres to the LCF (Logic for Computable Functions) approach where all proofs go through a small, trusted kernel.
*   **Code Generation:** Can generate executable code in SML, OCaml, Haskell, and Scala.
*   **Key Achievement:** **seL4 Microkernel**. The first OS kernel with a formal proof of functional correctness (the C code behaves exactly as the abstract spec).

### Agda & Idris (Dependent Types)
*   **Concept:** Types can depend on values. `Vec Int n` is a vector of integers of length $n$.
*   **Total Functional Programming:** The languages enforce totality (no infinite loops, no unhandled cases).
*   **Spec-is-Code:** In Agda, you don't write a separate spec. The type signature *is* the spec. If the function compiles, it satisfies the spec.

---

## 3. INDUSTRIAL FORMAL METHODS
**Theory:** Correct-by-Construction for safety-critical systems.

### B-Method / Event-B
*   **Creator:** Jean-Raymond Abrial (father of Z and B).
*   **Workflow:**
    1.  **Machine:** Define abstract state and invariants.
    2.  **Refinement:** Introduce concrete variables and events.
    3.  **Proof Obligations (POs):** The tool generates mathematical lemmas proving the refinement preserves invariants.
    4.  **Implementation:** The final refinement is translated to C or Ada.
*   **Use Case:** **Paris Metro Line 14** (Meteor). The safety-critical breaking and signaling software was generated using B. Zero bugs found in 20+ years of operation.

### SPARK Ada
*   **Concept:** A subset of the Ada language restricted to be unambiguous and formally verifiable.
*   **Contracts:** Uses Preconditions, Postconditions, and Loop Invariants.
*   **Flow Analysis:** Deterministically proves absence of runtime errors (buffer overflow, division by zero) and initializes data flow.
*   **Use Case:** Air Traffic Control (iFACTS), Jet Engine Control (Rolls-Royce).

### VDM (Vienna Development Method)
*   **Mechanism:** Model-based method. Uses explicit pre/post conditions.
*   **VDM++:** Object-oriented extension. Supports code generation to Java/C++.
*   **Status:** Strong in Japan (FeliCa chip firmware).

---

## 4. LIGHTWEIGHT FORMAL METHODS
**Theory:** Automated verification of developer-written code against specs (SMT Solvers).

### Dafny
*   **Mechanism:** A programming language designed for verification. It compiles to C#, Go, Java, etc.
*   **Process:** Developer writes code + annotations (`requires`, `ensures`, `invariant`).
*   **Solver:** Dafny translates this to **Boogie**, which translates to **Z3** (SMT solver). If Z3 finds a valid proof, the code is correct.
*   **Experience:** "Verify as you type." Red squigglies mean "Logic Error," not just Syntax Error.

### Liquid Haskell
*   **Concept:** **Refinement Types**. A type `T` paired with a predicate `P`.
    *   Example: `type Pos = {v:Int | v > 0}`.
*   **Mechanism:** Uses an SMT solver to check that terms satisfy the predicates at compile time.
*   **Result:** Haskell code that is provably free of certain classes of errors (e.g., array index out of bounds).

### TLA+ (Temporal Logic of Actions)
*   **Creator:** Leslie Lamport.
*   **Role:** Usually models the *design* (protocol), not the *implementation*.
*   **PlusCal:** An algorithmic language that translates to TLA+.
*   **Limitation:** It is generally used to verify the *algorithm*, not to generate the C code (though tools exist, manual translation is common). It proves the *architecture* is deterministic.

---

## 5. THE EXTRACTION PROBLEM
**Theory:** The "Last Mile" problem. How do we trust the transition from Math to Bits?

### The Trusted Computing Base (TCB)
Even with formal methods, you must trust:
1.  The Validity of the Spec (Did you ask for the right thing?)
2.  The Proof Kernel (Is the verifier correct?)
3.  The Compiler/Extractor (Is the CodeGen correct?)
4.  The Hardware (Is the CPU correct?)

### Solutions
1.  **Certified Compilers:** **CompCert**. The compiler is verified. If the source C is correct, the assembly is guaranteed correct.
2.  **Translation Validation:** Instead of verifying the compiler, verify the *output* of the compiler against the input for every run.
3.  **Proof-Carrying Code (PCC):** The binary contains a formal proof of its safety properties. The host system verifies the proof before execution.
4.  **CakeML:** A functional language (ML) with a verified compiler stack down to machine code, formalized in HOL4.

---

## 6. AI + FORMAL METHODS (Neurosymbolic)
**Theory:** Using Probabilistic AI to generate Deterministic Proofs.

### The Core Problem
LLMs are probabilistic (nondeterministic). They cannot be trusted to write critical code. However, they are excellent at "guessing."

### Neurosymbolic Approaches
1.  **Auto-Formalization:**
    *   **Workflow:** Human writes natural language spec $\to$ LLM generates Formal Spec (e.g., in Lean) $\to$ Human reviews Spec $\to$ LLM generates Proof/Code $\to$ **Verifier checks Proof**.
    *   **Benefit:** The "Hallucination" problem is solved by the compiler. If the LLM hallucinates a proof step, Lean rejects it.

2.  **Copilots for Provers (Lean Copilot):**
    *   LLMs are trained on Mathlib to suggest tactics (proof steps) in Lean.
    *   Google DeepMind's **AlphaGeometry** (and similar coding approaches) uses a neurosymbolic loop: A language model generates candidate constructions, and a symbolic engine deduces the consequences.

3.  **Dafny/Spec Generation:**
    *   Microsoft Research is exploring using LLMs to write the *invariants* and *pre/post conditions* for Dafny code, which is the hardest part for humans. The SMT solver then deterministically verifies if the LLM's annotations are correct.

### Status (2024-2025)
*   **LLMs as "Proof Officers":** Not writing the final code, but writing the intermediate proofs that allow the deterministic extractor to work.
*   **Verification is the Gatekeeper:** The output code is only accepted if the deterministic theorem prover validates the AI-generated proof.

---

## SUMMARY MATRIX

| Method | Rigor | Ease of Use | Output | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Refinement Calculus** | High | Low | Algorithm | Foundational Theory |
| **Coq / Lean** | Very High | Low (High Learning Curve) | OCaml / C | Compilers, Crypto, Math |
| **Isabelle/HOL** | Very High | Low | SML / Haskell | OS Kernels (seL4) |
| **B-Method / SPARK** | High | Medium | C / Ada | Trains, Avionics |
| **Dafny** | Medium | Medium-High | C# / Java | Cloud Infrastructure, AWS |
| **Agda / Idris** | High | Medium | Executable | Type-driven Dev |
| **Neurosymbolic** | High* | High | Verified Code | Future of Dev *(*Verification ensures rigor)* |

### Recommendation for Collider
Given Collider's focus on **deterministic analysis** and **codome definition**, the most relevant concepts are:
1.  **Refinement Types (Liquid Haskell/Dafny):** For analyzing the "purity" and "effect" dimensions of atoms.
2.  **Abstract Interpretation:** (Not listed above but adjacent) A technique used in tools like SPARK to mathematically prove value ranges without execution.
3.  **Graph/Lattice Theory (Back's Algebra):** Highly relevant for calculating the "Purpose Field" and topological changes in the codome.

---

## Citations

_No citations provided_
