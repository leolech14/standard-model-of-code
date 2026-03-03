# THEORY WINS - The 13 Ideas That Define SMoC

> Each idea in a paragraph. No proofs. No math beyond what clarifies. The big picture.

---

## 1. The MECE Partition

Every file in a software project is either **executable** (Codome) or **non-executable** (Contextome). Never both, never neither. This is the foundational axiom: `P = C ⊔ X`. The Codome is what runs. The Contextome is what informs. Together they form the Projectome -- the complete universe of a project.

This isn't just tidiness. It establishes that code and documentation are **dual aspects of a single system**, not separate concerns. You can't understand software by looking at code alone any more than you can understand biology by studying only DNA.

---

## 2. The 16-Level Holarchy

Code organizes into 16 levels from BIT (L-3) to UNIVERSE (L12), grouped in 5 zones: Physical, Syntactic, Semantic, Systemic, Cosmological. Each level is simultaneously a **whole** (containing parts below) and a **part** (contained by levels above). This is Koestler's Janus-faced holon.

The key insight: **emergence happens at every level transition**. A file's purpose isn't the sum of its functions' purposes -- it's something qualitatively new. The Collider operates at L3-L7 (function to system), which is where architectural decisions live.

---

## 3. Deterministic Classification

Code structure reveals its purpose **without AI**. Three signals provide 100% coverage:

- **Topology**: `/services/UserService.py` reveals the role from the path
- **Frameworks**: `@Controller` decorator reveals the role from metadata
- **Genealogy**: `extends Repository` reveals the role from inheritance

This was the pivotal discovery (Dec 23, 2025). LLMs are optional for structural classification. Heuristic pattern matching on naming, decorators, and inheritance achieves 100% atom assignment across 91 tested repositories with zero unknowns.

---

## 4. Eight-Dimensional Classification

Every code element can be classified along 8 independent dimensions:

| Dim | Question |
|-----|----------|
| WHAT | What type? (Atom) |
| LAYER | Where in architecture? (Domain, Application, Infrastructure, UI) |
| ROLE | What purpose? (33 canonical roles) |
| BOUNDARY | Internal or external? |
| STATE | Stateless or stateful? |
| EFFECT | Pure or impure? |
| LIFECYCLE | Init, active, or dispose? |
| TRUST | How confident is the classification? (0-100%) |

These dimensions are designed to be orthogonal. Knowing a function is a "Service" (ROLE) doesn't tell you whether it's stateless (STATE) or external-facing (BOUNDARY). The total semantic space: 94 atoms x 29 roles x 6,561 RPBL states = ~18M possible classifications.

---

## 5. Purpose Is Relational

A function's purpose doesn't come from its source code alone. Purpose is **relational** -- it emerges from how the function participates in a larger structure. A `hash()` function has different purpose in a security module vs a cache module. The code is identical; the purpose differs because context differs.

This is formalized as a **purpose field**: a vector field over the dependency graph where each node's purpose vector points toward the system-level goal it serves. Purpose is not a label you assign -- it's a position in a field you measure.

---

## 6. Purpose Hierarchy (Emergence)

Purpose aggregates upward through 4 levels:

| Level | Name | How Determined |
|-------|------|----------------|
| π1 | Atomic | Role of a single function |
| π2 | Molecular | Emerges from a class's methods |
| π3 | Organelle | Emerges from a package's classes |
| π4 | System | Emerges from a file/module's packages |

Critically, each level **genuinely emerges** from the one below. A class's purpose isn't just the average of its methods' purposes -- when methods combine, new capability appears. This follows Tononi's Integrated Information Theory: the whole has more integrated information than the parts.

---

## 7. Crystallization and Drift

Code **crystallizes** human intent at commit time. Between commits, the developer's understanding evolves while the code stays frozen. This gap is **purpose drift**: `delta = intent_human(t) - intent_code(t_commit)`.

Technical debt is the integral of drift over time. Small drifts are normal. Large accumulated drift means the code no longer represents what the team thinks it does. This reframes refactoring: it's not "cleanup" -- it's **re-crystallizing** updated intent.

---

## 8. Concordance Health

A concordance is a purpose-aligned region spanning both code and documentation. For example, the "Pipeline" concordance includes `full_analysis.py` (Codome) and `PIPELINE_STAGES.md` (Contextome). Four health states:

- **CONCORDANT**: Code and docs agree on purpose. Healthy.
- **UNVOICED**: Code exists without matching documentation. The traditional orphan.
- **UNREALIZED**: Documentation exists without matching code. A spec not yet built.
- **DISCORDANT**: Both exist but state contradictory purposes. The most dangerous state.

This extends the "orphan" concept from individual nodes to entire regions. A subsystem can be concordant even if individual functions lack docstrings.

---

## 9. Three Realms

The project is partitioned into three realms (directories):

- **PARTICLE** (`particle/`): The body. Deterministic measurement. The Collider engine lives here.
- **WAVE** (`wave/`): The brain. Probabilistic reasoning. AI tools and context management.
- **OBSERVER** (`.agent/`): Governance. Decides what to measure and what to do about it.

This maps to quantum mechanics' observation paradox: measurement (Particle) collapses potential (Wave) based on intent (Observer). It's a metaphor, not physics, but it creates clean separation of concerns.

---

## 10. Antimatter Patterns

Seven canonical violations where code contradicts architectural intent:

| ID | Pattern | Example |
|----|---------|---------|
| AM001 | Domain depends on infrastructure | Entity imports PostgresAdapter |
| AM002 | UI accesses domain directly | Component calls repository |
| AM003 | Test code in production | Test utils in main bundle |
| AM004 | Circular dependencies | A→B→C→A |
| AM005 | God class | Class with 20+ methods spanning roles |
| AM006 | Feature envy | Method primarily uses another class's data |
| AM007 | Scattered purpose | Class methods serve unrelated roles |

These are detected automatically by analyzing role-layer-boundary combinations in the dependency graph. They're called "antimatter" because they annihilate architectural intent on contact.

---

## 11. The Orphan Taxonomy

"Orphan" (zero in-degree, zero out-degree) is a **misclassification bucket** conflating 7 distinct phenomena. Only ~9% of orphans are truly dead code:

| Type | Example | Action |
|------|---------|--------|
| Test entry | Called by pytest/jest | OK |
| Entry point | `__main__`, CLI handler | OK |
| Framework-managed | Dataclass, DI container | OK |
| Cross-language | Python called from JS | CHECK |
| External boundary | Public API | CHECK |
| Dynamic target | Called via reflection | CHECK |
| Unreachable | True dead code | DELETE |

This means most "dead code" alerts are false positives. The disconnection taxonomy turns a boolean label into a rich classification.

---

## 12. Consumer Classes and Stone Tools

Three types of consumers interact with code analysis output:

- **END_USER**: Needs usability. Sees dashboards and summaries.
- **DEVELOPER**: Needs clarity. Reads code and structured reports.
- **AI_AGENT**: Needs parseability. Consumes JSON, YAML, structured data.

The **Stone Tool Principle**: tools MAY be designed that humans cannot directly use. AI mediates. The `unified_analysis.json` output (5,000+ lines of structured graph data) is a "stone tool" -- useful only through AI interpretation. This is a valid design choice, not a limitation.

---

## 13. Constructal Flow

Code is a conduit for four types of flow (inspired by Bejan's Constructal Law):

| Flow | Substance | Example |
|------|-----------|---------|
| Static | Data dependencies | Import chains, type hierarchies |
| Runtime | Control flow | Function calls, event propagation |
| Change | Development effort | Git history, commit frequency |
| Human | Attention and understanding | Reading paths, documentation flow |

Good architecture minimizes resistance to all four flows simultaneously. A refactoring that improves runtime flow but makes the code harder for humans to read may not be a net win.

---

## WHERE THESE IDEAS LIVE

| Idea | Formal Source |
|------|---------------|
| 1. MECE Partition | L0_AXIOMS.md, Axiom A1 |
| 2. 16-Level Holarchy | L1_DEFINITIONS.md, Section 2 |
| 3. Deterministic Classification | MODEL.md, Section 6 (History) |
| 4. Eight Dimensions | L1_DEFINITIONS.md, Section 4 |
| 5. Purpose Is Relational | L0_AXIOMS.md, Axioms D1-D7 |
| 6. Purpose Hierarchy | L2_PRINCIPLES.md, Section 1 |
| 7. Crystallization & Drift | L0_AXIOMS.md, Axiom D6 |
| 8. Concordance Health | L2_PRINCIPLES.md, Section 4 |
| 9. Three Realms | L1_DEFINITIONS.md, Section 0 |
| 10. Antimatter | L2_PRINCIPLES.md, Section 5 |
| 11. Orphan Taxonomy | MODEL.md, Section 3 |
| 12. Consumer Classes | L0_AXIOMS.md, Axioms H1-H5 |
| 13. Constructal Flow | L0_AXIOMS.md, Axioms E1-E2 |

---

*Distilled from ~3,000 lines of theory (L0-L2 + MODEL.md)*
*This file: ~200 lines, 13 ideas, zero proofs*
