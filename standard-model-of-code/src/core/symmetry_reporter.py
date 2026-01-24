"""
Symmetry Reporter for Wave-Particle Symmetry.
Generates reports comparing documentation (Wave) with implementation (Particle).
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field, asdict

from .visibility_analyzer import VisibilityAnalyzer, Visibility
from .wave_extractor import WaveExtractor
from .identity_matcher import IdentityMatcher, SymmetryResult


@dataclass
class ConfidenceBuckets:
    """Match confidence distribution."""
    exact: int = 0
    qualified: int = 0
    fuzzy: int = 0
    rejected: int = 0


@dataclass
class SymmetryMetrics:
    """Core symmetry metrics."""
    total_public_exports: int
    matched: int
    undocumented: int
    orphan_docs: int
    unresolved: int


@dataclass
class SymmetryReport:
    """Complete symmetry analysis report."""
    symmetry_score: float
    coverage: float
    tier: str
    metrics: SymmetryMetrics
    confidence_buckets: ConfidenceBuckets
    top_undocumented: List[str] = field(default_factory=list)
    top_orphan_docs: List[str] = field(default_factory=list)
    unresolved_matches: List[str] = field(default_factory=list)
    timestamp: str = ""
    files_analyzed: int = 0
    docs_analyzed: int = 0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "symmetry_score": round(self.symmetry_score, 4),
            "coverage": round(self.coverage, 4),
            "tier": self.tier,
            "metrics": asdict(self.metrics),
            "confidence_buckets": asdict(self.confidence_buckets),
            "top_offenders": {
                "undocumented": self.top_undocumented[:10],
                "orphan_docs": self.top_orphan_docs[:10]
            },
            "unresolved_matches": self.unresolved_matches[:10],
            "drift": {
                "timestamp": self.timestamp,
                "files_analyzed": self.files_analyzed,
                "docs_analyzed": self.docs_analyzed
            }
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            "# Wave-Particle Symmetry Report",
            "",
            f"**Generated:** {self.timestamp}",
            f"**Tier:** {self.tier}",
            "",
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Symmetry Score | {self.symmetry_score:.1%} |",
            f"| Coverage | {self.coverage:.1%} |",
            f"| Public Exports | {self.metrics.total_public_exports} |",
            f"| Matched | {self.metrics.matched} |",
            f"| Undocumented | {self.metrics.undocumented} |",
            f"| Orphan Docs | {self.metrics.orphan_docs} |",
            "",
            "## Confidence Distribution",
            "",
            f"| Match Type | Count |",
            f"|------------|-------|",
            f"| Exact (1.0) | {self.confidence_buckets.exact} |",
            f"| Qualified (0.95) | {self.confidence_buckets.qualified} |",
            f"| Fuzzy (>=0.75) | {self.confidence_buckets.fuzzy} |",
            f"| Rejected (<0.75) | {self.confidence_buckets.rejected} |",
            "",
        ]

        if self.top_undocumented:
            lines.extend([
                "## Top Undocumented APIs",
                "",
                "These public APIs lack documentation:",
                "",
            ])
            for item in self.top_undocumented[:10]:
                lines.append(f"- `{item}`")
            lines.append("")

        if self.top_orphan_docs:
            lines.extend([
                "## Orphan Documentation",
                "",
                "These documented items have no matching code:",
                "",
            ])
            for item in self.top_orphan_docs[:10]:
                lines.append(f"- `{item}`")
            lines.append("")

        if self.unresolved_matches:
            lines.extend([
                "## Unresolved Matches",
                "",
                "These references could not be confidently matched:",
                "",
            ])
            for item in self.unresolved_matches[:10]:
                lines.append(f"- `{item}`")
            lines.append("")

        return "\n".join(lines)

    def to_brief(self) -> str:
        """One-line summary."""
        return f"{self.tier} ({self.symmetry_score:.0%}) - {self.metrics.matched}/{self.metrics.total_public_exports} matched, {self.metrics.undocumented} undoc, {self.metrics.orphan_docs} orphan"


def get_tier(score: float) -> str:
    """Determine tier from symmetry score."""
    if score >= 0.98:
        return "DIAMOND"
    elif score >= 0.90:
        return "GOLD"
    elif score >= 0.75:
        return "SILVER"
    elif score >= 0.60:
        return "BRONZE"
    else:
        return "UNRANKED"


class SymmetryAnalyzer:
    """Orchestrates Wave-Particle symmetry analysis."""

    def __init__(self, repo_path: Path, docs_path: Path, threshold: float = 0.75):
        self.repo_path = Path(repo_path)
        self.docs_path = Path(docs_path)
        self.threshold = threshold

    def analyze(self) -> SymmetryReport:
        """Run full symmetry analysis and generate report."""
        # Extract Particle (code symbols with visibility)
        particle_ids, files_count = self._extract_particles()

        # Extract Wave (documentation references)
        wave_extractor = WaveExtractor(self.docs_path)
        wave_nodes = wave_extractor.extract_all()
        wave_ids = list(set(node.id for node in wave_nodes))
        docs_count = len(set(node.source_file for node in wave_nodes))

        # Match Wave to Particle
        matcher = IdentityMatcher(threshold=self.threshold)
        result = matcher.match(wave_ids, particle_ids)

        # Build confidence buckets
        buckets = ConfidenceBuckets()
        for match in result.matched:
            if match.match_type == "exact":
                buckets.exact += 1
            elif match.match_type == "qualified":
                buckets.qualified += 1
            elif match.match_type == "fuzzy":
                buckets.fuzzy += 1
        buckets.rejected = len(result.orphan_docs)

        # Calculate metrics
        total_public = len(particle_ids)
        matched_count = len([m for m in result.matched if m.confidence >= self.threshold])

        metrics = SymmetryMetrics(
            total_public_exports=total_public,
            matched=matched_count,
            undocumented=len(result.undocumented),
            orphan_docs=len(result.orphan_docs),
            unresolved=buckets.rejected
        )

        # Calculate scores
        coverage = matched_count / total_public if total_public > 0 else 0.0
        symmetry_score = result.symmetry_score

        # Unresolved matches (low confidence)
        unresolved = [m.wave_id for m in result.matched if m.confidence < self.threshold]

        return SymmetryReport(
            symmetry_score=symmetry_score,
            coverage=coverage,
            tier=get_tier(symmetry_score),
            metrics=metrics,
            confidence_buckets=buckets,
            top_undocumented=result.undocumented[:20],
            top_orphan_docs=result.orphan_docs[:20],
            unresolved_matches=unresolved[:20],
            files_analyzed=files_count,
            docs_analyzed=docs_count
        )

    def _extract_particles(self) -> tuple[List[str], int]:
        """Extract public symbols from Python files."""
        public_symbols = []
        files_count = 0

        for py_file in self.repo_path.rglob("*.py"):
            # Skip test files and hidden directories
            if "/test" in str(py_file) or "/.venv" in str(py_file):
                continue

            try:
                source = py_file.read_text(encoding='utf-8')
                module_path = str(py_file.relative_to(self.repo_path)).replace("/", ".").replace(".py", "")

                analyzer = VisibilityAnalyzer(source, module_path)
                exports = analyzer.get_public_exports()

                # Add qualified names
                for name in exports:
                    if "." not in name:
                        public_symbols.append(f"{module_path}.{name}")
                    else:
                        public_symbols.append(name)

                files_count += 1
            except Exception:
                continue

        return public_symbols, files_count


def run_symmetry_analysis(
    repo_path: str,
    docs_path: str,
    output_format: str = "brief",
    threshold: float = 0.75
) -> str:
    """
    Run symmetry analysis and return formatted output.

    Args:
        repo_path: Path to repository root
        docs_path: Path to documentation directory
        output_format: "brief", "json", or "markdown"
        threshold: Minimum confidence for matching (0.0-1.0)

    Returns:
        Formatted report string
    """
    analyzer = SymmetryAnalyzer(
        repo_path=Path(repo_path),
        docs_path=Path(docs_path),
        threshold=threshold
    )

    report = analyzer.analyze()

    if output_format == "json":
        return report.to_json()
    elif output_format == "markdown":
        return report.to_markdown()
    else:
        return report.to_brief()
