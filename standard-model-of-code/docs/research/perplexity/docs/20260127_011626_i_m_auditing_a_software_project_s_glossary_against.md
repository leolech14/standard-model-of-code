# Research: I'm auditing a software project's glossary against Domain-Driven Design (DDD) conventions. Here are ...

> **Date:** 2026-01-27 01:16:26
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:0e47c9fe700026fe1c5952108bde23368295b0a9f12be90056a5c29e0886b355`
> **Raw JSON:** `raw/20260127_011626_i_m_auditing_a_software_project_s_glossary_against.json`

---

## Query

I'm auditing a software project's glossary against Domain-Driven Design (DDD) conventions. Here are the key terms we use:

**Physical Organization:**
- REALM (Particle/Wave/Observer) - Directory partitions
- PROJECTOME - The complete set of all files
- CODOME - All executable code
- CONTEXTOME - All non-executable content (docs, configs)

**Semantic Organization:**
- DOMAIN - Vertical functional slice (we're killing this)
- CONCORDANCE - Purpose alignment between code and docs
- BOUNDED CONTEXT - Considering adopting from DDD

**Code Classification:**
- ATOM - Basic code unit type (167 types like Entity, Repository, Service, Factory)
- ROLE - Functional purpose (Controller, Validator, Transformer)
- DIMENSION - Classification axis (Kind, Layer, Lifecycle, State, Effect, Boundary)

**Process:**
- COLLIDER - Static analysis pipeline (physics metaphor)
- WAVE/PARTICLE duality - Planning vs Implementation
- OBSERVER - Decision/governance layer

**Which of these terms conflict with or redefine established DDD/software architecture terminology?**

Specifically:
1. Does 'Entity', 'Repository', 'Service', 'Factory' in our ATOM taxonomy clash with DDD's specific definitions?
2. Is 'Aggregate' a DDD term we should be careful with?
3. Does 'Layer' conflict with DDD's layered architecture?
4. Are there other DDD terms (Value Object, Domain Event, Application Service, etc.) that we might accidentally misuse?

I need to know which terms are SAFE (no DDD meaning), CAUTION (DDD meaning exists but ours is compatible), and DANGER (DDD meaning conflicts with ours).

---

## Response

### Terms from Your Glossary Classified Against DDD

Your project's terms largely use unique nomenclature (e.g., REALM, PROJECTOME, CODOME, CONTEXTOME, CONCORDANCE, ATOM, ROLE, DIMENSION, COLLIDER, WAVE/PARTICLE duality, OBSERVER), which have **no established DDD meanings** and are thus **SAFE** for use without conflict[1][2][3][4][5][6][7][8][9]. 

**DOMAIN** aligns closely with DDD's general concept of a problem space but is explicitly being retired in your project, avoiding any issues[1][2][3].  
**BOUNDED CONTEXT** matches DDD exactly (a boundary delimiting a model's applicability, enabling independent evolution), so if adopting, ensure **CAUTION**—your usage must align precisely to avoid confusion[1][3][5].

#### Specific Questions Answered

1. **ATOM types including 'Entity', 'Repository', 'Service', 'Factory'**: These directly match core DDD **tactical patterns**, where:
   - **Entity**: An object defined by identity and continuity, not just attributes[1][2][3][4].
   - **Repository**: A mechanism to access/save Aggregate Roots, abstracting persistence[1][2].
   - **Service** (Domain Service): Encapsulates domain operations not fitting Entities/Value Objects[2][3].
   - **Factory**: Encapsulates complex object creation[1].
   
   **DANGER** if your ATOM definitions diverge (e.g., if your Entity lacks identity focus or Repository isn't Aggregate-centric), as this redefines DDD building blocks. Limit to DDD-compatible meanings for **CAUTION**[1][2][3][4].

2. **'Aggregate'**: Yes, a key DDD term—an Entity cluster with an Aggregate Root enforcing consistency/transaction boundaries[1][2][3][4]. Not in your listed terms, but **DANGER** if introduced unless matching DDD exactly (e.g., avoid using for general grouping).

3. **'Layer' in DIMENSION**: Conflicts with DDD's **Layered Architecture** (separating concerns, e.g., Domain Layer for model logic, isolating from infrastructure)[1]. Your multi-axis classification (Kind, Layer, etc.) risks confusion. **DANGER** unless "Layer" explicitly mirrors DDD layers; otherwise, rename for safety.

4. **Other DDD terms at risk of misuse**:
   | Term              | DDD Meaning Summary                                                                 | Classification if Used in Your Project |
   |-------------------|-------------------------------------------------------------------------------------|---------------------------------------|
   | **Value Object** | Immutable object defined by attributes (no identity)[1][2][3][4].                  | **DANGER**—ATOM types could clash if not identity-less. |
   | **Domain Event** | Object signaling domain change (e.g., for integration)[1][3].                       | **DANGER**—No overlap now, but future use must match. |
   | **Application Service** | Orchestrates use cases (not pure domain logic; contrasts Domain Service)[2][3].    | **CAUTION**—Distinguishable from your ROLE/Service if prefixed. |
   | **Ubiquitous Language** | Shared domain vocabulary across team/experts[2][3][7][8].                          | **DANGER**—Your CONCORDANCE is similar but distinct; avoid if expanding. |

#### Recommendations
- **SAFE** terms dominate your glossary, preserving uniqueness.
- For **CAUTION/DANGER** items, audit definitions against DDD (e.g., via Evans' book[1][6]) or prefix (e.g., "OurAtomEntity") to namespace.
- No conflicts in physics-themed terms (COLLIDER, etc.), as DDD focuses on domain modeling, not processes[1][2][3][4].

---

## Citations

1. https://www.dddcommunity.org/resources/ddd_terms/
2. https://learn.microsoft.com/en-us/archive/msdn-magazine/2009/february/best-practice-an-introduction-to-domain-driven-design
3. https://domain-driven-software.com/an-introduction-to-domain-driven-design-ddd-1025bce518c2
4. https://martinfowler.com/bliki/DomainDrivenDesign.html
5. https://www.fabrizioduroni.it/blog/post/2021/06/06/ddd-dictionary
6. https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf
7. https://www.rst.software/blog/introduction-to-domain-driven-design-ddd-glossary
8. https://gist.github.com/marc0der/48a768e874a29950cdf5a4a0dd32fed6
9. https://bytebytego.com/guides/key-terms-in-domain-driven-design/

---

## Usage Stats

- Prompt tokens: 353
- Completion tokens: 816
- Total tokens: 1169
