#!/usr/bin/env python3
"""
Boundary Analyzer - PROJECT_elements Internal Organization Validator

Part of the Maintenance Layer. Validates that declared boundaries
(CODOME/CONTEXTOME/CONCORDANCES) match actual directory structure.

CONCORDANCE = A PURPOSE-defined region where code and docs share aligned purpose.
States: CONCORDANT (aligned), DISCORDANT (conflict), UNVOICED (no docs), UNREALIZED (no code)

Theory: L1_DEFINITIONS.md SS3.4 (Concordance definition)
Theory: L1_DEFINITIONS.md SS3.5 (Concordance Health Score)
  Health(k) = |CONCORDANT| / (|CONCORDANT| + |DISCORDANT| + |UNVOICED| + |UNREALIZED|)
  Target: > 80% for production systems.

Usage:
    python boundary_analyzer.py                    # Full analysis
    python boundary_analyzer.py --quick            # Quick check (exit code only)
    python boundary_analyzer.py --fix              # Generate fix suggestions
    python boundary_analyzer.py --json             # JSON output for CI
    python boundary_analyzer.py --watch            # Continuous monitoring

Integration:
    - Called by: boot.sh, pre-commit hooks, CI pipeline
    - Outputs to: .agent/intelligence/boundary_analysis.json
    - Logs to: .agent/intelligence/boundary_scan_log.txt
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any
from dataclasses import dataclass, field, asdict

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent

# Canonical boundary definitions
REALMS = {
    "PARTICLE": {
        "path": "particle/",
        "description": "Collider engine, atoms, schemas, theory",
        "contains_codome": True,
        "contains_contextome": True,
    },
    "WAVE": {
        "path": "wave/",
        "description": "AI tools, planning, research",
        "contains_codome": True,
        "contains_contextome": True,
    },
    "OBSERVER": {
        "path": ".agent/",
        "description": "Task registry, intelligence, governance",
        "contains_codome": True,
        "contains_contextome": True,
    },
}

# Declared concordances from CONCORDANCES.md
# Concordance = PURPOSE-aligned region spanning CODOME + CONTEXTOME
DECLARED_CONCORDANCES = {
    "Pipeline": {
        "codome": ["particle/src/core/"],
        "contextome": ["particle/docs/specs/"],
    },
    "Visualization": {
        "codome": ["particle/src/core/viz/"],
        "contextome": ["particle/docs/specs/VISUALIZATION*.md"],
    },
    "Governance": {
        "codome": [".agent/tools/"],
        "contextome": [".agent/registry/", ".agent/specs/"],
    },
    "AI_Tools": {
        "codome": ["wave/tools/ai/"],
        "contextome": ["wave/config/"],
    },
    "Theory": {
        "codome": [],  # Theory has no code (CONTEXTOME_ONLY)
        "contextome": ["particle/docs/MODEL.md"],
    },
    "Archive": {
        "codome": ["wave/tools/archive/"],
        "contextome": ["wave/tools/archive/config.yaml"],
    },
    "Research": {
        "codome": ["wave/tools/mcp/"],
        "contextome": ["wave/tools/mcp/mcp_factory/"],
    },
}

# File type classifications
CODOME_EXTENSIONS = {'.py', '.js', '.ts', '.go', '.rs', '.java', '.css', '.html', '.scm', '.sql', '.sh'}
CONTEXTOME_EXTENSIONS = {'.md', '.yaml', '.yml', '.json'}

# Known directories that should be declared
EXPECTED_DIRECTORIES = {
    # Particle hemisphere (Codome / Body)
    "particle/src/",
    "particle/docs/",
    "particle/tools/",
    "particle/schema/",
    "particle/tests/",
    "particle/research/",
    "particle/output/",
    "particle/.github/",
    "particle/audio/",
    "particle/collider_feedback/",
    "particle/data/",
    "particle/graphrag_out/",
    "particle/ops/",
    "particle/particle/",
    "particle/proofs/",
    "particle/scripts/",
    # Wave hemisphere (Contextome / Brain)
    "wave/tools/",
    "wave/docs/",
    "wave/config/",
    "wave/viz/",
    "wave/intelligence/",
    "wave/experiments/",
    "wave/data/",
    "wave/rainmaker/",
    "wave/llm-threads/",
    "wave/output/",
    "wave/reference_datasets/",
    "wave/registry/",
    "wave/services/",
    "wave/tests/",
    # Observer (.agent/)
    ".agent/registry/",
    ".agent/tools/",
    ".agent/specs/",
    ".agent/intelligence/",
    ".agent/macros/",
    ".agent/deck/",
    ".agent/hooks/",
    ".agent/emergency/",
    ".agent/docs/",
    ".agent/agents/",
    ".agent/config/",
    ".agent/citizenship/",
    ".agent/handoffs/",
    ".agent/roadmaps/",
    ".agent/runs/",
    ".agent/schema/",
    ".agent/sprints/",
    ".agent/state/",
    # Root-level project directories
    "research/",
    "research/gemini/",
    "research/perplexity/",
    "docs/",
    "docs/nav/",
    "docs/reader/",
    "docs/charts/",
    "docs/essentials/",
    "docs/frontier/",
    "docs/specs/",
    "reports/",
    "reports/archives/",
    "reports/consolidation/",
    "reports/audits/",
    "reports/refinery/",
    "governance/",
    "governance/staging/",
    "observer/",
    "observer/merged/",
    "observer/analysis/",
    "observer/docs/",
    "observer/source-a/",
    "observer/source-b/",
    "collider_feedback/",
    "context-management/",
    "context-management/intelligence/",
    "assets/",
    "logs/",
    "notebook-lm/",
    "output/",
    "output/audit/",
    "scripts/",
    "tools/",
    "tools/experiments/",
    "tools/file_explorer/",
}


@dataclass
class BoundaryIssue:
    """A single boundary violation or concern."""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # UNDECLARED, UNREALIZED, DISCORDANT, UNVOICED
    path: str
    message: str
    suggestion: str = ""


@dataclass
class ConcordanceHealth:
    """Health score for a single concordance region.

    Theory: L1_DEFINITIONS.md SS3.5
    Health(k) = |CONCORDANT| / (|CONCORDANT| + |DISCORDANT| + |UNVOICED| + |UNREALIZED|)

    Theory: L1_DEFINITIONS.md SS3.4
    sigma(k) = cosine_similarity(declared_purpose_vector, actual_pattern_vector)
    """
    name: str = ""
    state: str = ""  # CONCORDANT, DISCORDANT, UNVOICED, UNREALIZED, CONTEXTOME_ONLY, MISSING
    health: float = 0.0  # [0.0, 1.0]
    sigma: float = 0.0  # [0.0, 1.0] — structural alignment score
    concordant_count: int = 0
    discordant_count: int = 0
    unvoiced_count: int = 0
    unrealized_count: int = 0


@dataclass
class BoundaryReport:
    """Complete boundary analysis report."""
    timestamp: str = ""
    alignment_score: float = 0.0
    overall_health: float = 0.0  # Mean Health(k) across all concordances
    total_directories: int = 0
    declared_directories: int = 0
    undeclared_directories: int = 0
    phantom_declarations: int = 0
    issues: List[BoundaryIssue] = field(default_factory=list)
    realms_status: Dict[str, Any] = field(default_factory=dict)
    concordances_status: Dict[str, Any] = field(default_factory=dict)
    concordance_health: List[ConcordanceHealth] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "alignment_score": self.alignment_score,
            "overall_health": round(self.overall_health, 4),
            "total_directories": self.total_directories,
            "declared_directories": self.declared_directories,
            "undeclared_directories": self.undeclared_directories,
            "phantom_declarations": self.phantom_declarations,
            "issues": [asdict(i) for i in self.issues],
            "realms_status": self.realms_status,
            "concordances_status": self.concordances_status,
            "concordance_health": [asdict(h) for h in self.concordance_health],
            "recommendations": self.recommendations,
        }


class BoundaryAnalyzer:
    """Analyzes PROJECT_elements internal organization against declared boundaries."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.root = project_root
        self.report = BoundaryReport(timestamp=datetime.now().isoformat())

    def analyze(self) -> BoundaryReport:
        """Run complete boundary analysis."""
        self._analyze_realms()
        self._analyze_concordances()
        self._compute_concordance_health()
        self._compute_sigma()
        self._find_undeclared_directories()
        self._find_phantom_declarations()
        self._check_partition_integrity()
        self._calculate_score()
        self._generate_recommendations()
        return self.report

    def _analyze_realms(self):
        """Check if declared realms exist and contain expected content."""
        for realm_name, realm_info in REALMS.items():
            realm_path = self.root / realm_info["path"]
            exists = realm_path.exists()

            codome_count = 0
            contextome_count = 0

            if exists:
                for f in realm_path.rglob("*"):
                    if f.is_file():
                        if f.suffix in CODOME_EXTENSIONS:
                            codome_count += 1
                        elif f.suffix in CONTEXTOME_EXTENSIONS:
                            contextome_count += 1

            self.report.realms_status[realm_name] = {
                "path": str(realm_info["path"]),
                "exists": exists,
                "codome_files": codome_count,
                "contextome_files": contextome_count,
                "status": "VALID" if exists else "MISSING",
            }

            if not exists:
                self.report.issues.append(BoundaryIssue(
                    severity="CRITICAL",
                    category="PHANTOM",
                    path=str(realm_info["path"]),
                    message=f"Declared realm {realm_name} does not exist",
                    suggestion=f"Create {realm_info['path']} or remove from REALMS declaration",
                ))

    def _analyze_concordances(self):
        """Check if declared concordances have both codome and contextome components."""
        for conc_name, conc_info in DECLARED_CONCORDANCES.items():
            codome_exists = []
            contextome_exists = []

            # Check codome paths
            for pattern in conc_info.get("codome", []):
                if "*" in pattern:
                    matches = list(self.root.glob(pattern))
                    codome_exists.extend([str(m.relative_to(self.root)) for m in matches])
                else:
                    path = self.root / pattern
                    if path.exists():
                        codome_exists.append(pattern)

            # Check contextome paths
            for pattern in conc_info.get("contextome", []):
                if "*" in pattern:
                    matches = list(self.root.glob(pattern))
                    contextome_exists.extend([str(m.relative_to(self.root)) for m in matches])
                else:
                    path = self.root / pattern
                    if path.exists():
                        contextome_exists.append(pattern)

            # Determine status (concordance states)
            has_code = len(codome_exists) > 0
            has_context = len(contextome_exists) > 0
            expected_code = len(conc_info.get("codome", [])) > 0

            if has_code and has_context:
                status = "CONCORDANT"  # Purposes agree
            elif has_context and not expected_code:
                status = "CONTEXTOME_ONLY"  # Valid for Theory concordance
            elif has_code and not has_context:
                status = "UNVOICED"  # Code purpose not documented
            elif has_context and not has_code and expected_code:
                status = "UNREALIZED"  # Doc purpose not implemented
            else:
                status = "MISSING"

            self.report.concordances_status[conc_name] = {
                "codome_paths": codome_exists,
                "contextome_paths": contextome_exists,
                "status": status,
            }

            # Report issues
            if status == "UNVOICED":
                self.report.issues.append(BoundaryIssue(
                    severity="HIGH",
                    category="UNVOICED",
                    path=conc_name,
                    message=f"Concordance {conc_name} has code but no documentation",
                    suggestion=f"Add documentation to {conc_info.get('contextome', ['docs/'])[0]}",
                ))
            elif status == "UNREALIZED" and expected_code:
                self.report.issues.append(BoundaryIssue(
                    severity="MEDIUM",
                    category="UNREALIZED",
                    path=conc_name,
                    message=f"Concordance {conc_name} has documentation but no code",
                    suggestion="Implement the documented features or mark as planned",
                ))
            elif status == "MISSING":
                self.report.issues.append(BoundaryIssue(
                    severity="HIGH",
                    category="DISCORDANT",
                    path=conc_name,
                    message=f"Concordance {conc_name} is completely missing",
                    suggestion="Create concordance or remove from CONCORDANCES declaration",
                ))

    def _compute_concordance_health(self):
        """Compute Health(k) for each concordance and the overall project.

        Theory: L1_DEFINITIONS.md SS3.5
        Health(k) = |CONCORDANT| / (|CONCORDANT| + |DISCORDANT| + |UNVOICED| + |UNREALIZED|)

        Each concordance contributes 1 to exactly one state bucket.
        CONTEXTOME_ONLY is a valid non-pathological state (e.g., Theory) and
        counts as concordant for health purposes — its purpose is fully realized
        within the contextome alone.
        MISSING counts as discordant — the concordance was declared but nothing exists.
        """
        # Aggregate state counts across all concordances
        total_concordant = 0
        total_discordant = 0
        total_unvoiced = 0
        total_unrealized = 0

        for conc_name, conc_status in self.report.concordances_status.items():
            state = conc_status.get("status", "MISSING")

            # Map analyzer states to the four canonical L1 states
            c = d = u = r = 0
            if state == "CONCORDANT":
                c = 1
            elif state == "CONTEXTOME_ONLY":
                # Valid state — purpose is fully expressed in contextome
                c = 1
            elif state == "DISCORDANT" or state == "MISSING":
                d = 1
            elif state == "UNVOICED":
                u = 1
            elif state == "UNREALIZED":
                r = 1
            else:
                d = 1  # Unknown states treated as discordant

            total = c + d + u + r
            health = c / total if total > 0 else 0.0

            self.report.concordance_health.append(ConcordanceHealth(
                name=conc_name,
                state=state,
                health=round(health, 4),
                concordant_count=c,
                discordant_count=d,
                unvoiced_count=u,
                unrealized_count=r,
            ))

            total_concordant += c
            total_discordant += d
            total_unvoiced += u
            total_unrealized += r

        # Overall Health(k) = |CONCORDANT| / total
        grand_total = total_concordant + total_discordant + total_unvoiced + total_unrealized
        if grand_total > 0:
            self.report.overall_health = round(total_concordant / grand_total, 4)
        else:
            self.report.overall_health = 0.0

    def _compute_sigma(self):
        """Compute sigma alignment score for each concordance.

        Theory: L1_DEFINITIONS.md SS3.4
        sigma(k) = cosine_similarity(declared_purpose_vector, actual_pattern_vector)

        For each concordance region:
        - declared_vector: uniform [1, 1, 1, ...] across all declared paths
        - actual_vector: [file_count_path_1, file_count_path_2, ...] normalized

        Sigma measures structural SHAPE — how evenly content is distributed
        across declared paths. Health measures EXISTENCE (binary), sigma
        measures PROPORTION (continuous).

        A concordance with Health=1.0 but sigma=0.3 means: both codome and
        contextome exist, but content is heavily lopsided toward one path.
        """
        import math

        for ch in self.report.concordance_health:
            conc_info = DECLARED_CONCORDANCES.get(ch.name)
            if not conc_info:
                continue

            # Collect all declared paths (codome + contextome)
            all_paths = []
            for p in conc_info.get("codome", []):
                if "*" not in p:
                    all_paths.append(p)
            for p in conc_info.get("contextome", []):
                if "*" not in p:
                    all_paths.append(p)

            if not all_paths:
                # Glob-only patterns — skip sigma (can't define uniform vector)
                ch.sigma = 0.0
                continue

            # Build declared vector: uniform weight per path
            declared_vec = [1.0] * len(all_paths)

            # Build actual vector: file count per declared path
            actual_vec = []
            for path_str in all_paths:
                full_path = self.root / path_str
                if full_path.exists():
                    if full_path.is_dir():
                        count = sum(1 for f in full_path.rglob("*") if f.is_file())
                    else:
                        count = 1  # Single file declared
                else:
                    count = 0
                actual_vec.append(float(count))

            # Cosine similarity: dot(d, a) / (|d| * |a|)
            dot_product = sum(d * a for d, a in zip(declared_vec, actual_vec))
            mag_declared = math.sqrt(sum(d * d for d in declared_vec))
            mag_actual = math.sqrt(sum(a * a for a in actual_vec))

            if mag_declared > 0 and mag_actual > 0:
                ch.sigma = round(dot_product / (mag_declared * mag_actual), 4)
            else:
                ch.sigma = 0.0

    def _find_undeclared_directories(self):
        """Find directories that exist but aren't formally declared."""
        # Get all top-level directories and first-level subdirectories
        actual_dirs: Set[str] = set()

        # Top level
        for item in self.root.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in {'node_modules', '__pycache__', '.git', '.venv', '.tools_venv'}:
                actual_dirs.add(item.name + "/")
                # First level subdirs
                for subitem in item.iterdir():
                    if subitem.is_dir() and not subitem.name.startswith('__'):
                        actual_dirs.add(f"{item.name}/{subitem.name}/")

        # Add .agent explicitly
        agent_dir = self.root / ".agent"
        if agent_dir.exists():
            actual_dirs.add(".agent/")
            for subitem in agent_dir.iterdir():
                if subitem.is_dir():
                    actual_dirs.add(f".agent/{subitem.name}/")

        # Build set of declared directories
        declared_dirs: Set[str] = set()
        for realm_info in REALMS.values():
            declared_dirs.add(realm_info["path"])
        for conc_info in DECLARED_CONCORDANCES.values():
            for path in conc_info.get("codome", []) + conc_info.get("contextome", []):
                if not "*" in path:
                    declared_dirs.add(path.rstrip("/") + "/" if not path.endswith("/") else path)

        # Add expected directories
        declared_dirs.update(EXPECTED_DIRECTORIES)

        # Find undeclared
        undeclared = actual_dirs - declared_dirs
        self.report.total_directories = len(actual_dirs)
        self.report.declared_directories = len(declared_dirs & actual_dirs)
        self.report.undeclared_directories = len(undeclared)

        # Filter out build artifacts, caches, and virtual environments
        ignored = {
            'archive/', 'node_modules/', '.collider/', 'dist/', 'build/',
            'particle/artifacts/', 'particle/.venv/', 'particle/.collider/',
            'particle/.pytest_cache/', 'particle/collider.egg-info/',
            'wave/library/', '.claude/', '.git/', '__pycache__/',
            'governance/.quarto/',
        }
        significant_undeclared = {d for d in undeclared if not any(d.startswith(i.rstrip('/')) for i in ignored)}

        for dir_path in sorted(significant_undeclared):
            # Determine severity based on content
            full_path = self.root / dir_path
            file_count = sum(1 for _ in full_path.rglob("*") if _.is_file()) if full_path.exists() else 0

            severity = "HIGH" if file_count > 10 else "MEDIUM" if file_count > 0 else "LOW"

            self.report.issues.append(BoundaryIssue(
                severity=severity,
                category="UNDECLARED",
                path=dir_path,
                message=f"Directory exists but is not declared ({file_count} files)",
                suggestion=f"Add to CONCORDANCES.md or .agent/CODOME_MANIFEST.yaml",
            ))

    def _find_phantom_declarations(self):
        """Find declared paths that don't exist."""
        phantom_count = 0

        for conc_name, conc_info in DECLARED_CONCORDANCES.items():
            for path in conc_info.get("codome", []) + conc_info.get("contextome", []):
                if "*" not in path:
                    full_path = self.root / path
                    if not full_path.exists():
                        phantom_count += 1
                        self.report.issues.append(BoundaryIssue(
                            severity="MEDIUM",
                            category="UNREALIZED",
                            path=path,
                            message=f"Declared in {conc_name} but doesn't exist",
                            suggestion=f"Create {path} or remove from concordance declaration",
                        ))

        self.report.phantom_declarations = phantom_count

    def _check_partition_integrity(self):
        """Verify CODOME ∩ CONTEXTOME = ∅ (disjoint partition)."""
        # Sample check - verify no file is classified as both
        violations = []

        for realm_info in REALMS.values():
            realm_path = self.root / realm_info["path"]
            if realm_path.exists():
                for f in realm_path.rglob("*"):
                    if f.is_file():
                        is_codome = f.suffix in CODOME_EXTENSIONS
                        is_contextome = f.suffix in CONTEXTOME_EXTENSIONS

                        # Check for edge cases (e.g., .json could be config or data)
                        if f.suffix == '.json':
                            # JSON in src/ is likely data/config used by code
                            if 'src/' in str(f) or 'config/' in str(f):
                                continue  # Acceptable

                        if is_codome and is_contextome:
                            violations.append(str(f.relative_to(self.root)))

        if violations:
            self.report.issues.append(BoundaryIssue(
                severity="HIGH",
                category="DRIFT",
                path="PARTITION",
                message=f"Found {len(violations)} files that violate CODOME/CONTEXTOME partition",
                suggestion="Review file classifications in CODOME.md and CONTEXTOME.md",
            ))

    def _calculate_score(self):
        """Calculate alignment score (0-100)."""
        # Start with base score
        score = 100.0

        # Realm health (30 points)
        realm_score = 30.0
        for status in self.report.realms_status.values():
            if status["status"] != "VALID":
                realm_score -= 10
        score = score - (30 - realm_score)

        # Concordance health (40 points)
        conc_score = 40.0
        conc_count = len(self.report.concordances_status)
        for status in self.report.concordances_status.values():
            if status["status"] == "CONCORDANT":
                pass  # Full points - purposes aligned
            elif status["status"] == "CONTEXTOME_ONLY":
                conc_score -= (40 / conc_count) * 0.2  # Minor deduction
            elif status["status"] in ["UNVOICED", "UNREALIZED"]:
                conc_score -= (40 / conc_count) * 0.5
            elif status["status"] == "MISSING":
                conc_score -= (40 / conc_count)
        score = score - (40 - conc_score)

        # Issue deductions (20 points max)
        issue_deduction = 0
        for issue in self.report.issues:
            if issue.severity == "CRITICAL":
                issue_deduction += 2
            elif issue.severity == "HIGH":
                issue_deduction += 1
            elif issue.severity == "MEDIUM":
                issue_deduction += 0.5
            # LOW issues don't deduct
        score -= min(20, issue_deduction)

        # Undeclared ratio bonus/penalty (10 points)
        if self.report.total_directories > 0:
            declared_ratio = self.report.declared_directories / self.report.total_directories
            # At 50% declared, no bonus/penalty; above 50% gets bonus
            ratio_adjustment = (declared_ratio - 0.5) * 20  # -10 to +10
            score += ratio_adjustment

        self.report.alignment_score = max(0, min(100, score))

    def _generate_recommendations(self):
        """Generate actionable recommendations."""
        recs = []

        # Count issues by category
        by_category = {}
        for issue in self.report.issues:
            by_category[issue.category] = by_category.get(issue.category, 0) + 1

        if by_category.get("UNDECLARED", 0) > 5:
            recs.append("HIGH: Update .agent/CODOME_MANIFEST.yaml to declare undeclared directories")

        if by_category.get("UNREALIZED", 0) > 0:
            recs.append("MEDIUM: Remove or implement unrealized declarations in CONCORDANCES.md")

        if by_category.get("UNVOICED", 0) > 0:
            recs.append("MEDIUM: Add documentation for unvoiced code concordances")

        if self.report.alignment_score < 80:
            recs.append("CRITICAL: Purpose drift detected - schedule consolidation sprint")

        # Health(k) recommendations (L1 SS3.5: target > 80%)
        health_pct = self.report.overall_health * 100
        if health_pct < 60:
            recs.append(f"CRITICAL: Health(k) = {health_pct:.1f}% — below 60% threshold. Major concordance gaps.")
        elif health_pct < 80:
            recs.append(f"HIGH: Health(k) = {health_pct:.1f}% — below 80% production target (L1 SS3.5).")

        # Per-concordance health warnings
        for ch in self.report.concordance_health:
            if ch.health == 0.0 and ch.state not in ("CONCORDANT", "CONTEXTOME_ONLY"):
                recs.append(f"HIGH: Concordance '{ch.name}' has Health=0% ({ch.state})")

        # Sigma alignment warnings (L1 SS3.4)
        low_sigma = [ch for ch in self.report.concordance_health if ch.sigma > 0 and ch.sigma < 0.5]
        if low_sigma:
            names = ", ".join(ch.name for ch in low_sigma)
            recs.append(f"MEDIUM: Low sigma alignment in: {names} — content lopsided across paths")

        if not recs:
            recs.append("OK: Concordances are well-aligned. Health(k) meets production target.")

        self.report.recommendations = recs


def print_report(report: BoundaryReport, verbose: bool = False):
    """Print formatted report to stdout."""
    score = report.alignment_score
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           BOUNDARY ANALYSIS REPORT                           ║
║           {report.timestamp[:19]:<19}                        ║
╠══════════════════════════════════════════════════════════════╣
║  ALIGNMENT SCORE:  {score:>5.1f}/100  ({grade})                          ║
║  Total Directories:     {report.total_directories:>4}                              ║
║  Declared:              {report.declared_directories:>4}                              ║
║  Undeclared:            {report.undeclared_directories:>4}                              ║
║  Phantom:               {report.phantom_declarations:>4}                              ║
╠══════════════════════════════════════════════════════════════╣
║  REALMS STATUS:                                              ║""")

    for realm, status in report.realms_status.items():
        icon = "✓" if status["status"] == "VALID" else "✗"
        print(f"║    {icon} {realm:<12} {status['codome_files']:>4} code, {status['contextome_files']:>4} docs       ║")

    # Health(k) section
    health_pct = report.overall_health * 100
    health_grade = "HEALTHY" if health_pct >= 80 else "AT RISK" if health_pct >= 60 else "UNHEALTHY"
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  CONCORDANCE HEALTH (L1 SS3.5):                              ║
║  Overall Health(k): {health_pct:>5.1f}%  ({health_grade:<10})                   ║
╠══════════════════════════════════════════════════════════════╣
║  CONCORDANCES STATUS:                                        ║""")

    for ch in report.concordance_health:
        icon = "✓" if ch.state == "CONCORDANT" else "◐" if ch.state == "CONTEXTOME_ONLY" else "✗"
        h_str = f"{ch.health * 100:.0f}%"
        s_str = f"{ch.sigma:.2f}"
        print(f"║    {icon} {ch.name:<14} {ch.state:<14} H={h_str:>4} σ={s_str}  ║")

    if report.issues and verbose:
        print(f"""╠══════════════════════════════════════════════════════════════╣
║  ISSUES ({len(report.issues)}):                                              ║""")
        for issue in report.issues[:10]:  # Limit to 10
            sev_icon = "🔴" if issue.severity in ["CRITICAL", "HIGH"] else "🟡" if issue.severity == "MEDIUM" else "🟢"
            print(f"║  {sev_icon} [{issue.category}] {issue.path[:35]:<35}  ║")

    print(f"""╠══════════════════════════════════════════════════════════════╣
║  RECOMMENDATIONS:                                            ║""")
    for rec in report.recommendations[:3]:
        print(f"║    • {rec[:52]:<52} ║")

    print(f"╚══════════════════════════════════════════════════════════════╝")


def save_report(report: BoundaryReport, output_path: Path):
    """Save report to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report.to_dict(), f, indent=2)
    print(f"  Report saved to: {output_path}")


# ═══════════════════════════════════════════════════════════════════
# CONCORDANCE DRIFT TRACKING
# Theory: L0_AXIOMS.md A3 — Debt(T) = integral |dP_human/dt| dt
# ═══════════════════════════════════════════════════════════════════

CONCORDANCE_HISTORY_DIR = ".collider/concordance_history"


def save_snapshot(report: BoundaryReport, project_root: Path):
    """Save a concordance snapshot for drift comparison.

    Stores Health(k) and sigma(k) per region with timestamp.
    File: .collider/concordance_history/snapshot_YYYYMMDD_HHMMSS.json
    """
    history_dir = project_root / CONCORDANCE_HISTORY_DIR
    history_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot = {
        "timestamp": report.timestamp,
        "overall_health": report.overall_health,
        "alignment_score": report.alignment_score,
        "regions": {}
    }

    for ch in report.concordance_health:
        snapshot["regions"][ch.name] = {
            "state": ch.state,
            "health": ch.health,
            "sigma": ch.sigma,
        }

    snapshot_path = history_dir / f"snapshot_{ts}.json"
    with open(snapshot_path, 'w') as f:
        json.dump(snapshot, f, indent=2)

    return snapshot_path


def load_previous_snapshot(project_root: Path):
    """Load the most recent concordance snapshot for drift comparison.

    IMPORTANT: This function is called BEFORE save_snapshot() in the
    execution flow. So snapshots[-1] is the previous run's snapshot,
    not the current one (which hasn't been saved yet).

    Returns None if no history exists.
    """
    history_dir = project_root / CONCORDANCE_HISTORY_DIR
    if not history_dir.exists():
        return None

    snapshots = sorted(history_dir.glob("snapshot_*.json"))
    if not snapshots:
        return None

    # Load the most recent snapshot (= previous run, since current
    # run's snapshot hasn't been saved yet at this point)
    target = snapshots[-1]

    try:
        with open(target, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def compute_drift(current_report: BoundaryReport, project_root: Path, drift_threshold: float = 0.1):
    """Compare current Health(k) and sigma(k) against previous snapshot.

    Theory: L0_AXIOMS.md A3 — Debt(T) = integral |dP_human/dt| dt
    Drift approximates dP/dt for a single time step.

    Returns:
        dict with drift metrics, or None if no previous snapshot exists.
        Keys: per_region (dict), max_health_drift, max_sigma_drift, alerts (list)
    """
    previous = load_previous_snapshot(project_root)
    if previous is None:
        return None

    drift_result = {
        "previous_timestamp": previous.get("timestamp", "unknown"),
        "current_timestamp": current_report.timestamp,
        "per_region": {},
        "max_health_drift": 0.0,
        "max_sigma_drift": 0.0,
        "overall_health_drift": 0.0,
        "alerts": [],
    }

    prev_regions = previous.get("regions", {})

    for ch in current_report.concordance_health:
        prev = prev_regions.get(ch.name, {})
        prev_health = prev.get("health", 0.0)
        prev_sigma = prev.get("sigma", 0.0)

        health_drift = abs(ch.health - prev_health)
        sigma_drift = abs(ch.sigma - prev_sigma)

        drift_result["per_region"][ch.name] = {
            "health_drift": round(health_drift, 4),
            "sigma_drift": round(sigma_drift, 4),
            "health_prev": prev_health,
            "health_curr": ch.health,
            "sigma_prev": prev_sigma,
            "sigma_curr": ch.sigma,
        }

        drift_result["max_health_drift"] = max(drift_result["max_health_drift"], health_drift)
        drift_result["max_sigma_drift"] = max(drift_result["max_sigma_drift"], sigma_drift)

        # Alert if drift exceeds threshold
        if health_drift > drift_threshold:
            direction = "improved" if ch.health > prev_health else "degraded"
            drift_result["alerts"].append(
                f"DRIFT: '{ch.name}' health {direction} by {health_drift:.1%} "
                f"({prev_health:.0%} -> {ch.health:.0%})"
            )
        if sigma_drift > drift_threshold:
            direction = "improved" if ch.sigma > prev_sigma else "degraded"
            drift_result["alerts"].append(
                f"DRIFT: '{ch.name}' sigma {direction} by {sigma_drift:.2f} "
                f"({prev_sigma:.2f} -> {ch.sigma:.2f})"
            )

    # Overall health drift
    prev_overall = previous.get("overall_health", 0.0)
    drift_result["overall_health_drift"] = round(
        abs(current_report.overall_health - prev_overall), 4
    )

    return drift_result


def print_drift_report(drift_result: dict):
    """Print drift comparison to stdout."""
    if drift_result is None:
        print("\n  ℹ  No previous snapshot — drift comparison skipped (first run)")
        return

    prev_ts = drift_result["previous_timestamp"][:19]
    curr_ts = drift_result["current_timestamp"][:19]
    print(f"\n╔══════════════════════════════════════════════════════════════╗")
    print(f"║  CONCORDANCE DRIFT REPORT                                    ║")
    print(f"║  {prev_ts}  →  {curr_ts}                ║")
    print(f"╠══════════════════════════════════════════════════════════════╣")

    max_h = drift_result["max_health_drift"]
    max_s = drift_result["max_sigma_drift"]
    overall_h = drift_result["overall_health_drift"]
    print(f"║  Overall Health drift: {overall_h:.4f}                            ║")
    print(f"║  Max Health drift:     {max_h:.4f}                            ║")
    print(f"║  Max Sigma drift:      {max_s:.4f}                            ║")
    print(f"╠══════════════════════════════════════════════════════════════╣")

    for name, data in drift_result["per_region"].items():
        h_d = data["health_drift"]
        s_d = data["sigma_drift"]
        h_arrow = "→" if h_d == 0 else "↑" if data["health_curr"] > data["health_prev"] else "↓"
        s_arrow = "→" if s_d == 0 else "↑" if data["sigma_curr"] > data["sigma_prev"] else "↓"
        print(f"║  {name:<14} H:{h_arrow}{h_d:.4f}  σ:{s_arrow}{s_d:.4f}              ║")

    alerts = drift_result.get("alerts", [])
    if alerts:
        print(f"╠══════════════════════════════════════════════════════════════╣")
        print(f"║  ALERTS ({len(alerts)}):                                              ║")
        for alert in alerts:
            print(f"║    ⚠ {alert[:52]:<52} ║")
    else:
        print(f"╠══════════════════════════════════════════════════════════════╣")
        print(f"║  No drift alerts (all regions within threshold)              ║")

    print(f"╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(
        description="Boundary Analyzer - Validate PROJECT_elements internal organization"
    )
    parser.add_argument('--quick', '-q', action='store_true',
                        help="Quick check - return exit code only")
    parser.add_argument('--json', '-j', action='store_true',
                        help="Output JSON to stdout")
    parser.add_argument('--save', '-s', action='store_true',
                        help="Save report to .agent/intelligence/")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Show detailed issues")
    parser.add_argument('--fix', '-f', action='store_true',
                        help="Generate fix suggestions")
    parser.add_argument('--threshold', '-t', type=int, default=70,
                        help="Minimum alignment score (default: 70)")
    parser.add_argument('--snapshot', action='store_true',
                        help="Save concordance snapshot for drift tracking")
    parser.add_argument('--drift', action='store_true',
                        help="Show drift compared to previous snapshot (implies --snapshot)")
    parser.add_argument('--drift-threshold', type=float, default=0.1,
                        help="Drift alert threshold (default: 0.1)")

    args = parser.parse_args()

    analyzer = BoundaryAnalyzer()
    report = analyzer.analyze()

    if args.json:
        report_dict = report.to_dict()
        # Include drift data in JSON if requested
        if args.drift:
            drift_result = compute_drift(report, PROJECT_ROOT, args.drift_threshold)
            if drift_result:
                report_dict["drift"] = drift_result
        print(json.dumps(report_dict, indent=2))
    elif not args.quick:
        print_report(report, verbose=args.verbose or args.fix)

    # Drift comparison (before saving current snapshot)
    if args.drift and not args.json:
        drift_result = compute_drift(report, PROJECT_ROOT, args.drift_threshold)
        print_drift_report(drift_result)

    # Save concordance snapshot (--drift implies --snapshot)
    if args.snapshot or args.drift:
        snap_path = save_snapshot(report, PROJECT_ROOT)
        if not args.json and not args.quick:
            print(f"\n  ✓ Snapshot saved: {snap_path}")

    if args.save:
        output_path = PROJECT_ROOT / ".agent/intelligence/boundary_analysis.json"
        save_report(report, output_path)

    # Exit code based on threshold
    if report.alignment_score < args.threshold:
        if not args.json:
            print(f"\n  ⚠️  Alignment score {report.alignment_score:.1f} below threshold {args.threshold}")
        sys.exit(1)
    else:
        if not args.json and not args.quick:
            print(f"\n  ✓ Alignment score {report.alignment_score:.1f} meets threshold {args.threshold}")
        sys.exit(0)


if __name__ == "__main__":
    main()
