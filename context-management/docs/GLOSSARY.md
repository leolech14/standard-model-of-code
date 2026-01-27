# GLOSSARY - PROJECT_elements

> **Status:** ACTIVE
> **Version:** 2.0.0
> **Created:** 2026-01-25
> **Purpose:** Definitive terminology reference for humans and AI agents
> **RFC 2119:** Terms MUST, SHOULD, MAY have normative meaning

---

## NAVIGATION MAP

```
PROJECT_elements/
│
├── .agent/ ─────────────────────► OBSERVER (decides what to measure)
│   ├── registry/                   Tasks, schemas, state
│   ├── specs/                      Governance definitions
│   └── intelligence/               AI outputs
│
├── standard-model-of-code/ ─────► PARTICLE (collapsed reality)
│   ├── src/core/                   Collider pipeline
│   ├── docs/                       Theory (MODEL.md)
│   └── tools/                      Laboratory, utilities
│
└── context-management/ ──────────► WAVE (field of potential)
    ├── docs/                       This glossary, topology
    ├── tools/ai/                   analyze.py, ACI
    └── config/                     Semantic models
```

---

## THE ALGEBRA

```
UNIVERSES (Partition)
──────────────────────────────────────────────────────────
P = C ⊔ X           PROJECTOME = CODOME ⊔ CONTEXTOME
C ∩ X = ∅           Disjoint (no overlap)
X = P \ C           CONTEXTOME = PROJECTOME minus CODOME

REALMS (Partition)
──────────────────────────────────────────────────────────
P = Particle ⊔ Wave ⊔ Observer
    (directories are mutually exclusive)

CONCORDANCES (Cover)
──────────────────────────────────────────────────────────
⋃ Cᵢ = P            Concordances cover everything
Cᵢ ∩ Cⱼ ≠ ∅         Overlap allowed (a file can serve multiple purposes)
κ(Cᵢ) → [0,1]       Each concordance has an alignment score

CLASSIFICATION (Function)
──────────────────────────────────────────────────────────
σ: Nodes → Atoms    Every node MUST map to exactly one atom

SYMMETRY (Relation)
──────────────────────────────────────────────────────────
R ⊆ C × X × S       Code × Docs × State
S = {SYMMETRIC, ORPHAN, PHANTOM, DRIFT}
```

---

## THE LOOP OF TRUTH

```
[CODEBASE]
    │
    │ (1. Scan)
    ▼
[COLLIDER] ───────► unified_analysis.json (Ground Truth)
                              │
                              ▼
[HSL / analyze.py] ◄──────────┘
    │
    │ (2. Validate)
    ▼
[TASK REGISTRY] ◄─── (3. Claim) ─── [BARE / AGENT]
                                          │
[CODEBASE] ◄──────── (4. Commit) ─────────┘
```

---

## CORE TERMS

### Universes

| Term | Definition |
|------|------------|
| **PROJECTOME** | The complete set of all files in the project. P = C ⊔ X. The universe. |
| **CODOME** | All executable code (.py, .js, .ts, .go, .rs, .css, .html). What runs. |
| **CONTEXTOME** | All non-executable content (.md, .yaml, .json configs). What informs. |

### Realms

| Term | Path | Definition |
|------|------|------------|
| **PARTICLE** | `standard-model-of-code/` | The collapsed reality. Measurement. Implementation. The Collider lives here. |
| **WAVE** | `context-management/` | The field of potential. Context. AI tools. Planning happens here. |
| **OBSERVER** | `.agent/` | The decision layer. Chooses what to measure. Tasks and governance live here. |

### Phase States

| Phase | Symbol | Definition | Example |
|-------|--------|------------|---------|
| **MODULE** | 1st-order | WHAT runs. Pure capability logic. Takes input, gives output. | `analyze.py`, Collider |
| **AUTOMATION** | 2nd-order | WHEN it runs. Policy/triggers. Liquid phase - decides at runtime. | `autopilot.py`, `drift_guard.py` |
| **INFRASTRUCTURE** | 0th-order | WHERE it exists. Solid phase - frozen automation decisions. | `Dockerfile`, `cloud_run_job.yaml` |
| **CONFIG** | Slush | Parameters governing behavior. Semi-frozen. Tunable. | `aci_config.yaml` |

**Phase Transition Model:**
```
Automation (Liquid) --[Build/Deploy]--> Infrastructure (Solid)
```

**Realms × Phases Matrix:**

| Realm | Allowed Phases | Nature |
|-------|----------------|--------|
| **PARTICLE** | MODULE + CONFIG(frozen) | Deterministic |
| **WAVE** | MODULE + CONFIG(liquid) | Probabilistic |
| **OBSERVER** | AUTOMATION + INFRASTRUCTURE | Teleological |

### Concordances

| Term | Definition |
|------|------------|
| **CONCORDANCE** | A semantic grouping with measured purpose alignment between code and docs. Score ∈ [0,1]. |
| **Pipeline** | Concordance: Collider stages, analysis logic. Code in `src/core/`, docs in `docs/specs/`. |
| **Visualization** | Concordance: 3D graph rendering. Code in `viz/assets/`, docs in UI specs. |
| **Governance** | Concordance: Task registry, confidence scoring. Code in `.agent/tools/`, docs in `.agent/specs/`. |
| **AI Tools** | Concordance: analyze.py, ACI, research. Code in `tools/ai/`, docs in `config/`. |

---

## SUBSYSTEMS

| ID | Name | Type | Definition |
|----|------|------|------------|
| S1 | **Collider** | Engine | Static analysis pipeline. Parses code → extracts nodes → classifies atoms → builds graph. Outputs `unified_analysis.json`. |
| S2 | **HSL** | Framework | Holographic Socratic Layer. The conceptual validation rules. Detects drift between docs and code. |
| S3 | **analyze.py** | Tool | The implementation of HSL. Runs queries against the codebase with AI. `--verify` mode enforces rules. |
| S4 | **ACI** | System | Adaptive Context Intelligence. 5-tier query routing based on complexity. |
| S5 | **BARE** | Engine | Background Auto-Refinement Engine. Claims tasks, generates fixes, commits changes. The "hands" of the system. |
| S6 | **Laboratory** | Bridge | Research API connecting Wave (AI) to Particle (Collider). Runs experiments programmatically. |
| S7 | **Registry** | State | Task tracking system. Tasks are persistent, Runs are ephemeral. |
| S13 | **Macro Registry** | State | Recorded action patterns for automation. "If you do it twice manually, record it as a macro." |

---

## MACROS (Recorded Patterns)

| Term | Definition |
|------|------------|
| **Macro** | A recorded action pattern that can be auto-executed on triggers. Schema in `.agent/macros/schema/`. |
| **Trigger** | What causes a macro to execute: manual, schedule, event, file_change, post_commit. |
| **CARD-AUD-001** | Decision Deck card for invoking the Skeptical Audit (MACRO-001). |
| **Skeptical Audit** | MACRO-001. Systematic self-criticism to find dead code, integration failures, validation theater. |

**Principle:** If you do it twice manually, record it as a macro.

**Index:** `.agent/macros/INDEX.md`

---

## CLASSIFICATION

### Atoms

| Term | Definition |
|------|------------|
| **Atom** | A semantic category assigned to a code node. 3,616 total across tiers. |
| **Tier 0** | Core AST atoms (42). Definitional. 100% coverage. |
| **Tier 1** | Standard library patterns (21). 20-40% coverage. |
| **Tier 2** | Ecosystem-specific (3,531). Variable coverage. |

### Roles (33 Canonical)

| Category | Roles | Count |
|----------|-------|-------|
| Query | Query, Finder, Loader, Getter | 4 |
| Command | Command, Creator, Mutator, Destroyer | 4 |
| Factory | Factory, Builder | 2 |
| Storage | Repository, Store, Cache | 3 |
| Orchestration | Service, Controller, Manager, Orchestrator | 4 |
| Validation | Validator, Guard, Asserter | 3 |
| Transform | Transformer, Mapper, Serializer, Parser | 4 |
| Event | Handler, Listener, Subscriber, Emitter | 4 |
| Utility | Utility, Formatter, Helper | 3 |
| Internal | Internal, Lifecycle | 2 |
| **Total** | | **33** |

> Note: "Unknown" is a fallback label, not a canonical role.

---

## SYMMETRY STATES

| State | Code | Docs | Human Memory | Definition |
|-------|------|------|--------------|------------|
| **SYMMETRIC** | ✓ | ✓ | ✓ | Code, docs, and understanding aligned. Healthy. |
| **ORPHAN** | ✓ | ✗ | ? | Code exists without documentation. Traditional tech debt. |
| **PHANTOM** | ✗ | ✓ | ? | Documentation exists without implementation. Spec not built. |
| **DRIFT** | ✓ | ✓ | ? | Both exist but disagree. Dangerous. |
| **AMNESIAC** | ✓ | ✓ | ✗ | Code and session logs exist, but human has no structural memory. AI-assisted failure mode. |

---

## CONSUMER CLASSES (Axiom Group H)

| Consumer | Interface | Needs | Operates At |
|----------|-----------|-------|-------------|
| **END_USER** | GUI, voice | Usability | Output only |
| **DEVELOPER** | Code, CLI | Clarity | L₀, L₁, L₂ |
| **AI_AGENT** | Structured data | Parseability | L₀, L₁, L₂ (universal) |

**Stone Tool Principle (Axiom H4):** Tools MAY be designed that humans cannot directly use. AI mediates.

**Stone Tool Test:** "Can a human use this tool directly, without AI mediation?" If NO → AI-native tool (valid design).

**TOOL_UNIVERSE:** Complete tool taxonomy:
- **TOOLOME** (Development Tools): Shape the CODOME. Human-usable. (formatters, linters)
- **STONE_TOOLS** (Analysis Tools): Observe the CODOME. AI-native. (unified_analysis.json, POM YAML)

**Collaboration Level:** Human-AI collaboration occurs at L₁ (CONTEXTOME). Programming = CONTEXTOME curation.

**See:**
- `docs/specs/AI_CONSUMER_CLASS.md` (Stone Tool full spec)
- `docs/deep/THEORY_AMENDMENT_2026-01.md` (TOOLOME integration)

---

## OPERATIONAL PROTOCOL

### Work Units

| Term | Persistence | Definition |
|------|-------------|------------|
| **Task** | Persistent | Strategic unit. Survives sessions. What SHOULD be true. Stored in registry. |
| **Run** | Ephemeral | Tactical unit. Dies with session. What IS happening now. |

### Confidence

| Term | Definition |
|------|------------|
| **4D Confidence** | `min(Factual, Alignment, Current, Onwards)`. All four dimensions MUST score. |
| **Factual** | Does this match reality? Evidence-based. |
| **Alignment** | Does this serve the project mission? |
| **Current** | Is this up to date? |
| **Onwards** | Does this enable future work? |

### Artifacts

| Term | Definition |
|------|------------|
| **unified_analysis.json** | The canonical output of Collider. Single source of truth for code state. |
| **Ground Truth** | Data verified by Collider. Confidence 100%. |
| **Inference** | Data derived by AI. Confidence < 100%. |

---

## FOUNDATIONAL STRUCTURES

### Three Planes

| Plane | Substance | Question |
|-------|-----------|----------|
| **Physical** | Bits, bytes, files | Where is it stored? |
| **Virtual** | AST, runtime objects | What is its form? |
| **Semantic** | Meaning, intent | What does it mean? |

### 16-Level Scale

| Zone | Levels | Description |
|------|--------|-------------|
| Cosmological | L8-L12 | Universe → Domain → Org → Platform → Ecosystem |
| Systemic | L4-L7 | System → Package → File → Container |
| Semantic | L1-L3 | Node → Block → Statement |
| Syntactic/Physical | L-3-L0 | Token → Character → Byte → Bit |

**Operational Zone:** L3-L7 (Node to System). This is where Collider classifies.

### 8 Dimensions

| Dimension | Question |
|-----------|----------|
| WHAT | What type? (Atom) |
| LAYER | Where in architecture? |
| ROLE | What purpose? |
| BOUNDARY | Crosses boundaries? |
| STATE | Maintains state? |
| EFFECT | Side effects? |
| LIFECYCLE | What phase? |
| TRUST | How confident? |

---

## CONCEPT/OBJECT DUALITY

```
LEVEL           CONCEPT (Definition)        OBJECT (Instance)
─────────────   ────────────────────────    ─────────────────────
Work Mgmt       task.schema.yaml        ──► TASK-001.yaml
Execution       run.schema.yaml         ──► RUN-20260125-CLAUDE
Validation      semantic_models.yaml    ──► repo_truths.yaml
Classification  roles.json              ──► unified_analysis.json
```

**Rule:** Concepts define structure. Objects are instances. ALWAYS schema-first.

---

## EDGE TYPES

| Type | Direction | Meaning | Example |
|------|-----------|---------|---------|
| **calls** | A → B | A invokes B | `main() calls init()` |
| **imports** | A → B | A depends on B | `app.py imports utils` |
| **inherits** | A → B | A extends B | `Dog inherits Animal` |
| **implements** | A → B | A realizes B | `UserRepo implements IRepo` |
| **contains** | A → B | A holds B | `Class contains method` |
| **uses** | A → B | A references B | `handler uses logger` |

---

## ETYMOLOGY

| Term | Origin | Meaning |
|------|--------|---------|
| **-ome** | Greek -ωμα | Complete set (genome, proteome) |
| **Particle/Wave** | Quantum physics | Duality of measurement vs potential |
| **Collider** | Particle physics | Tool that smashes things to find constituents |
| **Holons** | Koestler | Parts that are also wholes |
| **Three Worlds** | Popper | Physical, mental, abstract knowledge |

---

## QUICK REFERENCE

```
PROJECTOME = CODOME ⊔ CONTEXTOME     (partition)
CODOME     = all executable code
CONTEXTOME = all non-executable content
CONCORDANCES = purpose-aligned regions (cover, may overlap)
REALMS     = Particle | Wave | Observer (partition by directory)

σ: Nodes → Atoms                     (classification function)
R: Code × Docs → Symmetry State      (symmetry relation)

Confidence = min(Factual, Alignment, Current, Onwards)
```

---

---

## PURPOSE FIELD (Teleological Layer)

> Full formalization in `CODESPACE_ALGEBRA.md` §10

| Term | Definition |
|------|------------|
| **Purpose Field** | 𝒫: N → ℝᵏ — Vector field over nodes defining WHAT each entity is FOR |
| **Purpose = Identity** | IDENTITY(n) ≡ 𝒫(n) — You ARE what you're FOR |
| **Focusing Funnel** | Purpose is diffuse at L0, sharp at L12 (emergent from aggregation) |
| **Transcendence** | Entity gains purpose by participating in level L+1 |
| **Dynamic Purpose** | 𝒫_human(t) — Flows and adapts moment-to-moment |
| **Crystallized Purpose** | 𝒫_code(t) — Frozen at commit, static until next change |
| **Purpose Drift** | Δ𝒫 = 𝒫_human - 𝒫_code — Gap between human intent and frozen code |
| **Technical Debt** | ∫|d𝒫_human/dt|dt — Accumulated purpose change since commit |
| **Emergence Signal** | ‖𝒫(parent)‖ > Σ‖𝒫(children)‖ → New layer born |

### Physical Analogy

| Code Concept | Physics Analogy |
|--------------|-----------------|
| Purpose vector | Magnetic dipole moment |
| System purpose | External B-field |
| Misalignment | Stored potential energy |
| Refactoring | Torque realigning dipoles |
| Evolution | Gradient descent on energy |

---

## QUERY MANIFEST (AI Record Format)

> The canonical record of an AI query. Schema in `config/query_manifest_schema.yaml`

| Field | Purpose |
|-------|---------|
| **hash** | SHA256 of (prompt + context) for deduplication |
| **model** | name, provider, tier, temperature |
| **context** | type, sources, tokens_est, truncation |
| **lineage** | parent_schema, cache_hit, run_index |
| **metrics** | input_tokens, output_tokens, latency_ms, cost_usd |
| **quality** | confidence, **reason**, validation_method |
| **result** | takeaway, key_findings |
| **implications** | applies_to, documented_in, action_items |

**Compact Format:**
```
# QUERY MANIFEST
hash: sha256:HASH
model: MODEL | temp=T | tier=TIER
context: TOKENSk from SOURCE
lineage: schema=SCHEMA | run=N/M | cache=HIT_OR_MISS
metrics: in=INk out=OUTk latency=Ts cost=$C
quality: conf=C | reason="WHY" | method=METHOD
takeaway: "SUMMARY"
documented_in: PATH
```

**Principle:** If you can't show the manifest, the query didn't happen.

---

## SEE ALSO

| Doc | Purpose |
|-----|---------|
| `CODOME.md` | Executable universe definition |
| `CONTEXTOME.md` | Non-executable universe definition |
| `PROJECTOME.md` | Complete contents definition |
| `CONCORDANCES.md` | Purpose-aligned region definitions |
| `TOPOLOGY_MAP.md` | Master navigation guide |
| `.agent/SUBSYSTEM_INTEGRATION.md` | System connections |
| `standard-model-of-code/docs/MODEL.md` | Full theory |
| `CODESPACE_ALGEBRA.md` | Mathematical formalization (Purpose Field, Emergence, Constructal Law) |

---

---

## RELATED FILES

| File | Purpose | Location |
|------|---------|----------|
| **GLOSSARY.yaml** | Machine-readable version (122 terms with provenance) | `standard-model-of-code/docs/` |
| **GLOSSARY_QUICK.md** | 10-term quick reference for Day 1 onboarding | This directory |
| **MODEL.md** | Theory source for physics metaphors | `standard-model-of-code/docs/` |

**Note:** This file (GLOSSARY.md) is the authoritative human-readable glossary. GLOSSARY.yaml provides the same terms in machine-readable format with attribution and category metadata.

---

*Created: 2026-01-25*
*Updated: 2026-01-27 (added related files section)*
*Sources: Gemini analysis, Perplexity validation, legacy glossary, MODEL.md*
*Structure: RFC 2119 compliant, AI-agent optimized*
