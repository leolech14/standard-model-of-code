#!/usr/bin/env python3
"""
WIRE - The Grand Orchestrator
=============================
SMoC Role: Orchestration/Integration/E | daemon | orchestrator

Wires ALL tools together into a single coherent pipeline:

  LOL Sync → TDJ Update → Collider Full → SMoC Merge → Unify → Dashboard

This is the tool that makes PROJECT_elements a self-aware system.

Usage:
  python wire.py                    # Full pipeline
  python wire.py --quick            # Skip Collider (use cached)
  python wire.py --dashboard        # Dashboard only
  python wire.py --watch            # Continuous mode
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent
INTELLIGENCE_DIR = REPO_ROOT / ".agent" / "intelligence"
COLLIDER_DIR = REPO_ROOT / "standard-model-of-code"

# Tool paths
LOL_SYNC = SCRIPT_DIR / "lol_sync.py"
LOL_SMOC_MERGER = SCRIPT_DIR / "lol_smoc_merger.py"
LOL_UNIFY = SCRIPT_DIR / "lol_unify.py"
SYMMETRY_CHECK = SCRIPT_DIR / "symmetry_check.py"
COMM_FABRIC = REPO_ROOT / ".agent" / "intelligence" / "comms" / "fabric.py"
REFINERY_SCRIPT = REPO_ROOT / "context-management" / "tools" / "ai" / "aci" / "refinery.py"

# Output paths
LOL_CSV = INTELLIGENCE_DIR / "LOL.csv"
LOL_SMOC_CSV = INTELLIGENCE_DIR / "LOL_SMOC.csv"
LOL_UNIFIED_CSV = INTELLIGENCE_DIR / "LOL_UNIFIED.csv"
TDJ_PATH = INTELLIGENCE_DIR / "tdj.jsonl"
COLLIDER_OUTPUT_DIR = REPO_ROOT / ".collider-full"
CHUNKS_DIR = INTELLIGENCE_DIR / "chunks"


class PipelineStage:
    """A single stage in the pipeline."""

    def __init__(self, name: str, command: list, description: str, optional: bool = False):
        self.name = name
        self.command = command
        self.description = description
        self.optional = optional
        self.duration = 0
        self.success = False
        self.output = ""

    def run(self) -> bool:
        """Execute the stage."""
        print(f"\n{'─' * 60}")
        print(f"▶ {self.name}: {self.description}")
        print(f"{'─' * 60}")

        start = time.time()
        try:
            result = subprocess.run(
                self.command,
                capture_output=True,
                text=True,
                timeout=600,  # 10 min timeout
                cwd=str(REPO_ROOT)
            )
            self.duration = time.time() - start
            self.output = result.stdout + result.stderr
            self.success = result.returncode == 0

            # Show condensed output
            lines = self.output.strip().split('\n')
            if len(lines) > 20:
                for line in lines[:5]:
                    print(f"  {line}")
                print(f"  ... ({len(lines) - 10} lines omitted) ...")
                for line in lines[-5:]:
                    print(f"  {line}")
            else:
                for line in lines:
                    print(f"  {line}")

            status = "✓" if self.success else "✗"
            print(f"\n  {status} {self.name} completed in {self.duration:.1f}s")

            return self.success

        except subprocess.TimeoutExpired:
            self.duration = time.time() - start
            print(f"  ✗ TIMEOUT after {self.duration:.1f}s")
            return False
        except Exception as e:
            self.duration = time.time() - start
            print(f"  ✗ ERROR: {e}")
            return False


def update_tdj():
    """Update the Temporal Daily Journal."""
    print("  Scanning filesystem for temporal data...")

    entries = []
    now = datetime.now()

    excluded = {".git", "__pycache__", "node_modules", ".venv", "archive", ".collider", ".collider-full"}

    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in excluded]

        for filename in files:
            filepath = Path(root) / filename
            rel_path = str(filepath.relative_to(REPO_ROOT))

            if any(excl in rel_path for excl in excluded):
                continue

            try:
                stat = filepath.stat()
                entries.append({
                    "path": rel_path,
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "ctime": stat.st_ctime,
                    "scan_ts": now.timestamp()
                })
            except:
                continue

    # Write TDJ
    TDJ_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TDJ_PATH, 'w') as f:
        f.write(json.dumps({
            "_meta": True,
            "version": "1.0.0",
            "type": "temporal_index",
            "project": "PROJECT_elements",
            "generated": now.isoformat(),
            "entry_count": len(entries),
            "scan_duration_ms": 0
        }) + '\n')
        for entry in entries:
            f.write(json.dumps(entry) + '\n')

    print(f"  Updated TDJ with {len(entries)} entries")
    return True


def find_latest_collider_output() -> Optional[Path]:
    """Find the most recent Collider output."""
    if not COLLIDER_OUTPUT_DIR.exists():
        return None
    outputs = list(COLLIDER_OUTPUT_DIR.glob("output_llm-oriented_*.json"))
    if not outputs:
        return None
    outputs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return outputs[0]


def collider_output_age_minutes() -> float:
    """Get age of latest Collider output in minutes."""
    latest = find_latest_collider_output()
    if not latest:
        return float('inf')
    age_seconds = time.time() - latest.stat().st_mtime
    return age_seconds / 60


def print_dashboard():
    """Print the unified health dashboard."""
    print("\n" + "=" * 70)
    print("PROJECT_elements HEALTH DASHBOARD")
    print("=" * 70)
    print(f"Generated: {datetime.now().isoformat()}")

    # Load LOL Unified
    if LOL_UNIFIED_CSV.exists():
        import csv
        with open(LOL_UNIFIED_CSV) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        total = len(rows)

        # Domain distribution
        from collections import Counter
        domains = Counter(r['domain'] for r in rows)
        categories = Counter(r['category'] for r in rows)
        freshness = Counter(r.get('freshness', 'N/A') for r in rows)
        symmetry = Counter(r.get('symmetry_state', 'N/A') for r in rows)

        print(f"\n## INVENTORY: {total} entities")

        print("\n  Domains:")
        for d, c in domains.most_common():
            pct = c / total * 100
            bar = "█" * int(pct / 3)
            print(f"    {d:<12} {c:>5} ({pct:>5.1f}%) {bar}")

        print("\n  Freshness:")
        for f, c in [("FRESH", freshness.get("FRESH", 0)),
                     ("RECENT", freshness.get("RECENT", 0)),
                     ("STABLE", freshness.get("STABLE", 0)),
                     ("AGED", freshness.get("AGED", 0))]:
            pct = c / total * 100 if total else 0
            print(f"    {f:<12} {c:>5} ({pct:>5.1f}%)")

        print("\n  Symmetry:")
        for s, c in symmetry.most_common(4):
            pct = c / total * 100 if total else 0
            print(f"    {s:<12} {c:>5} ({pct:>5.1f}%)")

    # Load Collider metrics
    collider_output = find_latest_collider_output()
    if collider_output:
        with open(collider_output) as f:
            data = json.load(f)

        counts = data.get("counts", {})
        knots = data.get("knots", {})
        purpose = data.get("purpose_field", {})
        topo = data.get("topology", {})

        print(f"\n## TOPOLOGY")
        print(f"    Shape:        {topo.get('shape', 'N/A')}")
        print(f"    Nodes:        {counts.get('nodes', 'N/A')}")
        print(f"    Edges:        {counts.get('edges', 'N/A')}")
        print(f"    Entry points: {counts.get('entry_points', 'N/A')}")

        print(f"\n## HEALTH")
        knot_score = knots.get('knot_score', 'N/A')
        knot_bar = "🔴" * int(knot_score) if isinstance(knot_score, (int, float)) else ""
        print(f"    Knot Score:   {knot_score}/10 {knot_bar}")
        print(f"    God Classes:  {purpose.get('god_class_count', 'N/A')}")
        print(f"    Purpose:      {purpose.get('alignment_health', 'N/A')}")
        print(f"    Clarity:      {purpose.get('purpose_clarity', 'N/A')}")

        # Collider age
        age = collider_output_age_minutes()
        print(f"\n    Collider age: {age:.0f} minutes")

    # Communication Fabric metrics
    comm_history = INTELLIGENCE_DIR / "comms" / "state_history.jsonl"
    if comm_history.exists():
        try:
            with open(comm_history) as f:
                lines = f.readlines()
                if lines:
                    latest = json.loads(lines[-1])
                    print(f"\n## COMMUNICATION FABRIC")
                    print(f"    F (Latency):      {latest.get('F', 0):.2f} hours")
                    print(f"    MI (Alignment):   {latest.get('MI', 0):.4f}")
                    print(f"    N (Noise):        {latest.get('N', 0):.4f}")
                    print(f"    SNR:              {latest.get('SNR', 0):.4f}")
                    print(f"    R_auto:           {latest.get('R_auto', 0):.4f}")
                    print(f"    R_manual:         {latest.get('R_manual', 0):.4f}")
                    print(f"    ΔH (Entropy):     {latest.get('dH', 0):.4f}")
                    margin = latest.get('margin', 0)
                    tier = latest.get('tier', 'N/A')
                    stability = "STABLE" if margin > 0 else "UNSTABLE"
                    print(f"    Stability:        {stability} (margin: {margin:+.4f})")
                    print(f"    Health Tier:      {tier}")
        except Exception:
            pass

    # Recommendations
    print(f"\n## STATUS")
    issues = []
    try:
        if knots.get('knot_score', 0) >= 8:
            issues.append("🔴 CRITICAL: Knot score >= 8 (high coupling)")
        if purpose.get('god_class_count', 0) > 50:
            issues.append("🔴 CRITICAL: >50 god classes (SRP violations)")
        if purpose.get('alignment_health') == 'CRITICAL':
            issues.append("🟡 WARNING: Purpose alignment is CRITICAL")
    except NameError:
        pass  # Collider data not loaded
    try:
        if latest.get('margin', 1) <= 0:
            issues.append("🔴 CRITICAL: Communication Fabric UNSTABLE")
    except NameError:
        pass  # Comm Fabric data not loaded

    if issues:
        for issue in issues:
            print(f"    {issue}")
    else:
        print("    ✅ No critical issues detected")

    print("\n" + "=" * 70)


def run_pipeline(skip_collider: bool = False, dashboard_only: bool = False):
    """Run the full wiring pipeline."""

    if dashboard_only:
        print_dashboard()
        return True

    print("=" * 70)
    print("WIRE - PROJECT_elements Grand Orchestrator")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")

    stages = []

    # Stage 1: LOL (List of Lists) Sync
    stages.append(PipelineStage(
        "LOL_SYNC",
        ["python3", str(LOL_SYNC)],
        "Scan filesystem, classify all entities"
    ))

    # Stage 2: TDJ Update (inline)
    # We'll handle this specially

    # Stage 3: Collider Full (optional if cached)
    collider_age = collider_output_age_minutes()
    if skip_collider:
        print(f"\n⏭ Skipping Collider (--quick mode, cached output is {collider_age:.0f}m old)")
    elif collider_age < 30:
        print(f"\n⏭ Skipping Collider (output is only {collider_age:.0f}m old)")
    else:
        stages.append(PipelineStage(
            "COLLIDER",
            ["bash", str(COLLIDER_DIR / "collider"), "full", "..",
             "--output", str(COLLIDER_OUTPUT_DIR)],
            "Full SMoC analysis of entire project"
        ))

    # Stage 4: SMoC Merger
    stages.append(PipelineStage(
        "SMOC_MERGE",
        ["python3", str(LOL_SMOC_MERGER),
         "--collider", str(find_latest_collider_output() or "")],
        "Merge Collider classifications into LOL (List of Lists)"
    ))

    # Stage 5: Unify
    stages.append(PipelineStage(
        "UNIFY",
        ["python3", str(LOL_UNIFY)],
        "Merge all sources (temporal, symmetry, purpose)"
    ))

    # Stage 6: Communication Fabric
    stages.append(PipelineStage(
        "COMM_FABRIC",
        ["python3", str(COMM_FABRIC), "--record"],
        "Record Communication Fabric state vector (F, MI, N, SNR, R, ΔH)"
    ))

    # Stage 7-9: Refinery (Knowledge Consolidation)
    # Ensure chunks directory exists
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    # Cleanup any temp files from failed runs
    for temp_file in CHUNKS_DIR.glob("*.tmp"):
        temp_file.unlink()

    # Check convergence (skip if knowledge hasn't changed)
    skip_refinery = False
    metadata_file = CHUNKS_DIR / "metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                prev_metadata = json.load(f)

            # Get current git SHA
            current_sha = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=str(REPO_ROOT),
                text=True
            ).strip()

            # If same SHA, knowledge hasn't changed
            if prev_metadata.get("git_sha") == current_sha:
                print(f"  ⊘ Refinery skipped (knowledge converged at SHA {current_sha[:8]})")
                skip_refinery = True
        except Exception:
            pass  # If check fails, proceed with refinery

    if not skip_refinery:
        stages.append(PipelineStage(
            "REFINERY_AGENT",
            ["python3", str(REFINERY_SCRIPT), str(REPO_ROOT / ".agent"),
             "--export", str(CHUNKS_DIR / "agent_chunks.json")],
            "Atomize .agent/ directory (tools, intelligence, registry)"
        ))

        stages.append(PipelineStage(
            "REFINERY_CORE",
            ["python3", str(REFINERY_SCRIPT), str(REPO_ROOT / "standard-model-of-code" / "src" / "core"),
             "--export", str(CHUNKS_DIR / "core_chunks.json")],
            "Atomize Collider core (pipeline, analysis, graph)"
        ))

        stages.append(PipelineStage(
            "REFINERY_ACI",
            ["python3", str(REFINERY_SCRIPT), str(REPO_ROOT / "context-management" / "tools" / "ai" / "aci"),
             "--export", str(CHUNKS_DIR / "aci_chunks.json")],
            "Atomize ACI tools (refinery, research, tier router)"
        ))

    # Execute pipeline
    total_start = time.time()
    results = []

    for stage in stages:
        if stage.name == "LOL_SYNC":
            # Run LOL sync first
            success = stage.run()
            results.append((stage.name, success, stage.duration))

            # Then update TDJ inline
            print(f"\n{'─' * 60}")
            print(f"▶ TDJ_UPDATE: Update Temporal Daily Journal")
            print(f"{'─' * 60}")
            tdj_start = time.time()
            update_tdj()
            tdj_duration = time.time() - tdj_start
            results.append(("TDJ_UPDATE", True, tdj_duration))
            print(f"\n  ✓ TDJ_UPDATE completed in {tdj_duration:.1f}s")
        else:
            success = stage.run()
            results.append((stage.name, success, stage.duration))
            if not success and not stage.optional:
                print(f"\n⚠ Pipeline stopped at {stage.name}")
                break

    total_duration = time.time() - total_start

    # Track chunk generation metadata
    try:
        chunk_stats = {}
        for chunk_name in ["agent", "core", "aci"]:
            chunk_file = CHUNKS_DIR / f"{chunk_name}_chunks.json"
            if chunk_file.exists():
                with open(chunk_file) as f:
                    data = json.load(f)
                    chunk_stats[chunk_name] = {
                        "chunks": data.get("node_count", 0),
                        "tokens": data.get("total_tokens", 0)
                    }

        if chunk_stats:
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "git_sha": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"],
                    cwd=str(REPO_ROOT),
                    text=True
                ).strip(),
                "chunks": chunk_stats,
                "total_chunks": sum(s["chunks"] for s in chunk_stats.values()),
                "total_tokens": sum(s["tokens"] for s in chunk_stats.values()),
            }

            with open(CHUNKS_DIR / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)

    except Exception as e:
        print(f"  ⚠ Warning: Failed to generate chunk metadata: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)

    for name, success, duration in results:
        status = "✓" if success else "✗"
        print(f"  {status} {name:<15} {duration:>6.1f}s")

    print(f"\n  Total time: {total_duration:.1f}s")

    # Show dashboard
    print_dashboard()

    return all(r[1] for r in results)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="WIRE - The Grand Orchestrator for PROJECT_elements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python wire.py                 # Full pipeline
  python wire.py --quick         # Skip Collider (use cached)
  python wire.py --dashboard     # Show dashboard only
  python wire.py --watch         # Continuous monitoring
        """
    )
    parser.add_argument("--quick", "-q", action="store_true",
                        help="Skip Collider analysis (use cached output)")
    parser.add_argument("--dashboard", "-d", action="store_true",
                        help="Show health dashboard only")
    parser.add_argument("--watch", "-w", action="store_true",
                        help="Continuous mode (re-run every 5 minutes)")

    args = parser.parse_args()

    if args.watch:
        print("WIRE - Watch Mode (Ctrl+C to stop)")
        print("Running pipeline every 5 minutes...\n")
        while True:
            try:
                run_pipeline(skip_collider=True)
                print(f"\nNext run in 5 minutes... (Ctrl+C to stop)")
                time.sleep(300)
            except KeyboardInterrupt:
                print("\nWatch mode stopped.")
                break
    else:
        success = run_pipeline(
            skip_collider=args.quick,
            dashboard_only=args.dashboard
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
