#!/usr/bin/env python3
"""
Overall Understanding Query

The meta-analysis query that answers in one shot:
1. Is this run trustworthy? (integrity + invariants)
2. What did we learn? (dark matter signature, confidence distribution)
3. What should we do next? (where theory/pipeline needs extension)

This is the foundation for "MEASURED CODOME" - treating analysis
output as a scientific measurement with provenance.

Usage:
    python -m src.core.queries.overall_understanding <unified_analysis.json>
    python -m src.core.queries.overall_understanding --run-dir .collider/
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_json(path: Path) -> Any:
    """Load JSON file safely."""
    return json.loads(path.read_text(encoding="utf-8"))


def safe_get(obj: Any, dotted_path: str, default: Any = None) -> Any:
    """Get nested value using dot notation."""
    cur = obj
    for part in dotted_path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit():
            idx = int(part)
            if 0 <= idx < len(cur):
                cur = cur[idx]
            else:
                return default
        else:
            return default
    return cur


def first_path(obj: Any, paths: List[str], default: Any = None) -> Any:
    """Try multiple paths, return first non-None value."""
    for p in paths:
        v = safe_get(obj, p)
        if v is not None:
            return v
    return default


class OverallUnderstandingQuery:
    """
    Executes the overall understanding query on analysis output.

    Produces:
    - Provenance section (was this run valid?)
    - Core metrics (what's in the codome?)
    - Dark matter analysis (invisible dependencies)
    - Confidence analysis (how certain are we?)
    - Quality gates (did we meet thresholds?)
    - Recommendations (what to do next?)
    """

    def __init__(self, unified: Dict[str, Any], manifest: Optional[Dict[str, Any]] = None):
        self.unified = unified
        self.manifest = manifest or {}
        self.metrics: Dict[str, Any] = {}
        self.issues: List[Dict[str, Any]] = []

    def execute(self) -> Dict[str, Any]:
        """Run the complete query."""
        self._extract_metrics()
        self._run_quality_gates()

        return {
            "query_id": "overall_understanding_v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "provenance": self._build_provenance(),
            "metrics": self.metrics,
            "dark_matter": self._analyze_dark_matter(),
            "confidence": self._analyze_confidence(),
            "quality_gates": self._build_quality_gates(),
            "recommendations": self._generate_recommendations(),
            "issues": self.issues,
        }

    def _extract_metrics(self) -> None:
        """Extract core metrics from unified analysis."""
        u = self.unified

        # Core scale
        by_kind = first_path(u, ["classification.by_kind"], {})
        self.metrics["total_nodes"] = sum(by_kind.values()) if isinstance(by_kind, dict) else 0
        self.metrics["total_edges"] = first_path(u, [
            "graph.total_edges",
            "codome.total_edges",
            "analytics.edges_count"
        ], len(first_path(u, ["edges"], [])))

        # Kind distribution
        self.metrics["by_kind"] = by_kind

        # Role distribution
        self.metrics["by_role"] = first_path(u, ["classification.by_role"], {})

        # Confidence distribution
        self.metrics["by_confidence"] = first_path(u, ["classification.by_confidence"], {})

        # Dark matter
        codome_boundaries = first_path(u, ["codome_boundaries.boundary_nodes"], [])
        self.metrics["dark_edge_count"] = sum(
            n.get("out_degree", 0) for n in codome_boundaries
            if isinstance(n, dict)
        )
        self.metrics["dark_by_source"] = {}
        for bn in codome_boundaries:
            if isinstance(bn, dict):
                source = bn.get("codome_source", bn.get("name", "unknown"))
                self.metrics["dark_by_source"][source] = bn.get("out_degree", 0)

        # Entropy (dimension information content)
        self.metrics["entropy"] = first_path(u, ["analytics.entropy"], {})

    def _run_quality_gates(self) -> None:
        """Check quality gate thresholds."""
        total = self.metrics.get("total_nodes", 0)
        edges = self.metrics.get("total_edges", 0)

        # Gate 1: Must have nodes
        if total == 0:
            self.issues.append({
                "gate": "has_nodes",
                "severity": "error",
                "message": "No nodes found in analysis"
            })

        # Gate 2: Must have edges (unless very small codebase)
        if edges == 0 and total > 10:
            self.issues.append({
                "gate": "has_edges",
                "severity": "warning",
                "message": f"No edges found for {total} nodes"
            })

        # Gate 3: Confidence distribution should be reasonable
        by_conf = self.metrics.get("by_confidence", {})
        if by_conf:
            low = by_conf.get("low", 0)
            total_conf = sum(by_conf.values())
            if total_conf > 0 and low / total_conf > 0.5:
                self.issues.append({
                    "gate": "confidence_acceptable",
                    "severity": "warning",
                    "message": f"Over 50% of nodes have low confidence ({low}/{total_conf})"
                })

        # Gate 4: Dark ratio should be sane (0-100%)
        dark = self.metrics.get("dark_edge_count", 0)
        if edges > 0:
            ratio = dark / edges
            if ratio > 1.0:
                self.issues.append({
                    "gate": "dark_ratio_sane",
                    "severity": "error",
                    "message": f"Dark ratio {ratio:.2f} > 1.0 (impossible)"
                })

    def _build_provenance(self) -> Dict[str, Any]:
        """Build provenance section from manifest."""
        m = self.manifest
        return {
            "run_id": safe_get(m, "input.git_commit", "unknown"),
            "schema_version": safe_get(m, "schema_version", "unknown"),
            "git_commit": safe_get(m, "input.git_commit"),
            "git_dirty": safe_get(m, "input.git_dirty", True),
            "collider_version": safe_get(m, "pipeline.collider_version", "unknown"),
            "merkle_root": safe_get(m, "checksums.merkle_root"),
            "generated_at": safe_get(m, "generated_at_utc"),
        }

    def _analyze_dark_matter(self) -> Dict[str, Any]:
        """Analyze dark matter (invisible dependencies)."""
        total_edges = self.metrics.get("total_edges", 0)
        dark_edges = self.metrics.get("dark_edge_count", 0)
        dark_by_source = self.metrics.get("dark_by_source", {})

        ratio = dark_edges / total_edges if total_edges > 0 else 0

        # Signature analysis
        signature = []
        if dark_edges > 0:
            for source, count in sorted(dark_by_source.items(), key=lambda x: -x[1]):
                pct = count / dark_edges
                signature.append({
                    "source": source,
                    "count": count,
                    "percent": round(pct * 100, 1),
                })

        # Heuristic predictions
        predictions = []
        if ratio >= 0.20:
            predictions.append("High Dark Matter (>=20%): heavy framework/test/runtime influence")
        elif ratio >= 0.10:
            predictions.append("Moderate Dark Matter (10-20%): boundaries should be theorized")
        else:
            predictions.append("Low Dark Matter (<10%): most dependencies observable in code")

        # Source-specific predictions
        test_pct = dark_by_source.get("test_entry", 0) / dark_edges if dark_edges else 0
        if test_pct >= 0.30:
            predictions.append("TestFramework dominates: likely high test harness influence")

        framework_pct = dark_by_source.get("framework_managed", 0) / dark_edges if dark_edges else 0
        if framework_pct >= 0.20:
            predictions.append("Heavy framework coupling: DI/decorators create invisible edges")

        return {
            "total_dark_edges": dark_edges,
            "dark_ratio": round(ratio, 4),
            "signature": signature,
            "predictions": predictions,
        }

    def _analyze_confidence(self) -> Dict[str, Any]:
        """Analyze confidence distribution."""
        by_conf = self.metrics.get("by_confidence", {})

        if not by_conf:
            return {"status": "no_confidence_data"}

        total = sum(by_conf.values())
        distribution = {}
        for level, count in by_conf.items():
            distribution[level] = {
                "count": count,
                "percent": round(count / total * 100, 1) if total > 0 else 0
            }

        # Compute overall confidence score (weighted average)
        weights = {"high": 1.0, "medium": 0.6, "low": 0.2}
        weighted_sum = sum(by_conf.get(k, 0) * v for k, v in weights.items())
        overall = weighted_sum / total if total > 0 else 0

        # Recommendations based on confidence
        recommendations = []
        low_pct = distribution.get("low", {}).get("percent", 0)
        if low_pct > 40:
            recommendations.append("High uncertainty: 40%+ nodes have low confidence. Extend classifiers.")
        elif low_pct > 25:
            recommendations.append("Moderate uncertainty: 25-40% low confidence. Review edge cases.")

        return {
            "distribution": distribution,
            "overall_score": round(overall, 3),
            "recommendations": recommendations,
        }

    def _build_quality_gates(self) -> Dict[str, Any]:
        """Build quality gates summary."""
        errors = [i for i in self.issues if i.get("severity") == "error"]
        warnings = [i for i in self.issues if i.get("severity") == "warning"]

        return {
            "passed": len(errors) == 0,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "gates": self.issues,
        }

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recs = []

        # From dark matter analysis
        dark = self._analyze_dark_matter()
        if dark.get("dark_ratio", 0) >= 0.10:
            recs.append({
                "priority": "high",
                "category": "theory",
                "title": "Formalize Dark Matter",
                "description": f"Dark ratio {dark['dark_ratio']:.1%} is significant. "
                               "Codome boundaries should be theoretically grounded.",
                "action": "Implement Proposal 2: Dark Matter as first-class theoretical object"
            })

        # From confidence analysis
        conf = self._analyze_confidence()
        if conf.get("overall_score", 1.0) < 0.7:
            recs.append({
                "priority": "high",
                "category": "theory",
                "title": "Model Uncertainty Explicitly",
                "description": f"Overall confidence {conf.get('overall_score', 0):.1%} is low. "
                               "Classification uncertainty should be modeled, not hidden.",
                "action": "Implement Proposal 3: Confidence as meta-dimension"
            })

        # From quality gates
        if self.issues:
            for issue in self.issues:
                if issue.get("severity") == "error":
                    recs.append({
                        "priority": "critical",
                        "category": "data_quality",
                        "title": f"Fix: {issue.get('gate', 'unknown')}",
                        "description": issue.get("message", ""),
                        "action": "Investigate and fix data quality issue"
                    })

        return recs


def render_markdown(result: Dict[str, Any]) -> str:
    """Render query result as markdown."""
    lines = []
    lines.append(f"# Overall Understanding Report")
    lines.append(f"")
    lines.append(f"**Query ID:** {result.get('query_id')}")
    lines.append(f"**Generated:** {result.get('generated_at_utc')}")
    lines.append("")

    # Provenance
    prov = result.get("provenance", {})
    lines.append("## Provenance")
    lines.append(f"- Git commit: `{prov.get('git_commit', 'unknown')}`")
    lines.append(f"- Dirty: {prov.get('git_dirty', 'unknown')}")
    lines.append(f"- Collider: {prov.get('collider_version', 'unknown')}")
    lines.append(f"- Merkle root: `{prov.get('merkle_root', 'not computed')[:16]}...`" if prov.get('merkle_root') else "- Merkle root: not computed")
    lines.append("")

    # Core metrics
    m = result.get("metrics", {})
    lines.append("## Core Metrics")
    lines.append(f"- Total nodes: **{m.get('total_nodes', 0):,}**")
    lines.append(f"- Total edges: **{m.get('total_edges', 0):,}**")
    lines.append("")

    # Dark matter
    dm = result.get("dark_matter", {})
    lines.append("## Dark Matter Analysis")
    lines.append(f"- Dark edges: {dm.get('total_dark_edges', 0)}")
    lines.append(f"- Dark ratio: **{dm.get('dark_ratio', 0):.1%}**")
    lines.append("")
    lines.append("### Signature")
    for sig in dm.get("signature", [])[:5]:
        lines.append(f"- {sig['source']}: {sig['count']} ({sig['percent']}%)")
    lines.append("")
    lines.append("### Predictions")
    for pred in dm.get("predictions", []):
        lines.append(f"- {pred}")
    lines.append("")

    # Confidence
    conf = result.get("confidence", {})
    lines.append("## Confidence Analysis")
    lines.append(f"- Overall score: **{conf.get('overall_score', 0):.1%}**")
    lines.append("")
    for level, data in conf.get("distribution", {}).items():
        lines.append(f"- {level}: {data.get('count', 0)} ({data.get('percent', 0)}%)")
    lines.append("")

    # Quality gates
    qg = result.get("quality_gates", {})
    status = "✅ PASSED" if qg.get("passed") else "❌ FAILED"
    lines.append(f"## Quality Gates: {status}")
    lines.append(f"- Errors: {qg.get('error_count', 0)}")
    lines.append(f"- Warnings: {qg.get('warning_count', 0)}")
    lines.append("")

    # Recommendations
    recs = result.get("recommendations", [])
    if recs:
        lines.append("## Recommendations")
        for rec in recs:
            lines.append(f"### [{rec.get('priority', 'medium').upper()}] {rec.get('title', 'Unknown')}")
            lines.append(f"{rec.get('description', '')}")
            lines.append(f"**Action:** {rec.get('action', '')}")
            lines.append("")

    return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run overall understanding query")
    parser.add_argument("input", nargs="?", help="Path to unified_analysis.json")
    parser.add_argument("--run-dir", help="Path to run directory (contains unified_analysis.json + manifest.json)")
    parser.add_argument("--output", help="Output directory for results")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--markdown", action="store_true", help="Output markdown only")
    args = parser.parse_args()

    # Determine input paths
    if args.run_dir:
        run_dir = Path(args.run_dir)
        unified_path = run_dir / "unified_analysis.json"
        manifest_path = run_dir / "manifest.json"
    elif args.input:
        unified_path = Path(args.input)
        manifest_path = unified_path.parent / "manifest.json"
        run_dir = unified_path.parent
    else:
        # Default to .collider/
        run_dir = Path(".collider")
        unified_path = run_dir / "unified_analysis.json"
        manifest_path = run_dir / "manifest.json"

    if not unified_path.exists():
        print(f"Error: {unified_path} not found")
        return 1

    # Load data
    unified = load_json(unified_path)
    manifest = load_json(manifest_path) if manifest_path.exists() else None

    # Execute query
    query = OverallUnderstandingQuery(unified, manifest)
    result = query.execute()

    # Output
    output_dir = Path(args.output) if args.output else run_dir / "derived"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.json or not args.markdown:
        json_path = output_dir / "overall_understanding.json"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Wrote: {json_path}")

    if args.markdown or not args.json:
        md_path = output_dir / "overall_understanding.md"
        md_path.write_text(render_markdown(result), encoding="utf-8")
        print(f"Wrote: {md_path}")

    # Print summary to console
    qg = result.get("quality_gates", {})
    status = "PASSED" if qg.get("passed") else "FAILED"
    print(f"\n=== Overall Understanding: {status} ===")
    print(f"Nodes: {result['metrics'].get('total_nodes', 0):,}")
    print(f"Dark ratio: {result['dark_matter'].get('dark_ratio', 0):.1%}")
    print(f"Confidence: {result['confidence'].get('overall_score', 0):.1%}")
    print(f"Issues: {qg.get('error_count', 0)} errors, {qg.get('warning_count', 0)} warnings")

    return 0 if qg.get("passed") else 1


if __name__ == "__main__":
    exit(main())
