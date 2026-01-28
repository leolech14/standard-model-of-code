
#!/usr/bin/env python3
"""
Gap Analysis Tool: Identifying the Symmetry Gap
===============================================
Phase 20: Perfect Architectural Symmetry

This script strictly compares the Codome (src/core) with the Contextome (docs/core)
to identify "Ghost Files" (Code without Context).
"""

import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
CODE_ROOT = PROJECT_ROOT / "standard-model-of-code/src/core"
CONTEXT_ROOT = PROJECT_ROOT / "standard-model-of-code/docs/core"

def analyze_gap():
    print(f"--- [ Gap Analysis: {CODE_ROOT.name} vs {CONTEXT_ROOT.name} ] ---")
    
    if not CONTEXT_ROOT.exists():
        print(f"CRITICAL: Context Root {CONTEXT_ROOT} does not exist!")
        # We define it logicly as missing 100% of files
    
    missing_docs = []
    total_code_files = 0
    
    for root, dirs, files in os.walk(CODE_ROOT):
        # Skip pycache and hidden
        if "__pycache__" in root: continue
        
        for file in files:
            if not file.endswith(".py"): continue
            if file == "__init__.py": continue
            
            total_code_files += 1
            
            # Calculate relative path from src/core
            # e.g. pipeline/stages/loader.py
            abs_code_path = Path(root) / file
            rel_path = abs_code_path.relative_to(CODE_ROOT)
            
            # Expected doc path: docs/core/pipeline/stages/loader.md
            expected_doc_path = CONTEXT_ROOT / rel_path.with_suffix(".md")
            
            if not expected_doc_path.exists():
                missing_docs.append({
                    "code": str(rel_path),
                    "doc": str(expected_doc_path.relative_to(PROJECT_ROOT))
                })

    print(f"Total Code Atoms: {total_code_files}")
    print(f"Missing Context Mirrors: {len(missing_docs)}")
    
    if total_code_files > 0:
        symmetry = 1.0 - (len(missing_docs) / total_code_files)
        print(f"Granular Symmetry Score: {symmetry:.2%}")
    
    return missing_docs

def generate_stubs(missing_docs):
    print("\n--- [ Generating Context Stubs ] ---")
    created_count = 0
    
    for item in missing_docs:
        doc_path = PROJECT_ROOT / item["doc"]
        code_rel = item["code"]
        
        # Create parent directories
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create stub content
        module_name = Path(code_rel).stem
        title = module_name.replace("_", " ").title()
        
        content = f"""# {title}

> **Mirror**: [`{code_rel}`](../../../src/core/{code_rel})
> **Role**: Contextome Stub (Auto-generated)

## Purpose
*Theory explanation pending...*

## Architecture
This document validates the logic in the corresponding code file.

## References
*   [Source Code](../../../src/core/{code_rel})
"""
        with open(doc_path, 'w') as f:
            f.write(content)
        created_count += 1
        print(f"Created: {doc_path.name}")
        
    print(f"\nSuccessfully created {created_count} Context stubs.")

if __name__ == "__main__":
    missing = analyze_gap()
    
    if missing:
        print("\nTo auto-generate stubs for these ghost files, run this script with --fix")
        import sys
        if "--fix" in sys.argv:
            generate_stubs(missing)
