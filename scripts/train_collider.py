#!/usr/bin/env python3
"""
Collider Training Script
========================
Runs the AutoPatternDiscovery engine against the Ground Truth dataset
to find new high-confidence classification rules.
"""

import sys
import csv
from pathlib import Path
from collections import defaultdict

# Add root to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core.auto_pattern_discovery import AutoPatternDiscovery
from core.unified_analysis import UnifiedNode

def train():
    print("🧠 Collider Self-Improvement Engine")
    print("===================================")
    
    csv_path = root_dir / "data/mini_validation_samples.csv"
    if not csv_path.exists():
        print(f"❌ Dataset not found: {csv_path}")
        return

    # 1. Load Ground Truth
    print(f"\n📂 Loading Ground Truth from {csv_path.name}...")
    samples = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create a mock dict for the learner
            node = {
                'name': row['name'],
                'file_path': row['file'],
                'annotated_role': row['annotated_role']
            }
            samples.append(node)
    
    print(f"   → Loaded {len(samples)} training samples")

    # 2. Run Discovery
    print("\n🔍 Analyzing feature correlations...")
    discoverer = AutoPatternDiscovery()
    
    # We use the 'learn_patterns_from_data' method we added
    new_patterns = discoverer.learn_patterns_from_data(samples)
    
    # 3. Report Results
    print(f"\n💡 Discovery Complete. Found {len(new_patterns)} high-confidence patterns:\n")
    
    print(f"{'TYPE':<10} | {'PATTERN':<20} | {'PREDICTED ROLE':<20} | {'CONFIDENCE':<10}")
    print("-" * 70)
    
    for pattern, (role, conf) in new_patterns.items():
        # p is (type, pattern, role, confidence)
        p_type = "Prefix" # Learner currently only does prefixes
        print(f"{p_type:<10} | {pattern:<20} | {role:<20} | {conf/100:.1%}")

    print("\n✅ These patterns suggest systematic improvements to the PatternRepository.")

if __name__ == "__main__":
    train()
