# Frontier Reframing: The Contextome Blindspot and Composition Layer

> **Date:** 2026-03-02
> **Status:** ANALYSIS + DESIGN PROPOSAL
> **Trigger:** Post-Trinity implementation audit revealed structural blindspot
> **Author:** Deep-research synthesis from codebase exploration

---

## 1. SITUATION: What We Built vs What We See

### 1.1 Capability Table (Updated 2026-03-02)

| Dimension | Module | Status | Data Source |
|-----------|--------|--------|-------------|
| Graph topology | `build_nx_graph` | BUILT | networkx DAG |
| Centrality / criticality | `graph_metrics.py` | BUILT | betweenness, PageRank |
| Markov chain (entanglement) | `information_geometry.py` | BUILT | transition matrix |
| IGT stability | `igt_metrics.py` | BUILT | φ_structural, orphan classification |
| Purpose field | `purpose_field.py` | BUILT | pi2/pi3 propagation |
| Purpose intelligence | `purpose_intelligence.py` | BUILT | semantic analysis |
| Semantic role | `file_enricher.py` | BUILT | atom taxonomy |
| Layer / dimension / level | `holarchy.py`, `dimensions.py` | BUILT | Standard Model |
| Scope analysis | `scope_analysis.py` | BUILT | tree-sitter |
| Control flow | `control_flow_metrics.py` | BUILT | cyclomatic, nesting |
| Pattern detection | `pattern_detector.py` | BUILT | atom patterns |
| Dead code detection | `dead_code_detector.py` | BUILT | scope + import |
| Fan-in/fan-out | `coupling_analysis.py` | BUILT | edge counting |
| Antimatter | `antimatter_detector.py` | BUILT | anti-patterns |
| Disconnection taxonomy | `disconnection_classifier.py` | BUILT | connectivity |
| Incoherence functional | `incoherence.py` | **BUILT (new)** | I(C) = 5-term Lagrangian |
| Purpose decomposition | `purpose_decomposition.py` | **BUILT (new)** | CONSTRAINT_RULES |
| Gap detection | `gap_detector.py` | **BUILT (new)** | missing sub-compartments |
| Temporal analysis (REH) | `temporal_analysis.py` | **BUILT (new)** | git history |
| LLM insights | `insights_generator.py` | BUILT | Gemini 2.0 Flash |
| Insights compilation | `insights_compiler.py` | BUILT | all 15 interpreters |
| **Contextome processing** | **NONE** | **MISSING** | **zero** |
| **Composition / cross-correlation** | **NONE** | **MISSING** | **zero** |
| **Constructal resistance** | **NONE** | **MISSING** | **zero** |

### 1.2 The Diagnosis

The system has 22 built analysis dimensions. It can dissect a codebase into atoms, layers, dimensions, purposes, graphs, entanglement matrices, stability scores, and temporal evolution.

**But it is fundamentally half-blind.**

Collider analyzes the CODOME exclusively. The CONTEXTOME -- documentation, READMEs, specs, ADRs, architecture decision records, docstrings at the file level, configuration manifests -- is **counted but never read**.

This matters because:

> **Purpose lives in documentation.**
> Code implements purpose. Documentation declares it.
> Bottom-up inference from code is reconstruction.
> Top-down declaration from docs is the ground truth.

The survey (Stage 0) counts 12 doc files. It records `composition.doc_files = 12`. Then it moves on. Nobody reads them. Nobody extracts the declared purposes. Nobody compares declared vs inferred.

---

## 2. THE BLINDSPOT: Where Purpose Actually Lives

### 2.1 Three Purpose Streams (Disconnected)

The pipeline currently computes purpose three independent ways:

| Stream | Source | Location | What It Produces |
|--------|--------|----------|-----------------|
| `semantic_role` | atom taxonomy + file name | `file_enricher.py` | "Repository", "Service", "Controller" |
| `pi2_purpose` | purpose field propagation | `purpose_field.py` | directional purpose vectors |
| `purpose_intelligence` | semantic heuristics | `purpose_intelligence.py` | role + responsibility + layer |

**None of these reads documentation.**

A `UserService.py` file might have a README.md that says "This service handles user authentication, session management, and profile CRUD." That sentence contains more purpose signal than all three bottom-up inference systems combined. But Collider never sees it.

### 2.2 The POM Skeleton

A complete spec exists: `wave/docs/specs/PROJECTOME_OMNISCIENCE_MODULE.md` (708 lines).
A working skeleton exists: `wave/tools/pom/projectome_omniscience.py` (891 lines).

The POM defines:
- **SYMMETRIC**: code and docs aligned
- **ORPHAN**: code without docs
- **PHANTOM**: docs without code
- **DRIFT**: code and docs misaligned

The POM skeleton actually implements:
- `ContextomeScanner` -- walks .md, .yaml, .json files, extracts headings and code refs
- `SymmetryDetector` -- matches code entities to doc entities, computes Jaccard drift
- `PurposeFieldAnalyzer` -- coverage, coherence, entropy across both universes

**But POM is in `wave/tools/pom/` -- completely disconnected from the Particle pipeline.**
It was designed as a standalone tool, not as a pipeline stage.

### 2.3 Why LLM Processing Is Required

The user's key insight:

> "It must run on any codebase and very few share common machine readable documentation
> and we would have to hardcode a parsing methodology."

Documentation formats are infinitely diverse:
- Markdown with custom conventions
- RST (Python ecosystem)
- JSDoc / TSDoc (JS ecosystem)
- Architecture Decision Records (ADR format)
- Plain text READMEs
- YAML/TOML config with embedded comments
- Jupyter notebooks with narrative cells
- GitHub wiki pages
- Inline module-level docstrings

**You cannot hardcode parsers for all of these.** An LLM can read any of them and extract:
1. Declared purpose (what the project/module/file claims to do)
2. Architectural intent (what patterns/layers are described)
3. Constraints (what MUST or MUST NOT happen)
4. Dependencies and relationships (what integrates with what)
5. Target audience / user stories

This is exactly where Gemini 2.0 Flash -- already integrated at `insights_generator.py` -- should be used. The infrastructure exists. The pipeline slot exists. The data just never gets fed in.

---

## 3. THE FIX: Contextome Processing Pipeline

### 3.1 Design: Stage 0.8 -- Contextome Intelligence

Insert a new stage between Survey (Stage 0) and Base Analysis (Stage 1):

```
Stage -1: SmartIgnore (exclusion discovery)
Stage  0: Survey (CODOME definition)
Stage  0.5: Incremental Detection
>>> Stage  0.8: Contextome Intelligence (NEW) <<<
Stage  1: Base Analysis
Stage  2: Standard Model Enrichment
...
```

**Why before Stage 1?** Because Contextome data should ORIENT the Codome analysis.
If the README says "This is a Django REST API with PostgreSQL," that information should:
- Validate Survey's framework detection
- Pre-populate expected architectural patterns
- Set purpose priors for the Purpose Field (Stage 3.7)
- Provide ground truth for the InsightsCompiler (Stage 11.95)

### 3.2 Design Philosophy: Deterministic Core + LLM Amplifier

> **Collider is a product FOR AI, not an AI product.**
>
> The deterministic layer is the diamond. It runs code on code, applies theory on
> code, extracts signal from structure. This works everywhere -- no API keys, no
> network, no cost. It IS the product.
>
> LLM processing is a signal amplifier. It takes what the deterministic core
> already extracted and expands it. Not to fill gaps, but to deepen what exists.
> A heading "Authentication" is a deterministic signal. An LLM reading that
> section and extracting "OAuth2 with PKCE flow for mobile clients" is
> enrichment that 10x the value. Both layers produce output in the same
> contract. The consumer doesn't care which layer produced a signal.
>
> The LLM layer is plug-and-play: provider-agnostic, optional, adapter-based.
> When present, it multiplies. When absent, the deterministic core delivers
> everything it has -- which is already substantial.

### 3.3 Architecture (Dual-Layer)

```
Stage 0.8: Contextome Intelligence
│
│  ┌─────────────────────────────────────────────┐
│  │  LAYER 1: DETERMINISTIC CORE (always runs)  │
│  └─────────────────────────────────────────────┘
│
├── 0.8.1: Doc Discovery
│   Input:  survey manifest (file list, doc_files count)
│   Output: contextome_inventory = [{path, type, size, heading_structure}]
│   Method: Walk doc files known from survey, extract headings + structure
│
├── 0.8.2: Structural Purpose Extraction
│   Input:  contextome_inventory + raw file contents
│   Output: declared_purposes = [{file, title_purpose, keywords, code_refs,
│                                  sections, framework_signals}]
│   Method: Heading hierarchy parsing, keyword extraction (regex-based),
│           code reference detection (path/class/function patterns),
│           framework signal matching (Django, React, FastAPI, etc.)
│
├── 0.8.3: Symmetry Seeding
│   Input:  declared_purposes + survey.codome_manifest
│   Output: symmetry_seeds = [{doc_path, code_targets, relationship, confidence}]
│   Method: Name matching, path proximity, explicit code refs in docs,
│           sibling file detection (README.md next to src/ → covers src/)
│
├── 0.8.4: Purpose Priors
│   Input:  structural declared_purposes + symmetry_seeds
│   Output: purpose_priors = {node_pattern: {purpose, confidence, source}}
│   Method: Map heading-derived purposes to code path patterns
│
│  ┌─────────────────────────────────────────────┐
│  │  LAYER 2: LLM ENRICHMENT (optional, plug-   │
│  │  and-play, provider-agnostic adapter)        │
│  └─────────────────────────────────────────────┘
│
├── 0.8.5: Semantic Purpose Enrichment
│   Input:  contextome_inventory + file contents (truncated to 4K tokens)
│   Output: enriched_purposes = [{file, semantic_purpose, constraints,
│                                  architecture_hints, relationships}]
│   Method: LLM adapter (any provider) with structured JSON prompt
│   Effect: DEEPENS existing declared_purposes -- does not replace them
│
└── 0.8.6: Enrichment Merge
    Input:  declared_purposes (deterministic) + enriched_purposes (LLM)
    Output: merged declared_purposes with enrichment annotations
    Method: Merge LLM semantic fields into deterministic base, tag source
```

### 3.4 Data Contract

```python
@dataclass
class ContextomeIntelligence:
    """Stage 0.8 output -- same contract whether LLM is present or not."""

    # 0.8.1: What docs exist (deterministic)
    inventory: list[dict]       # [{path, type, size, sections: [...]}]

    # 0.8.2 + 0.8.5: What the docs declare
    # Deterministic: title_purpose, keywords, code_refs, framework_signals
    # LLM-enriched: semantic_purpose, constraints, architecture_hints
    declared_purposes: list[dict]

    # 0.8.3: Doc-code mapping seeds (deterministic)
    symmetry_seeds: list[dict]  # [{doc_path, code_targets, relationship}]

    # 0.8.4: Purpose priors for codome analysis (deterministic base + LLM boost)
    purpose_priors: dict        # {glob_pattern: {purpose, confidence, source}}

    # Metadata
    llm_used: bool              # Whether LLM enrichment was available
    doc_count: int              # Total docs processed
    purpose_coverage: float     # % of docs with extractable purpose
    deterministic_signals: int  # Signals from Layer 1
    enriched_signals: int       # Additional signals from Layer 2
```

### 3.5 Deterministic Purpose Extraction (Layer 1 Detail)

Without any LLM, the deterministic core extracts:

1. **Title purpose**: First H1 heading → purpose declaration
   - `"# User Authentication Service"` → purpose = "User Authentication Service"

2. **Keywords**: Regex extraction of capitalized terms, technical terms, framework names
   - `"Uses Django REST Framework with PostgreSQL"` → ["Django", "REST", "PostgreSQL"]

3. **Code references**: Path, class, and function patterns in markdown
   - `` `src/auth/oauth.py` ``, `UserService`, `def authenticate()` → code refs

4. **Section structure**: H2/H3 headings as sub-purpose indicators
   - `"## Login Flow"`, `"## Session Management"` → sub-purposes

5. **Framework signals**: Pattern matching against known framework markers
   - `requirements.txt` mentions `django` → "Django" signal
   - `package.json` has `react` → "React" signal

6. **Constraint detection**: Regex for MUST/MUST NOT/SHALL/SHALL NOT patterns
   - `"Authentication MUST use HTTPS"` → deterministic constraint

### 3.6 LLM Adapter Design (Layer 2 Detail)

The LLM layer uses a **provider-agnostic adapter pattern**:

```python
class LLMAdapter(Protocol):
    """Any LLM provider implements this."""
    def extract_purpose(self, content: str, path: str) -> dict | None: ...

class GeminiAdapter(LLMAdapter): ...   # Vertex AI / Gemini Flash
class OpenAIAdapter(LLMAdapter): ...   # GPT-4o-mini
class CerebrasAdapter(LLMAdapter): ... # Cerebras (already integrated)
class LocalAdapter(LLMAdapter): ...    # Ollama, llama.cpp, etc.
```

When available, the LLM reads each doc and returns structured JSON:
- `semantic_purpose`: One-sentence declared purpose (from the doc's own words)
- `architecture_hints`: Architectural patterns mentioned
- `constraints`: MUST/MUST NOT declarations
- `relationships`: External systems, APIs, services

This DEEPENS the deterministic extraction. It doesn't replace it.

### 3.7 Integration Points

| Consumer | What It Gets | How It Uses It |
|----------|-------------|---------------|
| Purpose Field (Stage 3.7) | `purpose_priors` | Seed initial purpose vectors with declared intent |
| InsightsCompiler (Stage 11.95) | `declared_purposes` | Compare declared vs inferred purpose for drift detection |
| Incoherence (Stage 11.96) | `symmetry_seeds` | Feed I_sym term with real code-doc alignment data |
| Gap Detector (Stage 11.96) | `declared_purposes` + `constraints` | Check if declared constraints are actually implemented |
| LLM Insights (Stage 12) | Full `ContextomeIntelligence` | Ground the LLM summary in both Codome AND Contextome |

### 3.8 Behavior Matrix

| LLM Available? | What Runs | Output Quality |
|----------------|-----------|---------------|
| **No** | Layer 1 only: doc discovery, structural parsing, keyword extraction, name-matching symmetry, heading-based purposes | Good -- structural signals, code refs, framework detection |
| **Yes** | Layer 1 + Layer 2: all deterministic + semantic enrichment merged | Excellent -- structural + semantic, constraints, architecture hints |

**The pipeline never degrades below "good."** LLM makes it excellent, but good is already substantial.

---

## 4. THE COMPOSITION LAYER (Phase 2)

After Contextome Intelligence, the next frontier is **cross-correlation**.

### 4.1 The Problem

Currently, 22 analysis dimensions produce independent scores:
- IGT stability says "this cluster is unstable"
- Purpose field says "these nodes have weak purpose"
- Incoherence functional says "boundary violations detected"
- Temporal analysis says "this area has high churn"
- Gap detector says "missing required sub-compartment"

**Nobody asks: "Do these signals CONVERGE on the same location?"**

A module that IGT flags as unstable AND purpose field marks as purposeless AND temporal analysis shows is high-churn AND gap detector says is missing sub-compartments -- that's not 4 separate findings. That's one finding with 4x confidence.

### 4.2 Convergence Detection

The composition layer takes all per-node signals and asks:
1. **Convergence**: Where do 3+ dimensions agree on a problem? (HIGH severity)
2. **Contradiction**: Where do dimensions disagree? (INVESTIGATION target)
3. **Isolation**: Where does only 1 dimension see something? (LOW confidence)
4. **Coverage**: What % of nodes are seen by all dimensions?

### 4.3 Constructal Resistance (Theoretical)

From `PURPOSE_FIELD_INTEGRATION_SPEC.md`, the 4-flow resistance model:

```
R_total = R_static + R_runtime + R_change + R_human

R_static  = f(cyclomatic_complexity, coupling, layer_violations)
R_runtime = f(fan_out, async_chains, error_propagation_depth)
R_change  = f(git_churn, commit_coupling, test_coverage)
R_human   = f(naming_clarity, doc_coverage, cognitive_load)
```

Each R-term maps to existing data:
- R_static: control_flow_metrics + coupling_analysis + codome_boundary
- R_runtime: graph_metrics + disconnection_classifier (partial)
- R_change: temporal_analysis (REH) -- **now available**
- R_human: contextome_intelligence + purpose_field

**With Contextome Intelligence, ALL FOUR resistance channels have data sources.**

### 4.4 Dependency Chain

```
Contextome Intelligence (Stage 0.8) -- enables R_human
        ↓
Constructal Resistance (future) -- requires all 4 R-channels
        ↓
Composition Layer (future) -- correlates all dimensions + resistance
        ↓
Unified Diagnosis -- convergent findings with severity * confidence
```

---

## 5. UPDATED FRONTIER MAP

| Priority | Module | Depends On | Impact |
|----------|--------|-----------|--------|
| **P0** | Contextome Intelligence (Stage 0.8) | Gemini (already integrated) | Unlocks declared purpose, symmetry, R_human |
| P1 | Composition / Convergence | All existing dimensions | Multi-dimensional findings |
| P1 | Constructal Resistance | Contextome + REH + existing | Flow optimization metric |
| P2 | Purpose stream unification | 3 purpose systems | Single source of truth |
| P2 | POM integration into pipeline | POM skeleton + Stage 0.8 | Full Projectome visibility |
| P3 | LLM gap resolution | Gap detector + LLM | Fill well-circumscribed unknowns |

**P0 is the keystone.** Without Contextome Intelligence, the Composition Layer lacks its fourth resistance channel (R_human), the InsightsCompiler has no ground truth for purpose drift, and the Incoherence Functional I_sym term operates on proxy data (dead code %) instead of real code-doc alignment.

---

## 6. WHAT EXISTS ALREADY (Reusable Assets)

| Asset | Location | Reusability |
|-------|----------|-------------|
| POM ContextomeScanner | `wave/tools/pom/projectome_omniscience.py:279-495` | Can extract and adapt scan logic |
| POM SymmetryDetector | `wave/tools/pom/projectome_omniscience.py:501-580` | Jaccard drift computation |
| Gemini integration | `wave/tools/ai/insights_generator.py` | Working Vertex AI + Gemini Flash |
| ACI router | `wave/tools/ai/analyze.py` | INSTANT/RAG/LONG_CONTEXT tiers |
| Survey doc counting | `particle/src/core/survey.py:832` | Already walks doc files |
| Docling processor | `wave/tools/ai/docling_processor.py` | PDF/DOCX extraction (not md) |
| Purpose field priors | `particle/src/core/purpose_field.py:149-170` | EMERGENCE_RULES framework |
| Symmetry state enums | `wave/tools/pom/projectome_omniscience.py:42-48` | SYMMETRIC/ORPHAN/PHANTOM/DRIFT |

---

## 7. IMPLEMENTATION ESTIMATE

### Contextome Intelligence (P0)

| File | Action | Lines (est) |
|------|--------|-------------|
| `particle/src/core/contextome_intel.py` | CREATE | ~350 |
| `particle/src/core/full_analysis.py` | EDIT | +30 (Stage 0.8 slot) |
| `particle/src/core/insights_compiler.py` | EDIT | +40 (declared vs inferred comparison) |
| `particle/src/core/incoherence.py` | EDIT | +15 (real I_sym from symmetry seeds) |
| `particle/tests/test_contextome_intel.py` | CREATE | ~200 |

**Prerequisites**: None beyond what exists. Gemini API key already in Doppler.

### Composition Layer (P1, after P0)

| File | Action | Lines (est) |
|------|--------|-------------|
| `particle/src/core/composition.py` | CREATE | ~300 |
| `particle/src/core/constructal_resistance.py` | CREATE | ~200 |
| `particle/src/core/full_analysis.py` | EDIT | +20 (Stage 11.98 slot) |
| `particle/tests/test_composition.py` | CREATE | ~250 |
| `particle/tests/test_constructal.py` | CREATE | ~150 |

---

## 8. THE REFRAME

Before this analysis, the frontier looked like "build more dimensions."

After this analysis, the frontier is clear:

> **The bottleneck is not more measurement. It's measurement of the RIGHT THING.**
>
> Collider measures the body (Codome) with 22 instruments.
> It measures the mind (Contextome) with zero instruments.
>
> Purpose is declared in documentation. Collider infers it from code.
> That's like diagnosing a patient by X-ray alone, ignoring what they tell you.
>
> **Stage 0.8 (Contextome Intelligence) is the single highest-leverage addition.**
> It unlocks: declared purpose, code-doc symmetry, R_human channel,
> and ground truth for every purpose-dependent downstream module.
>
> After that, the Composition Layer becomes possible --
> because you finally have all four constructal resistance channels,
> and cross-correlation across 23+ dimensions becomes meaningful.
