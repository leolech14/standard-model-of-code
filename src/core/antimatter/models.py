"""
Antimatter Models
=================

Data models for antimatter evaluation results.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Violation:
    """A detected antimatter violation."""
    law_id: str
    law_name: str
    particle_id: str
    particle_name: str
    particle_type: str
    file_path: str
    line: int
    message: str
    severity: str  # error, warning, info
    confidence: float
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "law_id": self.law_id,
            "law_name": self.law_name,
            "particle": self.particle_name,
            "type": self.particle_type,
            "file": self.file_path,
            "line": self.line,
            "message": self.message,
            "severity": self.severity,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


@dataclass
class EvaluationResult:
    """Result of evaluating all laws against a particle set."""
    total_particles: int
    laws_checked: int
    violations: List[Violation] = field(default_factory=list)
    by_law: Dict[str, int] = field(default_factory=dict)
    by_severity: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "total_particles": self.total_particles,
            "laws_checked": self.laws_checked,
            "total_violations": len(self.violations),
            "by_law": self.by_law,
            "by_severity": self.by_severity,
            "violations": [v.to_dict() for v in self.violations],
        }

    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0

    @property
    def error_count(self) -> int:
        """Count of error-severity violations."""
        return self.by_severity.get("error", 0)

    @property
    def warning_count(self) -> int:
        """Count of warning-severity violations."""
        return self.by_severity.get("warning", 0)
