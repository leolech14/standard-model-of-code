#!/usr/bin/env python3
"""
Wave-Particle Symmetry Checker
==============================

TRUE SYMMETRY: Compares documentation (Wave) with implementation (Particle)
using Collider's symmetry analysis pipeline.

PROXY MODE (--proxy): Legacy rubric-based scoring for quick doc health checks.

Usage:
    python symmetry_check.py           # Run TRUE symmetry check
    python symmetry_check.py --json    # Output as JSON
    python symmetry_check.py --brief   # One-line summary
    python symmetry_check.py --proxy   # Use legacy proxy metrics
"""

import sys
import json
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent


def get_tier(score: float) -> str:
    """Return tier emoji based on score (0.0-1.0 scale)."""
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


def run_true_symmetry(output_format: str = "full") -> dict:
    """
    Run TRUE Wave-Particle symmetry analysis using Collider pipeline.

    Returns:
        dict with symmetry_score, tier, metrics, etc.
    """
    # Add SMoC to path
    smoc_path = PROJECT_ROOT / "standard-model-of-code"
    sys.path.insert(0, str(smoc_path))

    try:
        from src.core.symmetry_reporter import SymmetryAnalyzer

        # Focus on key documentation directories (avoid scanning all research docs)
        key_docs_dirs = [
            PROJECT_ROOT,  # README.md, CLAUDE.md, etc.
            PROJECT_ROOT / "context-management/docs",
            PROJECT_ROOT / ".agent/specs",
            smoc_path / "docs",
        ]

        analyzer = SymmetryAnalyzer(
            repo_path=smoc_path,
            docs_path=smoc_path / "docs",  # Focus on SMoC docs only
            threshold=0.75
        )

        report = analyzer.analyze()

        return {
            "mode": "TRUE_SYMMETRY",
            "symmetry_score": report.symmetry_score,
            "coverage": report.coverage,
            "tier": report.tier,
            "metrics": {
                "total_public_exports": report.metrics.total_public_exports,
                "matched": report.metrics.matched,
                "undocumented": report.metrics.undocumented,
                "orphan_docs": report.metrics.orphan_docs
            },
            "confidence_buckets": {
                "exact": report.confidence_buckets.exact,
                "qualified": report.confidence_buckets.qualified,
                "fuzzy": report.confidence_buckets.fuzzy,
                "rejected": report.confidence_buckets.rejected
            },
            "top_undocumented": report.top_undocumented[:5],
            "top_orphan_docs": report.top_orphan_docs[:5],
            "files_analyzed": report.files_analyzed,
            "docs_analyzed": report.docs_analyzed
        }

    except ImportError as e:
        return {
            "mode": "TRUE_SYMMETRY",
            "error": f"Collider symmetry modules not available: {e}",
            "symmetry_score": 0.0,
            "tier": "ERROR"
        }
    except Exception as e:
        return {
            "mode": "TRUE_SYMMETRY",
            "error": str(e),
            "symmetry_score": 0.0,
            "tier": "ERROR"
        }


def run_proxy_symmetry() -> dict:
    """
    Run PROXY symmetry check using legacy rubric-based metrics.

    This is the old 5-category scoring system:
    - Structural (25 pts): Docstring coverage
    - Behavioral (25 pts): CLI and key docs exist
    - Examples (20 pts): Code block count
    - References (15 pts): Broken link count
    - Freshness (15 pts): TODO/FIXME count
    """
    import ast
    import subprocess
    import re

    categories = []

    # STRUCTURAL: Docstring coverage
    total_funcs, documented_funcs = 0, 0
    total_classes, documented_classes = 0, 0

    for py_file in (PROJECT_ROOT / "standard-model-of-code/src").rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    total_classes += 1
                    if ast.get_docstring(node):
                        documented_classes += 1
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):
                        total_funcs += 1
                        if ast.get_docstring(node):
                            documented_funcs += 1
        except:
            pass

    class_pct = (documented_classes / max(total_classes, 1)) * 100
    func_pct = (documented_funcs / max(total_funcs, 1)) * 100
    struct_score = min(25, 5 if class_pct >= 90 else int(class_pct / 20) +
                           5 if func_pct >= 90 else int(func_pct / 20) + 14)
    categories.append({
        "name": "STRUCTURAL",
        "score": struct_score,
        "max_score": 25,
        "evidence": f"{int(class_pct)}% class, {int(func_pct)}% func docstrings"
    })

    # BEHAVIORAL: CLI + key docs
    behav_score = 0
    try:
        result = subprocess.run(
            [str(PROJECT_ROOT / "standard-model-of-code/collider"), "--help"],
            capture_output=True, timeout=5
        )
        if result.returncode == 0:
            behav_score += 10
    except:
        pass

    key_docs = [
        "context-management/docs/BACKGROUND_AI_LAYER_MAP.md",
        "context-management/docs/AI_USER_GUIDE.md",
        "context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md",
        ".agent/specs/WAVE_PARTICLE_SYMMETRY.md",
    ]
    docs_found = sum(1 for d in key_docs if (PROJECT_ROOT / d).exists())
    behav_score += docs_found * 3
    categories.append({
        "name": "BEHAVIORAL",
        "score": min(25, behav_score),
        "max_score": 25,
        "evidence": f"CLI works, {docs_found}/{len(key_docs)} key docs"
    })

    # EXAMPLES: Code block count
    total_blocks = 0
    for doc in ["README.md", "CLAUDE.md", "ARCHITECTURE_MAP.md",
                "context-management/docs/AI_USER_GUIDE.md",
                "context-management/docs/BACKGROUND_AI_LAYER_MAP.md",
                ".agent/specs/WAVE_PARTICLE_SYMMETRY.md"]:
        path = PROJECT_ROOT / doc
        if path.exists():
            total_blocks += path.read_text().count("```")

    categories.append({
        "name": "EXAMPLES",
        "score": min(total_blocks // 5, 20),
        "max_score": 20,
        "evidence": f"{total_blocks} code blocks in key docs"
    })

    # REFERENCES: Broken links
    broken_count, total_links = 0, 0
    for doc in ["CLAUDE.md", "ARCHITECTURE_MAP.md"]:
        path = PROJECT_ROOT / doc
        if path.exists():
            content = path.read_text()
            links = re.findall(r'\[.*?\]\((\.{1,2}/[^)]+\.md)\)', content)
            total_links += len(links)
            for link in links:
                if not (path.parent / link).resolve().exists():
                    broken_count += 1

    categories.append({
        "name": "REFERENCES",
        "score": 15 if broken_count == 0 else max(0, 15 - broken_count * 3),
        "max_score": 15,
        "evidence": f"{broken_count} broken links, {total_links} total"
    })

    # FRESHNESS: TODO/FIXME count
    todo_count, fixme_count = 0, 0
    for search_dir in ["standard-model-of-code/src", "context-management/tools", ".agent/tools"]:
        for py_file in (PROJECT_ROOT / search_dir).rglob("*.py"):
            try:
                content = py_file.read_text()
                todo_count += content.count("TODO")
                fixme_count += content.count("FIXME")
            except:
                pass

    total_todos = todo_count + fixme_count
    fresh_score = 15 if total_todos < 20 else 12 if total_todos < 50 else 9 if total_todos < 100 else 5
    categories.append({
        "name": "FRESHNESS",
        "score": fresh_score,
        "max_score": 15,
        "evidence": f"{todo_count} TODOs, {fixme_count} FIXMEs"
    })

    total_score = sum(c["score"] for c in categories)
    max_score = sum(c["max_score"] for c in categories)

    return {
        "mode": "PROXY_METRICS",
        "total_score": total_score,
        "max_score": max_score,
        "symmetry_score": total_score / max_score,
        "tier": get_tier(total_score / max_score),
        "categories": categories,
        "warning": "This is PROXY scoring based on existence checks, not true Wave-Particle symmetry"
    }


def main():
    parser = argparse.ArgumentParser(
        description="Wave-Particle Symmetry Checker (TRUE mode by default)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--brief", action="store_true", help="One-line summary")
    parser.add_argument("--proxy", action="store_true",
                       help="Use legacy proxy metrics instead of true symmetry")
    args = parser.parse_args()

    # Run appropriate analysis
    if args.proxy:
        result = run_proxy_symmetry()
    else:
        result = run_true_symmetry()

    # Format output
    if args.json:
        print(json.dumps(result, indent=2))
    elif args.brief:
        tier = result.get("tier", "ERROR")
        score = result.get("symmetry_score", 0)
        mode = "[PROXY] " if args.proxy else ""
        print(f"{mode}{tier} ({score:.0%})")
    else:
        # Full output
        mode = result.get("mode", "UNKNOWN")
        tier = result.get("tier", "ERROR")
        score = result.get("symmetry_score", 0)

        print("=" * 60)
        print(f"WAVE-PARTICLE SYMMETRY CHECK ({mode})")
        print("=" * 60)
        print()

        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(1)

        if mode == "TRUE_SYMMETRY":
            metrics = result.get("metrics", {})
            buckets = result.get("confidence_buckets", {})

            print(f"{'Metric':<25} {'Value':>15}")
            print("-" * 42)
            print(f"{'Symmetry Score':<25} {score:>14.1%}")
            print(f"{'Coverage':<25} {result.get('coverage', 0):>14.1%}")
            print(f"{'Tier':<25} {tier:>15}")
            print("-" * 42)
            print(f"{'Public Exports':<25} {metrics.get('total_public_exports', 0):>15}")
            print(f"{'Matched':<25} {metrics.get('matched', 0):>15}")
            print(f"{'Undocumented':<25} {metrics.get('undocumented', 0):>15}")
            print(f"{'Orphan Docs':<25} {metrics.get('orphan_docs', 0):>15}")
            print("-" * 42)
            print(f"{'Exact Matches':<25} {buckets.get('exact', 0):>15}")
            print(f"{'Qualified Matches':<25} {buckets.get('qualified', 0):>15}")
            print(f"{'Fuzzy Matches':<25} {buckets.get('fuzzy', 0):>15}")
            print(f"{'Rejected (<0.75)':<25} {buckets.get('rejected', 0):>15}")
            print()

            if result.get("top_undocumented"):
                print("Top Undocumented APIs:")
                for item in result["top_undocumented"][:5]:
                    print(f"  - {item}")
                print()

        else:  # PROXY mode
            print(f"{'Category':<15} {'Score':>8} {'Max':>6} {'Evidence'}")
            print("-" * 60)
            for c in result.get("categories", []):
                print(f"{c['name']:<15} {c['score']:>8} {c['max_score']:>6}   {c['evidence']}")
            print("-" * 60)
            print(f"{'TOTAL':<15} {result.get('total_score', 0):>8} {result.get('max_score', 100):>6}")
            print()
            print(f"TIER: {tier}")
            print()
            print("WARNING: This is PROXY scoring, not true Wave-Particle symmetry.")
            print("Run without --proxy for true symmetry analysis.")


if __name__ == "__main__":
    main()
