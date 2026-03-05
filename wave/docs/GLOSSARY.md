# GLOSSARY - PROJECT_elements

> **Status:** ACTIVE
> **Version:** 2.1.0
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
├── particle/ ─────► PARTICLE (collapsed reality)
│   ├── src/core/                   Collider pipeline
│   ├── docs/                       Theory (MODEL.md)
│   └── tools/                      Laboratory, utilities
│
└── wave/ ──────────► WAVE (field of potential)
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
| **PARTICLE** | `particle/` | The collapsed reality. Measurement. Implementation. The Collider lives here. |
| **WAVE** | `wave/` | The field of potential. Context. AI tools. Planning happens here. |
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
| S14 | **DataLedger** | Observability | Non-linear pipeline data traffic tracker. Stages publish keys on produce; consumers query before extract. Feeds `data_availability` in pipeline report. |

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

> **Prior Art:** Architecture erosion/documentation drift studied in Perry & Wolf (1992). Distinguished by the 5-state taxonomy, especially AMNESIAC (no prior equivalent).

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

## PIPELINE OBSERVABILITY

| Term | Definition |
|------|------------|
| **DataLedger** | Passive observer on `PipelineContext`. Stages publish data keys with status (ok/empty/skipped/failed). Consumers query availability before extraction. Not an event bus. |
| **LedgerEntry** | A single publication record: key, producer stage name, status, monotonic timestamp (ms), and optional summary string. |
| **MANIFEST** | Static dict mapping ~45 expected data keys to their producer stages. Declared in `data_ledger.py`. Keys in MANIFEST but not published = gap. Published but not in MANIFEST = undeclared output. |
| **Data Availability** | Section in `pipeline_report.json` produced by `DataLedger.to_dict()`. Shows total expected, total published, missing keys, status breakdown, and per-entry timestamps. |
| **Signal Availability** | ChemistryLab-specific view bridging DataLedger status to chemistry signal extraction. Each of the 14 chemistry signals maps to a ledger key, enabling "why is this signal None?" diagnostics. |

**Data Status Semantics:**

| Status | Meaning |
|--------|---------|
| `ok` | Stage ran and produced non-empty result |
| `empty` | Stage ran successfully but produced no output (legitimate zero) |
| `skipped` | Stage was not executed (dependency missing, feature disabled, condition unmet) |
| `failed` | Stage attempted execution but errored |

**Usage Pattern:**
```
ctx.data_ledger.publish("api_drift", "Stage 6.9: API Drift Detection",
    summary="91 items, score=3.3%")
ctx.data_ledger.is_available("api_drift")  # True if status == "ok"
ctx.data_ledger.get_status("api_drift")    # "ok"/"empty"/"skipped"/"failed"/None
ctx.data_ledger.missing_keys()             # MANIFEST keys not yet published
```

**Implementation:** `particle/src/core/data_ledger.py`

---

## EPISTEMIC FRAMEWORK

SMoC classifies every theoretical claim by its epistemic certainty:

| Level | Meaning | Validation Path | Examples |
|-------|---------|-----------------|----------|
| **AXIOM** | Assumed for the framework to function. Not falsifiable -- it's a modeling choice. | N/A (design decision) | Level Blindness |
| **CONJECTURE** | Believed but not yet empirically validated. Testable via Hunt Protocol. | Evidence Triangle + Hunt Protocol | Codespace geometry, Landscape, Observer Horizon |
| **THEOREM** | Proven within the system or derivable from established mathematics. | Mathematical proof or derivation | Kolmogorov bound, Rice's theorem |
| **FRAMEWORK DEFINITION** | Classification heuristic, not empirical claim. Subject to refinement. | Utility assessment | Natural Law recognition test |

> **On Physics Metaphors:** SMoC borrows physics terminology as structural analogies for pedagogical clarity. These are NOT claims of mathematical isomorphism. Every physics term is acknowledged in the glossary with its origin.

> **On Prior Art:** Terms marked "Original Invention" have no prior academic usage under their specific name and integrated formulation. Where the underlying analytical goal has precedent, a "Prior Art & Differentiation" field cites closest work and identifies the novel contribution.

---

## KNOWN LIMITATIONS

1. **Empirical Validation.** Most structural claims (Codespace geometry, emergence thresholds, concordance-defect correlation) are conjectures awaiting systematic validation across diverse codebases.
2. **Metaphor Boundaries.** Code "atoms" are not governed by conservation laws. Code "fermions" do not obey Fermi-Dirac statistics. The metaphors illuminate structural parallels only.
3. **Classification Subjectivity.** The 8 Dimensions involve judgment calls at boundaries. Inter-rater reliability studies are planned but not yet conducted.
4. **Scale Dependency.** Validated primarily on 10K-500K LOC codebases. Behavior at extremes (< 1K LOC or > 10M LOC) is untested.
5. **Language Bias.** AST extraction supports Python, JS/TS, Go. Language-specific idioms (Rust ownership, Haskell types) may require dimension extensions.

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

## GRAPH TOPOLOGY (Node Roles)

| Role | Condition | Meaning |
|------|-----------|---------|
| **orphan** | in=0, out=0 | Disconnected (but only ~9% are truly dead) |
| **root** | in=0, out>0 | Entry point |
| **leaf** | in>0, out=0 | Terminal node |
| **hub** | high degree | Central coordinator |
| **internal** | in>0, out>0 | Normal flow-through |

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

## DEEPER READING

| Need | File |
|------|------|
| The unifying equation | `docs/essentials/LAGRANGIAN.md` |
| The 13 big ideas | `docs/essentials/THEORY_WINS.md` |
| Why "Standard Model" | `docs/essentials/VISION.md` |
| Classification reference | `docs/essentials/CLASSIFICATION.md` |
| Architecture overview | `docs/essentials/ARCHITECTURE.md` |
| Quick topic lookup | `docs/nav/` (10 single-topic files) |
| Full theory (L0-L3) | `particle/docs/theory/THEORY_INDEX.md` |
| Math formalization | `CODESPACE_ALGEBRA.md` |
| Machine-readable terms | `particle/docs/GLOSSARY.yaml` (161 terms, epistemic status, prior art) |
| Day-1 survival kit | `wave/docs/GLOSSARY_QUICK.md` (10 terms, 60 seconds) |

**Note:** This file (GLOSSARY.md) is the single authoritative human-readable glossary. All other glossary-like documents are either machine-readable derivatives (GLOSSARY.yaml) or onboarding subsets (GLOSSARY_QUICK.md).

---

*Created: 2026-01-25*
*Updated: 2026-03-04 (v2.1.0: adversarial review hardening -- epistemic framework, prior art differentiation, known limitations, pipeline observability)*
*Sources: Gemini analysis, Perplexity validation, legacy glossary, MODEL.md*
*Structure: RFC 2119 compliant, AI-agent optimized*
