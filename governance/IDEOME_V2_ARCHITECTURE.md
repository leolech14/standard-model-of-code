# Ideome v2 — Architectural Decision Record

**Date:** 2026-03-16
**Status:** PROPOSAL — requires review before implementation
**Context:** Follows `governance/IDEOME_ARCHITECTURE_CRITIQUE.md` and session analysis

---

## The Core Insight That Resolves Q1

The Claude Code session recommended Option B (independent tool reading `unified_analysis.json`) with this reasoning:

> "Collider stages run during analysis of OTHER repos, not self-analysis. When you run `collider full /path/to/ytpipe`, it analyzes YTPipe's code. But the ideome principles (D6 headers, three-tier output) are ecosystem conventions that exist in the tool's OWN code."

**This reasoning is wrong.** Evidence:

1. `.collider/unified_analysis.json` exists at `PROJECT_elements/.collider/` — Collider HAS been run against its own ecosystem.
2. The Atlas Emitter (Phase 8 in `full_analysis.py:722`) already runs as a self-referential stage — it detects components within the analyzed repo and emits `atlas_candidates.yaml`.
3. `ideome_synthesis.py` (Stage 19) already runs on self-analysis and produces per-node ideome data for the ecosystem's own files.

Collider regularly analyzes its own ecosystem. A Stage 25 that reads Stage 19's node-level ideome output, cross-references with Atlas component mappings, and produces per-component alignment reports is architecturally natural. It's not analyzing "another repo" — it's running `collider full .` on itself.

**But there's a deeper problem with making it ONLY a Collider stage.**

The 15 IDEOME.yaml principles measure ecosystem design conventions — D6 headers, three-tier output, deterministic fallback. These are properties of `wave/tools/ai/` components. Collider's AST analysis can detect SOME of these (grep for `_generated`, count `except: pass`), but others require:

- **Cross-component knowledge:** Principle C4 (feeds documented) needs to cross-reference Atlas entries of DIFFERENT components. A Collider stage analyzing a single file doesn't have this context.
- **Output directory inspection:** Principle A2 (three-tier output) is best verified by checking what files a previous run actually produced — not by static analysis of what the code COULD produce.
- **Longitudinal data:** Principle A3 (JSONL tracking) should verify the JSONL file actually grows across runs — a temporal check that can't be done in a single Collider pass.

---

## Decision: Option D — Two-Layer Architecture

Neither pure Collider stage (A) nor pure standalone tool (B). A two-layer system:

### Layer 1: Collider Stage 25 — "Principle Evidence Collector"

**Runs inside the Collider pipeline**, after Stage 19 (Ideome Synthesis) and Stage 20 (Data Chemistry).

**What it does:**
- Reads `ctx.full_output['ideome']` (Stage 19's per-node drift data)
- Reads `ctx.full_output['nodes']` (AST data from earlier stages)
- For each node, runs deterministic checks that ARE possible from static analysis:
  - A1: grep node source for `_generated` dict construction → `evidence.a1_d6_header`
  - A3: grep for `open(...)` + `"a"` + `.jsonl` pattern → `evidence.a3_longitudinal`
  - A5: grep for `cost`, `token_count`, `usage` → `evidence.a5_cost_tracking`
  - B2: grep for `degradation`, `degraded`, `fallback_level` → `evidence.b2_degradation_signal`
  - B3: grep for self-evaluation patterns (function that checks own output) → `evidence.b3_auto_feedback`
  - B4: count `except: pass` vs `except:` with logging → `evidence.b4_error_observability`
- Stores results as `ctx.full_output['principle_evidence']` — a dict mapping node_id → {principle_id → {found: bool, file: str, line: int, snippet: str}}
- This data persists in `unified_analysis.json` alongside the existing ideome and chemistry data.

**What it does NOT do:**
- Does not compute component-level scores (it doesn't know about CMP-xxx)
- Does not check Atlas entries (that's Layer 2's job)
- Does not inspect output directories or run tools
- Does not produce reports

**Why this belongs in Collider:** It's pure AST/grep analysis on the codebase — exactly what Collider does. The evidence is per-NODE, matching Collider's data model. It enriches the existing data pipeline.

### Layer 2: Component Alignment Scorer — `ideome_scorer_v2.py`

**Runs independently**, after a Collider analysis has been done. Lives at `wave/tools/ai/ideome_scorer_v2.py`.

**What it does:**
1. **Reads `unified_analysis.json`** to get:
   - Stage 19 ideome data (per-node structural drift)
   - Stage 25 principle evidence (per-node grep results from Layer 1)
2. **Reads `ATLAS.yaml`** to get:
   - Component registry (CMP-xxx → source files via `invoke.method`)
   - Domain C integration data (Atlas IS the authority here)
3. **Maps CMP-xxx → source nodes** using Atlas `invoke.method` field → matches node_ids in `unified_analysis.json`
4. **Aggregates node-level evidence to component level:**
   - A1 (D6 header): If ANY node in this component's source files has `evidence.a1_d6_header.found = true` → component passes
   - B4 (Observable failure): Ratio of `evidence.b4_error_observability.logged` vs `evidence.b4_error_observability.swallowed` across all component nodes
5. **Adds Layer 2-only checks:**
   - A2 (Three-tier output): Inspects component's output directory for .json + .md + briefing files
   - A3 (Longitudinal tracking): Checks if JSONL file exists AND has multiple entries (temporal)
   - A4 (Meta envelope): Reads most recent output JSON and validates envelope fields
   - C1-C5: Pure Atlas checks (correct, Atlas IS the authority for integration)
   - B1 (Deterministic fallback): Heuristic — checks if component has a code path that doesn't import API clients (or cached from manual assessment)
   - B5 (Config SSOT): Manual/cached assessment
6. **Produces the alignment report** with full evidence trail:
   - Per-principle: score (0.0-1.0), evidence source (file:line or "output inspection" or "Atlas check"), confidence tier (deterministic/heuristic/manual)
   - Domain scores and overall alignment grade
   - Stored at `.ecoroot/alignment/CMP-xxx.json` (Tier 1) + `.md` (Tier 3)

**Why this is separate from Collider:** It needs cross-component knowledge (Atlas), output directory inspection (filesystem), temporal checks (JSONL growth), and the CMP-xxx mapping layer. These don't fit the Collider pipeline's per-node, per-run model.

---

## How the Two Layers Connect

```
collider full .  (runs on ecosystem)
    │
    ├── Stage 19: ideome_synthesis.py
    │   └── Produces: per-node drift (constraint, declaration, decomposition)
    │       Stored in: ctx.full_output['ideome']
    │
    ├── Stage 20: data_chemistry.py
    │   └── Extracts ideome_coherence as cross-signal
    │
    ├── Stage 25 (NEW): principle_evidence_collector
    │   └── Reads: ctx.full_output['nodes'] + source files
    │   └── Produces: per-node evidence for A1, A3, A5, B2, B3, B4
    │       Stored in: ctx.full_output['principle_evidence']
    │
    └── Output: unified_analysis.json
            Contains: ideome{} + principle_evidence{}


ideome_scorer_v2.py  (runs independently, AFTER collider)
    │
    ├── Reads: unified_analysis.json (ideome + principle_evidence)
    ├── Reads: ATLAS.yaml (CMP-xxx → source files)
    ├── Reads: IDEOME.yaml (principle definitions + weights)
    ├── Inspects: output directories (A2, A4 runtime evidence)
    ├── Inspects: JSONL files (A3 temporal evidence)
    │
    └── Produces:
        ├── .ecoroot/alignment/CMP-xxx.json  (Tier 1 report)
        ├── .ecoroot/alignment/CMP-xxx.md    (Tier 3 human report)
        └── .ecoroot/alignment/alignment_index.jsonl  (longitudinal)
```

---

## Answering the 7 Open Questions

### Q1: Collider stage vs independent? → BOTH (Option D)
Layer 1 is a Collider stage (evidence collection). Layer 2 is independent (component scoring). Neither alone is sufficient.

### Q2: Should the scorer execute the tool? → C (cached output) with optional B (runtime)
Layer 2 inspects output from PREVIOUS runs (cached evidence). An `--execute` flag could optionally run the tool and inspect fresh output, but the default is non-destructive filesystem inspection.

### Q3: Non-code components? → Component-type taxonomy with N/A handling
Define 4 component types:
- **Code tool** (has source, produces output): Full 15-principle scoring
- **Library** (has source, no output artifacts): Domain A scored as N/A except A1. Domain B applicable. Domain C applicable.
- **Infrastructure** (scripts on VPS, no Collider analysis): Domain A and B scored by manual assessment or VPS-specific checks. Domain C applicable.
- **External** (third-party tools like Syncthing): Only Domain C applicable. Domains A and B = N/A.

N/A principles are excluded from the weighted average (weight redistributed to applicable principles).

### Q4: Binary vs graded? → Graded with defined rubrics
Each principle gets a 0.0-1.0 score with defined thresholds:
- 1.0: Full compliance (all subfields present, pattern implemented correctly)
- 0.7: Substantial compliance (main pattern present, minor gaps)
- 0.3: Partial compliance (evidence of intent but incomplete implementation)
- 0.0: No evidence

Example for A1 (D6 header):
- 1.0: `_generated` dict with source, version, timestamp, git_sha all present
- 0.7: `_generated` present with source + timestamp but missing git_sha
- 0.3: Some provenance metadata exists but not in `_generated` format
- 0.0: No provenance metadata found

### Q5: Enforced or advisory? → Advisory NOW, enforced at P3 LATER
Alignment remains FREE for v2 launch. After 3+ months of accurate scoring and the Atlas Validator (EG-001) being built, consider making `alignment >= 0.55 (C)` ENFORCED at P3. This gives components time to improve before enforcement.

### Q6: Human role? → Explicit "unverified" tier with decay
Three confidence tiers in every score:
- **Deterministic:** Checked by code (grep, AST, file existence). Confidence: 1.0.
- **Heuristic:** Checked by pattern matching (grep approximations). Confidence: 0.7.
- **Manual:** Human-assessed. Confidence: starts at 0.9, decays 0.1/month until re-assessed. After 6 months without reassessment: flagged as STALE and excluded from score.

B5 (Config SSOT) and B1 (Deterministic fallback) include manual components. The report clearly marks which principles used manual vs automated evidence.

### Q7: Gaming prevention? → Three mechanisms

1. **Evidence-based scoring (primary):** Every score cites file:line. The report is auditable. Dummy `_generated = {}` would score 0.3 (partial — dict exists but subfields missing), not 1.0.

2. **Collider cross-validation:** Layer 1's AST evidence comes from Collider's actual source analysis, not from what the developer claims. If Collider sees `except: pass` in 80% of exception handlers, B4 scores low regardless of what Atlas says.

3. **Runtime spot-checks (optional):** The `--verify` flag on Layer 2 runs the component and inspects actual output. This catches dummy code paths that exist in source but never execute. Expensive, so optional — but available for promotion reviews (P2→P3).

---

## The 121% Metadata Test

For each Domain A/B principle in the v2 design, verify:

| ID | Evidence source in v2 | YAML-only edit changes score? | Pass? |
|----|---|---|---|
| A1 | Source grep for `_generated` (Layer 1) | No — grep reads .py files, not YAML | ✓ |
| A2 | Output directory inspection (Layer 2) | No — checks actual files on disk | ✓ |
| A3 | Source grep + JSONL file existence (Layer 1 + 2) | No — checks .py + .jsonl files | ✓ |
| A4 | Output JSON inspection (Layer 2) | No — reads actual JSON output | ✓ |
| A5 | Source grep for cost patterns (Layer 1) | No — reads .py files | ✓ |
| B1 | AST code path analysis + manual (Layer 1 + manual) | No — reads AST, not YAML | ✓ |
| B2 | Source grep for degradation field (Layer 1) | No — reads .py files | ✓ |
| B3 | Source grep for self-eval patterns (Layer 1) | No — reads .py files | ✓ |
| B4 | AST exception handler analysis (Layer 1) | No — reads AST | ✓ |
| B5 | Manual assessment with decay | No — human judgment | ✓ |

Domain C uses Atlas by design (Atlas IS the authority). YAML edits DO change C-domain scores — this is correct because C measures ecosystem registration, which IS a YAML activity.

---

## Migration Plan

1. **Rename:** `ideome_scorer.py` → `atlas_completeness_checker.py`. Update any references. This tool remains useful for tracking Atlas documentation quality.
2. **Existing reports:** `.ecoroot/alignment/CMP-xxx.json` files from v0 are tagged with `"source": "ideome", "version": "1.0.0"`. v2 reports use `"version": "2.0.0"`. Both can coexist. v0 reports should be marked as `deprecated` in their `_generated` header.
3. **IDEOME.yaml:** Preserved as-is. v2 adds `evidence_method` and `partial_credit` fields to each principle but doesn't change the principle definitions or weights.
4. **Layer 1 (Stage 25):** New Collider stage. Requires re-running `collider full .` to populate `principle_evidence` in `unified_analysis.json`. Until then, Layer 2 operates in "no-evidence" mode (lower confidence, Atlas-only for Domain C, manual for A/B).
5. **Layer 2:** Replaces v0 scorer. Same CLI interface (`--component CMP-xxx`, `--all`, `--auto`). Reports stored at same location. Backward-compatible.
