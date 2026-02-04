# Overclaiming Language Audit - Input for Cerebras Validation

## Context
We are reframing the Standard Model of Code documentation from "scientific discovery" language to "practical tool / reference model" language. The key principle is: SMC is NOT claiming to discover universal laws, it's proposing a reference model that makes code structure machine-actionable for AI agents.

## Language Guidelines (from PAPER_FRAMING.md)

### MUST AVOID (Overclaiming):
- "We discovered..." → Use "We propose..."
- "We proved..." → Use "We show evidence..."
- "Universal law" → Use "Behavioral pattern"
- "Fundamental truth" → Use "Useful abstraction"
- "VALIDATED" (for our claims) → Use "GROUNDED" or "AI-REVIEWED"
- "PROOF" (for our arguments) → Use "ARGUMENT" or "MOTIVATION"
- "Laws of Code" → Use "Principles of Code"
- "Natural Laws" → Use "Behavioral Patterns"

### OK TO KEEP:
- References to external mathematical work (Lawvere's theorem, Gödel's theorem)
- References to external frameworks (Bejan's Constructal Law, Lehman's Laws)
- "proof" when referring to mathematical proofs in Lean 4 verification
- "validated" when referring to empirical testing (e.g., "tested on 91 repos")
- Theorem Candidates clearly marked as "conjectures"

## Files to Audit

### Priority 1 - Core Theory (CRITICAL)
1. particle/docs/theory/L0_AXIOMS.md
2. particle/docs/theory/L1_DEFINITIONS.md
3. particle/docs/theory/L2_PRINCIPLES.md
4. particle/docs/theory/L3_APPLICATIONS.md
5. particle/docs/theory/THEORY_INDEX.md

### Priority 2 - Complete Documents
6. particle/docs/theory/STANDARD_MODEL_THEORY_COMPLETE.md
7. particle/docs/theory/THEORY_COMPLETE_ALL.md
8. particle/docs/theory/THEORY_AXIOMS.md

### Priority 3 - Supporting Theory
9. particle/docs/theory/PHILOSOPHICAL_FOUNDATIONS.md
10. particle/docs/theory/EPISTEMOLOGICAL_STATUS.md
11. particle/docs/theory/SCOPE_LIMITATIONS.md
12. particle/docs/theory/EMPIRICAL_VALIDATION.md
13. particle/docs/theory/COMPLETE_THEORY_READING_GUIDE.md

## Issues Found (from grep scan)

### Category A: "VALIDATED" status labels that may need softening
- L1_DEFINITIONS.md:34 - "Status: VALIDATED"
- L1_DEFINITIONS.md:628 - "Validated 2026-01-31"
- L1_DEFINITIONS.md:688 - "Status: Validated"
- STANDARD_MODEL_THEORY_COMPLETE.md:37 - "L0 | VALIDATED"
- THEORY_COMPLETE_ALL.md:11 - "Status: VALIDATED"
- THEORY_COMPLETE_ALL.md:60 - "Status: VALIDATED"
- THEORY_COMPLETE_ALL.md:866-873 - Multiple "✅ VALIDATED" in table

### Category B: "proof" when referring to our arguments
- STANDARD_MODEL_THEORY_COMPLETE.md:402 - "PROOF (via Lawvere's...)"
- THEORY_COMPLETE_ALL.md:115 - "PROOF (via Lawvere's...)"
- Multiple "Lawvere proof" references (need to verify: is this citing external work or our application?)

### Category C: "validated" claims about our theories
- STANDARD_MODEL_THEORY_COMPLETE.md:77 - "Most validated theory"
- STANDARD_MODEL_THEORY_COMPLETE.md:118 - "validated laws"
- STANDARD_MODEL_THEORY_COMPLETE.md:358 - "has been validated"
- THEORY_COMPLETE_ALL.md:25-28 - "[95% validated]", "[78% validated]", "[75% validated]"

### Category D: Remaining "PARTIALLY VALIDATED" labels
- THEORY_COMPLETE_ALL.md:851 - "⚠️ PARTIALLY VALIDATED"

## Task for Cerebras

For each file listed above:
1. Identify ALL remaining instances of overclaiming language
2. Classify each instance as:
   - MUST_FIX: Our claim using overclaiming language
   - OK_EXTERNAL: Reference to external academic work (keep as-is)
   - OK_EMPIRICAL: Reference to actual empirical testing (keep as-is)
   - REVIEW: Ambiguous - needs human decision
3. Suggest specific replacement text for MUST_FIX items
4. Output a structured report with file:line:category:suggestion format
