
import sys
import os
import ast
sys.path.append(os.getcwd())

# Mock required classes
class MockClassifier:
    def classify_extracted_symbol(self, **kwargs):
        return {"id": "mock"}

from src.core.parser.python_extractor import PythonASTExtractor

def reproduce():
    target_file = "src/core/edge_extractor.py"
    print(f"Reading {target_file}...")
    with open(target_file, 'r') as f:
        content = f.read()
    
    print(f"Read {len(content)} bytes.")
    
    classifier = MockClassifier()
    extractor = PythonASTExtractor(classifier)
    
    print("Calling extract_particles_ast...")
    try:
        extractor.extract_particles_ast(content, target_file, include_depth_metrics=True)
        print("Success!")
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reproduce()
