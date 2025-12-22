#!/usr/bin/env python3
"""
Canonical Paths Oracle Extractor.

Extracts architecture ground truth from canonical directory structure.
This is the simplest oracle type: files in certain paths belong to certain layers.

Example config:
    oracle_type: canonical_paths
    oracle_config:
      layers:
        domain: ["src/allocation/domain/**"]
        application: ["src/allocation/service_layer/**"]
        infrastructure: ["src/allocation/adapters/**"]
        presentation: ["src/allocation/entrypoints/**"]
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .base import (
    OracleExtractor,
    OracleResult,
    ComponentMembership,
    DependencyConstraints,
)


# Common architectural layering rules (which layer can depend on which)
# These are well-established patterns from Clean Architecture / Onion / Hexagonal
DEFAULT_LAYER_ORDER = ["presentation", "application", "domain", "infrastructure"]

# Default allowed dependencies (inner layers should not depend on outer layers)
# presentation -> application -> domain <- infrastructure
DEFAULT_ALLOWED_DEPS = [
    ("presentation", "application"),
    ("presentation", "domain"),
    ("application", "domain"),
    ("infrastructure", "domain"),
    ("infrastructure", "application"),  # Adapters can use application services
]

DEFAULT_FORBIDDEN_DEPS = [
    ("domain", "presentation"),
    ("domain", "application"),
    ("domain", "infrastructure"),
    ("application", "presentation"),
    ("application", "infrastructure"),
]


class CanonicalPathsOracle(OracleExtractor):
    """
    Oracle that derives component membership from canonical directory paths.
    
    This is the simplest and most reliable oracle type for repos that follow
    established directory conventions (DDD, Clean Architecture, etc.).
    """
    
    @property
    def oracle_type(self) -> str:
        return "canonical_paths"
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        oracle_config = config.get("oracle_config", {})
        
        if "layers" not in oracle_config:
            errors.append("oracle_config.layers is required for canonical_paths oracle")
        elif not isinstance(oracle_config["layers"], dict):
            errors.append("oracle_config.layers must be a dict of layer_name -> [glob_patterns]")
        
        return errors
    
    def extract(self, repo_root: Path, config: Dict[str, Any]) -> OracleResult:
        """
        Extract component membership from canonical paths.
        
        For each layer defined in config, glob the patterns and assign
        matching files to that layer.
        """
        oracle_config = config.get("oracle_config", {})
        layers_config = oracle_config.get("layers", {})
        
        membership = ComponentMembership()
        warnings: List[str] = []
        
        # Track which patterns matched nothing (potential config errors)
        empty_patterns: List[str] = []
        
        for layer_name, patterns in layers_config.items():
            if not isinstance(patterns, list):
                patterns = [patterns]
            
            layer_files = set()
            for pattern in patterns:
                # Glob the pattern
                matched = list(repo_root.glob(pattern))
                for path in matched:
                    if path.is_file() and path.suffix == ".py":
                        rel_path = str(path.relative_to(repo_root))
                        # Normalize to forward slashes
                        rel_path = rel_path.replace("\\", "/")
                        layer_files.add(rel_path)
                
                if not matched:
                    empty_patterns.append(f"{layer_name}:{pattern}")
            
            # Add all files to membership
            for rel_path in layer_files:
                membership.add_file(rel_path, layer_name)
        
        if empty_patterns:
            warnings.append(f"Empty patterns (no matches): {empty_patterns}")
        
        # Build dependency constraints based on layer architecture
        constraints = self._build_constraints(
            layers_config.keys(),
            oracle_config.get("allowed_deps"),
            oracle_config.get("forbidden_deps"),
        )
        
        # Build oracle source description
        layer_summary = ", ".join(f"{k}:{len(v) if isinstance(v, list) else 1} patterns" 
                                   for k, v in layers_config.items())
        oracle_source = f"canonical_paths:[{layer_summary}]"
        
        validation_note = config.get(
            "validated_source", 
            "Canonical directory structure matching documented architecture"
        )
        
        return OracleResult(
            membership=membership,
            constraints=constraints,
            oracle_source=oracle_source,
            validation_note=validation_note,
            warnings=warnings,
        )
    
    def _build_constraints(
        self,
        layer_names: List[str],
        custom_allowed: List[List[str]] | None,
        custom_forbidden: List[List[str]] | None,
    ) -> DependencyConstraints:
        """
        Build dependency constraints for the given layers.
        
        Uses custom rules if provided, otherwise falls back to defaults
        for known layer names.
        """
        constraints = DependencyConstraints()
        
        # Normalize layer names for matching
        normalized_layers = {layer.lower(): layer for layer in layer_names}
        
        if custom_allowed:
            for dep in custom_allowed:
                if len(dep) == 2:
                    constraints.add_allowed(dep[0], dep[1])
        else:
            # Use defaults for recognized layer names
            for from_layer, to_layer in DEFAULT_ALLOWED_DEPS:
                actual_from = normalized_layers.get(from_layer)
                actual_to = normalized_layers.get(to_layer)
                if actual_from and actual_to:
                    constraints.add_allowed(actual_from, actual_to)
        
        if custom_forbidden:
            for dep in custom_forbidden:
                if len(dep) == 2:
                    constraints.add_forbidden(dep[0], dep[1])
        else:
            # Use defaults for recognized layer names
            for from_layer, to_layer in DEFAULT_FORBIDDEN_DEPS:
                actual_from = normalized_layers.get(from_layer)
                actual_to = normalized_layers.get(to_layer)
                if actual_from and actual_to:
                    constraints.add_forbidden(actual_from, actual_to)
        
        return constraints


def _test_canonical_paths():
    """Quick self-test."""
    import tempfile
    
    # Create a temp repo structure
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        
        # Create some files
        (repo / "src" / "domain" / "model.py").parent.mkdir(parents=True)
        (repo / "src" / "domain" / "model.py").write_text("# domain model")
        (repo / "src" / "domain" / "entities.py").write_text("# entities")
        
        (repo / "src" / "application" / "services.py").parent.mkdir(parents=True)
        (repo / "src" / "application" / "services.py").write_text("# services")
        
        config = {
            "oracle_config": {
                "layers": {
                    "domain": ["src/domain/**/*.py"],
                    "application": ["src/application/**/*.py"],
                }
            },
            "validated_source": "Test canonical structure",
        }
        
        oracle = CanonicalPathsOracle()
        result = oracle.extract(repo, config)
        
        print(f"Oracle source: {result.oracle_source}")
        print(f"Total files: {result.membership.total_files}")
        print(f"Components: {result.membership.components}")
        print(f"File mappings: {result.membership.file_to_component}")
        print(f"Allowed deps: {result.constraints.allowed}")
        print(f"Forbidden deps: {result.constraints.forbidden}")
        print(f"Summary: {result.summary()}")


if __name__ == "__main__":
    _test_canonical_paths()
