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
