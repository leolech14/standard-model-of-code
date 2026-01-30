# Research: Tarski hierarchy meta-language levels L0 L1 L2 object language formal definition how many levels

> **Date:** 2026-01-29 19:06:31
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:60e4cdbd536023359c787aa6641d909839279484b51b1176dd92810d62846947`
> **Raw JSON:** `raw/20260129_190631_tarski_hierarchy_meta_language_levels_l0_l1_l2_obj.json`

---

## Query

Tarski hierarchy meta-language levels L0 L1 L2 object language formal definition how many levels

---

## Response

Tarski's hierarchy of languages distinguishes the **object language** (where sentences are stated) from successively higher **meta-languages** (used to define semantic concepts like truth for the language below), preventing self-reference paradoxes such as the liar paradox[1][2][5].

### Formal Definition
Tarski's construction places languages in a stratified hierarchy:
- Let **L₀** be the base **object language** (a formal language whose syntax and semantics we aim to analyze, e.g., a first-order language with logical constants, variables, nonlogical predicates, and quantifiers interpreted over a structure)[2].
- **L₁** is the meta-language for L₀: it extends L₀ with additional notation (e.g., a truth predicate **Tr₁**) to define satisfaction or truth for sentences of L₀ via Tarski's **Convention T** (a sentence φ of L₀ is true in the structure iff pφp, where pφp is its structural-descriptive name in L₁)[1][2][5].
- **L₂** is the meta-language for L₁: it extends L₁ with a new truth predicate **Tr₂** to define truth for sentences of L₁ (including those expressing truth for L₀)[1][5].
- In general, **L_{n+1}** is the meta-language for **L_n**, containing a truth predicate **Tr_{n+1}** defining truth for **L_n** sentences compositionally (via recursive clauses for connectives, quantifiers, etc., grounded in atomic satisfaction)[2].

This yields an infinite ascending hierarchy **L₀ ⊂ L₁ ⊂ L₂ ⊂ ...**, where each level semantically characterizes the one below but cannot define its own truth (per Tarski's undefinability theorem: truth for L_n is not definable in L_n itself)[1][5].

### Number of Levels
The hierarchy has **infinitely many levels** (L₀, L₁, L₂, ..., continuing indefinitely), as no finite level suffices for self-representation in sufficiently expressive languages[1][3][5]. Tarski showed truth definitions exist for each L_n in L_{n+1}, but the full hierarchy avoids collapse[2]. Some expositions mention finite initial segments (e.g., up to L₂ for illustration), but the structure is transfinite[4].

---

## Citations

1. https://en.wikipedia.org/wiki/Tarski's_undefinability_theorem
2. https://plato.stanford.edu/entries/tarski-truth/
3. https://philarchive.org/archive/HORTLO-19
4. https://www.jstor.org/stable/20012662
5. http://philosophyfaculty.ucsd.edu/faculty/gsher/TLTS.pdf
6. https://academic.oup.com/book/32548/chapter/270316719
7. https://dingo.sbs.arizona.edu/~hharley/courses/522/522/MPPLecture4.html

---

## Usage Stats

- Prompt tokens: 20
- Completion tokens: 494
- Total tokens: 514
