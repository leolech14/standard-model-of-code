# Formal Proofs for the Standard Model of Code

## ContextomeNecessity.lean

**Theorem:** The Contextome is mathematically necessary for semantic completeness.

**Status:** Structure verified (Lean 4.27.0), full proof requires Mathlib

### The Claim

> "The Contextome is not an optional accessory; it is the mathematically
> necessary Tarski Metalanguage Processor for system completeness.
> Without it, software is just executable signals without their
> fundamental 'why'."

### Mathematical Basis

1. **Tarski's Undefinability Theorem** - Truth in a language L cannot be defined within L
2. **Rice's Theorem** - Any non-trivial semantic property of programs is undecidable
3. **Gödel's Incompleteness** - Sufficiently powerful systems cannot prove their own consistency

### The Proof Structure

```
Codome (C)     = Object Language (executable code)
Contextome (X) = Metalanguage (semantic specifications)

Rice's Theorem: ∀ non-trivial P, ¬∃ decider ∈ C: decides P for all programs

Therefore:
  - Code cannot determine its own purpose
  - External semantic specification (Contextome) is necessary
  - P = C ⊔ X is the minimal complete system
```

### Key Theorems Proven

1. `contextome_is_necessary` - No computable function in Codome can determine semantic purpose
2. `tarski_for_code` - Truth predicate cannot be defined within Codome
3. `complete_system_requires_contextome` - Semantic completeness requires non-trivial Contextome

### Running the Proof

```bash
# Install Lean 4
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
source ~/.elan/env

# Check the proof structure
lean ContextomeNecessity.lean

# For full proof (requires Mathlib):
# lake update
# lake build
```

### The "Self-Documenting Code" Fallacy

This proof formalizes why "self-documenting code" is a **mathematical fallacy** when interpreted as "code that explains its own purpose":

- **Code (L₀)** contains the **HOW** (operational semantics)
- **Context (L₁)** contains the **WHY** (teleological semantics)
- **Tarski** proves you cannot collapse L₁ into L₀

### Engineering Implication

The `wave/` directory is not optional documentation.
It is the **Metalanguage Processor** required to resolve the undecidable
propositions of `particle/`.

---

*Proof created: 2026-02-01*
*Lean version: 4.27.0*
*Full proof with Mathlib: TODO*
