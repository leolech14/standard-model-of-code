# Ideome Architecture: Open Critique & Design Map

**Date:** 2026-03-16
**Status:** DRAFT — requires scrutiny before v2 implementation
**Author:** Session analysis (Claude Opus 4.6)

---

## What We Built (v0)

A scoring engine (`ideome_scorer.py`) that checks 15 principles across 3 domains by reading Atlas YAML entries. It produces per-component alignment reports.

**First run results:** 21 components scored. Average: 0.24 (F) -> 0.53 (D) after Atlas YAML enrichment.

**The problem:** The score improved by 121% from editing YAML metadata, not from any component actually improving. The scorer measures **documentation completeness**, not **alignment to principles**.

---

## The Architecture Gap

### What exists (3 disconnected layers)

```
Layer 1: CODOME (what IS)
├── Source code, ASTs, dependency graphs
├── Collider reads this (stages 1-24)
├── Produces: unified_analysis.json, collider_insights.json, collider.db
├── Contains: 8D health score, topology, constraints, dead code, etc.
└── Confidence: 0.55-0.85 (deterministic)

Layer 2: ATLAS (what we CLAIM)
├── YAML metadata about components
├── Fields: id, name, purpose, outputs, metrics, affordances
├── Progressive Requirements (P0-P5) enforce field presence
├── Contains: claims about what components do
└── Confidence: UNVERIFIED (human-authored, drift-prone)

Layer 3: IDEOME (what SHOULD BE)
├── IDEOME.yaml: 15 principles, 3 domains
├── Defines: D6 headers, three-tier output, deterministic fallback, etc.
├── Currently: principles are defined but not connected to evidence
└── Confidence: 0.40 (Collider's lowest category — speculative)
```

### What's missing (the bridge)

```
Layer 1 (Codome truth) ←→ Layer 3 (Ideome principles)
         ↑                          ↑
         |                          |
    NOT CONNECTED              NOT CONNECTED
         |                          |
         ↓                          ↓
    Layer 2 (Atlas claims) ← current scorer checks THIS
```

The scorer checks Layer 2 against Layer 3. It should check Layer 1 against Layer 3.

---

## What Each Principle Actually Needs

### Domain A: Output Contract

| ID | Principle | v0 checks (Atlas YAML) | Should check (Codome truth) |
|----|-----------|----------------------|---------------------------|
| A1 | D6 `_generated` header | "Does Atlas say outputs include JSON?" | Grep source code for `_generated` dict construction. Run tool, inspect output JSON for the field. |
| A2 | Three-tier output | "Does Atlas list 3 output types?" | Check output directory for actual .json + .md/.html + briefing files after a real run. |
| A3 | Longitudinal tracking | "Does Atlas mention JSONL?" | Check for `open(..., "a")` + `.jsonl` pattern in source. Verify file grows across runs. |
| A4 | Meta envelope | "Same as A1" | Inspect actual output JSON for run_id, timestamp, hostname, processing_time fields. |
| A5 | Cost awareness | "Does Atlas have metrics.cost_metric?" | Check source for token counting + cost estimation logic. Inspect output for cost fields. |

### Domain B: Operational Resilience

| ID | Principle | v0 checks (Atlas YAML) | Should check (Codome truth) |
|----|-----------|----------------------|---------------------------|
| B1 | Deterministic fallback | "Does description mention 'fallback'?" | Trace code path with no API keys. Does it produce output? Does it have a non-LLM code path? |
| B2 | LLM degradation signal | "Does Atlas text contain 'degradation'?" | Check source for degradation model/field. Inspect output when LLM unavailable. |
| B3 | Auto-feedback | "Does Atlas mention 'feedback'?" | Check for self-evaluation logic: does the component run checks on its own output? |
| B4 | Observable failure | "Does description mention 'error'?" | Check exception handlers: do they log or silently pass? Count `except: pass` patterns. |
| B5 | Config single-source | "Return 0.5 (unknown)" | Count configuration surfaces. Check if derived configs match declared SSOT. |

### Domain C: Ecosystem Integration

| ID | Principle | v0 checks (Atlas YAML) | Should check (Codome truth) |
|----|-----------|----------------------|---------------------------|
| C1 | Atlas registered P2+ | "Check Atlas for entry" | This one IS correct (Atlas IS the source of truth for registration). |
| C2 | Tools registry entry | "Check TOOLS_REGISTRY" | This one IS correct (registry IS the source of truth). |
| C3 | Progressive compliance | "Check field presence" | This one IS mostly correct (field presence is the check). But should also validate field CONTENT is real. |
| C4 | Feeds documented | "Check non-empty feeds" | Cross-validate: do declared feeds actually exist as code-level imports/calls? |
| C5 | Agent affordances | "Check 3 subfields" | Cross-validate: does `cannot: [modify_source_code]` hold? Does the tool actually NOT write to source files? |

**Verdict:** Domain C is mostly valid as YAML checks (the Atlas IS the authority for integration claims). Domains A and B are fundamentally broken — they check claims, not evidence.

---

## The Collider Bridge Architecture

### Option 1: Ideome as Collider Stage 25

```
Collider Pipeline (existing stages 1-24)
  → Stage 25: Ideome Alignment
      Input: unified_analysis.json (Codome structural truth)
      Input: IDEOME.yaml (principles)
      Process:
        A1: Search AST for _generated dict pattern in output functions
        A2: Count distinct output format types (JSON, MD, HTML, JSONL)
        A3: Search for append("a") + jsonl pattern
        B1: Trace entry points — is there a non-API code path?
        B4: Count except-pass vs except-log patterns
        ...etc
      Output: alignment_report.json (per-principle with CODE EVIDENCE)
```

**Pro:** Uses Codome truth. Deterministic. Runs automatically with every Collider analysis.
**Con:** Only works for code components that Collider can analyze. Doesn't cover infrastructure (EcoSync), services (OpenClaw gateway), or external tools.

### Option 2: Hybrid Scorer (Codome + Atlas + Runtime)

```
ideome_scorer_v2.py
  ├── Source checks (grep/AST) — for principles checkable from code
  ├── Atlas checks (YAML) — for integration principles (C1-C5)
  ├── Runtime checks (execute tool, inspect output) — for output principles
  └── Manual overrides (human-declared) — for uncheckable principles
```

**Pro:** Most complete. Handles all component types.
**Con:** Runtime checks require executing the tool (API keys, dependencies, side effects). Expensive.

### Option 3: Evidence-Attached Atlas Claims

```
Atlas entry:
  outputs:
    - name: evolution_report
      type: file:json
      evidence:                    # NEW: prove the claim
        source_file: wave/tools/mcp/reh_evolution.py
        source_line: 91
        pattern: "\"_generated\": _d6_header()"
        last_verified: 2026-03-16
```

**Pro:** Atlas remains the single scoring surface, but claims have evidence pointers.
**Con:** Evidence can still drift from code. Someone has to maintain the pointers.

---

## Open Questions (Need Answers Before v2)

### Q1: What is the ideome's relationship to Collider?

Options:
- A) Ideome IS a Collider stage (fully integrated, runs on Collider's Codome)
- B) Ideome USES Collider output (reads unified_analysis.json, independent scorer)
- C) Ideome is independent (doesn't use Collider, has its own source analysis)

Tradeoffs: A is most rigorous but couples ideome to Collider's pipeline. C is most independent but duplicates analysis.

### Q2: Should the scorer execute the tool?

If A2 checks for three-tier output, should it:
- A) Grep source code for output file writes (static)
- B) Actually run the tool and inspect the output directory (runtime)
- C) Check if output files from a previous run exist (cached evidence)

Tradeoffs: A is fast but can miss runtime-only patterns. B is accurate but expensive and requires API keys/dependencies. C is pragmatic but evidence gets stale.

### Q3: What about non-code components?

EcoSync (infrastructure), OpenClaw Gateway (service), Syncthing (external tool) — these don't have source code in PROJECTS_all that Collider can analyze. How do we score them?

Options:
- A) Different scoring schema for infrastructure vs code
- B) Score only what's scorable, mark the rest N/A
- C) Extend the ideome to have infrastructure-specific principles

### Q4: Is binary (0/1) scoring appropriate?

v0 uses binary checks. But "has a D6 header" is not binary in practice:
- Has it on main output but not on secondary artifacts (0.7?)
- Has a partial header (source + timestamp but no git_sha) (0.5?)
- Has it but with wrong schema (0.3?)

Should principles have graded scoring (0.0-1.0) instead of binary?

### Q5: Should alignment be enforced or advisory?

Currently `alignment` is a FREE field in Atlas (any stage can have it, none required). Should it become ENFORCED at some stage?

- If P3 enforces alignment >= 0.55 (C), it means "others depend on you, so prove you're aligned"
- If never enforced, it's advisory only (useful but ignorable)

### Q6: What role does the human play?

Some principles (B5: config single-source) can't be checked automatically. Options:
- A) Skip uncheckable principles in --auto mode (current approach, loses signal)
- B) Use last-known human assessment (decays over time)
- C) Flag as "unverified" in the report with explicit confidence

### Q7: How do we prevent gaming?

If alignment score is tracked and visible, there's incentive to optimize for the score rather than the principle. A component could add a dummy `_generated` field without actually using it. How do we ensure the score reflects genuine alignment?

- Evidence-based scoring (show me the code, not the claim)
- Random spot-checks (run the tool, verify output)
- Cross-validation (does Collider's structural analysis agree with ideome claims?)

---

## What v0 Got Right

1. **IDEOME.yaml principles are sound.** The 15 principles across 3 domains capture real ecosystem values. They were derived from patterns proven across 3 tools (Collider, REH, YTPipe) this session.

2. **Three-domain weighting is reasonable.** Output Contract (40%), Operational Resilience (35%), Ecosystem Integration (25%) matches the real priority: what you produce > how you fail > how you fit.

3. **Grade mapping matches Collider.** A >= 0.85, B >= 0.70, etc. Consistent scale across the ecosystem.

4. **Longitudinal tracking pattern.** alignment_index.jsonl enables "is the ecosystem getting more aligned over time?" queries.

5. **The Atlas enrichment was genuine value.** 17 thin entries getting outputs, metrics, and affordances is real documentation work that helps agents navigate the ecosystem — even if the scorer shouldn't have treated it as "alignment improvement."

## What v0 Got Wrong

1. **Checking Atlas YAML instead of Codome truth.** The scorer verifies metadata, not reality. A component can score B by having the right YAML fields while its code does none of those things.

2. **Binary scoring hides nuance.** A component with a partial D6 header (missing git_sha) scores the same as one with no header at all: 0.

3. **No evidence trail.** The report says "A1: 1" but doesn't show WHERE in the code the D6 header is constructed. Without evidence, the score is unverifiable.

4. **Heuristic checks are keyword matching.** B1 (deterministic fallback) checks if the word "fallback" appears in the description. This is not analysis — it's grep on marketing copy.

5. **The 121% improvement from YAML editing.** This should never be possible. If editing metadata doubles your alignment score, the score doesn't measure alignment.

---

## Recommended Next Steps

1. **Scrutinize IDEOME.yaml principles** — Are these the right 15? Are any missing? Are any wrong?
2. **Choose the bridge architecture** (Q1) — Collider stage vs hybrid vs evidence-attached Atlas
3. **Design v2 checks** — For each principle, define what Codome evidence looks like
4. **Build v2 scorer** — Reads Codome (source code / Collider output), not just Atlas
5. **Backtest** — Score the 3 tools we elevated this session (YTPipe, REH, analyze.py) with v2 and compare to v0 scores
