# Research: What is the simplest way for a software system to describe itself using its own theory/ontology? I h...

> **Date:** 2026-01-26 03:21:43
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:a1a4589a8299a96e36e831d16593c84cc3ed3a0ad2cb81cdfb59f4dd043ed441`
> **Raw JSON:** `raw/20260126_032143_what_is_the_simplest_way_for_a_software_system_to.json`

---

## Query

What is the simplest way for a software system to describe itself using its own theory/ontology? I have a codebase analysis tool (like a 'Standard Model of Code') that classifies code into atoms, roles, layers, dimensions. I want this tool to classify ITSELF - true self-reference/dogfooding. What's the minimal architecture for a self-describing system? Looking for: 1) Computer science concepts (reflection, metacircular evaluators, bootstrapping) 2) Practical patterns (how compilers compile themselves, how type systems type themselves) 3) The absolute simplest implementation approach

---

## Response

# Self-Describing Systems: Theory and Practice

Self-describing systems fundamentally require **metacircular evaluation**—where a system uses its own representation language and rules to analyze itself. This is achieved through **reflection** (the ability to inspect and reason about your own structure) combined with **bootstrapping** (using the system's own mechanisms to build itself).

## Core Computer Science Concepts

**Reflection and Introspection** form the foundation. A self-describing system must expose its own structure as data that can be processed by the same analysis rules it applies to external code. In your case, this means your "Standard Model of Code" (atoms, roles, layers, dimensions) must be expressible in the same ontology it uses to classify code. When your tool analyzes itself, it should produce atoms, roles, layers, and dimensions describing its own components.

**Metacircular evaluation** is the formal concept here. A metacircular interpreter is one that is written in the language it interprets—like a Lisp interpreter written in Lisp. For your system, this means your classification tool should be classifiable by itself using identical rules. The tool's source code becomes input to its own analysis engine.

**Bootstrapping** refers to the process of using a minimal version of a system to build more sophisticated versions. Compilers that compile themselves (like GCC compiling C code to compile C) work by first having a basic compiler in place, then using it to compile an improved version. Your minimal approach would start with a hand-coded or external classification of your tool's core, then use that to generate increasingly refined self-descriptions.

## Practical Patterns from Self-Compiling Systems

Compiler self-compilation follows this pattern:
1. Write a compiler in language X using a different tool or language
2. Use that compiler to compile its own source code
3. Verify the output matches expectations (bootstrapping verification)

For type systems, languages like Haskell and Scala demonstrate **type systems typing themselves**: the type checker is itself written in a typed language and must satisfy its own type constraints. This ensures consistency—the tool cannot violate rules it enforces on others.

## Minimal Architecture for Self-Reference

The simplest implementation requires three layers:

**Layer 1 - Base Ontology** (hand-coded initially): Define your atoms, roles, layers, and dimensions in a language-agnostic format (e.g., JSON schema, or abstract syntax). This is your "seed" definition—the bootstrap point.

**Layer 2 - Analysis Engine**: Write the classification logic that takes source code and produces classifications using your ontology. Keep this engine simple and modular.

**Layer 3 - Self-Application**: Point the analysis engine at its own source code. The output is a self-description in your ontology. Crucially, this self-description should match (or improve upon) your initial hand-coded Layer 1 definition.

The absolute minimal approach:

1. **Define your ontology formally** (atoms, roles, layers, dimensions) as structured data
2. **Implement one classifier function** that can parse any source code and map it to your ontology
3. **Run this function on your ontology definition itself** and on the classifier source
4. **Compare output**: The self-generated description should be consistent with your manual understanding
5. **Iterate**: Use the self-generated description to refine the classifier, creating a virtuous cycle

This creates true dogfooding—your tool doesn't just describe code *like* itself, it actually describes its own code using identical mechanisms.

## Implementation Considerations

Start with a single, pure function: `classify(source_code) → description_in_ontology`. This function:
- Takes source as input (whether external code or your own classifier)
- Produces a structured output conforming to your ontology
- Contains no special cases for "self" vs. "other" code

If your classifier can analyze Python and you write it in Python, applying it to itself is trivial. If it's written in a different language, you'll need a parser for that language as well.

The key insight: **avoid dual standards**. Don't have one set of rules for analyzing other code and another for analyzing yourself. Single, unified rules are what make self-description meaningful and testable.

---

## Citations

1. https://arxiv.org/html/2511.05165v1
2. https://www.mirkosertic.de/blog/2021/04/scs-light-and-shadow/
3. https://vfunction.com/blog/what-is-software-architecture/
4. https://dl.acm.org/doi/10.1145/3129790.3129824

---

## Usage Stats

- Prompt tokens: 124
- Completion tokens: 870
- Total tokens: 994
