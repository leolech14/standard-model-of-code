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
