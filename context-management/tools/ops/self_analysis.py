
"""
Self-Analysis Script
====================
Uses the Collider engine to analyze the codebase and generate content
for the 110 empty Contextome stubs.
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent.parent.resolve())
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "standard-model-of-code"))
sys.path.append(os.path.join(project_root, "standard-model-of-code/src/core"))

from src.core.tree_sitter_engine import TreeSitterUniversalEngine

def run_self_analysis():
    print("--- [ Self-Analysis: Reading Source Code ] ---")
    
    # Target: src/core (The Codome)
    src_path = os.path.abspath("standard-model-of-code/src/core")
    
    # Initialize Engine directly
    print("Initializing TreeSitterUniversalEngine...")
    engine = TreeSitterUniversalEngine()
    
    # Configure it to analyze Python files
    print(f"Analyzing {src_path}...")
    results = engine.analyze_directory(src_path, extensions=['.py'])
    
    print(f"Analysis complete. Found {len(results)} file results.")
    
    # Map results by file path
    particles_by_file = {}
    for res in results:
        fpath = res.get('file_path')
        if fpath:
            # Normalize path
            fpath_obj = Path(fpath).resolve()
            src_path_obj = Path(src_path).resolve()
            
            try:
                rel_path = fpath_obj.relative_to(src_path_obj)
                particles_by_file[str(rel_path)] = res.get('particles', [])
            except ValueError:
                # If file is not subpath of source root (shouldn't happen but safety first)
                pass
            
    # Now fill the stubs
    docs_root = Path("standard-model-of-code/docs/core")
    
    updated_count = 0
    for rel_path_str, particles in particles_by_file.items():
        doc_rel = Path(rel_path_str).with_suffix(".md")
        doc_path = docs_root / doc_rel
        
        if True: # Always ensure doc exists
            if not doc_path.parent.exists():
                doc_path.parent.mkdir(parents=True, exist_ok=True)
                
            print(f"Propagating to {doc_path}...")
            
            # Generate Content
            # Debug: print first particle keys to ensure schema
            if particles:
                # print(f"DEBUG keys: {particles[0].keys()}")
                pass

            classes = [p for p in particles if p.get('kind') == 'class' or p.get('symbol_kind') == 'class']
            functions = [p for p in particles if p.get('kind') == 'function' or p.get('symbol_kind') == 'function']
            
            content = f"# {doc_path.stem.replace('_', ' ').title()}\n\n"
            content += f"> **Mirror**: [`{rel_path_str}`](../../../src/core/{rel_path_str})\n"
            content += f"> **Role**: Core Component\n\n"
            
            content += "## Purpose\n"
            content += "*(Auto-generated summary based on code structure)*\n\n"
            
            content += "## Architecture\n"
            if classes:
                content += "### Classes\n"
                for c in classes:
                    doc = c.get('docstring') or "No docstring"
                    summary = doc.splitlines()[0] if doc else "No docstring"
                    content += f"- **`{c.get('name')}`**: {summary}\n"
            
            if functions:
                content += "\n### Functions\n"
                for f in functions:
                     doc = f.get('docstring') or "No docstring"
                     summary = doc.splitlines()[0] if doc else "No docstring"
                     content += f"- **`{f.get('name')}`**: {summary}\n"

            content += "\n## Waybill\n"
            content += f"- **ID**: `PARCEL-{rel_path_str.upper().replace('/', '-')}`\n"
            content += f"- **Source**: `Codome://{rel_path_str}`\n"
            content += f"- **Refinery**: `SelfAnalysis-v1.0`\n"
            content += f"- **Generated**: `{datetime.utcnow().isoformat()}Z`\n"
            content += f"- **Status**: REFINED\n"

            with open(doc_path, 'w') as f:
                f.write(content)
            updated_count += 1
            
    print(f"Successfully populated {updated_count} Contextome files.")

if __name__ == "__main__":
    run_self_analysis()
