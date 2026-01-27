"""
Output Module - Stone Tool Contract
===================================

Standard Model Classification:
-----------------------------
D1_KIND:     DAT.ENT.A (Data Entity - structured output)
D2_LAYER:    Core (domain objects, no dependencies)
D3_ROLE:     Mapper (transforms internal state to external format)
D4_BOUNDARY: Output (produces JSON/dict for external consumption)
D5_STATE:    Stateless (dataclasses are immutable value objects)
D6_EFFECT:   Pure (serialization is deterministic)
D7_LIFECYCLE: Use (created during analysis, consumed by callers)
D8_TRUST:    98 (simple dataclasses, no complex logic)

RPBL: (1, 1, 3, 1)
    R=1: Single responsibility - define output schema
    P=1: Pure - no side effects, just data structures
    B=3: Output boundary (exported to external consumers)
    L=1: Ephemeral - instances created per analysis run

Communication Theory:
    Source:   Analysis pipeline
    Channel:  JSON/dict serialization
    Message:  AnalyzeResult structure
    Receiver: AI consumers, external tools, human readers
    Redundancy: Fields have defaults, schema is explicit

Tool Theory:
    Universe: STONE_TOOLS (AI-native output)
    Role:     S-StructuredData (produces JSON for AI parsing)
    Stone Tool Test: PARTIAL (JSON readable, but designed for AI)
    Consumer: S-AIConsumer (primary), S-HybridConsumer (secondary)

See Also:
    context-management/docs/specs/ANALYZE_OUTPUT_CONTRACT.md
"""

import json
import hashlib
import random
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class ContextManifest:
    """
    Manifest of what context was actually seen (for auditability).

    This enables reproducibility - given the same manifest, you can
    reconstruct exactly what the model saw.

    Aligns with Theory Amendment A3 (Confidence): We track WHAT
    the model saw, not just WHAT it said.
    """
    bundle_hash: str = ""
    token_estimate: int = 0
    char_count: int = 0
    truncated: bool = False
    limits: Dict[str, int] = field(default_factory=lambda: {"max_files": 50, "max_tokens": 200000})
    injections: List[Dict[str, Any]] = field(default_factory=list)
    files_included: List[Dict[str, Any]] = field(default_factory=list)
    files_excluded: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AnalyzeResult:
    """
    Structured output for Stone Tool contract.

    This is the canonical output format for all analyze.py operations.
    External consumers (AI agents, pipelines) can rely on this schema.

    The design follows Information Theory principles:
    - All fields have defaults (noise tolerance)
    - Structure is explicit (Shannon encoding)
    - Metadata enables provenance tracking (scientific measurement)
    """
    # Identity
    run_id: str = ""
    query: str = ""
    mode: str = "standard"

    # Models used
    models: Dict[str, str] = field(default_factory=dict)

    # ACI routing (if used)
    aci: Dict[str, Any] = field(default_factory=dict)

    # Context manifest (what the model saw)
    context: ContextManifest = field(default_factory=ContextManifest)

    # External research (if used)
    external: Dict[str, Any] = field(default_factory=lambda: {
        "requested": False,
        "queries": [],
        "results": []
    })

    # The actual answer
    answer: Dict[str, Any] = field(default_factory=lambda: {
        "summary": "",
        "body": "",
        "citations": [],
        "confidence": 0.0
    })

    # Actions suggested by analysis
    actions: List[Dict[str, Any]] = field(default_factory=list)

    # Artifacts produced
    artifacts: List[Dict[str, Any]] = field(default_factory=list)

    # Timing metrics
    timing: Dict[str, int] = field(default_factory=lambda: {
        "total_ms": 0,
        "context_build_ms": 0,
        "model_call_ms": 0
    })

    # Cost tracking
    cost: Dict[str, Any] = field(default_factory=lambda: {
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_usd": 0.0
    })

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling nested dataclasses."""
        result = asdict(self)
        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @staticmethod
    def generate_run_id() -> str:
        """
        Generate unique run ID: ISO timestamp + short hash.

        Format: 2026-01-27T15:30:00Z__a1b2c3
        This enables:
        - Chronological sorting
        - Uniqueness via hash
        - Human readability
        """
        ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        short_hash = hashlib.sha256(f"{ts}{random.random()}".encode()).hexdigest()[:6]
        return f"{ts}__{short_hash}"


def compute_bundle_hash(files: List[Path]) -> str:
    """
    Compute SHA256 hash of file contents for reproducibility.

    This implements the Manifest Writer pattern from Theory Amendment.
    Given the same files, you get the same hash.

    Args:
        files: List of file paths to hash

    Returns:
        Hash string in format "sha256:<first 16 chars>"
    """
    hasher = hashlib.sha256()
    for f in sorted(files):
        try:
            hasher.update(f.read_bytes())
        except Exception:
            pass
    return f"sha256:{hasher.hexdigest()[:16]}"


def estimate_cost(input_tokens: int, output_tokens: int, model: str, pricing: Dict[str, Any] = None) -> float:
    """
    Estimate cost based on token usage.

    Default pricing is for Gemini models (per 1M tokens).
    Actual pricing should be loaded from config.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name
        pricing: Optional pricing dict from config

    Returns:
        Estimated cost in USD
    """
    # Default pricing (Gemini, per 1M tokens)
    default_pricing = {
        "gemini-3-pro-preview": {"input": 1.25, "output": 5.00},
        "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-2.0-flash-001": {"input": 0.075, "output": 0.30},
        "gemini-2.0-flash": {"input": 0.075, "output": 0.30},
    }

    pricing = pricing or default_pricing

    # Find matching model pricing
    model_pricing = None
    for model_key, prices in pricing.items():
        if model_key in model or model in model_key:
            model_pricing = prices
            break

    if not model_pricing:
        # Fallback to flash pricing
        model_pricing = default_pricing.get("gemini-2.0-flash-001", {"input": 0.075, "output": 0.30})

    input_cost = (input_tokens / 1_000_000) * model_pricing.get("input", 0.075)
    output_cost = (output_tokens / 1_000_000) * model_pricing.get("output", 0.30)

    return input_cost + output_cost
