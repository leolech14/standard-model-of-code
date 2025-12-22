#!/usr/bin/env python3
"""
Base classes for architecture oracle extractors.

An oracle extracts "ground truth" architecture information from a repository's
own conformance tools (Import Linter, ArchUnit, Nx, etc.) or canonical structure.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


@dataclass
class ComponentMembership:
    """
    Ground truth: which files/symbols belong to which architectural components.
    
    This represents the oracle's view of "what layer/component does each file belong to?"
    Symbols within a file inherit their file's component membership.
    """
    # File path (relative to repo root) -> component name
    file_to_component: Dict[str, str] = field(default_factory=dict)
    
    # Component name -> set of file paths
    component_to_files: Dict[str, Set[str]] = field(default_factory=dict)
    
    def add_file(self, rel_path: str, component: str) -> None:
        """Add a file to component mapping."""
        self.file_to_component[rel_path] = component
        if component not in self.component_to_files:
            self.component_to_files[component] = set()
        self.component_to_files[component].add(rel_path)
    
    def get_component(self, rel_path: str) -> str | None:
        """Get the component a file belongs to, or None if unknown."""
        return self.file_to_component.get(rel_path)
    
    @property
    def total_files(self) -> int:
        return len(self.file_to_component)
    
    @property
    def components(self) -> List[str]:
        return sorted(self.component_to_files.keys())


@dataclass
class DependencyConstraints:
    """
    Ground truth: which component-to-component dependencies are allowed/forbidden.
    
    This represents the oracle's view of "what import directions are valid?"
    """
    # List of (from_component, to_component) that ARE allowed
    allowed: List[Tuple[str, str]] = field(default_factory=list)
    
    # List of (from_component, to_component) that are FORBIDDEN
    forbidden: List[Tuple[str, str]] = field(default_factory=list)
    
    def is_allowed(self, from_comp: str, to_comp: str) -> bool | None:
        """
        Check if a dependency is allowed.
        Returns True if explicitly allowed, False if explicitly forbidden, None if not specified.
        """
        if (from_comp, to_comp) in self.forbidden:
            return False
        if (from_comp, to_comp) in self.allowed:
            return True
        return None
    
    def add_allowed(self, from_comp: str, to_comp: str) -> None:
        if (from_comp, to_comp) not in self.allowed:
            self.allowed.append((from_comp, to_comp))
    
    def add_forbidden(self, from_comp: str, to_comp: str) -> None:
        if (from_comp, to_comp) not in self.forbidden:
            self.forbidden.append((from_comp, to_comp))


@dataclass
class OracleResult:
    """
    Complete ground truth extracted from an oracle.
    """
    # Component membership (files -> components)
    membership: ComponentMembership
    
    # Dependency constraints (allowed/forbidden edges)
    constraints: DependencyConstraints
    
    # Human-readable description of oracle source
    # e.g., "import_linter:.importlinter" or "canonical_paths:src/allocation/**"
    oracle_source: str
    
    # Why this oracle is trusted (for paper citations)
    # e.g., "Import Linter contracts enforced in CI"
    validation_note: str
    
    # Any warnings or notes from extraction
    warnings: List[str] = field(default_factory=list)
    
    def summary(self) -> Dict[str, Any]:
        """Return a summary dict for reporting."""
        return {
            "oracle_source": self.oracle_source,
            "validation_note": self.validation_note,
            "total_files": self.membership.total_files,
            "components": self.membership.components,
            "allowed_deps": len(self.constraints.allowed),
            "forbidden_deps": len(self.constraints.forbidden),
            "warnings": self.warnings,
        }


class OracleExtractor(ABC):
    """
    Abstract base class for oracle extractors.
    
    Each oracle type (Import Linter, ArchUnit, Nx, canonical paths, etc.)
    implements this interface to extract ground truth from its config format.
    """
    
    @property
    @abstractmethod
    def oracle_type(self) -> str:
        """Return the oracle type identifier (e.g., 'import_linter', 'canonical_paths')."""
        pass
    
    @abstractmethod
    def extract(self, repo_root: Path, config: Dict[str, Any]) -> OracleResult:
        """
        Extract ground truth from the repository.
        
        Args:
            repo_root: Path to the repository root
            config: Oracle-specific configuration from manifest.yaml
            
        Returns:
            OracleResult with membership and constraints
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate oracle-specific config. Returns list of error messages (empty if valid).
        Subclasses can override to add validation.
        """
        return []
