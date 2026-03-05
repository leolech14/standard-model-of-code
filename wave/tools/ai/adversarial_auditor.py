#!/usr/bin/env python3
"""
Three-Layer Adversarial Auditor
================================
Automated document audit for IP claims, citation accuracy, and methodological soundness.

Layer 1 (Adversarial Review): LLM finds overclaims, missing citations, metaphor abuse
Layer 2 (Evidence Audit):     Web search fact-checks citations from Layer 1
Layer 3 (Domain Audit):       Methodology checks -- math, compression ratios, definitions

Pipeline:
    Document ──→ Layer 1 (Cerebras) ──→ Layer 2 (Perplexity) ──→ Synthesis
                      │                                               ↑
                      └──→ Layer 3 (Cerebras + deterministic) ────────┘

Usage:
    # Full three-layer audit
    doppler run -- python wave/tools/ai/adversarial_auditor.py audit path/to/doc.md --domain smoc

    # Single layer only
    doppler run -- python wave/tools/ai/adversarial_auditor.py audit path/to/doc.md --layer 1

    # Via collider-hub
    ./collider-hub audit-doc path/to/doc.md --domain smoc

    # Dry run (no API calls)
    doppler run -- python wave/tools/ai/adversarial_auditor.py audit path/to/doc.md --dry-run

Cost per run: ~$0.01-0.04 (Cerebras: 3 calls ~ $0.003, Perplexity: 5-15 calls ~ $0.01-0.03)
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
FEEDBACK_DIR = PROJECT_ROOT / "collider_feedback"

CEREBRAS_API_URL = "https://api.cerebras.ai/v1/chat/completions"
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "qwen-3-235b-a22b-instruct-2507")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")

MIN_REQUEST_INTERVAL = 0.15
_last_cerebras_time = 0.0

SCHEMA_VERSION = "adversarial_audit.v1"

# Max chars before chunking a document for Layer 1
CHUNK_THRESHOLD = 28000
CHUNK_SIZE = 25000
CHUNK_OVERLAP = 2000

# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class Finding:
    """A single audit finding from any layer."""
    layer: int
    finding_id: str
    severity: str  # critical, high, medium, low, info
    category: str  # overclaim, missing_citation, metaphor_abuse, math_error, etc.
    title: str
    description: str
    location: str = ""  # section/line reference in document
    evidence: str = ""
    suggestion: str = ""
    source_urls: list[str] = field(default_factory=list)
    verified: Optional[bool] = None  # None=unchecked, True=confirmed, False=refuted


@dataclass
class CitationToCheck:
    """Typed handoff from Layer 1 to Layer 2."""
    claim_text: str
    cited_source: str
    document_location: str
    finding_id: str  # back-reference to L1 finding


@dataclass
class LayerReport:
    """Output of a single audit layer."""
    layer: int
    layer_name: str
    started_at: str
    completed_at: str
    llm_model: str
    findings: list[Finding] = field(default_factory=list)
    error: str = ""


@dataclass
class MandatoryEdit:
    """A concrete edit that must be applied to the document."""
    location: str
    original: str
    replacement: str
    reason: str
    severity: str
    finding_ids: list[str] = field(default_factory=list)


@dataclass
class AuditReport:
    """Complete three-layer audit report."""
    schema_version: str
    document_path: str
    domain: str
    generated_at: str
    layers: list[LayerReport] = field(default_factory=list)
    synthesis: dict[str, Any] = field(default_factory=dict)
    mandatory_edits: list[MandatoryEdit] = field(default_factory=list)


# =============================================================================
# DOMAIN PROFILES
# =============================================================================

DOMAIN_PROFILES: dict[str, dict[str, Any]] = {
    "smoc": {
        "name": "Standard Model of Code",
        "checks": [
            "compression_ratio_math",
            "atom_count_consistency",
            "citation_authority",
            "falsifiability_presence",
            "metaphor_physics_boundary",
        ],
        "custom_prompt_suffix": (
            "This document describes the Standard Model of Code (SMoC), "
            "a framework that uses physics metaphors to classify code structures. "
            "Physics metaphors MUST be bounded -- they are analogies for communication, "
            "not literal claims about code obeying physical laws. "
            "Flag any unbounded physics metaphor (e.g., 'code obeys conservation laws' "
            "without qualifying 'as an analogy'). "
            "Check atom counts against the canonical 167 structural types. "
            "Verify compression ratio math (e.g., 50:1 claims need source data). "
            "Ensure falsifiability: every testable claim should have a stated test."
        ),
        "deterministic_validators": [
            "check_atom_count_claims",
            "check_compression_ratio_claims",
            "check_unbounded_metaphors",
        ],
    },
    "general": {
        "name": "General Document",
        "checks": [
            "internal_consistency",
            "definition_completeness",
            "claim_evidence_ratio",
        ],
        "custom_prompt_suffix": "",
        "deterministic_validators": [],
    },
}


# =============================================================================
# LLM CLIENTS
# =============================================================================


def _get_cerebras_key() -> str:
    """Get Cerebras API key from environment or Doppler."""
    key = os.getenv("CEREBRAS_API_KEY")
    if not key:
        try:
            result = subprocess.run(
                ["doppler", "secrets", "get", "CEREBRAS_API_KEY", "--plain"],
                capture_output=True, text=True, timeout=5,
            )
            key = result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            pass
    if not key:
        print("Error: CEREBRAS_API_KEY not found", file=sys.stderr)
        sys.exit(1)
    return key


def _get_perplexity_key() -> str:
    """Get Perplexity API key from environment or Doppler."""
    key = os.getenv("PERPLEXITY_API_KEY")
    if not key:
        try:
            result = subprocess.run(
                ["doppler", "secrets", "get", "PERPLEXITY_API_KEY", "--plain"],
                capture_output=True, text=True, timeout=5,
            )
            key = result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            pass
    if not key:
        print("Error: PERPLEXITY_API_KEY not found", file=sys.stderr)
        sys.exit(1)
    return key


def _cerebras_query(prompt: str, system: str = "", max_tokens: int = 4000) -> str:
    """Send query to Cerebras with rate limiting."""
    global _last_cerebras_time
    import httpx

    elapsed = time.time() - _last_cerebras_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)

    api_key = _get_cerebras_key()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = httpx.post(
            CEREBRAS_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": CEREBRAS_MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.2,
            },
            timeout=60.0,
        )
        _last_cerebras_time = time.time()

        if response.status_code == 429:
            print("Rate limited by Cerebras API (429)", file=sys.stderr)
            return ""

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"Cerebras error: {e}", file=sys.stderr)
        return ""


def _perplexity_query(prompt: str, model: str = "") -> dict[str, Any]:
    """Send query to Perplexity and return content + citations."""
    import httpx

    api_key = _get_perplexity_key()
    model = model or PERPLEXITY_MODEL

    try:
        response = httpx.post(
            PERPLEXITY_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "return_citations": True,
            },
            timeout=120.0,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
            "citations": data.get("citations", []),
        }
    except Exception as e:
        print(f"Perplexity error: {e}", file=sys.stderr)
        return {"content": "", "citations": []}


def _parse_json_response(response: str) -> dict[str, Any]:
    """Extract JSON from LLM response that may contain markdown code blocks."""
    if not response:
        return {}
    try:
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]
        elif "{" in response:
            start = response.index("{")
            end = response.rindex("}") + 1
            json_str = response[start:end]
        else:
            json_str = response
        return json.loads(json_str.strip())
    except (json.JSONDecodeError, ValueError):
        return {}


# =============================================================================
# LAYER 1: ADVERSARIAL REVIEW
# =============================================================================

LAYER1_SYSTEM = """You are an adversarial document reviewer. Your job is to find:
1. OVERCLAIMS: Language that overstates what was achieved or discovered
2. MISSING CITATIONS: Claims that need evidence but have none
3. METAPHOR ABUSE: Analogies presented as literal truths
4. INTERNAL CONTRADICTIONS: Statements that conflict with each other
5. VAGUE QUANTIFICATION: Numbers without sources or methodology

Be thorough but fair. Flag real issues, not stylistic preferences."""

LAYER1_PROMPT = """Analyze this document for intellectual property and accuracy issues.

{domain_suffix}

DOCUMENT:
---
{document_text}
---

OUTPUT FORMAT (JSON):
{{
  "findings": [
    {{
      "finding_id": "L1-001",
      "severity": "critical|high|medium|low|info",
      "category": "overclaim|missing_citation|metaphor_abuse|contradiction|vague_quantification",
      "title": "short title",
      "description": "detailed explanation of the issue",
      "location": "section name or approximate location in document",
      "evidence": "the exact text that is problematic",
      "suggestion": "how to fix it"
    }}
  ],
  "citations_to_check": [
    {{
      "claim_text": "the claim being made",
      "cited_source": "the source referenced (author, paper, URL)",
      "document_location": "where in the document"
    }}
  ],
  "summary": {{
    "total_findings": 0,
    "by_severity": {{"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}}
  }}
}}

Respond with ONLY the JSON output."""


def _chunk_document(text: str) -> list[str]:
    """Split document into overlapping chunks for large documents."""
    if len(text) <= CHUNK_THRESHOLD:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        # Try to break at a paragraph boundary
        if end < len(text):
            newline_pos = text.rfind("\n\n", start + CHUNK_SIZE - 2000, end)
            if newline_pos > start:
                end = newline_pos
        chunks.append(text[start:end])
        start = end - CHUNK_OVERLAP
    return chunks


def run_layer1(document_text: str, document_path: str, domain: str) -> tuple[LayerReport, list[CitationToCheck]]:
    """Layer 1: Adversarial review via Cerebras."""
    started = datetime.now(timezone.utc).isoformat()
    profile = DOMAIN_PROFILES.get(domain, DOMAIN_PROFILES["general"])
    domain_suffix = profile.get("custom_prompt_suffix", "")
    if domain_suffix:
        domain_suffix = f"DOMAIN-SPECIFIC INSTRUCTIONS:\n{domain_suffix}"

    chunks = _chunk_document(document_text)
    all_findings: list[Finding] = []
    all_citations: list[CitationToCheck] = []
    finding_counter = 0

    for i, chunk in enumerate(chunks):
        chunk_label = f" (chunk {i + 1}/{len(chunks)})" if len(chunks) > 1 else ""
        print(f"  Layer 1: analyzing{chunk_label}...", file=sys.stderr)

        prompt = LAYER1_PROMPT.format(
            domain_suffix=domain_suffix,
            document_text=chunk,
        )
        response = _cerebras_query(prompt, LAYER1_SYSTEM)
        data = _parse_json_response(response)

        for f in data.get("findings", []):
            finding_counter += 1
            fid = f"L1-{finding_counter:03d}"
            all_findings.append(Finding(
                layer=1,
                finding_id=fid,
                severity=f.get("severity", "medium"),
                category=f.get("category", "overclaim"),
                title=f.get("title", "Untitled finding"),
                description=f.get("description", ""),
                location=f.get("location", ""),
                evidence=f.get("evidence", ""),
                suggestion=f.get("suggestion", ""),
            ))

        for c in data.get("citations_to_check", []):
            all_citations.append(CitationToCheck(
                claim_text=c.get("claim_text", ""),
                cited_source=c.get("cited_source", ""),
                document_location=c.get("document_location", ""),
                finding_id=f"L1-{finding_counter:03d}",
            ))

    report = LayerReport(
        layer=1,
        layer_name="Adversarial Review",
        started_at=started,
        completed_at=datetime.now(timezone.utc).isoformat(),
        llm_model=CEREBRAS_MODEL,
        findings=all_findings,
    )
    return report, all_citations


# =============================================================================
# LAYER 2: EVIDENCE AUDIT
# =============================================================================


def run_layer2(citations_to_check: list[CitationToCheck]) -> LayerReport:
    """Layer 2: Fact-check citations via Perplexity + Cerebras classification."""
    started = datetime.now(timezone.utc).isoformat()
    findings: list[Finding] = []

    if not citations_to_check:
        return LayerReport(
            layer=2,
            layer_name="Evidence Audit",
            started_at=started,
            completed_at=datetime.now(timezone.utc).isoformat(),
            llm_model=f"{PERPLEXITY_MODEL} + {CEREBRAS_MODEL}",
            findings=[],
        )

    for i, citation in enumerate(citations_to_check):
        fid = f"L2-{i + 1:03d}"
        print(f"  Layer 2: checking citation {i + 1}/{len(citations_to_check)}...", file=sys.stderr)

        # Step 1: Perplexity web search for the cited source
        search_query = (
            f"Verify this claim and source: \"{citation.claim_text}\" "
            f"Source: {citation.cited_source}. "
            f"Is this citation accurate? Does the source actually say this? "
            f"Provide specific evidence."
        )
        pxr = _perplexity_query(search_query)

        if not pxr["content"]:
            findings.append(Finding(
                layer=2,
                finding_id=fid,
                severity="medium",
                category="citation_unverifiable",
                title=f"Could not verify: {citation.cited_source[:60]}",
                description="Perplexity search returned no results for this citation.",
                location=citation.document_location,
                evidence=citation.claim_text,
                suggestion="Add direct URL or DOI, or remove claim if unverifiable.",
                verified=None,
            ))
            continue

        # Step 2: Cerebras classifies the Perplexity result
        classify_prompt = f"""Given this claim and the web search results, classify the citation.

CLAIM: "{citation.claim_text}"
CITED SOURCE: {citation.cited_source}

WEB SEARCH RESULTS:
{pxr['content'][:3000]}

SOURCES FOUND: {json.dumps(pxr['citations'][:5])}

Classify as JSON:
{{
  "verdict": "verified|refuted|inconclusive|partially_verified",
  "confidence": 0.0-1.0,
  "explanation": "why this verdict",
  "corrected_claim": "if refuted or partially_verified, what the source actually says"
}}"""

        classify_response = _cerebras_query(classify_prompt, max_tokens=500)
        classify_data = _parse_json_response(classify_response)

        verdict = classify_data.get("verdict", "inconclusive")
        confidence = classify_data.get("confidence", 0.5)
        explanation = classify_data.get("explanation", "")
        corrected = classify_data.get("corrected_claim", "")

        if verdict == "verified":
            severity = "info"
            verified = True
        elif verdict == "refuted":
            severity = "critical"
            verified = False
        elif verdict == "partially_verified":
            severity = "high"
            verified = False
        else:
            severity = "medium"
            verified = None

        findings.append(Finding(
            layer=2,
            finding_id=fid,
            severity=severity,
            category=f"citation_{verdict}",
            title=f"Citation {verdict}: {citation.cited_source[:60]}",
            description=f"{explanation} (confidence: {confidence:.0%})",
            location=citation.document_location,
            evidence=citation.claim_text,
            suggestion=corrected if corrected else "",
            source_urls=pxr.get("citations", [])[:3],
            verified=verified,
        ))

    return LayerReport(
        layer=2,
        layer_name="Evidence Audit",
        started_at=started,
        completed_at=datetime.now(timezone.utc).isoformat(),
        llm_model=f"{PERPLEXITY_MODEL} + {CEREBRAS_MODEL}",
        findings=findings,
    )


# =============================================================================
# LAYER 3: DOMAIN AUDIT
# =============================================================================

LAYER3_SYSTEM = """You are a domain methodology auditor. You check documents for:
1. MATHEMATICAL CORRECTNESS: Are calculations and ratios correct?
2. DEFINITION COMPLETENESS: Are all key terms defined before use?
3. INTERNAL CONSISTENCY: Do numbers, counts, and claims agree throughout?
4. METHODOLOGY SOUNDNESS: Are methods described with enough detail to reproduce?
5. FALSIFIABILITY: Are testable claims stated with clear pass/fail criteria?"""

LAYER3_PROMPT = """Perform a domain methodology audit on this document.

{domain_suffix}

DOCUMENT:
---
{document_text}
---

For each issue found, output JSON:
{{
  "findings": [
    {{
      "finding_id": "L3-001",
      "severity": "critical|high|medium|low|info",
      "category": "math_error|definition_incomplete|inconsistency|methodology_gap|falsifiability_missing",
      "title": "short title",
      "description": "detailed explanation",
      "location": "section or context",
      "evidence": "the exact text",
      "suggestion": "concrete fix"
    }}
  ]
}}

Respond with ONLY the JSON output."""


# -- Deterministic validators for SMoC domain --

def _check_atom_count_claims(text: str) -> list[Finding]:
    """Check that atom count claims are consistent with canonical 167."""
    findings = []
    # Look for claims about atom counts
    patterns = [
        r'(\d+)\s*(?:structural\s+)?(?:atom|type)s?\b',
        r'(\d+)\s*(?:code\s+)?(?:atom|element)s?\b',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            count = int(match.group(1))
            if count > 100 and count != 167 and count < 500:
                # Likely an atom count claim that doesn't match 167
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                findings.append(Finding(
                    layer=3,
                    finding_id="L3-DET-ATOM",
                    severity="high",
                    category="inconsistency",
                    title=f"Atom count mismatch: {count} vs canonical 167",
                    description=f"Document claims {count} atoms/types but the canonical count is 167.",
                    location="",
                    evidence=text[context_start:context_end].strip(),
                    suggestion=f"Verify count. If correct, update canonical reference. If not, use 167.",
                ))
    return findings


def _check_compression_ratio_claims(text: str) -> list[Finding]:
    """Check compression ratio claims have supporting math."""
    findings = []
    ratio_pattern = r'(\d+)\s*:\s*1\s*(?:compression|ratio)'
    for match in re.finditer(ratio_pattern, text, re.IGNORECASE):
        ratio = int(match.group(1))
        # Check if there's supporting data nearby (within 500 chars)
        context_start = max(0, match.start() - 300)
        context_end = min(len(text), match.end() + 300)
        context = text[context_start:context_end]
        has_data = any(word in context.lower() for word in [
            "measured", "calculated", "from", "based on", "source",
            "bytes", "tokens", "lines", "files",
        ])
        if not has_data and ratio > 5:
            findings.append(Finding(
                layer=3,
                finding_id="L3-DET-RATIO",
                severity="high",
                category="math_error",
                title=f"Unsupported compression ratio: {ratio}:1",
                description=f"Compression ratio {ratio}:1 claimed without supporting methodology or data.",
                location="",
                evidence=match.group(0),
                suggestion=f"Add: 'Measured as [input_size] / [output_size] = {ratio}:1 on [dataset]'.",
            ))
    return findings


def _check_unbounded_metaphors(text: str) -> list[Finding]:
    """Check for physics metaphors used without bounding language."""
    findings = []
    physics_claims = [
        (r'code\s+(?:obeys?|follows?|satisfies?)\s+(?:conservation|thermodynamic|physical)\s+laws?', "conservation/physics laws"),
        (r'(?:fundamental|universal|natural)\s+(?:law|truth|principle)\s+of\s+(?:code|software)', "universal law claim"),
        (r'we\s+(?:discovered|proved|demonstrated)\s+that\s+code', "discovery language"),
    ]
    bounding_words = ["analogy", "metaphor", "like", "similar to", "as if", "model", "framework", "reference"]

    for pattern, label in physics_claims:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            context_start = max(0, match.start() - 200)
            context_end = min(len(text), match.end() + 200)
            context = text[context_start:context_end].lower()
            is_bounded = any(word in context for word in bounding_words)
            if not is_bounded:
                findings.append(Finding(
                    layer=3,
                    finding_id="L3-DET-META",
                    severity="critical",
                    category="metaphor_abuse",
                    title=f"Unbounded physics metaphor: {label}",
                    description="Physics metaphor used without qualifying language. Readers may interpret as literal claim.",
                    location="",
                    evidence=text[match.start():match.end()],
                    suggestion="Add bounding: 'as a reference model' or 'by analogy with'.",
                ))
    return findings


DETERMINISTIC_VALIDATORS = {
    "check_atom_count_claims": _check_atom_count_claims,
    "check_compression_ratio_claims": _check_compression_ratio_claims,
    "check_unbounded_metaphors": _check_unbounded_metaphors,
}


def run_layer3(document_text: str, domain: str) -> LayerReport:
    """Layer 3: Domain methodology audit via Cerebras + deterministic checks."""
    started = datetime.now(timezone.utc).isoformat()
    profile = DOMAIN_PROFILES.get(domain, DOMAIN_PROFILES["general"])
    domain_suffix = profile.get("custom_prompt_suffix", "")
    if domain_suffix:
        domain_suffix = f"DOMAIN-SPECIFIC CHECKS:\n{domain_suffix}"

    findings: list[Finding] = []

    # Step 1: Deterministic validators
    for validator_name in profile.get("deterministic_validators", []):
        validator_fn = DETERMINISTIC_VALIDATORS.get(validator_name)
        if validator_fn:
            det_findings = validator_fn(document_text)
            findings.extend(det_findings)

    # Step 2: LLM methodology audit
    # Truncate for LLM context
    truncated = document_text[:30000] if len(document_text) > 30000 else document_text
    print("  Layer 3: running domain audit...", file=sys.stderr)

    prompt = LAYER3_PROMPT.format(
        domain_suffix=domain_suffix,
        document_text=truncated,
    )
    response = _cerebras_query(prompt, LAYER3_SYSTEM)
    data = _parse_json_response(response)

    finding_counter = len(findings)
    for f in data.get("findings", []):
        finding_counter += 1
        findings.append(Finding(
            layer=3,
            finding_id=f.get("finding_id", f"L3-{finding_counter:03d}"),
            severity=f.get("severity", "medium"),
            category=f.get("category", "methodology_gap"),
            title=f.get("title", "Untitled finding"),
            description=f.get("description", ""),
            location=f.get("location", ""),
            evidence=f.get("evidence", ""),
            suggestion=f.get("suggestion", ""),
        ))

    return LayerReport(
        layer=3,
        layer_name="Domain Audit",
        started_at=started,
        completed_at=datetime.now(timezone.utc).isoformat(),
        llm_model=CEREBRAS_MODEL,
        findings=findings,
    )


# =============================================================================
# SYNTHESIS
# =============================================================================

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def _deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    """Remove duplicate findings across layers based on similar evidence/title."""
    seen: set[str] = set()
    deduped: list[Finding] = []
    for f in findings:
        key = (f.evidence.strip().lower()[:100], f.category)
        if key not in seen:
            seen.add(key)
            deduped.append(f)
    return deduped


def _generate_mandatory_edits(findings: list[Finding]) -> list[MandatoryEdit]:
    """Generate mandatory edits from critical and high severity findings that have suggestions."""
    edits: list[MandatoryEdit] = []
    actionable = [f for f in findings if f.severity in ("critical", "high") and f.suggestion]

    for f in actionable:
        edits.append(MandatoryEdit(
            location=f.location,
            original=f.evidence,
            replacement=f.suggestion,
            reason=f.description,
            severity=f.severity,
            finding_ids=[f.finding_id],
        ))
    return edits


def synthesize(layer_reports: list[LayerReport], document_path: str, domain: str) -> AuditReport:
    """Merge layer reports, deduplicate, and generate mandatory edits."""
    all_findings: list[Finding] = []
    for report in layer_reports:
        all_findings.extend(report.findings)

    # Sort by severity
    all_findings.sort(key=lambda f: SEVERITY_ORDER.get(f.severity, 99))

    # Deduplicate
    deduped = _deduplicate_findings(all_findings)

    # Count by severity
    by_severity: dict[str, int] = {}
    for f in deduped:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1

    # Citation stats from Layer 2
    l2_findings = [f for f in deduped if f.layer == 2]
    citations_checked = len(l2_findings)
    citations_verified = sum(1 for f in l2_findings if f.verified is True)
    citations_refuted = sum(1 for f in l2_findings if f.verified is False)

    # Generate mandatory edits
    mandatory_edits = _generate_mandatory_edits(deduped)

    synthesis = {
        "total_findings": len(deduped),
        "findings_by_severity": by_severity,
        "citations_checked": citations_checked,
        "citations_verified": citations_verified,
        "citations_refuted": citations_refuted,
        "mandatory_edit_count": len(mandatory_edits),
        "layers_run": [r.layer for r in layer_reports],
    }

    return AuditReport(
        schema_version=SCHEMA_VERSION,
        document_path=document_path,
        domain=domain,
        generated_at=datetime.now(timezone.utc).isoformat(),
        layers=layer_reports,
        synthesis=synthesis,
        mandatory_edits=mandatory_edits,
    )


# =============================================================================
# OUTPUT FORMATTERS
# =============================================================================


def _to_feedback_json(report: AuditReport) -> dict[str, Any]:
    """Convert to collider_feedback/ compatible JSON."""
    return {
        "schema_version": report.schema_version,
        "document_path": report.document_path,
        "domain": report.domain,
        "generated_at": report.generated_at,
        "synthesis": report.synthesis,
        "mandatory_edits": [asdict(e) for e in report.mandatory_edits],
        "layers": [
            {
                "layer": lr.layer,
                "layer_name": lr.layer_name,
                "llm_model": lr.llm_model,
                "finding_count": len(lr.findings),
                "findings": [asdict(f) for f in lr.findings],
            }
            for lr in report.layers
        ],
    }


def _to_markdown(report: AuditReport) -> str:
    """Convert to actionable markdown with diff-style mandatory edits."""
    lines = [
        "# Adversarial Audit Report",
        "",
        f"**Document:** `{report.document_path}`",
        f"**Domain:** {report.domain}",
        f"**Generated:** {report.generated_at}",
        "",
        "## Executive Summary",
        "",
    ]

    syn = report.synthesis
    lines.append(f"- **Total findings:** {syn.get('total_findings', 0)}")
    by_sev = syn.get("findings_by_severity", {})
    sev_parts = [f"{k}: {v}" for k, v in sorted(by_sev.items(), key=lambda x: SEVERITY_ORDER.get(x[0], 99))]
    if sev_parts:
        lines.append(f"- **By severity:** {', '.join(sev_parts)}")
    if syn.get("citations_checked"):
        lines.append(
            f"- **Citations:** {syn['citations_checked']} checked, "
            f"{syn.get('citations_verified', 0)} verified, "
            f"{syn.get('citations_refuted', 0)} refuted"
        )
    lines.append(f"- **Mandatory edits:** {syn.get('mandatory_edit_count', 0)}")
    lines.append("")

    # Mandatory edits section
    if report.mandatory_edits:
        lines.append("## Mandatory Edits")
        lines.append("")
        for i, edit in enumerate(report.mandatory_edits, 1):
            lines.append(f"### Edit {i} [{edit.severity.upper()}]")
            lines.append(f"**Location:** {edit.location}")
            lines.append(f"**Reason:** {edit.reason}")
            lines.append("")
            lines.append("```diff")
            lines.append(f"- {edit.original}")
            lines.append(f"+ {edit.replacement}")
            lines.append("```")
            lines.append("")

    # Per-layer findings
    for lr in report.layers:
        lines.append(f"## Layer {lr.layer}: {lr.layer_name}")
        lines.append(f"*Model: {lr.llm_model} | Findings: {len(lr.findings)}*")
        lines.append("")

        if lr.error:
            lines.append(f"> **Error:** {lr.error}")
            lines.append("")

        for f in lr.findings:
            severity_icon = {"critical": "!!!", "high": "!!", "medium": "!", "low": "~", "info": "i"}.get(f.severity, "?")
            lines.append(f"- **[{severity_icon}] {f.finding_id}** ({f.severity}/{f.category}): {f.title}")
            if f.description:
                lines.append(f"  - {f.description}")
            if f.evidence:
                lines.append(f"  - Evidence: `{f.evidence[:120]}`")
            if f.suggestion:
                lines.append(f"  - Fix: {f.suggestion}")
            if f.verified is not None:
                lines.append(f"  - Verified: {'YES' if f.verified else 'NO'}")
            lines.append("")

    # Metadata
    lines.extend([
        "---",
        f"*Schema: {report.schema_version} | Layers: {[r.layer for r in report.layers]}*",
    ])

    return "\n".join(lines)


def _write_to_feedback_sink(report: AuditReport) -> list[str]:
    """Write JSON report to collider_feedback/ sink."""
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    doc_slug = re.sub(r"[^a-z0-9]", "_", Path(report.document_path).stem.lower())[:40]

    paths_written: list[str] = []

    # JSON
    json_path = FEEDBACK_DIR / f"adversarial_audit_{doc_slug}_{stamp}.json"
    json_data = _to_feedback_json(report)
    json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
    paths_written.append(str(json_path))

    # Latest symlink-style copy
    latest_json = FEEDBACK_DIR / f"adversarial_audit_{doc_slug}_latest.json"
    shutil.copy2(json_path, latest_json)
    paths_written.append(str(latest_json))

    # Markdown
    md_path = FEEDBACK_DIR / f"adversarial_audit_{doc_slug}_{stamp}.md"
    md_path.write_text(_to_markdown(report), encoding="utf-8")
    paths_written.append(str(md_path))

    return paths_written


# =============================================================================
# ORCHESTRATOR
# =============================================================================


def run_audit(
    document_path: str,
    domain: str = "general",
    layers: Optional[list[int]] = None,
    dry_run: bool = False,
    output_json: Optional[str] = None,
    output_md: Optional[str] = None,
    no_sink: bool = False,
) -> AuditReport:
    """Run the full three-layer adversarial audit pipeline."""
    path = Path(document_path)
    if not path.exists():
        print(f"Error: Document not found: {document_path}", file=sys.stderr)
        sys.exit(1)

    document_text = path.read_text(encoding="utf-8", errors="ignore")
    run_layers = layers or [1, 2, 3]

    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"ADVERSARIAL AUDITOR", file=sys.stderr)
    print(f"  Document: {document_path} ({len(document_text):,} chars)", file=sys.stderr)
    print(f"  Domain:   {domain} ({DOMAIN_PROFILES.get(domain, {}).get('name', 'unknown')})", file=sys.stderr)
    print(f"  Layers:   {run_layers}", file=sys.stderr)
    print(f"  Models:   Cerebras={CEREBRAS_MODEL}, Perplexity={PERPLEXITY_MODEL}", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)

    if dry_run:
        print("\n[DRY RUN] Would execute:", file=sys.stderr)
        if 1 in run_layers:
            chunks = _chunk_document(document_text)
            print(f"  Layer 1: {len(chunks)} chunk(s) via Cerebras", file=sys.stderr)
        if 2 in run_layers:
            print(f"  Layer 2: citation checks via Perplexity + Cerebras", file=sys.stderr)
        if 3 in run_layers:
            validators = DOMAIN_PROFILES.get(domain, {}).get("deterministic_validators", [])
            print(f"  Layer 3: {len(validators)} deterministic checks + Cerebras domain audit", file=sys.stderr)
        print(f"\n  Estimated cost: $0.01-0.04", file=sys.stderr)
        print(f"  Output: JSON + Markdown to collider_feedback/", file=sys.stderr)
        # Return empty report for dry run
        return AuditReport(
            schema_version=SCHEMA_VERSION,
            document_path=document_path,
            domain=domain,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    layer_reports: list[LayerReport] = []
    citations_to_check: list[CitationToCheck] = []

    # Layer 1: Adversarial Review
    if 1 in run_layers:
        print(f"\n[Layer 1/3] Adversarial Review", file=sys.stderr)
        l1_report, citations_to_check = run_layer1(document_text, document_path, domain)
        layer_reports.append(l1_report)
        print(f"  Found {len(l1_report.findings)} findings, {len(citations_to_check)} citations to check", file=sys.stderr)

    # Layer 3: Domain Audit (runs independently from raw document)
    if 3 in run_layers:
        print(f"\n[Layer 3/3] Domain Audit ({domain})", file=sys.stderr)
        l3_report = run_layer3(document_text, domain)
        layer_reports.append(l3_report)
        print(f"  Found {len(l3_report.findings)} findings", file=sys.stderr)

    # Layer 2: Evidence Audit (consumes citations from Layer 1)
    if 2 in run_layers:
        if not citations_to_check and 1 not in run_layers:
            print(f"\n[Layer 2/3] Evidence Audit: skipped (no citations from Layer 1)", file=sys.stderr)
        else:
            print(f"\n[Layer 2/3] Evidence Audit ({len(citations_to_check)} citations)", file=sys.stderr)
            l2_report = run_layer2(citations_to_check)
            layer_reports.append(l2_report)
            print(f"  Checked {len(citations_to_check)} citations", file=sys.stderr)

    # Synthesis
    print(f"\n[Synthesis]", file=sys.stderr)
    report = synthesize(layer_reports, document_path, domain)
    print(f"  Total findings: {report.synthesis.get('total_findings', 0)}", file=sys.stderr)
    print(f"  Mandatory edits: {report.synthesis.get('mandatory_edit_count', 0)}", file=sys.stderr)

    # Output
    if output_json:
        json_data = _to_feedback_json(report)
        Path(output_json).write_text(json.dumps(json_data, indent=2), encoding="utf-8")
        print(f"  JSON: {output_json}", file=sys.stderr)

    if output_md:
        Path(output_md).write_text(_to_markdown(report), encoding="utf-8")
        print(f"  Markdown: {output_md}", file=sys.stderr)

    if not no_sink:
        sink_paths = _write_to_feedback_sink(report)
        print(f"  Feedback sink:", file=sys.stderr)
        for p in sink_paths:
            print(f"    - {p}", file=sys.stderr)

    # Print markdown to stdout
    print("")
    print(_to_markdown(report))

    return report


# =============================================================================
# CLI
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Three-Layer Adversarial Auditor for document IP and accuracy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full three-layer audit
  doppler run -- python adversarial_auditor.py audit doc.md --domain smoc

  # Single layer only
  doppler run -- python adversarial_auditor.py audit doc.md --layer 1

  # Dry run (no API calls)
  python adversarial_auditor.py audit doc.md --dry-run

Domains: smoc, general
Layers:  1=Adversarial, 2=Evidence, 3=Domain
""",
    )
    sub = parser.add_subparsers(dest="command")

    audit = sub.add_parser("audit", help="Run adversarial audit on a document")
    audit.add_argument("document", help="Path to document (md, txt)")
    audit.add_argument("--domain", "-d", default="general",
                       choices=list(DOMAIN_PROFILES.keys()),
                       help="Domain profile (default: general)")
    audit.add_argument("--layer", "-l", type=int, action="append", dest="layers",
                       choices=[1, 2, 3],
                       help="Run specific layer(s) only (repeatable)")
    audit.add_argument("--dry-run", action="store_true",
                       help="Show what would run without making API calls")
    audit.add_argument("--output-json", "-oj", help="Write JSON report to this path")
    audit.add_argument("--output-md", "-om", help="Write Markdown report to this path")
    audit.add_argument("--no-sink", action="store_true",
                       help="Skip writing to collider_feedback/ sink")

    args = parser.parse_args()

    if args.command == "audit":
        run_audit(
            document_path=args.document,
            domain=args.domain,
            layers=args.layers,
            dry_run=args.dry_run,
            output_json=args.output_json,
            output_md=args.output_md,
            no_sink=args.no_sink,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
