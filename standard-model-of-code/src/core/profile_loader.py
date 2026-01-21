#!/usr/bin/env python3
"""
Profile Loader for Constraint Field

Loads architecture and dimension semantic profiles from YAML.
Profiles determine how constraints are interpreted.

Usage:
    from profile_loader import ProfileLoader, get_default_profiles

    loader = ProfileLoader()
    arch_profile = loader.load_architecture_profile('clean_onion')
    dim_profile = loader.load_dimension_profile('oop_conventional')
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class ArchitectureProfile:
    """Architecture profile defining layer hierarchy and dependencies."""
    id: str
    name: str
    version: str
    layer_hierarchy: List[str]
    allowed_dependencies: Dict[str, List[str]]
    forbidden_dependencies: List[Dict[str, Any]]
    role_layer_mapping: Dict[str, Any] = field(default_factory=dict)

    def is_dependency_allowed(self, source_layer: str, target_layer: str) -> bool:
        """Check if a dependency from source to target layer is allowed."""
        allowed = self.allowed_dependencies.get(source_layer, [])
        return target_layer in allowed

    def get_forbidden_reason(self, source_layer: str, target_layer: str) -> Optional[str]:
        """Get the reason why a dependency is forbidden, if any."""
        for rule in self.forbidden_dependencies:
            if rule.get('source') == source_layer and rule.get('target') == target_layer:
                return rule.get('reason', 'Forbidden by architecture profile')
        return None

    def get_expected_layer(self, role: str) -> Optional[List[str]]:
        """Get expected layer(s) for a role."""
        mapping = self.role_layer_mapping.get(role)
        if mapping is None:
            return None
        if isinstance(mapping, list):
            return mapping
        return [mapping]


@dataclass
class DimensionProfile:
    """Dimension semantic profile defining purity and lifecycle semantics."""
    id: str
    name: str
    version: str
    purity: Dict[str, Dict[str, Any]]
    lifecycle: Dict[str, Dict[str, Any]]
    constraints: List[Dict[str, Any]] = field(default_factory=list)

    def get_purity_semantics(self, purity_value: str) -> Dict[str, Any]:
        """Get semantics for a purity value."""
        return self.purity.get(purity_value, {})

    def get_lifecycle_semantics(self, lifecycle_value: str) -> Dict[str, Any]:
        """Get semantics for a lifecycle value."""
        return self.lifecycle.get(lifecycle_value, {})

    def is_mutation_allowed(self, lifecycle: str) -> bool:
        """Check if mutation is allowed for a lifecycle value."""
        semantics = self.get_lifecycle_semantics(lifecycle)
        if lifecycle == 'Immutable':
            return False
        return True


class ProfileLoader:
    """Loads and caches profile definitions from YAML files."""

    def __init__(self, schema_dir: Optional[Path] = None):
        if schema_dir is None:
            # Default to schema/ relative to this file's location
            self.schema_dir = Path(__file__).parent.parent.parent / 'schema'
        else:
            self.schema_dir = Path(schema_dir)

        self._arch_cache: Dict[str, ArchitectureProfile] = {}
        self._dim_cache: Dict[str, DimensionProfile] = {}

    def load_architecture_profile(self, profile_id: str) -> ArchitectureProfile:
        """Load an architecture profile by ID."""
        if profile_id in self._arch_cache:
            return self._arch_cache[profile_id]

        profile_path = self.schema_dir / 'profiles' / 'architecture' / f'{profile_id}.yaml'
        if not profile_path.exists():
            raise FileNotFoundError(f"Architecture profile not found: {profile_path}")

        with open(profile_path) as f:
            data = yaml.safe_load(f)

        profile = ArchitectureProfile(
            id=data.get('id', profile_id),
            name=data.get('name', profile_id),
            version=data.get('version', '1.0.0'),
            layer_hierarchy=data.get('layer_hierarchy', []),
            allowed_dependencies=data.get('allowed_dependencies', {}),
            forbidden_dependencies=data.get('forbidden_dependencies', []),
            role_layer_mapping=data.get('role_layer_mapping', {}),
        )

        self._arch_cache[profile_id] = profile
        return profile

    def load_dimension_profile(self, profile_id: str) -> DimensionProfile:
        """Load a dimension semantic profile by ID."""
        if profile_id in self._dim_cache:
            return self._dim_cache[profile_id]

        profile_path = self.schema_dir / 'profiles' / 'dimensions' / f'{profile_id}.yaml'
        if not profile_path.exists():
            raise FileNotFoundError(f"Dimension profile not found: {profile_path}")

        with open(profile_path) as f:
            data = yaml.safe_load(f)

        profile = DimensionProfile(
            id=data.get('id', profile_id),
            name=data.get('name', profile_id),
            version=data.get('version', '1.0.0'),
            purity=data.get('purity', {}),
            lifecycle=data.get('lifecycle', {}),
            constraints=data.get('constraints', []),
        )

        self._dim_cache[profile_id] = profile
        return profile

    def list_architecture_profiles(self) -> List[str]:
        """List available architecture profile IDs."""
        arch_dir = self.schema_dir / 'profiles' / 'architecture'
        if not arch_dir.exists():
            return []
        return [p.stem for p in arch_dir.glob('*.yaml')]

    def list_dimension_profiles(self) -> List[str]:
        """List available dimension profile IDs."""
        dim_dir = self.schema_dir / 'profiles' / 'dimensions'
        if not dim_dir.exists():
            return []
        return [p.stem for p in dim_dir.glob('*.yaml')]


# Singleton loader
_loader: Optional[ProfileLoader] = None


def get_profile_loader() -> ProfileLoader:
    """Get the singleton ProfileLoader instance."""
    global _loader
    if _loader is None:
        _loader = ProfileLoader()
    return _loader


def get_default_profiles() -> tuple:
    """Get default architecture and dimension profiles."""
    loader = get_profile_loader()
    arch = loader.load_architecture_profile('classic_layered')
    dim = loader.load_dimension_profile('oop_conventional')
    return arch, dim


if __name__ == '__main__':
    # Test loading
    loader = ProfileLoader()

    print("Available architecture profiles:", loader.list_architecture_profiles())
    print("Available dimension profiles:", loader.list_dimension_profiles())

    arch = loader.load_architecture_profile('clean_onion')
    print(f"\nLoaded: {arch.name}")
    print(f"  Layer hierarchy: {arch.layer_hierarchy}")
    print(f"  Forbidden deps: {len(arch.forbidden_dependencies)}")

    dim = loader.load_dimension_profile('fp_strict')
    print(f"\nLoaded: {dim.name}")
    print(f"  Purity values: {list(dim.purity.keys())}")
    print(f"  Lifecycle values: {list(dim.lifecycle.keys())}")
