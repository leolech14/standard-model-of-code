# Socratic Validator Extraction: Design Spec

**Date:** 2026-03-16
**Status:** Approved
**Scope:** Extract Socratic Validator from analyze.py (4,136 lines) into standalone package
**Goal:** Proof-of-concept decomposition. First sub-engine extracted from the gateway monolith.

---

## Problem

`analyze.py` is a 4,136-line gateway monolith containing 3 distinct sub-engines:
1. ACI Router (tier dispatch)
2. Research Engine (multi-config orchestration)
3. Socratic Validator (hypothesis-driven semantic verification)

The Socratic Validator (~460 lines, lines 1986-2446) is the cleanest extraction target:
- Has its own class (`SocraticValidator`)
- Has its own config file (`semantic_models.yaml`)
- Has a duplicate `verify_domain()` function (lines 2161 AND 2318) confirming it was already trying to split
- Has its own output format (JSON audit + markdown report)

## Architecture

### Risk Mitigation: _shared.py

analyze.py has a venv bootstrap at lines 84-98 that uses `os.execv()` to re-execute under `.tools_venv`. Importing analyze.py from the socratic package would trigger this, replacing the process.

**Solution:** Extract shared utilities into `wave/tools/ai/_shared.py` -- a module with zero venv bootstrap side effects. Both analyze.py and the socratic package import from `_shared`.

**Scope intent:** `_shared.py` is deliberately broad (16+ functions). It is the foundation for ALL future sub-engine extractions (ACI Router, Research Engine), not just socratic. Accepting this scope means analyze.py gains a hard dependency on `_shared.py` -- this is the desired architecture direction. The monolith becomes a thin CLI shell importing from `_shared` + sub-packages.

### Package Structure

```
wave/tools/ai/
  _shared.py              # NEW: shared utilities (no venv bootstrap)
  analyze.py              # MODIFIED: shrinks ~460 lines, imports from _shared
  socratic/               # NEW: extracted package
    __init__.py           # Public API
    models.py             # Pydantic data models
    hypothesis.py         # Hypothesis generation from config
    verifier.py           # 3-phase verification loop
    validator.py          # SocraticValidator class (antimatter detection)
    domain_runner.py      # verify_domain() orchestrator + output
    cli.py                # Standalone CLI entry point
```

### _shared.py Contents

Extracted from analyze.py with zero venv bootstrap logic:

| Function | From analyze.py | Purpose |
|----------|----------------|---------|
| `PROJECT_ROOT` | Line 74 | Path constant |
| `SEMANTIC_MODELS_PATH` | Line 213 | Config path |
| `DEFAULT_MODEL` | Line 381 | Model name (loaded from prompts.yaml) |
| `FAST_MODEL` | Line 383 | Fast model name |
| `PRICING` | Line 389 | Token pricing dict |
| `read_file_content()` | Lines 1445-1464 | UTF-8 file reading with line numbers |
| `retry_with_backoff()` | Lines 1504-1525 | Exponential retry on rate limits |
| `auto_diagnose_error()` | Lines 1475-1501 | Parse Gemini errors |
| `estimate_cost()` | Lines 1467-1472 | Token cost estimation |
| `create_client()` | Lines 1629-1694 | Gemini client factory |
| `create_developer_client()` | Lines 1235-1323 | File Search client factory |
| `list_file_search_stores()` | Lines 1029-1063 | Store listing |
| `get_or_create_store()` | Lines 1039-1063 | Store acquisition |
| `search_with_file_search()` | Lines 1111-1171 | RAG query with citations |
| `list_local_files()` | Lines 1342-1418 | File discovery with security excludes |
| `index_files_to_store()` | Lines 1065-1108 | File indexing |
| `load_sets_config()` | Lines 372-376 | YAML config loader |
| `PROMPTS_CONFIG_PATH` | Line 212 | Path to prompts.yaml |
| `BACKEND` | Line 418 | `aistudio` or `vertex` (computed from env/config) |
| `_find_doppler()` | Lines 1251-1267 | Locate doppler binary |
| `get_doppler_secret()` | Lines 1270-1287 | Read secret from Doppler |
| `get_gcloud_project()` | Lines 1326-1331 | GCP project for Vertex AI |
| `get_access_token()` | Lines 1334-1339 | GCP auth token for Vertex AI |
| Config resolution block | Lines 372-418 | Model selection, backend, pricing |

**Transitive dependency note:** `create_client()` depends on `get_doppler_secret()`, `get_gcloud_project()`, `get_access_token()`, `BACKEND`, and the config resolution block. All must move together.

**Critical:** `_shared.py` imports google.genai at the top (after checking the venv path is correct via sys.prefix, but WITHOUT os.execv). If the venv is wrong, it raises ImportError instead of replacing the process.

### Data Models (socratic/models.py)

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import datetime

class Hypothesis(BaseModel):
    concept: str
    claim: str
    description: str
    invariants: List[str]
    anchors: List[Dict[str, str]] = Field(default_factory=list)
    scope: str = ""

class VerificationResult(BaseModel):
    verified: bool
    candidates: List[str] = Field(default_factory=list)
    analysis: str = ""
    guardrails: Dict[str, Any] = Field(default_factory=dict)
    reason: Optional[str] = None

class AuditReport(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    generated: Dict[str, Any] = Field(default_factory=dict, alias="_generated")
    domain: str
    timestamp: str
    hypotheses_count: int
    verified_count: int
    violation_count: int
    results: List[Dict[str, Any]] = Field(default_factory=list)
    markdown: str = ""
```

### hypothesis.py

Pure function, no dependencies beyond models:

```python
def generate_hypotheses(domain_config: dict) -> List[Hypothesis]:
    """Convert domain definitions from semantic_models.yaml into testable hypotheses."""
```

Extracted from analyze.py lines 1986-2012. Stateless.

### validator.py

The `SocraticValidator` class (analyze.py lines 2246-2304):

```python
class SocraticValidator:
    """Critic Agent: detect AI liabilities (Antimatter Patterns)."""

    def __init__(self, semantic_config: dict):
        self.laws = semantic_config.get('antimatter', [])

    def validate(self, client, model: str, code_context: str, concept_role: str) -> dict:
        """Run antimatter audit. Returns {compliant, violations, critique_summary}."""
```

Depends on: `retry_with_backoff` from `_shared`.

### verifier.py

The 3-phase verification loop (analyze.py lines 2014-2159):

```python
def verify_hypothesis(
    dev_client, vertex_client, hypothesis: Hypothesis,
    store_name: str, candidate_override: str = None,
    project_root: Path = None,
) -> VerificationResult:
    """
    Phase A: Discovery (anchors, File Search fallback)
    Phase B: Deep verification (Gemini invariant check)
    Phase C: Socratic validation (antimatter audit)
    """
```

Depends on: `_shared` (read_file_content, retry_with_backoff, search_with_file_search, DEFAULT_MODEL, PROJECT_ROOT).

**Change from original:** `PROJECT_ROOT` passed as parameter instead of module-level global. Makes the function testable with any repo path.

**Dead code cleanup:** Lines 2056-2063 contain a dead `pass` block that shadows the real File Search fallback at line 2066. During extraction, remove the dead block and keep only the canonical File Search path (lines 2066-2082).

### domain_runner.py

Merges the two duplicate `verify_domain()` functions (lines 2161-2242 and 2318-2446) into one canonical version. Takes the second copy as canonical (has intelligence storage + dict-aware output).

Also contains `load_semantic_models()` (moved from analyze.py lines 2306-2311).

**GCS sync:** The original code syncs to `gs://elements-archive-2026/intelligence` via `gsutil`. Since GCS billing is disabled (T4 Cold deferred), this call always fails silently. Make it conditional: only attempt if `gsutil` is on PATH and `--sync-gcs` flag is passed. Default: skip.

```python
def verify_domain(
    domain: str,
    store_name: str = None,
    output: str = None,
    index: bool = False,
    candidate: str = None,
    project_root: Path = None,
) -> AuditReport:
    """Orchestrate full domain verification with three-tier output."""
```

Outputs:
- `.socratic/latest_report.json` (Tier 1: full AuditReport)
- `.socratic/latest_briefing.json` (Tier 2: reserved for future AI briefing, not implemented yet)
- `.socratic/latest_report.md` (Tier 3: markdown)
- `.socratic/run_index.jsonl` (longitudinal tracking)
- `wave/intelligence/socratic_audit_{domain}_{timestamp}.json` (legacy path, kept for backward compat)

### cli.py

Standalone entry point. Uses `sys.path` preamble matching analyze.py line 178 pattern:

```python
# cli.py top:
import sys
from pathlib import Path
_AI_DIR = Path(__file__).resolve().parent.parent  # wave/tools/ai/
sys.path.insert(0, str(_AI_DIR))
```

```bash
# From PROJECT_elements root:
doppler run -- .venv/bin/python3 wave/tools/ai/socratic/cli.py --domain atoms
doppler run -- .venv/bin/python3 wave/tools/ai/socratic/cli.py --domain atoms --candidate particle/src/core/atom.py
doppler run -- .venv/bin/python3 wave/tools/ai/socratic/cli.py --domain pipeline --index
doppler run -- .venv/bin/python3 wave/tools/ai/socratic/cli.py --list-domains
```

### __init__.py

```python
from .domain_runner import verify_domain
from .validator import SocraticValidator
from .hypothesis import generate_hypotheses
from .models import Hypothesis, VerificationResult, AuditReport

__all__ = [
    "verify_domain", "SocraticValidator", "generate_hypotheses",
    "Hypothesis", "VerificationResult", "AuditReport",
]
```

## Changes to analyze.py

1. **Delete lines 1986-2446** (~460 lines removed)
2. **Delete duplicate verify_domain** (both copies gone)
3. **Delete load_semantic_models** (moved to socratic package)
4. **Replace --verify handler** (line 2532) with:
   ```python
   if args.verify:
       from socratic import verify_domain
       verify_domain(args.verify, store_name=args.store_name,
                     output=args.output, index=args.index,
                     candidate=args.candidate)
       sys.exit(0)
   ```
5. **Move shared utilities to _shared.py**, replace with imports in analyze.py:
   ```python
   from _shared import (
       PROJECT_ROOT, read_file_content, retry_with_backoff,
       create_client, create_developer_client, ...
   )
   ```

analyze.py shrinks from ~4,136 to ~3,600 lines.

## Atlas & Registry

**New CMP-090 (P2):**
```yaml
- id: CMP-090
  kind: component
  name: socratic-validator
  display_name: Socratic Semantic Validator
  purpose: Hypothesis-driven code verification against semantic definitions with antimatter pattern detection.
  owner: leo
  application: wave-ai-tools
  stage: P2
  version: "1.0.0"
  status: active
  category: verification
  delivery: cli_tool
  tags: [ai, verification, semantic, audit, socratic]
  invoke:
    method: "doppler run -- python -m socratic --domain {domain}"
    environment: [doppler:ai-tools/prd/GEMINI_API_KEY]
  inputs:
    - name: domain
      type: string
      required: true
      description: Domain name from semantic_models.yaml
    - name: candidate
      type: string
      required: false
      description: Explicit file path to verify (skips discovery)
  outputs:
    - name: audit_report
      type: file:json
      description: Full AuditReport with hypothesis results and guardrails
    - name: audit_markdown
      type: file:md
      description: Human-readable verification report
    - name: run_index
      type: file:jsonl
      description: Longitudinal tracking
  metrics:
    usage_event: socratic_domain_verified
    cost_metric: "$0.10-$2.00 per domain (depends on hypothesis count and file context size)"
  requires_connections: [CON-008]
  feeds_into: [CMP-052]
  fed_by: [CMP-052]
  agent:
    explanation: >
      Socratic Validator — hypothesis-driven semantic verification. Given a domain
      (e.g., "atoms", "pipeline") and its definitions in semantic_models.yaml,
      generates testable hypotheses, discovers candidate implementations via anchors
      or File Search, verifies invariants via Gemini, then runs antimatter pattern
      detection (Socratic critique). Outputs structured JSON + markdown report.
    context_priority: 0.4
    affordances:
      can_read: [codebase, semantic_models.yaml, file_search_stores]
      can_write: [.socratic/, wave/intelligence/]
      cannot: [modify_source_code, commit, deploy]
```

**New ECO-061 in TOOLS_REGISTRY.yaml**

**Updated CMP-052:** Add CMP-090 to feeds_into and fed_by.

## Verification Plan

1. `python -m socratic --list-domains` -- lists available domains from semantic_models.yaml
2. `python -m socratic --domain atoms --candidate particle/src/core/atom.py` -- runs targeted verification
3. Verify `.socratic/latest_report.json` and `.socratic/latest_report.md` are created
4. Verify `.socratic/run_index.jsonl` has 1 entry
5. Verify analyze.py `--verify atoms` still works (imports from socratic package)
6. Verify analyze.py line count decreased by ~460

## Not In Scope

- MCP server for socratic (Approach 3, deferred)
- Extracting other sub-engines (ACI Router, Research Engine)
- Extracting _shared.py utilities into their own Atlas components
- Tier 2 AI briefing for socratic output (batch tool, not query tool)
- Refactoring the verification prompts (LLM prompt engineering)
