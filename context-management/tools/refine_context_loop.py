#!/usr/bin/env python3
"""
Continuous Context Refinement Loop (The Holographic Socratic Layer)
==================================================================
This script orchestrates the 24/7 autonomous refinement process.
It:
1.  Runs the Collider Analysis Pipeline.
2.  Audits the results against Antimatter Laws (semantic_models.yaml).
3.  Identifies specific violations (AM001-AM004).
4.  (Future) Autonomously proposes fixes or refactors context.

Usage:
    python3 refine_context_loop.py [--loop] [--interval SECONDS]
"""
import sys
import time
import subprocess
import json
import argparse
import os
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
COLLIDER_SCRIPT = PROJECT_ROOT / "standard-model-of-code/src/core/full_analysis.py"
LOG_DIR = PROJECT_ROOT / "context-management/intelligence/logs"
ANALYSIS_TOOL = PROJECT_ROOT / "context-management/tools/ai/analyze.py"

def run_collider():
    """Execute the full collider analysis."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🧪 Starting Collider Analysis...")
    try:
        # Run collider full analysis on the project root
        # Set PYTHONPATH to include standard-model-of-code
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT / "standard-model-of-code") + os.pathsep + env.get("PYTHONPATH", "")
        
        result = subprocess.run(
            [sys.executable, str(COLLIDER_SCRIPT), "full", str(PROJECT_ROOT)],
            capture_output=True, text=True, check=True, env=env
        )
        print("   ✅ Collider Analysis Complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Collider Failed: {e}")
        print(e.stderr[:500] + "...")
        return False

def get_latest_audit_log():
    """Find the most recent socratic audit log."""
    try:
        logs = sorted(LOG_DIR.glob("socratic_audit_pipeline_*.json"))
        return logs[-1] if logs else None
    except Exception:
        return None

def analyze_violations(log_path):
    """Parse the audit log and return actionable violations."""
    if not log_path:
        return []
    
    violations = []
    try:
        with open(log_path, 'r') as f:
            data = json.load(f)
            
        for res in data.get('results', []):
            concept = res.get('hypothesis', {}).get('concept', 'Unknown')
            guardrails = res.get('result', {}).get('guardrails', {})
            
            if not guardrails.get('compliant', True):
                for v in guardrails.get('violations', []):
                    violations.append({
                        'concept': concept,
                        'law': v.get('law_id'),
                        'severity': v.get('severity'),
                        'reasoning': v.get('reasoning')
                    })
    except Exception as e:
        print(f"   ❌ Error reading log {log_path}: {e}")
        
    return violations

def refine_context(violations):
    """
    The 'Socratic' Step:
    Take violations and determine next steps for refinement.
    """
    if not violations:
        print("   ✨ No violations found. System is logically consistent.")
        return

    print(f"   ⚠️  Found {len(violations)} Context Violations:")
    
    # Bundle violations by Law
    by_law = {}
    for v in violations:
        law = v['law']
        if law not in by_law: by_law[law] = []
        by_law[law].append(v)

    for law, items in by_law.items():
        print(f"      - {law} ({len(items)}): {items[0]['reasoning'][:80]}...")
        
        # PROPOSED AUTONOMOUS ACTION (Placeholder)
        # 1. Select the highest leverage violation
        # 2. Construct a prompt for analyze.py to "Fix this context"
        # 3. Apply the fix (update docs, refactor code)
        
    print(f"\n   [NEXT ACTION] Would trigger autonomous refinement for top violation: {violations[0]['law']}")


def main_loop(interval=300, loop=False):
    print("=" * 60)
    print("♾️  HOLOGRAPHIC SOCRATIC LAYER ACTIVATED")
    print("=" * 60)
    
    while True:
        # 1. Run Analysis
        success = run_collider()
        
        # 2. Audit
        if success:
            latest_log = get_latest_audit_log()
            violations = analyze_violations(latest_log)
            
            # 3. Refine
            refine_context(violations)
        
        if not loop:
            break
            
        print(f"\n   💤 Sleeping for {interval}s...")
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="Run in continuous loop")
    parser.add_argument("--interval", type=int, default=300, help="Loop interval in seconds")
    args = parser.parse_args()
    
    main_loop(interval=args.interval, loop=args.loop)
