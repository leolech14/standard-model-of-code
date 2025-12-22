"""
Naive Baselines for Layer Inference Comparison.

These baselines provide a lower-bound for performance comparison.
If Spectrometer cannot beat these simple regexes, it adds no value.
"""
from typing import Dict, Any, List

class NaiveLayerBaseline:
    """
    Predicts architectural layer based SOLELY on file path matching.
    No AST parsing, no dependency analysis.
    """
    
    def predict(self, file_path: str) -> str:
        """Predict layer from file path."""
        path = file_path.lower()
        
        # Domain Layer
        if any(x in path for x in ["/domain/", "/entities/", "/model/", "/core/"]):
            return "Core" # or Domain, depending on mapping
            
        # Application Layer
        if any(x in path for x in ["/app/", "/application/", "/usecase/", "/services/", "/service/"]):
            return "Application"
            
        # Infrastructure Layer
        if any(x in path for x in ["/infra/", "/infrastructure/", "/repo/", "/db/", "/external/", "/adapters/"]):
            return "Infrastructure"
            
        # Interface/Presentation Layer
        if any(x in path for x in ["/api/", "/web/", "/ui/", "/controller/", "/routes/", "/presentation/"]):
            return "Interface"
            
        return "Unknown"

    def analyze_repo(self, repo_path: str, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Mimic Spectrometer's analyze_repository output format.
        Returns a list of 'particles' (one per file).
        """
        particles = []
        for fp in file_paths:
            layer = self.predict(fp)
            if layer != "Unknown":
                particles.append({
                    "name": fp.split("/")[-1],
                    "type": "NaiveFile", # Dummy type
                    "file_path": fp,
                    "inferred_layer": layer, # Direct prediction
                    "confidence": 1.0
                })
        return particles
