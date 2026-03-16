# Ideome v2 — Session Prompt

**Priority:** HIGH
**Prerequisite reading:** Do ALL of this before writing a single line of code.

---

## The Mistake We're Correcting

On 2026-03-16, we built `wave/tools/ai/ideome_scorer.py` (449 lines) — a standalone tool that scores ecosystem components against 15 alignment principles by checking Atlas YAML field presence. A deep post-hoc critique revealed three fatal flaws:

1. **Wrong input surface.** Every check reads `component: dict` from Atlas YAML — not source code, not Collider output, not runtime behavior. A component can score B by having the right YAML fields while its code does none of those things.

2. **Duplicate Ideome.** `particle/src/core/ideome_synthesis.py` (500 lines) already exists as Collider Stage 19. It computes per-node triangulated drift between Codome (code) and Contextome (docs) using three pillars: Constraint, Declaration, Decomposition. The scorer ignored this entirely and reinvented alignment measurement with keyword matching on YAML.

3. **Gameable by metadata editing.** We enriched 17 Atlas YAML entries (pure text editing, zero code changes) and the ecosystem average jumped from 0.24 (F) to 0.53 (D) — a 121% improvement. If editing metadata doubles your alignment score, the score doesn't measure alignment.

**Full critique:** `governance/IDEOME_ARCHITECTURE_CRITIQUE.md` (245 lines, 7 open design questions)


---

## What Already Exists (Read All Before Designing)

### 1. `ideome_synthesis.py` — The Real Ideome (Stage 19)
**Location:** `particle/src/core/ideome_synthesis.py` (500 lines)
**Tests:** `particle/tests/test_ideome_synthesis.py` (536 lines, 5 test classes)
**Wired into pipeline at:** `particle/src/core/phases/synthesis.py:490` (`_run_ideome`)
**Output key:** `ctx.full_output['ideome']` → persisted in `unified_analysis.json`

**What it computes:**
- Per-node `IdeomeNode` with three pillar scores:
  - `constraint_score` [0,1] — from `purpose_decomposition` completeness
  - `declaration_score` [0,1] — from `contextome.purpose_priors` confidence
  - `decomposition_score` [0,1] — from `gap_report` gap density (inverted)
- Per-node drift vectors:
  - `alignment_C` = how well CODE matches the ideal (equal-weight avg of 3 pillars)
  - `alignment_X` = how well DOCS match the ideal (declaration_score)
  - `delta_CX` = |alignment_C - alignment_X|
  - `drift_direction` ∈ {aligned, code_drifted, docs_drifted, both_drifted, unknown}
- `DomainAlignment` — aggregated by directory prefix (first 2 path components)
- `IdeomeResult` — global coherence, drift scores, coverage, node count

**Key constants:**
- `UNKNOWN = 0.5` (missing data = midpoint, not penalty)
- `DRIFT_THRESHOLD = 0.15` (below = considered aligned)
- `BOTH_DRIFTED_FLOOR = 0.4` (both below = both_drifted)

**Insight interpretation:** `particle/src/core/insights_compiler.py:2990` (`_interpret_ideome`) produces `category='ideome'` insights with severity based on coherence thresholds.

**Data Chemistry extraction:** `particle/src/core/data_chemistry.py:297` (`_extract_ideome_coherence`) pulls `global_coherence` into the chemistry lab's cross-signal correlation.

### 2. `IDEOME.yaml` — Principle Definitions
**Location:** `.ecoroot/IDEOME.yaml` (134 lines)
**Status:** Sound principles, wrong enforcement mechanism

Defines 15 principles across 3 domains:
- **Domain A: Output Contract (weight 0.40)** — A1 D6 header, A2 Three-tier output, A3 Longitudinal tracking, A4 Meta envelope, A5 Cost awareness
- **Domain B: Operational Resilience (weight 0.35)** — B1 Deterministic fallback, B2 LLM degradation signal, B3 Auto-feedback, B4 Observable failure, B5 Config SSOT
- **Domain C: Ecosystem Integration (weight 0.25)** — C1 Atlas registered, C2 Tools registry, C3 Progressive compliance, C4 Feeds documented, C5 Agent affordances

Grade boundaries match Collider: A ≥ 0.85, B ≥ 0.70, C ≥ 0.55, D ≥ 0.40, F < 0.40

### 3. `ideome_scorer.py` — The Broken v0 (To Be Renamed)
**Location:** `wave/tools/ai/ideome_scorer.py` (449 lines)
**Status:** Measures Atlas documentation completeness, NOT alignment. Should be renamed to `atlas_completeness_checker.py`.

**What it actually checks:** YAML field presence in Atlas entries. Keywords in `agent.explanation` prose. File type strings. Never touches source code.

### 4. `_shared.py` — Extraction Foundation
**Location:** `wave/tools/ai/_shared.py` (362 lines)
**Status:** Clean import foundation for wave/tools/ai/ ecosystem. Zero side effects on import.

### 5. Collider Pipeline Architecture
- **Entry:** `particle/cli.py`
- **Pipeline orchestration:** `particle/src/core/full_analysis.py`
- **Phase 6 (Synthesis):** `particle/src/core/phases/synthesis.py` — stages 9-20+
- **Stage 19:** `_run_ideome()` calls `synthesize_ideome(ctx.full_output)` and stores result in `ctx.full_output['ideome']`
- **Stage base class:** `particle/src/core/pipeline/base_stage.py` — `BaseStage(ABC)` with `name`, `stage_number`, `execute(state)`, `validate_input()`, `validate_output()`
- **Output:** `unified_analysis.json` contains ALL stage outputs including ideome data

### 6. Open Concerns (Relevant)
**Location:** `governance/OPEN_CONCERNS.md` (284 lines, 42 concerns)
- **EG-001 (CRITICAL):** Atlas Validator does not exist. 349 field violations undetected.
- **EG-002 (CRITICAL):** Atlas coverage is 16%. 175 Python files unregistered.
- **EG-005 (HIGH):** Emitter generates non-compliant entities (P1/P2 claims, missing fields).
- **HIGH-001:** Discoverability anti-pattern — tools built but not wired.

These concerns are upstream dependencies: if the Atlas is 84% incomplete and has no validator, any system that reads Atlas data inherits that uncertainty. The v2 design must account for this — either by not depending on Atlas for Domains A/B, or by explicitly flagging Atlas-derived scores as low-confidence.

---

## The Design Task

**Design (brainstorm, not implement) the Ideome v2 scoring architecture.**

### Mandatory Constraints

1. **Codome truth, not Atlas claims.** Domain A and B checks must verify against source code (grep/AST) or Collider output (`unified_analysis.json`). Domain C checks may use Atlas because Atlas IS the authority for ecosystem integration.

2. **Build on ideome_synthesis.py, not alongside it.** The v2 scorer should consume `ideome_synthesis.py`'s output (per-node drift scores, pillar data) and extend it — not duplicate the analysis. The question is HOW: does it read `unified_analysis.json` post-hoc, or does it run as a later Collider stage?

3. **Evidence trail mandatory.** Every principle score must include: evidence source (file path + line number, or Collider node reference, or "no evidence found"), raw evidence snippet, and confidence qualifier.

4. **The 121% metadata test.** After v2 is designed, run this thought experiment: "If someone edited only YAML files and no source code, would the score change?" If yes for any Domain A or B principle, the check is wrong.

5. **No implementation this session.** Design the spec, write it to `governance/IDEOME_V2_SPEC.md`, review it against the 7 open questions in `IDEOME_ARCHITECTURE_CRITIQUE.md`. Get the architecture right before building.

### The 7 Open Questions (Must Be Answered in the Spec)

From `governance/IDEOME_ARCHITECTURE_CRITIQUE.md`:

1. **Q1: Collider stage vs independent scorer?** Options: (A) Ideome IS a new Collider stage 25 that runs after Stage 19 within the pipeline, (B) Independent tool that reads `unified_analysis.json` post-hoc, (C) Fully independent with its own source analysis. Consider: `ideome_synthesis.py` is already Stage 19. It produces per-node drift data stored in `ctx.full_output['ideome']`. A Stage 25 could read that + do source grep. An independent tool would need to parse `unified_analysis.json`. Option C would duplicate Collider's work.

2. **Q2: Should the scorer execute the tool?** For A2 (three-tier output): (A) grep source for output file writes (static analysis), (B) run the tool and inspect output directory (runtime verification), (C) check cached output from previous runs (filesystem evidence). Each has tradeoffs in accuracy vs cost vs side effects.

3. **Q3: Non-code components?** EcoSync (infra scripts on VPS), OpenClaw Gateway (service), Syncthing (external tool), Industrial UI Library (terminal styling) — these either have no Collider-analyzable source or are fundamentally different from "tools that produce output." How to score? Different schema per component type? Score only what's scorable and mark rest N/A?

4. **Q4: Binary vs graded scoring?** A partial D6 header (has `source` + `timestamp` but missing `git_sha`) currently scores 0. Should it score 0.5? If graded, define the gradient for each principle — what earns 0.3 vs 0.7 vs 1.0.

5. **Q5: Enforced or advisory?** Currently `alignment` is FREE in Atlas Progressive Requirements. Should it become ENFORCED at P3 ("others depend on you, prove you're aligned")? Or remain advisory forever?

6. **Q6: Human role?** B5 (Config SSOT) can't be fully automated — counting config surfaces requires understanding the component's architecture. Options: (A) skip in `--auto` mode, (B) cache last human assessment with decay, (C) flag as "unverified" with explicit confidence penalty.

7. **Q7: Gaming prevention?** If alignment score is tracked and visible, there's incentive to game it. A component could add a dummy `_generated = {}` dict that's never populated at runtime. Evidence-based scoring (show the code), spot-checks (actually run it), cross-validation (does Collider's structural analysis agree?) — which mechanisms, and at what cost?

### Per-Principle Evidence Map (v2 Must Define for All 15)

For each principle, the spec must define exactly:
- **Evidence source:** What proves compliance (source grep pattern, Collider node attribute, filesystem check, runtime output inspection)
- **Evidence location:** How to find it (source file path resolution from Atlas `invoke.method` → source file → Collider nodes, or Collider output field path in `unified_analysis.json`, or output directory convention)
- **Partial credit rules:** If graded — what earns 0.3 vs 0.7 vs 1.0
- **Anti-gaming mechanism:** Why editing YAML alone can't satisfy this check
- **Confidence tier:** deterministic (binary, provable), heuristic (grep-based, high confidence), or manual (human judgment required)

**Starter mapping from the v0 critique (the "what v2 must check" column):**

| ID | v0 checks (wrong) | v2 must check (right) |
|----|---|---|
| A1 | "YAML has JSON output type" | `grep '_generated'` in source; inspect actual output JSON |
| A2 | "YAML lists 3 output types" | Count distinct output format writes in source; check output dir after run |
| A3 | "YAML mentions JSONL" | `grep 'open.*"a".*jsonl'` in source; verify JSONL file grows across runs |
| A4 | "Same as A1" | Inspect output JSON for run_id, timestamp, hostname, processing_time |
| A5 | "YAML has cost_metric" | `grep 'cost\|token.*count\|usage'` in source; check output for cost fields |
| B1 | "Description mentions 'fallback'" | Trace code paths: is there a non-API execution path? (AST/Collider) |
| B2 | "YAML mentions 'degradation'" | Check for degradation model/field in source and output schema |
| B3 | "YAML mentions 'feedback'" | Check for self-evaluation functions that grade own output |
| B4 | "Description mentions 'error'" | Count `except: pass` vs `except: log` patterns (AST analysis) |
| B5 | "Returns 0.5 always" | Count configuration surfaces, check single import path (manual/heuristic) |
| C1 | Atlas entry exists at P2+ | **Correct as-is** — Atlas IS the authority for registration |
| C2 | TOOLS_REGISTRY entry exists | **Correct as-is** — registry IS the authority |
| C3 | Enforced fields present | **Mostly correct** — but should also validate field CONTENT is non-empty/non-placeholder |
| C4 | feeds_into/fed_by non-empty | Cross-validate: do declared feeds exist as code-level imports/calls? |
| C5 | agent.affordances 3 subfields | Cross-validate: does `cannot: [modify_source_code]` hold in reality? |

### Relationship to Existing Systems (Must Be Precisely Delineated)

The spec must avoid the v0 mistake of building a parallel system. Define clearly:

- **ideome_synthesis.py (Stage 19):** Codome↔Contextome triangulated drift at NODE level. Measures how well code matches docs matches ideal. Operates per-file/per-function. Already integrated into Collider pipeline, insights compiler, and data chemistry. This is the *structural alignment* layer — does the code match its documentation?

- **Ideome v2 scorer:** COMPONENT-level ecosystem alignment. Measures how well a component follows ecosystem design principles (D6 headers, three-tier output, fallback, etc.). Operates per-CMP-xxx. This is the *design principle* layer — does the component follow ecosystem conventions?

- **Bridge:** How do node-level structural scores from Stage 19 aggregate to component-level design scores in v2? The Atlas `invoke.method` field maps CMP-xxx → source file → Collider nodes. The v2 scorer can pull the relevant node's ideome data and incorporate structural alignment as one signal. But the 15 ecosystem principles are ADDITIONAL to structural drift — a component can have perfect code-docs alignment (Stage 19 coherence = 1.0) but still not produce D6 headers or three-tier output.

- **atlas_completeness_checker.py (renamed v0):** Measures Atlas documentation quality. Useful for tracking which Atlas entries need enrichment. NOT alignment. Should be clearly labeled as a documentation quality tool, not a scoring system.

### The Deeper Question: What IS Alignment?

The v0 mistake reveals a definitional gap. "Alignment" in this ecosystem conflates three things:

1. **Structural alignment** (ideome_synthesis.py) — does code match docs? Does the architecture match its declarations?
2. **Design principle compliance** (IDEOME.yaml principles) — does the component follow ecosystem conventions like D6 headers, three-tier output?
3. **Documentation completeness** (v0 scorer) — does the Atlas entry describe the component fully?

The v2 spec must decide: is the "Component Alignment Score" one number that blends all three, or three separate scores that are reported independently? Blending risks hiding problems. Separating risks information overload.

---

## Deliverable

`governance/IDEOME_V2_SPEC.md` containing:
1. Architecture decision for each of Q1-Q7, with rationale and tradeoffs acknowledged
2. Evidence map for all 15 principles (source of truth, check method, partial credit, anti-gaming)
3. Data flow diagram (what reads what, what produces what, where outputs are stored)
4. Scoring formula with partial credit rules and confidence weighting
5. Anti-gaming analysis (run the 121% metadata test against every Domain A/B check)
6. Relationship to ideome_synthesis.py (Stage 19) — consume, extend, or parallel?
7. Component-type taxonomy (code tools vs libraries vs infrastructure vs services vs externals) with per-type scoring expectations
8. Migration plan (rename v0, what happens to existing `.ecoroot/alignment/` reports, backward compatibility)

**Do NOT implement.** Design, write spec, scrutinize against the critique document. The v0 mistake was building before understanding. Don't repeat it.


---

## Architectural Decision (Pre-resolved — see `governance/IDEOME_V2_ARCHITECTURE.md`)

The architectural decision has been made based on codebase analysis. Read the full rationale in `governance/IDEOME_V2_ARCHITECTURE.md` (209 lines). Summary:

### Option D: Two-Layer Architecture

**Layer 1 — Collider Stage 25: "Principle Evidence Collector"**
- Runs INSIDE the Collider pipeline after Stage 19 (Ideome Synthesis)
- Performs source grep/AST checks on actual code: `_generated` patterns, `except: pass` counts, JSONL tracking patterns, cost tracking, degradation signals, self-eval functions
- Stores per-NODE evidence in `ctx.full_output['principle_evidence']` → persisted in `unified_analysis.json`
- Does NOT know about CMP-xxx components, does NOT read Atlas, does NOT produce reports

**Layer 2 — `ideome_scorer_v2.py` (standalone tool)**
- Runs AFTER Collider, reads `unified_analysis.json` + `ATLAS.yaml` + `IDEOME.yaml`
- Maps CMP-xxx → source files (via Atlas `invoke.method`) → Collider nodes → Layer 1 evidence
- Adds Layer 2-only checks: output directory inspection (A2, A4), JSONL temporal checks (A3), Atlas integration checks (C1-C5)
- Aggregates node-level evidence to component-level scores with full evidence trail
- Produces alignment reports at `.ecoroot/alignment/`

**Why neither pure Collider stage nor pure standalone:**
- A pure Collider stage can't do cross-component checks (C4 feeds), output inspection (A2), or temporal checks (A3)
- A pure standalone tool would duplicate Collider's AST analysis and miss the rich per-node data already computed by stages 1-19

### Q1-Q7 Resolved

| Q | Decision | Rationale |
|---|---|---|
| Q1 | Option D: Two-layer | Layer 1 = Collider stage (evidence), Layer 2 = standalone (scoring) |
| Q2 | C (cached) + optional B (runtime) | Default: inspect previous output. `--verify` flag: run tool and inspect fresh output |
| Q3 | Component-type taxonomy | 4 types: code tool (full), library (A=N/A mostly), infrastructure (manual), external (C-only) |
| Q4 | Graded 0.0-1.0 | Defined rubrics per principle: 1.0/0.7/0.3/0.0 thresholds |
| Q5 | Advisory now, enforce at P3 later | After Atlas Validator exists and 3+ months of accurate scoring |
| Q6 | Explicit "unverified" with decay | Manual assessments start at 0.9 confidence, decay 0.1/month, STALE after 6mo |
| Q7 | Evidence + cross-validation + spot-checks | Every score cites file:line. Collider AST is independent from Atlas claims. `--verify` for runtime checks |

### 121% Metadata Test: All Domain A/B checks PASS
No YAML-only edit can change any Domain A or B score. Domain C correctly changes with YAML because Atlas IS the authority for integration. Full per-principle analysis in the architecture document.

---

## Remaining Task for This Session

With the architecture decided, the session should:

1. **Read** `governance/IDEOME_V2_ARCHITECTURE.md` in full
2. **Read** `governance/IDEOME_ARCHITECTURE_CRITIQUE.md` for context
3. **Read** `particle/src/core/ideome_synthesis.py` to understand Stage 19's data model
4. **Design Layer 1** (Stage 25): Define the exact grep/AST checks, output schema, and how it integrates into `phases/synthesis.py`
5. **Design Layer 2** (scorer v2): Define the exact CMP-xxx → node mapping, evidence aggregation logic, and report schema
6. **Write the complete spec** to `governance/IDEOME_V2_SPEC.md`
7. **Rename** `ideome_scorer.py` → `atlas_completeness_checker.py`
8. **Do NOT implement** the actual code — spec only

The spec should be detailed enough that a fresh session can implement both layers without re-deriving any design decisions.
