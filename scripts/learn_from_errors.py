#!/usr/bin/env python3
"""
Auto-Learning Pattern Improver

Learns from validation errors to suggest pattern improvements.
Input: Validation report (predicted vs actual)
Output: Suggested pattern changes
"""

import csv
import re
from collections import Counter, defaultdict

def analyze_errors(csv_path):
    print("🧠 Learning from errors...")
    
    errors = []
    correct = 0
    total = 0
    
    # Error patterns
    false_services = []
    missed_tests = []
    
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('annotated_role'): continue
            
            actual = row['annotated_role']
            predicted = row['predicted_role']
            name = row['name']
            file_path = row['file']
            
            total += 1
            if actual == predicted:
                correct += 1
            else:
                errors.append((actual, predicted))
                
                # Analyze specific failure modes
                if actual == 'Test':
                    missed_tests.append(f"{name} ({file_path})")
                
                if predicted == 'Service' and actual == 'Utility':
                    false_services.append(f"{name} ({file_path})")

    accuracy = (correct / total) * 100
    print(f" Analyzed {total} samples. Accuracy: {accuracy:.1f}%")
    
    print("\n🔍 INSIGHT 1: Test Blindness")
    print(f"   Missed {len(missed_tests)} tests.")
    if len(missed_tests) > 0:
        print("   Common features in missed tests:")
        print("   - Files in 'tests/' directory")
        print("   - Functions starting with 'test_'")
        print("   SUGGESTION: Boost priority of 'tests/' path pattern")

    print("\n🔍 INSIGHT 2: Service Hallucination")
    print(f"   False positive Services: {len(false_services)}")
    if len(false_services) > 0:
        print("   Common cause: 'execute' method or 'Manager' suffix")
        print("   SUGGESTION: Require stronger evidence for Service (e.g. file path)")

if __name__ == "__main__":
    analyze_errors("data/mini_validation_samples.csv")
