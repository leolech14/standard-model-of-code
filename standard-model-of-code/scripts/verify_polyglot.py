
import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
src_path = project_root / "src"
sys.path.append(str(src_path))

from core.complete_extractor import CompleteExtractor
from core.edge_extractor import extract_call_edges

def verify_complete_extractor():
    print("\n--- Verifying CompleteExtractor (JS) ---")
    extractor = CompleteExtractor()
    assets_dir = Path("standard-model-of-code/src/core/viz/assets")
    
    if not assets_dir.exists():
        print(f"Directory not found: {assets_dir}")
        return

    codebase = extractor.extract(str(assets_dir), language="javascript")
    
    print(f"Files found: {list(codebase.files.keys())}")
    print(f"Functions found: {len(codebase.functions)}")
    
    # Check for specific expected functions in app.js
    found_init = False
    for fid, func in codebase.functions.items():
        if "init" in func.name or "animate" in func.name:
            found_init = True
            break
            
    if found_init:
        print("✅ JS parsing successful (found known functions)")
    else:
        print("❌ JS parsing failed (no expected functions found)")

def verify_edge_extractor():
    print("\n--- Verifying EdgeExtractor (Polyglot) ---")
    
    # Mock JS particle
    js_particle = {
        "id": "app.js:animate",
        "name": "animate",
        "file_path": "src/core/viz/assets/app.js", 
        "body_source": "render(); this.update();"
    }
    # Mock JS Targets
    js_render = {"id": "app.js:render", "name": "render", "file_path": "app.js"}
    js_update = {"id": "app.js:update", "name": "update", "file_path": "app.js"}
    
    # Mock Python particle
    py_particle = {
        "id": "test.py:main",
        "name": "main",
        "file_path": "test.py",
        "body_source": "process_data()\nobj.method()"
    }
    # Mock Python Targets
    py_process = {"id": "test.py:process_data", "name": "process_data", "file_path": "test.py"}
    py_method = {"id": "test.py:method", "name": "method", "file_path": "test.py"} # obj.method calls 'method'? Or needs type inference.
    # Current strategy only matches if 'method' is in particle_by_name.
    
    particles = [js_particle, js_render, js_update, py_particle, py_process, py_method]
    results = [] 
    
    edges = extract_call_edges(particles, results)
    
    # Check Python
    py_edges = [e for e in edges if e['source'] == 'test.py:main']
    print(f"Python Edges Found: {len(py_edges)}")
    for e in py_edges:
        print(f"  -> {e['edge_type']} {e['target']}")

    # Check JS
    js_edges = [e for e in edges if e['source'] == 'app.js:animate']
    print(f"JS Edges Found: {len(js_edges)}")
    for e in js_edges:
        print(f"  -> {e['edge_type']} {e['target']}")
        
    if len(py_edges) >= 1 and len(js_edges) >= 1:
        print("✅ Polyglot strategies working")
    else:
        print("❌ Strategies failed to find expected edges")

if __name__ == "__main__":
    verify_complete_extractor()
    verify_edge_extractor()
