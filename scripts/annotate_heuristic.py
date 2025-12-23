#!/usr/bin/env python3
"""
LLM Heuristic Annotator

Implements the "LLM Assistant" logic for role classification as a robust heuristic script.
Used to bootstrap ground truth for large datasets (500+ samples) where interactive
chat annotation is too slow.

Logic emphasizes:
1. Canonical 27 roles
2. Pattern recognition (naming, ancestry)
3. Context awareness (file path analysis)
"""

import csv
import re
import sys

# Canonical 27 Roles
ROLES = {
    # Data Access
    "Query", "Command", "Repository",
    # Domain
    "Entity", "Service",
    # Creation
    "Factory", "Builder",
    # Processing
    "Validator", "Transformer",
    # Structural
    "Adapter", "Decorator", "Strategy",
    # Interface
    "Controller", "Presenter", "View",
    # Config
    "Configuration", "Constant",
    # Testing
    "Test", "Mock", "Fixture",
    # Lifecycle
    "EventHandler", "Observer", "Migration",
    # Infra
    "Singleton", "Guard",
    # Cross-cutting
    "Utility", "Middleware"
}

def classify(name, kind, file_path, signature=""):
    """
    Classify semantic role based on name, kind, file path, and signature.
    Returns (role, confidence)
    """
    
    # 1. Strong Name Patterns
    # ----------------------
    lower_name = name.lower()
    
    # Testing
    if (lower_name.startswith('test_') or 
        lower_name.endswith('test') or 
        'tests/' in file_path or 
        '/test_' in file_path):
        if 'fixture' in lower_name: return "Fixture", 0.95
        if 'mock' in lower_name: return "Mock", 0.95
        return "Test", 0.95
        
    # Data Access
    if 'repository' in lower_name: return "Repository", 0.95
    if lower_name.startswith('get_') or lower_name.startswith('fetch_') or lower_name.startswith('find_'): return "Query", 0.90
    if lower_name.startswith('save_') or lower_name.startswith('delete_') or lower_name.startswith('update_'): return "Command", 0.90
    
    # Domain Logic
    if 'service' in lower_name: return "Service", 0.95
    if 'usecase' in lower_name: return "Service", 0.95 # Migrated
    if 'manager' in lower_name: return "Service", 0.85
    
    # Creation
    if 'factory' in lower_name: return "Factory", 0.95
    if 'builder' in lower_name: return "Builder", 0.95
    if lower_name.startswith('create_') or lower_name.startswith('make_') or lower_name.startswith('build_'): return "Factory", 0.90
    
    # Processing
    if 'validator' in lower_name or lower_name.startswith('validate_') or lower_name.startswith('is_'): return "Validator", 0.90
    if 'transformer' in lower_name or lower_name.startswith('transform_') or 'mapper' in lower_name or 'converter' in lower_name: return "Transformer", 0.90
    if lower_name.startswith('convert_') or lower_name.startswith('map_') or lower_name.startswith('serialize_'): return "Transformer", 0.90
    
    # Interface
    if 'controller' in lower_name or 'handler' in lower_name and 'http' in file_path: return "Controller", 0.95
    if 'view' in lower_name: return "View", 0.90
    if 'presenter' in lower_name: return "Presenter", 0.90
    
    # Events
    if 'handler' in lower_name and ('event' in file_path or 'handler' in file_path): return "EventHandler", 0.85
    if 'observer' in lower_name or 'listener' in lower_name: return "Observer", 0.95
    
    # Config
    if 'config' in lower_name or 'settings' in lower_name or 'constant' in lower_name: return "Configuration", 0.90
    if name.isupper() and '_' in name: return "Constant", 0.90
    
    # Structural
    if 'adapter' in lower_name or 'wrapper' in lower_name: return "Adapter", 0.90
    if 'decorator' in lower_name: return "Decorator", 0.95
    if 'strategy' in lower_name: return "Strategy", 0.95
    
    # Cross-cutting
    if 'middleware' in lower_name: return "Middleware", 0.95
    if 'utils' in file_path or 'helper' in file_path: return "Utility", 0.85
    
    # 2. File Path / Context Analysis
    # -----------------------------
    if '/models/' in file_path or '/entities/' in file_path:
        if kind == 'AGG' or kind == 'HDL': return "Entity", 0.80
        
    if '/services/' in file_path: return "Service", 0.80
    if '/controllers/' in file_path: return "Controller", 0.80
    if '/repositories/' in file_path: return "Repository", 0.80
    
    # 3. Signature / Kind Fallbacks
    # ---------------------------
    if kind == 'FNC' and (lower_name.startswith('_') and not lower_name.startswith('__')): 
        return "Utility", 0.70  # Internal helper
        
    if kind == 'AGG' and 'model' in lower_name: return "Entity", 0.80
    if kind == 'AGG' and 'dto' in lower_name: return "Entity", 0.85
    
    return "Utility", 0.50 # Default fallback

def annotate_file(input_file):
    print(f"Annotating {input_file} using Heuristic Assistant...")
    
    rows = []
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if 'annotated_role' not in fieldnames:
            fieldnames.append('annotated_role')
        if 'annotated_atom' not in fieldnames:
            fieldnames.append('annotated_atom')
            
        for row in reader:
            role, conf = classify(row['name'], row['kind'], row['file'])
            
            # If our confidence is high, overwrite prediction
            # Otherwise keep it (or if it matches)
            row['annotated_role'] = role
            rows.append(row)
            
    with open(input_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"✅ Context extraction & annotation complete for {len(rows)} samples.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 annotate_heuristic.py <input_csv>")
        sys.exit(1)
        
    annotate_file(sys.argv[1])
