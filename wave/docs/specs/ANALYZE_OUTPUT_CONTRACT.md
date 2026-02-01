# analyze.py Output Contract Specification

**Status:** PROPOSED
**Date:** 2026-01-27
**Priority:** P0 (Foundation for all other improvements)

---

## Problem Statement

analyze.py currently outputs prose to stdout. This works for human readers but fails the Stone Tool test:
- AI agents cannot programmatically consume results
- No auditability of what context was actually used
- No reproducibility (same query may see different files)
- Deck cannot close the loop without structured data

---

## Contract: Structured Output

### 1. New Flag: `--output`

```bash
python analyze.py --aci --output json "question"   # JSON to stdout
python analyze.py --aci --output md "question"     # Markdown to stdout (current behavior)
python analyze.py --aci --output bundle "question" # JSON + manifest + artifacts to directory
```

Default: `md` (backward compatible)

### 2. JSON Schema (v1)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AnalyzeResult",
  "type": "object",
  "required": ["run_id", "query", "aci", "context", "answer"],
  "properties": {
    "run_id": {
      "type": "string",
      "description": "ISO timestamp + short hash: 2026-01-27T12:34:56Z__a1b2c3"
    },
    "query": {
      "type": "string",
      "description": "The user's question"
    },
    "mode": {
      "type": "string",
      "enum": ["standard", "architect", "forensic", "insights"]
    },
    "models": {
      "type": "object",
      "properties": {
        "primary": { "type": "string", "description": "Main reasoning model" },
        "context_expander": { "type": "string", "description": "2M model if used" },
        "external": { "type": "string", "description": "Perplexity if used" }
      }
    },
    "aci": {
      "type": "object",
      "properties": {
        "tier": { "type": "string" },
        "primary_sets": { "type": "array", "items": { "type": "string" } },
        "merged_sets": { "type": "array", "items": { "type": "string" } },
        "confidence": { "type": "number" },
        "reasoning": { "type": "string" }
      }
    },
    "context": {
      "type": "object",
      "description": "CRITICAL: The manifest of what was actually seen",
      "properties": {
        "bundle_hash": {
          "type": "string",
          "description": "SHA256 of concatenated file contents for reproducibility"
        },
        "token_estimate": { "type": "integer" },
        "char_count": { "type": "integer" },
        "truncated": { "type": "boolean" },
        "limits": {
          "type": "object",
          "properties": {
            "max_files": { "type": "integer" },
            "max_tokens": { "type": "integer" }
          }
        },
        "injections": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": { "type": "string", "enum": ["critical_files", "architect_docs", "agent_kernel", "agent_tasks", "deck_snapshot"] },
              "files": { "type": "array", "items": { "type": "string" } },
              "strategy": { "type": "string", "enum": ["front-load", "sandwich", "append"] },
              "tokens": { "type": "integer" }
            }
          }
        },
        "files_included": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "path": { "type": "string" },
              "tokens": { "type": "integer" },
              "lines": { "type": "integer" }
            }
          }
        },
        "files_excluded": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "path": { "type": "string" },
              "reason": { "type": "string", "enum": ["max_files_cutoff", "token_budget", "exclude_pattern", "binary", "too_large"] }
            }
          }
        }
      }
    },
    "external": {
      "type": "object",
      "description": "Perplexity/external research if used",
      "properties": {
        "requested": { "type": "boolean" },
        "queries": { "type": "array", "items": { "type": "string" } },
        "results": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "query": { "type": "string" },
              "answer": { "type": "string" },
              "citations": { "type": "array", "items": { "type": "string" } }
            }
          }
        }
      }
    },
    "answer": {
      "type": "object",
      "properties": {
        "summary": { "type": "string", "description": "1-3 sentence TL;DR" },
        "body": { "type": "string", "description": "Full response (markdown)" },
        "citations": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "path": { "type": "string" },
              "lines": { "type": "string", "description": "L10-L20 format" },
              "snippet": { "type": "string" }
            }
          }
        },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "actions": {
      "type": "array",
      "description": "Recommended follow-up actions",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["recommend_set", "recommend_card", "flag_issue", "suggest_bundle"] },
          "target": { "type": "string" },
          "reason": { "type": "string" }
        }
      }
    },
    "artifacts": {
      "type": "array",
      "description": "Files generated by this run",
      "items": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "kind": { "type": "string", "enum": ["report", "manifest", "deck_patch", "bundle"] }
        }
      }
    },
    "timing": {
      "type": "object",
      "properties": {
        "total_ms": { "type": "integer" },
        "context_build_ms": { "type": "integer" },
        "model_call_ms": { "type": "integer" },
        "external_ms": { "type": "integer" }
      }
    },
    "cost": {
      "type": "object",
      "properties": {
        "input_tokens": { "type": "integer" },
        "output_tokens": { "type": "integer" },
        "estimated_usd": { "type": "number" }
      }
    }
  }
}
```

### 3. Manifest-Only Mode

For debugging/auditing without running the full query:

```bash
python analyze.py --aci --emit-manifest-only --set theory "question"
# Outputs ONLY the context section (what would be seen)
# Does NOT call the model
# Useful for: validating sets, checking truncation, building bundles
```

### 4. Bundle Output Mode

```bash
python analyze.py --aci --output bundle --bundle-dir ./runs/my_analysis "question"
```

Creates:
```
./runs/my_analysis/
├── result.json          # Full JSON output
├── manifest.json        # Just the context section (for reuse)
├── answer.md            # Human-readable report
├── deck_patch.json      # Recommended deck actions (if any)
└── context_bundle.json  # Reusable context snapshot
```

---

## Implementation Plan

### Phase 1: Add `--output json` (Minimal)

1. Add argparse flag
2. Create `AnalyzeResult` dataclass
3. Collect context metadata during `build_context_from_files()`
4. Wrap response in JSON structure
5. Output to stdout or file

### Phase 2: Add Manifest Collection

1. Track files included/excluded with reasons
2. Compute bundle_hash (SHA256 of sorted file contents)
3. Track injections with token counts
4. Add `--emit-manifest-only` flag

### Phase 3: Add Bundle Mode

1. Create output directory
2. Split outputs into separate files
3. Generate `deck_patch.json` skeleton

---

## Backward Compatibility

- Default `--output md` preserves current behavior
- Existing scripts continue to work
- New features are opt-in via flags

---

## Success Criteria

1. AI agent can parse any analyze.py output programmatically
2. Every run is auditable (what files were seen)
3. Runs are reproducible (same bundle_hash = same context)
4. Deck can consume `deck_patch.json` to close the loop

---

## Related Specs

- `THEORY_AMENDMENT_2026-01.md` - Tools as Objects (TOOLOME)
- `AI_CONSUMER_CLASS.md` - Stone Tool Principle
- Deck integration spec (TBD)
- Chain spec for Gemini→Perplexity→Gemini (TBD)
