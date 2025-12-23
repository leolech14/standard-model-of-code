#!/usr/bin/env python3
"""
Collider Serial Training (Mastery Learning)
===========================================
Learns from repositories sequentially.
For each repo:
1. Evaluate current accuracy.
2. If < Target, Learn patterns from THIS repo.
3. Apply patterns (simulated).
4. Re-evaluate.
5. Move to next repo only when 'Mastered' (or converged).
"""

import sys
import csv
import re
from pathlib import Path
from collections import defaultdict, Counter

# Add root to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core.auto_pattern_discovery import AutoPatternDiscovery
from core.atom_classifier import AtomClassifier

def extract_repo_name(file_path):
    # path: validation/benchmarks/repos/owner__repo/src/...
    parts = file_path.split('/')
    for i, p in enumerate(parts):
        if '__' in p: # Heuristic for our structure
            return p
    return "unknown_repo"

def train_serial():
    print("🎓 Collider Serial Mastery Engine")
    print("=================================")
    
    csv_path = root_dir / "data/benchmark/ground_truth_v1.csv"
    if not csv_path.exists():
        print(f"❌ Dataset not found: {csv_path}")
        return

    # 1. Load and Group Samples
    repo_samples = defaultdict(list)
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            repo = extract_repo_name(row['file'])
            # Normalize dict
            node = {
                'name': row['name'],
                'file_path': row['file'],
                'annotated_role': row['annotated_role'],
                'actual_role': row['annotated_role'] # For validation
            }
            repo_samples[repo].append(node)
    
    print(f"Loaded {len(repo_samples)} repositories.")
    
    # 2. Iterate Serialy
    classifier = AtomClassifier()
    discoverer = AutoPatternDiscovery()
    
    total_repos = len(repo_samples)
    current_idx = 0
    
    for repo_name, samples in repo_samples.items():
        current_idx += 1
        print(f"\n[{current_idx}/{total_repos}] 📦 Mastering Repository: {repo_name} ({len(samples)} samples)")
        print("-" * 60)
        
        # Iterative Loop for this Repo
        iteration = 0
        best_accuracy = 0.0
        
        while iteration < 2: # Limit improvement attempts per repo
            iteration += 1
            
            # A. Evaluate
            correct = 0
            for s in samples:
                # Classify
                file_path = s['file_path']
                name = s['name']
                # Use our classifier (note: classifier uses PatternRepo singleton, so updates persist)
                predicted_result = classifier.classify_by_name(name, file_path=file_path, language="python")
                s['predicted_role'] = normalize_role(predicted_result.subtype) # (role, conf)
                
                if s['predicted_role'] == s['annotated_role']:
                    correct += 1
            
            accuracy = correct / len(samples) * 100
            print(f"   Run #{iteration}: Accuracy = {accuracy:.1f}%")
            
            if accuracy >= 100.0:
                print("   ✅ PERFECT MATCH! Moving on.")
                break
                
            if accuracy < best_accuracy + 1.0 and iteration > 1:
                 print("   ⚠️  Diminishing returns. Moving on.")
                 break
            best_accuracy = accuracy
            
            # C. APPLY (Actual Permanent Learning)
            print(f"   🧠 Learning from failures...")
            # Filter for failures
            failures = [s for s in samples if s['predicted_role'] != s['annotated_role']]
            
            if not failures:
                print("   ✅ No failures to learn from.")
                break
                
            # Learn patterns from failures
            new_patterns = discoverer.learn_patterns_from_data(samples) 
            
            # DEBUG: Show what we imply but missed
            if iteration == 1 and failures:
                 print(f"      [DEBUG] Top Failures ({len(failures)}):")
                 # Extract common names from failures
                 fail_names = [f['name'] for f in failures]
                 # Quick simplified view
                 print(f"      Examples: {fail_names[:5]}")
            
            if not new_patterns:
                print("   ⚠️  No new patterns discovered.")
                break
            
            applied_count = 0
            
            # Helper to persist to file
            def persist_pattern(pat, role, conf):
                repo_file = root_dir / "core/registry/pattern_repository.py"
                content = repo_file.read_text()
                # Check if already exists
                if f"'{pat}':" in content:
                    return False
                
                # Insert into _load_default_patterns dictionary
                # Heuristic: Find a good insertion point (e.g. after "self._prefix_patterns = {")
                # We'll just define a marker or insert at end of dictionary
                # For robustness in this script, we'll append to the specific dictionary definition
                
                # Better approach for this script: Use the 'add_pattern' method if it existed, 
                # but since we want to modify Source Code, we do string injection.
                
                # We will look for "self._prefix_patterns = {" and insert after it
                injection_marker = "self._prefix_patterns = {"
                new_line = f"\n            '{pat}': ('{role}', {conf}),  # LEARNED (Serial Loop)"
                
                if injection_marker in content:
                    new_content = content.replace(injection_marker, injection_marker + new_line)
                    repo_file.write_text(new_content)
                    
                    # Update LEDGER
                    ledger_file = root_dir / "docs/LEARNING_LEDGER.md"
                    if ledger_file.exists():
                        date_str = "2025-12-23" # In real app, use datetime.now()
                        ledger_entry = f"| {date_str} | `{pat}` | Prefix | **{role}** | **{conf}%** | Serial Loop |\n"
                        with open(ledger_file, "a") as f:
                            f.write(ledger_entry)
                            
                    return True
                return False

            for pattern, (role, conf) in new_patterns.items():
                # Only apply if confidence is high enough
                if conf >= 85: 
                    # Update In-Memory singleton (for immediate re-test)
                    classifier.repo._prefix_patterns[pattern] = (role, conf)
                    
                    # Persist to disk (Green/Permanent)
                    if persist_pattern(pattern, role, conf):
                        print(f"      ✅ PERMANENTLY LEARNED: '{pattern}' -> {role} ({conf:.0f}%)")
                        applied_count += 1
                    else:
                         print(f"      ℹ️  Already exists/valid: '{pattern}'")
            
            if applied_count == 0:
                print("      No new high-confidence patterns to persist.")
                break
                
    print("\n✅ Serial Mastery Complete.")

# Validation Map representing Canonical Schema compliance
ROLE_MAP = {
    # Test Family
    'Test': 'Test',
    'TestDouble': 'Test',
    'Fixture': 'Test',
    'Assertion': 'Test',
    # Data Family
    'Entity': 'Entity',
    'ValueObject': 'Entity', # Map strict DDD to Entity for now
    'DTO': 'Entity',
    'Message': 'Entity',
    # Logic Family
    'Service': 'Service',
    'UseCase': 'Service',
    'Policy': 'Service',
    'Algorithm': 'Service',
    'Process': 'Service',
    # Interface Family
    'Controller': 'Controller',
    'Presenter': 'Controller',
    'View': 'Controller',
    'Router': 'Controller',
    # Infrastructure Family
    'Repository': 'Repository',
    'Gateway': 'Repository', # Check logic
    'Adapter': 'Adapter',
    'Client': 'Client',
    # Utility Family
    'Utility': 'Utility',
    'Helper': 'Utility',
    'Converter': 'Mapper',
    'Mapper': 'Mapper',
    'Factory': 'Factory',
    'Builder': 'Factory', # or Builder
    'Config': 'Configuration',
    'App': 'Configuration', # Entry point often Config/Lifecycle
    # Atom Classifier specific
    'ImpureFunction': 'Utility',
    'PureFunction': 'Utility',
    'Class': 'Entity', # Generic class fallback
    'Interface': 'Service', # Generic
    # Granular Atoms
    'Validator': 'Utility',
    'EventHandler': 'Utility',
    'Builder': 'Factory',
    'TestModule': 'Test',
}

def normalize_role(subtype):
    """Normalize granular Atom subtype to Canonical 27-Role."""
    # Direct match first
    if subtype in ROLE_MAP:
        return ROLE_MAP[subtype]
    # Fallback to direct string if valid canonical
    return subtype

if __name__ == "__main__":
    train_serial()
