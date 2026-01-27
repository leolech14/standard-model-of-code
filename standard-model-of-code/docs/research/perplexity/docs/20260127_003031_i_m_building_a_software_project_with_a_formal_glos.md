# Research: I'm building a software project with a formal glossary for AI agents and human developers. We have a...

> **Date:** 2026-01-27 00:30:31
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:98dfa0bb6e713989a9e5c16a46141de18893a4a554c6ce7b12ceda48a776fe71`
> **Raw JSON:** `raw/20260127_003031_i_m_building_a_software_project_with_a_formal_glos.json`

---

## Query

I'm building a software project with a formal glossary for AI agents and human developers. We have a terminology problem with three overlapping concepts:

1. REALM - Physical directory partition (like packages/modules). Files belong to exactly ONE realm. Works well.

2. DOMAIN - Originally defined mathematically as 'vertical functional slice across codebase'. Properties:
   - Should contain both code AND documentation
   - Can OVERLAP (mathematical 'cover' not 'partition')
   - But in practice: all domains are contained within single realms (no cross-cutting)
   - One domain (Theory) has docs but NO code, violating its own definition
   - Term marked deprecated in one file, still used in main glossary

3. CONCORDANCE - Proposed replacement emphasizing PURPOSE ALIGNMENT between code and docs, with measurable similarity score.

In software architecture and Domain-Driven Design literature:
- How is 'domain' typically defined?
- Is there precedent for separating physical organization (realm/module) from semantic organization (domain/bounded context)?
- When terminology conflicts arise in technical glossaries, what's the recommended resolution approach?
- Is 'concordance' a standard term or would it confuse developers familiar with DDD?

I need to pick ONE clear approach. What do software architecture experts recommend?

---

## Response

**In Domain-Driven Design (DDD) literature, "domain" refers to the specific business problem area or subject matter (e.g., banking with accounts and transactions) that software models, distinct from physical code organization.[1][3][5]**

### Standard Definition of "Domain" in DDD and Software Architecture
DDD defines **domain** as the core subject area or problem space the software addresses, modeled through collaboration with domain experts to create a domain model reflecting business concepts, entities, and rules. This emphasizes a **ubiquitous language** shared by developers, experts, and stakeholders, ensuring code aligns semantically with business needs.[1][2][3] It is not a physical structure but a conceptual one, often partitioned into **bounded contexts**—logical boundaries where a specific model and language apply consistently, allowing independent evolution and reducing overlap confusion.[1][2][3]

### Precedent for Separating Physical Organization (e.g., Realm/Module) from Semantic Organization (e.g., Domain/Bounded Context)
Yes, DDD explicitly separates these: physical structures like directories, packages, or modules organize code files (your **REALM**), while **domains** and **bounded contexts** provide semantic partitioning across the codebase. Bounded contexts act as "vertical slices" with their own models, enabling overlap via **context mapping** (e.g., shared kernels or partnerships) without requiring physical co-location. This aligns with your DOMAIN properties (overlapping cover, functional slices), but DDD prioritizes semantic alignment over strict physical containment.[1][2][3]

### Resolving Terminology Conflicts in Technical Glossaries
DDD experts recommend establishing a **ubiquitous language** as the primary resolution: collaboratively define terms with stakeholders, deprecate inconsistent usages, and enforce consistency through the domain model and documentation. When conflicts arise (e.g., deprecated terms or violations like your Theory domain lacking code), audit against business intent, partition into bounded contexts to isolate ambiguities, and iterate via domain expert feedback. Mark deprecated terms clearly and migrate to precise alternatives.[1][2]

### "Concordance" as a Term
**Concordance** is not a standard DDD or software architecture term; it typically means textual agreement or indexing (e.g., Bible concordances) and risks confusion for DDD-familiar developers, who associate similar ideas with ubiquitous language or context alignment rather than measurable similarity scores.[1][2][3]

### Recommended Approach: Pick Bounded Context from DDD
Adopt **bounded context** as your single clear term for semantic organization (replacing DOMAIN and CONCORDANCE). It directly matches your needs—overlapping functional slices with code/docs alignment, measurable via ubiquitous language consistency—while distinguishing from physical **REALM** partitions. Deprecate DOMAIN globally, audit exceptions (e.g., Theory as a documentation-only context), and define in your glossary:

| Term          | Type          | Definition                                                                 | Key Properties                  |
|---------------|---------------|----------------------------------------------------------------------------|---------------------------------|
| **Realm**    | Physical     | Directory/module partition; files belong to exactly one.                   | Non-overlapping, file-centric. |
| **Bounded Context** | Semantic | Functional slice across code/docs with aligned purpose/language.          | Overlapping OK; ubiquitous language; context mapping for integration.[1][2][3] |

This follows DDD best practices for clarity, scalability, and expert consensus, avoiding reinvention.[1][2][3]

---

## Citations

1. https://en.wikipedia.org/wiki/Domain-driven_design
2. https://redis.io/glossary/domain-driven-design-ddd/
3. https://www.geeksforgeeks.org/system-design/domain-driven-design-ddd/
4. https://learn.microsoft.com/en-us/archive/msdn-magazine/2009/february/best-practice-an-introduction-to-domain-driven-design
5. https://sensiolabs.com/blog/2024/understanding-domain-driven-design
6. https://martinfowler.com/bliki/DomainDrivenDesign.html

---

## Usage Stats

- Prompt tokens: 264
- Completion tokens: 713
- Total tokens: 977
