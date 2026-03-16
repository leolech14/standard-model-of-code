# Socratic Validator Extraction Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the Socratic Validator (~460 lines) from `analyze.py` into a standalone `wave/tools/ai/socratic/` package, creating `_shared.py` as the shared utility foundation.

**Architecture:** Two-phase extraction. Phase A creates `_shared.py` (shared utilities extracted from analyze.py, no venv bootstrap). Phase B creates the `socratic/` package (7 files) and removes the code from analyze.py. analyze.py's `--verify` flag continues working via lazy import from the new package.

**Tech Stack:** Python 3.14, Pydantic v2, google-genai SDK, PyYAML, existing `.venv`

**Spec:** `docs/superpowers/specs/2026-03-16-socratic-validator-extraction-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `wave/tools/ai/_shared.py` | **Create** | Shared utilities: paths, config, clients, file ops, retry logic |
| `wave/tools/ai/socratic/__init__.py` | **Create** | Public API exports |
| `wave/tools/ai/socratic/models.py` | **Create** | Pydantic models: Hypothesis, VerificationResult, AuditReport |
| `wave/tools/ai/socratic/hypothesis.py` | **Create** | generate_hypotheses() -- config to hypothesis transform |
| `wave/tools/ai/socratic/validator.py` | **Create** | SocraticValidator class -- antimatter pattern detection |
| `wave/tools/ai/socratic/verifier.py` | **Create** | verify_hypothesis() -- 3-phase verification loop |
| `wave/tools/ai/socratic/domain_runner.py` | **Create** | verify_domain() orchestrator + output management |
| `wave/tools/ai/socratic/cli.py` | **Create** | Standalone CLI entry point |
| `wave/tools/ai/analyze.py` | **Modify** | Remove ~460 lines, add _shared imports, update --verify handler |
| `atlas/ATLAS.yaml` | **Modify** | Add CMP-090, update CMP-052 |
| `.ecoroot/TOOLS_REGISTRY.yaml` | **Modify** | Add ECO-061 |
| `.gitignore` | **Modify** | Add `.socratic/` |

---

## Chunk 1: Foundation (_shared.py + models)

### Task 1: Create _shared.py

**Files:**
- Create: `wave/tools/ai/_shared.py`

This is the critical risk mitigation. Must have zero venv bootstrap side effects.

- [ ] **Step 1: Create _shared.py with path constants and config loading**

```python
"""
Shared utilities for wave/tools/ai/ ecosystem.

Extracted from analyze.py to break the os.execv() venv bootstrap dependency.
This module has ZERO side effects on import -- no process replacement, no
interactive prompts. If the venv is wrong, imports fail cleanly via ImportError.

Foundation for: socratic/, future ACI Router extraction, Research Engine extraction.
"""

import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# --- Path constants ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
SETS_CONFIG_PATH = PROJECT_ROOT / "wave/config/analysis_sets.yaml"
PROMPTS_CONFIG_PATH = PROJECT_ROOT / "wave/config/prompts.yaml"
SEMANTIC_MODELS_PATH = PROJECT_ROOT / "wave/config/semantic_models.yaml"

# --- Config loading ---
def _load_prompts_config() -> dict:
    """Load prompts.yaml for model names, pricing, modes."""
    if PROMPTS_CONFIG_PATH.exists():
        with open(PROMPTS_CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    return {}

_PROMPTS = _load_prompts_config()

# Model selection
DEFAULT_MODEL = _PROMPTS.get("default_model", "gemini-3-pro-preview")
FAST_MODEL = _PROMPTS.get("fast_model", "gemini-2.0-flash-001")
FALLBACK_MODELS = _PROMPTS.get("fallback_models", [])
PRICING = _PROMPTS.get("pricing", {})
MODES = _PROMPTS.get("modes", {})

# Backend selection
GEMINI_API_KEY_ENV = _PROMPTS.get("api_key_env", "GEMINI_API_KEY")
_GEMINI_BACKEND_ENV = os.environ.get("GEMINI_BACKEND", "")
BACKEND = _GEMINI_BACKEND_ENV or _PROMPTS.get("backend", "aistudio")


# --- Doppler / secrets ---
def _find_doppler() -> str:
    """Find doppler executable in PATH or common locations."""
    import shutil
    if shutil.which("doppler"):
        return "doppler"
    candidates = [
        os.path.expanduser("~/.local/bin/doppler"),
        "/usr/local/bin/doppler",
        "/opt/homebrew/bin/doppler",
        "/usr/bin/doppler",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "doppler"


def get_doppler_secret(key: str) -> Optional[str]:
    """Fetch a secret from Doppler. Returns None if unavailable."""
    try:
        doppler_exe = _find_doppler()
        result = subprocess.run(
            [doppler_exe, "secrets", "get", key, "--plain"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


# --- Gemini clients ---
try:
    from google import genai
    from google.genai.types import Part
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    genai = None
    Part = None


def get_gcloud_project() -> Optional[str]:
    try:
        res = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True, text=True,
        )
        return res.stdout.strip() if res.returncode == 0 else None
    except Exception:
        return None


def get_access_token() -> Optional[str]:
    try:
        res = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True, text=True,
        )
        return res.stdout.strip() if res.returncode == 0 else None
    except Exception:
        return None


def create_client():
    """Create a Gemini client (AI Studio or Vertex AI).

    Returns (client, identifier_string) or (None, error_string).
    """
    if not HAS_GENAI:
        return None, "google-genai not installed"

    if BACKEND == "vertex":
        project = get_gcloud_project()
        if not project:
            return None, "No GCP project found"
        client = genai.Client(
            vertexai=True,
            project=project,
            location="us-central1",
        )
        return client, f"vertex:{project}"
    else:
        api_key = os.environ.get(GEMINI_API_KEY_ENV) or get_doppler_secret("GEMINI_API_KEY")
        if not api_key:
            return None, f"No API key (set {GEMINI_API_KEY_ENV} or configure Doppler)"
        client = genai.Client(api_key=api_key)
        return client, "aistudio"


def create_developer_client():
    """Create a Gemini Developer API client for File Search."""
    if not HAS_GENAI:
        return None

    api_key = get_doppler_secret("GEMINI_API_KEY")
    if not api_key:
        api_key = os.environ.get(GEMINI_API_KEY_ENV)
    if not api_key:
        print("File Search requires GEMINI_API_KEY (Doppler or env var)")
        return None

    return genai.Client(api_key=api_key)


# --- File operations ---
def read_file_content(file_path, with_line_numbers=False) -> str:
    """Read file content with UTF-8/latin-1 fallback."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception:
            return f"[Binary or unreadable file: {file_path}]"
    except Exception as e:
        return f"[Error reading {file_path}: {e}]"

    if with_line_numbers:
        lines = content.split('\n')
        return '\n'.join(f"{i+1:4d}: {line}" for i, line in enumerate(lines))
    return content


def list_local_files(base_dir, patterns=None, user_excludes=None) -> List[Path]:
    """Walk filesystem with glob patterns and security excludes."""
    import fnmatch

    base = Path(base_dir)
    if not base.exists():
        return []

    # Security excludes
    security_excludes = {
        '.env', '.env.local', '.env.production', 'credentials.json',
        'serviceAccountKey.json', '.git', 'node_modules', '.venv',
        '__pycache__', '.tools_venv', 'venv', '.cache',
    }
    if user_excludes:
        security_excludes.update(user_excludes)

    # Extension excludes (binaries, media)
    ext_excludes = {
        '.pyc', '.pyo', '.so', '.dylib', '.o', '.a',
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
        '.woff', '.woff2', '.ttf', '.eot',
        '.zip', '.tar', '.gz', '.7z',
        '.mp4', '.mp3', '.wav', '.avi',
    }

    files = []
    for path in sorted(base.rglob('*')):
        if not path.is_file():
            continue
        parts = path.relative_to(base).parts
        if any(p in security_excludes for p in parts):
            continue
        if path.suffix in ext_excludes:
            continue
        if patterns:
            rel = str(path.relative_to(base))
            if not any(fnmatch.fnmatch(rel, p) for p in patterns):
                continue
        files.append(path)

    return files


# --- File Search / RAG ---
def list_file_search_stores(client) -> list:
    """List all File Search vector stores."""
    if not client:
        return []
    try:
        stores = list(client.file_search_stores.list())
        return stores
    except Exception:
        return []


def get_or_create_store(client, store_name: str) -> str:
    """Get existing store by name or create new one. Returns resource name."""
    stores = list_file_search_stores(client)
    existing = next((s for s in stores if s.display_name == store_name), None)
    if existing:
        return existing.name

    store = client.file_search_stores.create(display_name=store_name)
    return store.name


def index_files_to_store(client, store_name: str, files: list, base_dir: Path) -> dict:
    """Upload files to a File Search store."""
    stats = {"indexed": 0, "failed": 0, "skipped": 0, "errors": []}
    for f in files:
        if f.suffix in {'.yaml', '.yml'}:
            stats["skipped"] += 1
            continue
        try:
            rel = str(f.relative_to(base_dir))
            with open(f, 'rb') as fh:
                client.file_search_stores.upload(
                    name=store_name,
                    file=fh,
                    metadata={"display_name": rel},
                )
            stats["indexed"] += 1
        except Exception as e:
            stats["failed"] += 1
            stats["errors"].append(str(e)[:100])
    return stats


def search_with_file_search(client, store_name: str, query: str, model: str = None) -> dict:
    """Query a File Search store with citations."""
    if not client or not HAS_GENAI:
        return {"text": "", "citations": []}

    use_model = model or DEFAULT_MODEL
    try:
        response = client.models.generate_content(
            model=use_model,
            contents=query,
            config=genai.types.GenerateContentConfig(
                tools=[genai.types.Tool(
                    file_search=genai.types.FileSearch(
                        vector_store_names=[store_name]
                    )
                )]
            ),
        )
        citations = []
        for candidate in response.candidates:
            gm = getattr(candidate, 'grounding_metadata', None)
            if gm:
                for chunk in getattr(gm, 'grounding_chunks', []):
                    cite = {}
                    rc = getattr(chunk, 'retrieved_context', None)
                    if rc:
                        cite['file'] = getattr(rc, 'uri', '')
                        cite['title'] = getattr(rc, 'title', '')
                    if cite:
                        citations.append(cite)
        return {
            "text": response.text or "",
            "citations": citations,
            "usage": {
                "input_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0) if response.usage_metadata else 0,
                "output_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0) if response.usage_metadata else 0,
            },
        }
    except Exception as e:
        return {"text": "", "citations": [], "error": str(e)}


# --- Retry / resilience ---
def auto_diagnose_error(error_str: str) -> None:
    """Parse Gemini API errors and suggest fixes."""
    import re as _re
    print("\n  --- AUTO-DIAGNOSIS ---")
    match = _re.search(r'retry.*?(\d+\.?\d*)\s*s', error_str, _re.IGNORECASE)
    if match:
        print(f"  Retry in: {float(match.group(1)):.0f} seconds")
    if 'input_token' in error_str.lower():
        print("  Cause: Input token quota exceeded")
        print("  Fix: Use --model gemini-2.5-flash")
    elif 'quota' in error_str.lower():
        print("  Cause: Rate limit exceeded")
        print("  Fix: Wait 60s or use gemini-2.5-flash")


def retry_with_backoff(func, max_retries=5, base_delay=1.0):
    """Execute function with exponential backoff on rate limit errors."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            is_rate_limit = any(
                x in error_str for x in ['429', 'rate limit', 'quota', 'resource exhausted']
            )
            if not is_rate_limit or attempt == max_retries - 1:
                if is_rate_limit:
                    auto_diagnose_error(str(e))
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"  Rate limited. Retrying in {delay:.1f}s ({attempt + 1}/{max_retries})...")
            time.sleep(delay)
    raise Exception("Max retries exceeded")


def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Estimate cost in USD."""
    rates = PRICING.get(model, PRICING.get(DEFAULT_MODEL, {"input": 0.10, "output": 0.40}))
    return (input_tokens / 1_000_000) * rates.get("input", 0.10) + \
           (output_tokens / 1_000_000) * rates.get("output", 0.40)


def load_sets_config() -> dict:
    """Load analysis_sets.yaml."""
    if SETS_CONFIG_PATH.exists():
        with open(SETS_CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    return {}
```

- [ ] **Step 2: Verify _shared.py imports cleanly**

Run: `cd ~/PROJECTS_all/PROJECT_elements && .venv/bin/python3 -c "from wave.tools.ai._shared import PROJECT_ROOT, DEFAULT_MODEL, create_client; print(f'ROOT={PROJECT_ROOT.name}, MODEL={DEFAULT_MODEL}')"`

Expected: `ROOT=PROJECT_elements, MODEL=gemini-3-pro-preview` (or current default)

- [ ] **Step 3: Commit _shared.py**

```bash
git add wave/tools/ai/_shared.py
git commit -m "refactor: extract _shared.py from analyze.py — shared utility foundation"
```

---

### Task 2: Create socratic/models.py

**Files:**
- Create: `wave/tools/ai/socratic/__init__.py`
- Create: `wave/tools/ai/socratic/models.py`

- [ ] **Step 1: Create package directory and models**

`socratic/__init__.py`:
```python
"""Socratic Semantic Validator — hypothesis-driven code verification."""

from .domain_runner import verify_domain
from .validator import SocraticValidator
from .hypothesis import generate_hypotheses
from .models import Hypothesis, VerificationResult, AuditReport

__all__ = [
    "verify_domain", "SocraticValidator", "generate_hypotheses",
    "Hypothesis", "VerificationResult", "AuditReport",
]
```

Note: `__init__.py` will fail to import until all modules exist. That's expected -- we create it now but test it at the end.

`socratic/models.py`:
```python
"""Pydantic data models for Socratic Validator."""

import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Hypothesis(BaseModel):
    """A testable claim derived from semantic_models.yaml definitions."""
    concept: str
    claim: str
    description: str
    invariants: List[str]
    anchors: List[Dict[str, str]] = Field(default_factory=list)
    scope: str = ""


class VerificationResult(BaseModel):
    """Result of verifying a single hypothesis against code."""
    verified: bool
    candidates: List[str] = Field(default_factory=list)
    analysis: str = ""
    guardrails: Dict[str, Any] = Field(default_factory=dict)
    reason: Optional[str] = None


class AuditReport(BaseModel):
    """Full domain audit report with D6 provenance header."""
    model_config = ConfigDict(populate_by_name=True)

    generated: Dict[str, Any] = Field(default_factory=dict, alias="_generated")
    domain: str
    timestamp: str
    hypotheses_count: int
    verified_count: int = 0
    violation_count: int = 0
    results: List[Dict[str, Any]] = Field(default_factory=list)
    markdown: str = ""

    @staticmethod
    def d6_header() -> Dict[str, Any]:
        """D6 provenance header (ecosystem standard)."""
        sha = "unknown"
        try:
            sha = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(Path(__file__).resolve().parents[4]),  # PROJECT_ROOT
                stderr=subprocess.DEVNULL,
            ).decode().strip()
        except Exception:
            pass
        return {
            "source": "socratic",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "git_sha": sha,
        }
```

- [ ] **Step 2: Verify models import**

Run: `cd ~/PROJECTS_all/PROJECT_elements && .venv/bin/python3 -c "import sys; sys.path.insert(0, 'wave/tools/ai'); from socratic.models import Hypothesis, AuditReport; h = Hypothesis(concept='test', claim='c', description='d', invariants=['i']); print(h.concept); print(AuditReport.d6_header()['source'])"`

Expected: `test` and `socratic`

- [ ] **Step 3: Commit models**

```bash
git add wave/tools/ai/socratic/
git commit -m "feat(socratic): add package skeleton with Pydantic models"
```

---

## Chunk 2: Core Logic (hypothesis, validator, verifier)

### Task 3: Create hypothesis.py

**Files:**
- Create: `wave/tools/ai/socratic/hypothesis.py`

- [ ] **Step 1: Create hypothesis.py**

Extract from analyze.py lines 1986-2012:

```python
"""Hypothesis generation from semantic_models.yaml domain definitions."""

from typing import Dict, List
from .models import Hypothesis


def generate_hypotheses(domain_config: Dict) -> List[Hypothesis]:
    """Convert domain definitions into testable hypotheses.

    Args:
        domain_config: A domain entry from semantic_models.yaml
            with 'definitions' dict and optional 'scope' string.

    Returns:
        List of Hypothesis objects, one per concept in the domain.
    """
    hypotheses = []
    definitions = domain_config.get("definitions", {})
    domain_scope = domain_config.get("scope", "")

    for concept, details in definitions.items():
        desc = details.get("description", "No description")
        invariants = details.get("invariants", [])
        anchors = details.get("anchors", [])

        claim = f"Hypothesis: The concept '{concept}' is implemented according to strict invariants."

        hypotheses.append(Hypothesis(
            concept=concept,
            claim=claim,
            description=desc,
            invariants=invariants,
            anchors=anchors,
            scope=domain_scope,
        ))

    return hypotheses
```

- [ ] **Step 2: Commit**

```bash
git add wave/tools/ai/socratic/hypothesis.py
git commit -m "feat(socratic): add hypothesis generation from semantic config"
```

---

### Task 4: Create validator.py

**Files:**
- Create: `wave/tools/ai/socratic/validator.py`

- [ ] **Step 1: Create validator.py**

Extract from analyze.py lines 2246-2304:

```python
"""SocraticValidator — antimatter pattern detection (the Critic Agent)."""

import json
from typing import Any, Dict

import sys
from pathlib import Path
_AI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AI_DIR))

from _shared import retry_with_backoff, HAS_GENAI
if HAS_GENAI:
    from google import genai


class SocraticValidator:
    """Detect AI liabilities (Antimatter Patterns) via Socratic critique."""

    def __init__(self, semantic_config: dict):
        self.laws = semantic_config.get("antimatter", [])

    def validate(
        self, client, model: str, code_context: str, concept_role: str
    ) -> Dict[str, Any]:
        """Run antimatter audit on code context.

        Returns dict with {compliant, violations, critique_summary}
        or {status: "SKIPPED"/"ERROR", reason/error}.
        """
        if not self.laws:
            return {"status": "SKIPPED", "reason": "No Antimatter Patterns defined"}

        prompt = f"""
        ACT AS: Socratic Supervisor (Senior Architect Auditor).
        TASK: Audit the following code candidate (Role: {concept_role}) for 'Antimatter' violations.

        CODE CONTEXT:
        {code_context[:30000]}

        ANTIMATTER LAWS (Violations to detect):
        """
        for law in self.laws:
            prompt += (
                f"- [{law['id']}] {law['name']}: {law['description']}\n"
                f"  Check: {law['detection_prompt']}\n"
            )

        prompt += """

        OUTPUT FORMAT (JSON):
        {
          "compliant": boolean,
          "violations": [
            {"law_id": "AMxxx", "severity": "HIGH/MEDIUM/LOW", "reasoning": "..."}
          ],
          "critique_summary": "One sentence summary of the audit."
        }
        """

        try:
            def make_request():
                return client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )

            response = retry_with_backoff(make_request)
            return json.loads(response.text)
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
```

- [ ] **Step 2: Commit**

```bash
git add wave/tools/ai/socratic/validator.py
git commit -m "feat(socratic): add SocraticValidator antimatter detection"
```

---

### Task 5: Create verifier.py

**Files:**
- Create: `wave/tools/ai/socratic/verifier.py`

- [ ] **Step 1: Create verifier.py**

Extract from analyze.py lines 2014-2159 with dead code removed and PROJECT_ROOT parameterized:

```python
"""3-phase hypothesis verification loop."""

import glob
import time
from pathlib import Path
from typing import Optional

import yaml

import sys
_AI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AI_DIR))

from _shared import (
    PROJECT_ROOT as _DEFAULT_ROOT,
    SEMANTIC_MODELS_PATH,
    DEFAULT_MODEL,
    read_file_content,
    retry_with_backoff,
    search_with_file_search,
    HAS_GENAI,
)
if HAS_GENAI:
    from google.genai.types import Part

from .models import Hypothesis, VerificationResult
from .validator import SocraticValidator


def verify_hypothesis(
    dev_client,
    vertex_client,
    hypothesis: Hypothesis,
    store_name: Optional[str],
    candidate_override: Optional[str] = None,
    project_root: Optional[Path] = None,
) -> VerificationResult:
    """Execute 3-phase verification for a single hypothesis.

    Phase A: Discovery — find candidate files via anchors, File Search, or explicit override.
    Phase B: Deep verification — check invariants via Gemini.
    Phase C: Socratic validation — run antimatter audit.
    """
    root = project_root or _DEFAULT_ROOT
    concept = hypothesis.concept
    invariants = hypothesis.invariants

    print(f"Targeting Concept: {concept}")

    # --- Phase A: Discovery ---
    candidate_files: set = set()

    # Priority 1: Explicit candidate override
    if candidate_override:
        print(f"    [Explicit Candidate]: {candidate_override}")
        candidate_files.add(candidate_override)

    # Priority 2: Anchors from semantic_models.yaml
    if hypothesis.anchors and not candidate_override:
        print(f"    [Anchor Discovery]: {len(hypothesis.anchors)} anchor patterns")
        for anchor in hypothesis.anchors:
            pattern = anchor.get("file", "")
            if not pattern:
                continue
            full_path = root / pattern
            if "*" not in pattern and full_path.exists():
                candidate_files.add(str(full_path))
                print(f"      Found (Direct): {full_path.name}")
            else:
                matches = glob.glob(str(full_path), recursive=True)
                for match in matches:
                    candidate_files.add(match)
                    print(f"      Found (Glob): {Path(match).name}")

    # Priority 3: File Search fallback
    if not candidate_files and store_name:
        print("    [File Search Fallback]")
        discovery_query = (
            f"Find code that implements or represents the concept '{concept}'. "
            "List relevant classes or modules."
        )
        search_result = search_with_file_search(dev_client, store_name, discovery_query)
        if search_result.get("citations"):
            for cite in search_result["citations"]:
                fpath = cite.get("file", "")
                if fpath and fpath.startswith("file://"):
                    fpath = fpath[7:]
                if fpath:
                    candidate_files.add(fpath)

    if not candidate_files:
        print("    No candidates found.")
        return VerificationResult(verified=False, reason="No candidates found")

    print(f"    Found {len(candidate_files)} candidates: "
          f"{', '.join(Path(f).name for f in list(candidate_files)[:3])}...")

    # --- Phase B: Deep Verification ---
    files_context = ""
    for fpath in list(candidate_files)[:5]:
        full_path = Path(fpath)
        if not full_path.is_absolute():
            full_path = root / fpath
        if full_path.exists():
            try:
                content = read_file_content(full_path)
                files_context += f"\n--- FILE: {fpath} ---\n{content}\n"
            except Exception:
                pass

    if not files_context:
        return VerificationResult(verified=False, reason="Could not read files")

    print("  Phase B: Verifying Invariants...")

    prompt = f"""
    You are a Semantic Auditor. Verify if the code matches the Semantic Definition.

    CONCEPT: {concept}
    DESCRIPTION: {hypothesis.description}

    INVARIANTS (MUST BE TRUE):
    {chr(10).join(f'- {i}' for i in invariants)}

    CODEBASE CONTEXT:
    {files_context[:50000]}

    TASK:
    1. Identify which classes/functions correspond to '{concept}'.
    2. Check each against the invariants.
    3. Output a structured report.

    FORMAT:
    ### Findings
    - **Entity**: [Name]
    - **Status**: [Compliant / Non-Compliant]
    - **Evidence**: [Quote or reasoning]
    - **Deviation**: [If non-compliant, explain why]
    """

    def make_request():
        return vertex_client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=[Part.from_text(text=prompt)],
        )

    response = retry_with_backoff(make_request)
    analysis_result = response.text

    # --- Phase C: Socratic Validation ---
    print("  Phase C: Running Socratic Validator (Antimatter Check)...")
    try:
        with open(SEMANTIC_MODELS_PATH) as f:
            full_config = yaml.safe_load(f)
        validator = SocraticValidator(full_config)
        socratic_result = validator.validate(
            vertex_client, DEFAULT_MODEL, files_context, concept
        )
    except Exception as e:
        print(f"  Warning: Socratic Validator failed: {e}")
        socratic_result = {"status": "ERROR", "error": str(e)}

    return VerificationResult(
        verified=True,
        candidates=list(candidate_files),
        analysis=analysis_result,
        guardrails=socratic_result,
    )
```

- [ ] **Step 2: Commit**

```bash
git add wave/tools/ai/socratic/verifier.py
git commit -m "feat(socratic): add 3-phase verification loop with dead code cleanup"
```

---

## Chunk 3: Orchestrator, CLI, and Integration

### Task 6: Create domain_runner.py

**Files:**
- Create: `wave/tools/ai/socratic/domain_runner.py`

- [ ] **Step 1: Create domain_runner.py**

Merges the two duplicate verify_domain() functions into one canonical version with three-tier output:

```python
"""Domain verification orchestrator with three-tier output."""

import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

import sys
_AI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AI_DIR))

from _shared import (
    PROJECT_ROOT as _DEFAULT_ROOT,
    SEMANTIC_MODELS_PATH,
    create_client,
    create_developer_client,
    list_file_search_stores,
    get_or_create_store,
    index_files_to_store,
    list_local_files,
)

from .models import AuditReport
from .hypothesis import generate_hypotheses
from .verifier import verify_hypothesis


def load_semantic_models() -> dict:
    """Load semantic_models.yaml."""
    if not SEMANTIC_MODELS_PATH.exists():
        print(f"Error: Semantic models not found at {SEMANTIC_MODELS_PATH}")
        return {}
    with open(SEMANTIC_MODELS_PATH) as f:
        return yaml.safe_load(f) or {}


def _append_run_index(report: AuditReport, output_dir: Path) -> None:
    """Append compact record to run_index.jsonl."""
    record = {
        "_generated": report.generated,
        "domain": report.domain,
        "hypotheses_count": report.hypotheses_count,
        "verified_count": report.verified_count,
        "violation_count": report.violation_count,
        "timestamp": report.timestamp,
    }
    with open(output_dir / "run_index.jsonl", "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def verify_domain(
    domain: str,
    store_name: Optional[str] = None,
    output: Optional[str] = None,
    index: bool = False,
    candidate: Optional[str] = None,
    project_root: Optional[Path] = None,
    sync_gcs: bool = False,
) -> AuditReport:
    """Orchestrate full domain verification with three-tier output.

    Args:
        domain: Domain name from semantic_models.yaml (e.g., "atoms", "pipeline")
        store_name: File Search store name (default: collider-{domain})
        output: Optional explicit output file path
        index: If True, index files to store before verifying
        candidate: Explicit candidate file path (skips discovery)
        project_root: Override PROJECT_ROOT for testing
        sync_gcs: If True, attempt gsutil cp to GCS (requires billing)
    """
    root = project_root or _DEFAULT_ROOT
    models = load_semantic_models()

    if domain not in models:
        print(f"Error: Domain '{domain}' not found in semantic_models.yaml")
        available = list(models.keys())
        print(f"Available: {available}")
        return AuditReport(
            _generated=AuditReport.d6_header(),
            domain=domain,
            timestamp=datetime.now(timezone.utc).isoformat(),
            hypotheses_count=0,
        )

    domain_config = models[domain]
    store_name = store_name or f"collider-{domain}"

    # Initialize clients
    print("Initializing clients...")
    dev_client = create_developer_client()
    vertex_client, _ = create_client()

    # Optional indexing
    if index and dev_client:
        print(f"Indexing domain '{domain}'...")
        target_dir = None
        if domain == "pipeline":
            target_dir = root / "particle/src/core"
        elif domain == "theory":
            target_dir = root / "particle/docs/theory"
        if target_dir:
            store_res = get_or_create_store(dev_client, store_name)
            files = list_local_files(target_dir)
            index_files_to_store(dev_client, store_res, files, root)

    # Resolve store
    store_resource_name = None
    if not candidate and dev_client:
        print(f"Resolving store '{store_name}'...")
        stores = list_file_search_stores(dev_client)
        t_store = next((s for s in stores if s.display_name == store_name), None)
        if t_store:
            store_resource_name = t_store.name
            print(f"  Found store: {store_resource_name}")
        else:
            print(f"  Warning: Store '{store_name}' not found.")

    # Generate and verify hypotheses
    hypotheses = generate_hypotheses(domain_config)
    print(f"\nLoaded {len(hypotheses)} hypotheses for domain '{domain}'")

    results = []
    for h in hypotheses:
        print("-" * 60)
        res = verify_hypothesis(
            dev_client, vertex_client, h,
            store_resource_name, candidate_override=candidate,
            project_root=root,
        )
        results.append({"hypothesis": h.model_dump(), "result": res.model_dump()})
        time.sleep(1)

    # Build markdown report
    md = f"# Validated Semantic Map: {domain.upper()}\n\n"
    md += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    verified_count = 0
    violation_count = 0

    for item in results:
        h = item["hypothesis"]
        res = item["result"]
        md += f"## Concept: {h['concept']}\n> {h['description']}\n\n"
        if res["verified"]:
            verified_count += 1
            analysis_text = (
                res["analysis"].get("summary", str(res["analysis"]))
                if isinstance(res["analysis"], dict) else str(res["analysis"])
            )
            md += analysis_text + "\n\n"
            gr = res.get("guardrails", {})
            md += "### Semantic Guardrails (Antimatter Check)\n"
            if gr.get("compliant"):
                md += "**PASSED**: No liabilities detected.\n"
            else:
                md += "**DETECTED LIABILITIES**:\n"
                for v in gr.get("violations", []):
                    violation_count += 1
                    md += f"- **[{v.get('law_id')}]**: {v.get('reasoning')} (Severity: {v.get('severity')})\n"
            md += "\n"
        else:
            md += f"**Verification Failed**: {res.get('reason')}\n\n"

    # Build AuditReport
    report = AuditReport(
        _generated=AuditReport.d6_header(),
        domain=domain,
        timestamp=datetime.now(timezone.utc).isoformat(),
        hypotheses_count=len(hypotheses),
        verified_count=verified_count,
        violation_count=violation_count,
        results=results,
        markdown=md,
    )

    # --- Three-tier output ---
    socratic_dir = root / ".socratic"
    socratic_dir.mkdir(exist_ok=True)

    # Tier 1: Full JSON report
    (socratic_dir / "latest_report.json").write_text(
        report.model_dump_json(by_alias=True, indent=2)
    )

    # Tier 3: Markdown report
    (socratic_dir / "latest_report.md").write_text(md)

    # Longitudinal tracking
    _append_run_index(report, socratic_dir)

    # Legacy output path (backward compat)
    intelligence_dir = root / "wave/intelligence"
    intelligence_dir.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    legacy_path = intelligence_dir / f"socratic_audit_{domain}_{timestamp}.json"
    legacy_path.write_text(report.model_dump_json(by_alias=True, indent=2))

    # Optional GCS sync
    if sync_gcs and shutil.which("gsutil"):
        try:
            import subprocess
            subprocess.run(
                ["gsutil", "cp", str(legacy_path),
                 f"gs://elements-archive-2026/intelligence/{legacy_path.name}"],
                check=False, capture_output=True,
            )
        except Exception:
            pass

    # Explicit output file
    if output:
        Path(output).write_text(md)
        print(f"\nReport saved to: {output}")
    else:
        print(md)

    print(f"\nOutputs:")
    print(f"  Tier 1 (JSON): {socratic_dir / 'latest_report.json'}")
    print(f"  Tier 3 (MD):   {socratic_dir / 'latest_report.md'}")
    print(f"  Index:         {socratic_dir / 'run_index.jsonl'}")
    print(f"  Legacy:        {legacy_path}")

    return report
```

- [ ] **Step 2: Commit**

```bash
git add wave/tools/ai/socratic/domain_runner.py
git commit -m "feat(socratic): add domain_runner with three-tier output and longitudinal tracking"
```

---

### Task 7: Create cli.py

**Files:**
- Create: `wave/tools/ai/socratic/cli.py`

- [ ] **Step 1: Create cli.py**

```python
#!/usr/bin/env python3
"""Socratic Semantic Validator CLI.

Usage:
    doppler run -- python wave/tools/ai/socratic/cli.py --domain atoms
    doppler run -- python wave/tools/ai/socratic/cli.py --domain atoms --candidate particle/src/core/atom.py
    doppler run -- python wave/tools/ai/socratic/cli.py --list-domains
"""

import sys
from pathlib import Path

# Ensure wave/tools/ai/ is on sys.path for _shared imports
_AI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AI_DIR))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Socratic Semantic Validator — hypothesis-driven code verification",
    )
    parser.add_argument("--domain", help="Domain name from semantic_models.yaml")
    parser.add_argument("--candidate", help="Explicit file path to verify (skips discovery)")
    parser.add_argument("--store-name", help="File Search store name")
    parser.add_argument("--output", "-o", help="Output file path for markdown report")
    parser.add_argument("--index", action="store_true", help="Index files to store before verifying")
    parser.add_argument("--list-domains", action="store_true", help="List available domains")
    parser.add_argument("--sync-gcs", action="store_true", help="Sync output to GCS (requires billing)")

    args = parser.parse_args()

    if args.list_domains:
        from socratic.domain_runner import load_semantic_models
        models = load_semantic_models()
        print("Available domains:")
        for name, config in models.items():
            desc = config.get("description", config.get("scope", ""))
            n_defs = len(config.get("definitions", {}))
            print(f"  {name:20s} ({n_defs} concepts) {desc}")
        sys.exit(0)

    if not args.domain:
        parser.error("--domain is required (or use --list-domains)")

    from socratic.domain_runner import verify_domain
    verify_domain(
        domain=args.domain,
        store_name=args.store_name,
        output=args.output,
        index=args.index,
        candidate=args.candidate,
        sync_gcs=args.sync_gcs,
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add wave/tools/ai/socratic/cli.py
git commit -m "feat(socratic): add standalone CLI entry point"
```

---

### Task 8: Update analyze.py — remove extracted code, wire imports

**Files:**
- Modify: `wave/tools/ai/analyze.py`

- [ ] **Step 1: Add _shared imports to analyze.py**

After the venv bootstrap block (after line 99), add:

```python
# Import shared utilities (extracted from this file to break os.execv dependency)
from _shared import (
    PROJECT_ROOT, SEMANTIC_MODELS_PATH, PROMPTS_CONFIG_PATH, SETS_CONFIG_PATH,
    DEFAULT_MODEL, FAST_MODEL, FALLBACK_MODELS, PRICING, MODES, BACKEND,
    GEMINI_API_KEY_ENV,
    read_file_content, retry_with_backoff, auto_diagnose_error, estimate_cost,
    create_client, create_developer_client,
    list_file_search_stores, get_or_create_store, search_with_file_search,
    index_files_to_store, list_local_files, load_sets_config,
    get_doppler_secret, get_gcloud_project, get_access_token,
    HAS_GENAI,
)
```

- [ ] **Step 2: Delete Socratic code (lines 1986-2446)**

Remove: `generate_hypotheses()`, `verify_hypothesis()`, first `verify_domain()` (line 2161), `SocraticValidator` class, `load_semantic_models()`, second `verify_domain()` (line 2318).

- [ ] **Step 3: Replace --verify handler**

Find the `if args.verify:` block and replace with:

```python
    if args.verify:
        from socratic import verify_domain
        verify_domain(
            args.verify,
            store_name=args.store_name,
            output=args.output,
            index=args.index,
            candidate=args.candidate,
        )
        sys.exit(0)
```

- [ ] **Step 4: Delete duplicate function definitions from analyze.py**

Remove the original versions of all functions now in `_shared.py`: `read_file_content()`, `retry_with_backoff()`, `auto_diagnose_error()`, `estimate_cost()`, `create_client()`, `create_developer_client()`, `list_file_search_stores()`, `get_or_create_store()`, `search_with_file_search()`, `index_files_to_store()`, `list_local_files()`, `load_sets_config()`, `_find_doppler()`, `get_doppler_secret()`, `get_gcloud_project()`, `get_access_token()`.

Keep the original `PROJECT_ROOT`, config loading, and path constants as comments pointing to `_shared.py` for maintainer context.

**IMPORTANT:** This is the riskiest step. Run `python analyze.py --list-sets` after each batch of deletions to verify nothing broke.

- [ ] **Step 5: Verify analyze.py still works**

Run: `cd ~/PROJECTS_all/PROJECT_elements && doppler run -- .venv/bin/python3 wave/tools/ai/analyze.py --list-sets 2>&1 | head -20`

Expected: List of analysis sets (no import errors)

- [ ] **Step 6: Verify line count decreased**

Run: `wc -l wave/tools/ai/analyze.py`

Expected: ~3,600 lines (was ~4,136)

- [ ] **Step 7: Commit**

```bash
git add wave/tools/ai/analyze.py
git commit -m "refactor: remove socratic code from analyze.py, wire _shared imports"
```

---

### Task 9: Registry updates + gitignore

**Files:**
- Modify: `atlas/ATLAS.yaml`
- Modify: `.ecoroot/TOOLS_REGISTRY.yaml`
- Modify: `.gitignore`

- [ ] **Step 1: Add CMP-090 to Atlas**

Add the entry from the spec (after CMP-052).

- [ ] **Step 2: Update CMP-052 feeds_into/fed_by**

Add CMP-090 to both lists.

- [ ] **Step 3: Add ECO-061 to TOOLS_REGISTRY**

- [ ] **Step 4: Add `.socratic/` to .gitignore**

- [ ] **Step 5: Commit**

```bash
git add atlas/ATLAS.yaml .gitignore
git commit -m "feat(atlas): register Socratic Validator as CMP-090 (P2), ECO-061"
```

---

### Task 10: Integration test

- [ ] **Step 1: Test socratic CLI --list-domains**

Run: `cd ~/PROJECTS_all/PROJECT_elements && doppler run -- .venv/bin/python3 wave/tools/ai/socratic/cli.py --list-domains`

Expected: List of domains from semantic_models.yaml

- [ ] **Step 2: Test analyze.py --verify backward compat**

Run: `cd ~/PROJECTS_all/PROJECT_elements && doppler run -- .venv/bin/python3 wave/tools/ai/analyze.py --verify atoms --candidate particle/src/core/atom.py 2>&1 | head -30`

Expected: Verification output (may require Gemini API key)

- [ ] **Step 3: Verify output files**

Check: `.socratic/latest_report.json`, `.socratic/latest_report.md`, `.socratic/run_index.jsonl`

- [ ] **Step 4: Verify analyze.py line count**

Run: `wc -l wave/tools/ai/analyze.py`

Expected: < 3,700 lines

- [ ] **Step 5: Run existing Collider tests**

Run: `cd ~/PROJECTS_all/PROJECT_elements && .venv/bin/python3 -m pytest particle/tests/test_temporal_analysis.py -q`

Expected: 53 passed
