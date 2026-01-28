
import sys
import os
import ast
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

# Import REAL components
try:
    from src.core.classification.universal_classifier import UniversalClassifier
    from src.core.parser.python_extractor import PythonASTExtractor
    print("Imports successful from src.core...")
except ImportError:
    # Fallback for different execution context
    sys.path.append(str(Path(os.getcwd()) / "standard-model-of-code"))
    from src.core.classification.universal_classifier import UniversalClassifier
    from src.core.parser.python_extractor import PythonASTExtractor
    print("Imports successful with adjusted path...")

def reproduce():
    target_file = "standard-model-of-code/src/core/edge_extractor.py"
    abs_path = os.path.abspath(target_file)
    
    print(f"Reading {abs_path}...")
    with open(abs_path, 'r') as f:
        content = f.read()
    
    print(f"Read {len(content)} bytes.")
    
    print("Initializing UniversalClassifier (Real)...")
    classifier = UniversalClassifier()
    print("Classifier initialized.")
    
    print("Initializing PythonASTExtractor...")
    extractor = PythonASTExtractor(classifier)
    
    print("Calling extract_particles_ast...")
    try:
        extractor.extract_particles_ast(content, abs_path, include_depth_metrics=True)
        print("Success!")
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reproduce()
