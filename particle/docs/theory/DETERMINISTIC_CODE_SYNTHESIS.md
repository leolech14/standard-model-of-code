# Deterministic Code Synthesis
## From Specification to Implementation: The Formal Methods Landscape

**Status:** COMPLETE
**Date:** 2026-02-01
**Version:** 1.0.0
**Author:** Leonardo Lech + Claude (Opus 4.5)
**Validated:** Gemini 3 Pro (CDPS: 96/100)

---

## Abstract

This document catalogs methods for **deterministic transformation** of specifications into executable code. Unlike probabilistic AI code generation, these methods provide **mathematical guarantees** that the implementation satisfies the specification. This is the "hard science" complement to Spec-Driven Development.

**Core Question:** *Can we mechanically derive correct code from specifications?*

**Answer:** Yes, with varying degrees of automation and expressiveness.

---

## 1. The Synthesis Spectrum

```
SPECIFICATION                                           IMPLEMENTATION
     │                                                        │
     │  ┌─────────────────────────────────────────────────┐  │
     │  │           SYNTHESIS METHODS                      │  │
     │  │                                                  │  │
     │  │  FULLY AUTOMATIC          SEMI-AUTOMATIC        │  │
     │  │  ────────────────         ──────────────        │  │
     │  │  • Refinement Calculus    • Proof Assistants    │  │
     │  │  • Synthesis Tools        • Interactive Proofs  │  │
     │  │  • Model Compilers        • Guided Development  │  │
     │  │                                                  │  │
     │  │           GUARANTEE LEVELS                       │  │
     │  │  ────────────────────────────                   │  │
     │  │  TOTAL: Proven correct for all inputs           │  │
     │  │  PARTIAL: Proven correct if terminates          │  │
     │  │  CONDITIONAL: Proven under assumptions          │  │
     │  └─────────────────────────────────────────────────┘  │
     │                                                        │
     ▼                                                        ▼
   L₁ (Contextome)                                    L₀ (Codome)
```

---

## 2. Refinement Calculus

### 2.1 The Core Idea

**Refinement** is a relation between specifications: S₁ ⊑ S₂ means "S₂ is at least as good as S₁" — it meets all requirements of S₁ and possibly more.

```
ABSTRACT SPEC (What)
       │
       │ ⊑ (refines to)
       ▼
INTERMEDIATE SPEC
       │
       │ ⊑ (refines to)
       ▼
CONCRETE CODE (How)
```

**Key Insight:** Code is just the most refined specification.

### 2.2 Morgan's Refinement Calculus (1990)

Carroll Morgan's "Programming from Specifications" established:

**Refinement Laws:**
```
1. ASSIGNMENT INTRODUCTION
   w: [pre, post] ⊑ w := E
   where post[w\E] ∧ pre ⇒ post is valid

2. SEQUENTIAL COMPOSITION
   w: [pre, post] ⊑ w: [pre, mid]; w: [mid, post]

3. CONDITIONAL
   w: [pre, post] ⊑ if B then w: [pre ∧ B, post] else w: [pre ∧ ¬B, post]

4. LOOP INTRODUCTION
   w: [pre, post] ⊑ while B do w: [inv ∧ B, inv] od
   where inv ∧ ¬B ⇒ post and pre ⇒ inv
```

**Example: Deriving Integer Square Root**
```
SPEC:   r: [n ≥ 0, r² ≤ n < (r+1)²]

STEP 1: Introduce loop with invariant r² ≤ n
        r := 0; while (r+1)² ≤ n do r := r+1 od

STEP 2: Optimize (eliminate squaring in condition)
        r, s := 0, 1; while s ≤ n do r, s := r+1, s+2*r+3 od

RESULT: Proven correct by construction
```

### 2.3 Back's Refinement Calculus (1978-1998)

Ralph-Johan Back extended refinement with:

- **Data Refinement:** Changing data representations
- **Action Systems:** Concurrent refinement
- **Lattice Theory:** Complete lattice of specifications

**Data Refinement Example:**
```
ABSTRACT: Set ADT with {add, remove, contains}
CONCRETE: Sorted array with binary search

Coupling Invariant: array is sorted ∧ set = array_elements
Proves: All operations preserve invariant
```

### 2.4 Tools Implementing Refinement

| Tool | Language | Status | Use Case |
|------|----------|--------|----------|
| **Refinement Workbench** | Various | Academic | Teaching/Research |
| **Rodin** | Event-B | Active | Safety-critical systems |
| **ProB** | B/Event-B | Active | Animation & Model Checking |
| **Atelier B** | B-Method | Commercial | Railway, Defense |

---

## 3. Proof Assistants (Interactive Theorem Provers)

### 3.1 The Paradigm

**Proof Assistants** are software tools where:
1. You write specifications in a rich type theory
2. You prove properties interactively
3. You extract executable code from proofs

**Curry-Howard Correspondence:**
```
PROPOSITIONS = TYPES
PROOFS = PROGRAMS

A proof of "∀x. P(x) → Q(x)" IS a function from P to Q.
Extract the function, get verified code.
```

### 3.2 Major Proof Assistants

#### Coq (1984-present)

**Foundation:** Calculus of Inductive Constructions (CIC)

**Key Features:**
- Dependent types (types can depend on values)
- Tactic-based proofs
- Extraction to OCaml, Haskell, Scheme

**Landmark Projects:**
- **CompCert:** Verified C compiler (no miscompilation bugs possible)
- **Mathematical Components:** Formalized Four Color Theorem
- **Verified Software Toolchain:** Verified C runtime

**Example:**
```coq
(* Specification: sorted list insertion *)
Fixpoint insert (x : nat) (l : list nat) : list nat :=
  match l with
  | [] => [x]
  | h :: t => if x <=? h then x :: l else h :: insert x t
  end.

(* Proof: insert preserves sortedness *)
Theorem insert_sorted : forall x l,
  sorted l -> sorted (insert x l).
Proof.
  intros x l H. induction l.
  - simpl. constructor.
  - simpl. destruct (x <=? a) eqn:E.
    + constructor; auto. apply Nat.leb_le in E. auto.
    + constructor; auto.
Qed.

(* Extract to OCaml *)
Extraction "insert.ml" insert.
```

#### Lean 4 (2021-present)

**Foundation:** Dependent Type Theory with Quotient Types

**Key Features:**
- Fast compilation (self-hosting)
- Metaprogramming in Lean itself
- Excellent IDE integration
- Mathlib: 1M+ lines of formalized math

**Example (from our ContextomeNecessity.lean):**
```lean
-- The Contextome Necessity Theorem
theorem contextome_is_necessary :
  ¬∃ (self_verify : Codome → Contextome),
    ∀ (c : Codome) (intended : Contextome),
      HasPurpose c intended → self_verify c = intended := by
  intro ⟨f, hf⟩
  -- Construct adversarial case using diagonalization
  exact absurd rfl (semantic_undecidability f hf)
```

#### Isabelle/HOL (1986-present)

**Foundation:** Higher-Order Logic (Classical)

**Key Features:**
- Sledgehammer: Automatic proof search
- Code generation to Haskell, Scala, SML, OCaml
- Large proof library (AFP: Archive of Formal Proofs)

**Example:**
```isabelle
theorem sqrt_correct:
  assumes "n ≥ 0"
  shows "∃r. r² ≤ n ∧ n < (r+1)²"
  using assms
  by (induction n rule: nat_less_induct) auto

(* Generate Haskell code *)
export_code sqrt in Haskell
```

#### Agda (1999-present)

**Foundation:** Intuitionistic Type Theory with Pattern Matching

**Key Features:**
- First-class pattern matching
- Cubical Agda: Homotopy Type Theory
- Excellent for programming language semantics

#### F* (F-star) (2011-present)

**Foundation:** Dependent types with effects

**Key Features:**
- Refinement types (lightweight verification)
- Effect system for reasoning about state, exceptions
- Compiles to C, OCaml, F#, JavaScript
- Used in Project Everest (verified TLS)

**Example:**
```fstar
(* Refined type: positive integers *)
type pos = x:int{x > 0}

(* Function that requires positive input *)
let divide (n:int) (d:pos) : int = n / d

(* Compiler rejects: divide 10 0 *)
```

### 3.3 Comparison Matrix

| Aspect | Coq | Lean 4 | Isabelle/HOL | Agda | F* |
|--------|-----|--------|--------------|------|-----|
| **Logic** | Constructive | Constructive | Classical | Constructive | Classical |
| **Automation** | Medium | Medium | High | Low | High |
| **Extraction** | OCaml/Haskell | Lean/C | Many | Haskell | C/JS |
| **Learning Curve** | High | Medium | Medium | High | Medium |
| **Industry Use** | High | Growing | High | Academic | High |
| **Library Size** | Large | Huge (Mathlib) | Large | Medium | Medium |

---

## 4. Industrial Formal Methods

### 4.1 B-Method (1996-present)

**Creator:** Jean-Raymond Abrial

**Philosophy:** Abstract Machine Notation (AMN) for stepwise refinement

**Used In:**
- Paris Metro Line 14 (driverless)
- 87% of French railway signaling
- Aerospace (Airbus)

**Structure:**
```b
MACHINE BankAccount
VARIABLES balance
INVARIANT balance ∈ ℕ
INITIALISATION balance := 0
OPERATIONS
  deposit(amount) = PRE amount > 0 THEN balance := balance + amount END;
  withdraw(amount) = PRE amount ≤ balance THEN balance := balance - amount END
END
```

**Toolchain:**
- **Atelier B:** Commercial IDE (ClearSy)
- **ProB:** Animator and Model Checker
- **Rodin:** Event-B (reactive systems)

### 4.2 SPARK Ada (1988-present)

**Philosophy:** Subset of Ada with formal annotations

**Used In:**
- DO-178C Level A avionics
- CENELEC SIL 4 railways
- UK military systems
- NASA missions

**Key Features:**
- Information flow analysis
- Automatic proof of absence of runtime errors
- No pointers, no dynamic allocation, no tasks in core subset

**Example:**
```ada
procedure Increment (X : in out Integer)
  with Global  => null,
       Depends => (X => X),
       Pre     => X < Integer'Last,
       Post    => X = X'Old + 1
is
begin
   X := X + 1;
end Increment;
```

**Toolchain:**
- **GNATprove:** Automatic prover
- **GPS:** IDE with proof integration

### 4.3 VDM (Vienna Development Method) (1970s-present)

**History:** Oldest formal method, from IBM Vienna Lab

**Variants:**
- VDM-SL: Sequential
- VDM++: Object-oriented
- VDM-RT: Real-time

**Example:**
```vdm
class Stack
  instance variables
    elements: seq of nat := []

  operations
    push: nat ==> ()
    push(n) == elements := [n] ^ elements
    pre len elements < MAX_SIZE;

    pop: () ==> nat
    pop() == (dcl top: nat := hd elements;
              elements := tl elements;
              return top)
    pre elements <> [];
end Stack
```

**Tool:** Overture (open source)

### 4.4 Alloy (2000-present)

**Creator:** Daniel Jackson (MIT)

**Philosophy:** Lightweight formal methods via bounded model checking

**Key Insight:** Most bugs manifest in small instances. Check all instances up to bound k.

**Example:**
```alloy
sig Person {
  parent: lone Person
}

fact NoSelfParent {
  no p: Person | p in p.^parent
}

pred HasGrandparent[p: Person] {
  some p.parent.parent
}

run HasGrandparent for 5
check NoSelfParent for 10
```

**Tool:** Alloy Analyzer (free)

---

## 5. Lightweight Formal Methods

### 5.1 Dafny (2009-present)

**Creator:** Rustan Leino (Microsoft Research)

**Philosophy:** Verification as part of the language

**Key Features:**
- Auto-active verification (mostly automatic)
- Compiles to C#, Java, JavaScript, Go, Python
- Ghost code for specifications (erased at runtime)

**Example:**
```dafny
method BinarySearch(a: array<int>, key: int) returns (index: int)
  requires forall i, j :: 0 <= i < j < a.Length ==> a[i] <= a[j]
  ensures index >= 0 ==> a[index] == key
  ensures index < 0 ==> forall i :: 0 <= i < a.Length ==> a[i] != key
{
  var lo, hi := 0, a.Length;
  while lo < hi
    invariant 0 <= lo <= hi <= a.Length
    invariant forall i :: 0 <= i < lo ==> a[i] < key
    invariant forall i :: hi <= i < a.Length ==> a[i] > key
  {
    var mid := (lo + hi) / 2;
    if a[mid] < key { lo := mid + 1; }
    else if a[mid] > key { hi := mid; }
    else { return mid; }
  }
  return -1;
}
```

### 5.2 Liquid Haskell (2012-present)

**Philosophy:** Refinement types for Haskell

**Key Features:**
- Extends Haskell types with logical predicates
- SMT-based verification (Z3)
- Gradual adoption (can verify parts of codebase)

**Example:**
```haskell
{-@ type Pos = {v:Int | v > 0} @-}
{-@ type NonEmpty a = {v:[a] | len v > 0} @-}

{-@ safeHead :: NonEmpty a -> a @-}
safeHead (x:_) = x

{-@ divide :: Int -> Pos -> Int @-}
divide n d = n `div` d
```

### 5.3 TLA+ (Temporal Logic of Actions)

**Creator:** Leslie Lamport (Turing Award 2013)

**Philosophy:** Specify concurrent and distributed systems

**Used At:** Amazon (DynamoDB, S3, EBS), Microsoft, Intel

**Example:**
```tla
---- MODULE SimpleTransfer ----
VARIABLES balance

Init == balance = [a |-> 100, b |-> 50]

Transfer(from, to, amount) ==
  /\ balance[from] >= amount
  /\ balance' = [balance EXCEPT ![from] = @ - amount,
                                ![to] = @ + amount]

Next == \E from, to \in {"a", "b"}, amt \in 1..50:
          Transfer(from, to, amt)

TotalConstant == balance["a"] + balance["b"] = 150

Spec == Init /\ [][Next]_balance
====

(* TLC model checker verifies TotalConstant holds *)
```

---

## 6. The Extraction Problem

### 6.1 The Gap

**The Problem:** Proofs are about abstract mathematical objects. Programs execute on finite machines with:
- Limited memory
- Finite precision arithmetic
- I/O side effects
- Concurrency

**The Question:** Does extracted code actually work?

### 6.2 Verified Compilers

#### CompCert (2005-present)

**Achievement:** First formally verified C compiler

**Guarantee:** If source program has defined behavior, compiled code has same behavior.

**Method:**
- 23 compilation passes
- Each pass proven correct in Coq
- Composition yields end-to-end correctness

**Stats:**
- ~100,000 lines of Coq proofs
- ~35,000 lines of ML code (generated)
- Found bugs in GCC and LLVM during testing

#### CakeML (2014-present)

**Achievement:** Verified compiler for ML-like language

**Unique Feature:** Compiler verified down to machine code

**Bootstrap:** CakeML compiler is written in CakeML and compiles itself

### 6.3 Proof-Carrying Code

**Concept:** Ship code with its proof. Recipient verifies locally.

**Benefit:** Don't trust compiler, trust math.

**Example:** Certifying LLVM optimizations with Alive2

---

## 7. The AI Inflection Point

### 7.1 Neurosymbolic Approaches

**The Convergence:**
- AI generates code candidates
- Formal methods verify correctness
- Combine speed of AI with guarantees of proofs

**Example Flow:**
```
SPEC (Natural Language + Formal)
        │
        ▼
┌───────────────────┐
│   LLM Generator   │ → Candidate₁, Candidate₂, ...
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Formal Verifier  │ → ✓ or ✗ with counterexample
└───────────────────┘
        │
        ▼
   VERIFIED CODE
```

### 7.2 Current Projects

| Project | Approach | Status |
|---------|----------|--------|
| **LeanDojo** | LLM-powered theorem proving | Active research |
| **AlphaProof** | DeepMind IMO solver | Breakthrough 2024 |
| **GPT-f** | OpenAI + Lean | Research |
| **Baldur** | LLM + Isabelle | Berkeley research |
| **Clover** | Code + Proofs jointly | Meta AI |

### 7.3 The SMC Perspective

**From SPEC_DRIVEN_DEVELOPMENT.md:**

```
Traditional: Human → Code
AI Era:     Human → Spec → AI → Code → Verifier → Proven Code
```

**The Loop:**
1. Write spec in L₁ (Contextome)
2. AI generates L₀ candidate (Codome)
3. Verifier checks L₀ ⊧ L₁
4. If fails, AI refines based on counterexample
5. Repeat until proven

**This is Spec-Driven Development with guaranteed correctness.**

---

## 8. Comparison: Probabilistic vs Deterministic

| Aspect | AI Code Gen (GPT, Claude) | Formal Methods |
|--------|---------------------------|----------------|
| **Speed** | Fast (seconds) | Slow (hours-days) |
| **Guarantee** | None (probabilistic) | Mathematical proof |
| **Spec Format** | Natural language | Formal logic |
| **Failures** | Silent (code looks right) | Loud (proof fails) |
| **Scalability** | Any size | Limited by proof complexity |
| **Learning Curve** | Low | High |
| **Trust** | Requires testing | Requires spec correctness |
| **Creativity** | High (novel solutions) | Low (follows rules) |

**Synthesis (the future):**
- AI for creative exploration and candidate generation
- Formal methods for verification and guarantee
- Human for spec writing and strategy

---

## 9. Implementation Recommendations

### 9.1 Adoption Ladder

```
LEVEL 1: Lightweight                   LEVEL 4: Full Formal
─────────────────────                  ─────────────────────
• Type hints                           • Coq/Lean proofs
• Property-based testing               • Verified extraction
• Design by Contract                   • CompCert compilation
• Static analyzers                     • Proof-carrying code

LEVEL 2: Refinement Types              LEVEL 5: Certified Stack
─────────────────────────              ──────────────────────
• Liquid Haskell                       • Verified OS (seL4)
• F* for security-critical             • Verified compiler
• Dafny for algorithms                 • Verified hardware

LEVEL 3: Model Checking
───────────────────────
• TLA+ for protocols
• Alloy for design
• SPIN for concurrency
```

### 9.2 When to Use What

| Situation | Recommended Approach |
|-----------|---------------------|
| Safety-critical (avionics, medical) | SPARK Ada, B-Method |
| Crypto & Security | F*, Dafny, Coq |
| Distributed Systems | TLA+, Alloy |
| Algorithms & Data Structures | Coq, Lean, Dafny |
| Fast Prototyping with Guarantees | Liquid Haskell |
| Teaching Formal Methods | Alloy, Dafny |
| Mathematical Formalization | Lean (Mathlib) |

### 9.3 Integration with SMC

**LOCUS Extension for Verified Atoms:**
```
LOCUS(verified_atom) = ⟨λ, Ω, τ, α, R, V⟩

V = Verification Level:
  V₀: Unverified (standard code)
  V₁: Type-checked (standard types)
  V₂: Refined (refinement types)
  V₃: Model-checked (bounded verification)
  V₄: Proven (full formal proof)
  V₅: Extracted (verified compilation)
```

**New Dimension for Atoms Schema:**
```yaml
verification:
  level: "V₀" | "V₁" | "V₂" | "V₃" | "V₄" | "V₅"
  tool: string (e.g., "Lean 4", "Dafny", "SPARK")
  proof_artifact: path | null
```

---

## 10. The Future: Verified AI-Generated Code

### 10.1 The Vision

```
2020s: AI generates code, human tests
2030s: AI generates code + proof sketch, tool completes proof
2040s: AI generates spec from intent, synthesizes verified code

The Contextome becomes the ONLY artifact humans write.
The Codome is mechanically derived and proven correct.
```

### 10.2 Open Problems

1. **Spec Correctness:** Proofs are only as good as specs. How do we verify specs?
2. **Proof Scalability:** Proofs grow faster than code. Can AI help?
3. **Natural Language to Formal:** Bridging L₁ (human) to L₁ (formal)
4. **Incremental Verification:** Maintaining proofs as code evolves
5. **Verified AI:** Can we prove properties of the AI itself?

### 10.3 Key Insight

**The Contextome is not just documentation. It is the source of truth from which the Codome is derived.**

Formal methods make this derivation **deterministic and verifiable**.

AI makes this derivation **fast and accessible**.

Together, they realize the vision of Spec-Driven Development with mathematical guarantees.

---

## 11. Glossary

| Term | Definition |
|------|------------|
| **Refinement** | Relation ⊑ where S₁ ⊑ S₂ means S₂ meets all requirements of S₁ |
| **Extraction** | Generating executable code from proofs |
| **Dependent Types** | Types that depend on values |
| **SMT Solver** | Satisfiability Modulo Theories - automated logic solver |
| **Model Checking** | Exhaustive state-space exploration |
| **Proof Assistant** | Interactive tool for constructing formal proofs |
| **Certified** | Proven correct with machine-checked proof |
| **Sound** | Never produces false positives (all reported properties hold) |
| **Complete** | Never produces false negatives (all holding properties reported) |

---

## 12. References

### Foundational Texts

1. Morgan, C. (1990). *Programming from Specifications*
2. Back, R-J. & von Wright, J. (1998). *Refinement Calculus*
3. Abrial, J-R. (2010). *Modeling in Event-B*
4. Nipkow, T. et al. (2002). *Isabelle/HOL: A Proof Assistant for Higher-Order Logic*
5. Bertot, Y. & Castéran, P. (2004). *Interactive Theorem Proving and Program Development (Coq)*

### Modern Resources

6. de Moura, L. & Ullrich, S. (2021). *The Lean 4 Theorem Prover*
7. Leino, K.R.M. (2010). *Dafny: An Automatic Program Verifier*
8. Vazou, N. et al. (2014). *Refinement Types for Haskell*
9. Lamport, L. (2002). *Specifying Systems: The TLA+ Language*
10. Jackson, D. (2012). *Software Abstractions: Logic, Language, and Analysis (Alloy)*

### Verified Systems

11. Leroy, X. (2009). *Formal Verification of a Realistic Compiler (CompCert)*
12. Klein, G. et al. (2009). *seL4: Formal Verification of an OS Kernel*
13. Kumar, R. et al. (2014). *CakeML: A Verified Implementation of ML*

---

## Appendix A: Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                DETERMINISTIC CODE SYNTHESIS                      │
│                     Quick Reference                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  REFINEMENT CALCULUS          PROOF ASSISTANTS                   │
│  ────────────────────         ────────────────                   │
│  Morgan's: Laws for           Coq: CompCert, verified crypto     │
│  stepwise refinement          Lean: Mathlib, growing fast        │
│                               Isabelle: Automation, AFP          │
│  B-Method: Railway,           F*: Effects, TLS (Project Everest) │
│  metro, aerospace                                                │
│                                                                  │
│  LIGHTWEIGHT                  INDUSTRIAL                         │
│  ───────────                  ──────────                         │
│  Dafny: Auto-active           SPARK Ada: DO-178C Level A         │
│  Liquid Haskell: Gradual      VDM: Oldest, still relevant        │
│  TLA+: Distributed systems    Alloy: Bounded model checking      │
│                                                                  │
│  THE SMC CONNECTION                                              │
│  ──────────────────                                              │
│  L₁ (Spec/Contextome) ──[Refinement]──> L₀ (Code/Codome)        │
│                                                                  │
│  LOCUS Extension: ⟨λ, Ω, τ, α, R, V⟩                            │
│  V = Verification Level (V₀ unverified → V₅ extracted)          │
│                                                                  │
│  THE FUTURE                                                      │
│  ──────────                                                      │
│  AI generates, Formal verifies, Human specifies                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Appendix B: Tool Installation

```bash
# Lean 4 (recommended for new projects)
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
lake new myproject math

# Coq
brew install coq     # macOS
opam install coq     # via OCaml

# Dafny
brew install dafny   # macOS
dotnet tool install -g Dafny

# Isabelle
brew install --cask isabelle   # macOS

# TLA+
brew install --cask tla-plus-toolbox

# Alloy
brew install --cask alloy
```

---

*This document synthesizes research on deterministic code synthesis methods, connecting classical formal methods with modern AI-assisted development. It serves as a companion to SPEC_DRIVEN_DEVELOPMENT.md, providing the technical foundation for guaranteed-correct code generation.*
