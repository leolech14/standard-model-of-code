#!/usr/bin/env python3
import json
import glob
import os
from datetime import datetime

LOG_DIR = "context-management/intelligence/logs"

def analyze_audit_logs():
    files = sorted(glob.glob(os.path.join(LOG_DIR, "socratic_audit_pipeline_*.json")))
    
    print(f"Analyzing {len(files)} audit logs...")
    print("-" * 50)
    
    executions_count = 0
    compliance_stats = {'passed': 0, 'failed': 0}
    
    for f_path in files:
        try:
            with open(f_path, 'r') as f:
                data = json.load(f)
                
            timestamp = data.get('timestamp', 'Unknown')
            # Adapt these keys based on actual JSON structure. 
            # Assuming typical fields like 'issues_found', 'drift_detected' based on filename intent.
            # I will inspect one file content next to be sure, but for now assuming generic structure.
            
            executions_count += 1
            
            print(f"[{timestamp}] {os.path.basename(f_path)}")
            
            for res in data.get('results', []):
                concept = res.get('hypothesis', {}).get('concept', 'Unknown')
                result_data = res.get('result', {})
                verified = result_data.get('verified', False)
                
                if verified:
                    compliance_stats['passed'] += 1
                else:
                    compliance_stats['failed'] += 1
                    
                guardrails = result_data.get('guardrails', {})
                if not guardrails.get('compliant', True):
                    for violation in guardrails.get('violations', []):
                        law_id = violation.get('law_id', 'Unknown')
                        print(f"  [VIOLATION] {concept} failed {law_id}: {violation.get('severity', 'UNKNOWN')}")
                        
        except Exception as e:
            print(f"Error reading {f_path}: {e}")

    print("-" * 50)
    print(f"Total Logs: {executions_count}")
    print(f"Compliance: {compliance_stats}")

executions_count = 0
compliance_stats = {'passed': 0, 'failed': 0}

if __name__ == "__main__":
    analyze_audit_logs()
