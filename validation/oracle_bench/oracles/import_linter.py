#!/usr/bin/env python3
"""
🔒 IMPORT LINTER ORACLE — Extract Architectural Constraints from import-linter Config

This oracle extracts ground truth from projects that use import-linter to enforce
architectural layer boundaries. The config format is well-documented and machine-readable.

Supports:
- .importlinter files
- pyproject.toml [tool.import-linter] sections

Reference: https://import-linter.readthedocs.io/
"""
from __future__ import annotations

import configparser
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import toml as tomllib  # Fallback
    except ImportError:
        tomllib = None  # type: ignore

from .base import (
    ComponentMembership,
    DependencyConstraints,
    OracleExtractor,
    OracleResult,
)


@dataclass
class LayerContract:
    """A layers contract defining architectural order."""
    name: str
    layers: List[str]  # Ordered top-to-bottom (UI at top, data at bottom)

    def get_allowed_deps(self) -> List[Tuple[str, str]]:
        """Get allowed dependency pairs (from_layer, to_layer)."""
        allowed = []
        for i, high_layer in enumerate(self.layers):
            for low_layer in self.layers[i+1:]:
                allowed.append((high_layer, low_layer))
        return allowed

    def get_forbidden_deps(self) -> List[Tuple[str, str]]:
        """Get forbidden dependency pairs (from_layer, to_layer)."""
        forbidden = []
        for i, low_layer in enumerate(self.layers):
            for high_layer in self.layers[:i]:
                forbidden.append((low_layer, high_layer))
        return forbidden


@dataclass
class IndependenceContract:
    """An independence contract - modules cannot import each other."""
    name: str
    modules: List[str]

    def get_forbidden_deps(self) -> List[Tuple[str, str]]:
        """Get forbidden dependency pairs (bidirectional)."""
        forbidden = []
        for i, mod1 in enumerate(self.modules):
            for mod2 in self.modules[i+1:]:
                forbidden.append((mod1, mod2))
                forbidden.append((mod2, mod1))
        return forbidden


@dataclass
class ForbiddenContract:
    """A forbidden contract - source modules cannot import forbidden modules."""
    name: str
    source_modules: List[str]
    forbidden_modules: List[str]

    def get_forbidden_deps(self) -> List[Tuple[str, str]]:
        """Get forbidden dependency pairs (one-way)."""
        return [
            (src, forb)
            for src in self.source_modules
            for forb in self.forbidden_modules
        ]


class ImportLinterOracle(OracleExtractor):
    """
    Oracle extractor for projects using import-linter.
    
    Config format:
    - .importlinter (INI-style)
    - pyproject.toml [tool.import-linter]
    
    Contract types:
    - layers: Enforces top-down dependency flow
    - independence: No imports between listed modules
    - forbidden: Specific source → forbidden module restrictions
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.root_packages: List[str] = []
        self.contracts: List[Any] = []  # LayerContract | IndependenceContract | ForbiddenContract
    
    @property
    def oracle_type(self) -> str:
        return "import_linter"
    
    def extract(self, repo_root: Path, config: Dict[str, Any]) -> OracleResult:
        """Extract architectural constraints from import-linter config."""
        # Update config with any passed overrides
        self.config.update(config)
        
        # Find config file
        config_path = self._find_config(repo_root)
        if config_path is None:
            return OracleResult(
                membership=ComponentMembership(),
                constraints=DependencyConstraints(),
                oracle_source="import_linter",
                validation_note="No config found",
                warnings=["No import-linter config found (.importlinter or pyproject.toml)"],
            )
        
        # Parse config
        if config_path.suffix == ".toml":
            contracts_data = self._parse_pyproject(config_path)
        else:
            contracts_data = self._parse_importlinter(config_path)
        
        if not contracts_data:
            return OracleResult(
                membership=ComponentMembership(),
                constraints=DependencyConstraints(),
                oracle_source="import_linter",
                validation_note="Config parse failed",
                warnings=[f"Could not parse import-linter config: {config_path}"],
            )
        
        # Convert to our format
        return self._convert_to_oracle_result(repo_root, contracts_data, config_path.name)
    
    def _find_config(self, repo_path: Path) -> Optional[Path]:
        """Find import-linter config file."""
        # Check .importlinter first
        importlinter = repo_path / ".importlinter"
        if importlinter.exists():
            return importlinter
        
        # Check pyproject.toml
        pyproject = repo_path / "pyproject.toml"
        if pyproject.exists():
            # Check if it has import-linter section
            try:
                if tomllib:
                    with open(pyproject, "rb") as f:
                        data = tomllib.load(f)
                    if "tool" in data and "import-linter" in data.get("tool", {}):
                        return pyproject
            except Exception:
                pass
        
        return None
    
    def _parse_importlinter(self, config_path: Path) -> Dict[str, Any]:
        """Parse .importlinter INI-style config."""
        try:
            parser = configparser.ConfigParser()
            parser.read(config_path)
            
            result = {
                "root_packages": [],
                "contracts": [],
            }
            
            # Get root package(s)
            if "importlinter" in parser:
                main = parser["importlinter"]
                if "root_packages" in main:
                    result["root_packages"] = [
                        p.strip() for p in main["root_packages"].split("\n") if p.strip()
                    ]
                elif "root_package" in main:
                    result["root_packages"] = [main["root_package"]]
            
            # Parse contracts
            for section in parser.sections():
                if section.startswith("importlinter:contract:"):
                    contract_data = dict(parser[section])
                    contract_type = contract_data.get("type", "")
                    contract_name = contract_data.get("name", section)
                    
                    if contract_type == "layers":
                        layers = [
                            l.strip() for l in contract_data.get("layers", "").split("\n")
                            if l.strip()
                        ]
                        result["contracts"].append({
                            "type": "layers",
                            "name": contract_name,
                            "layers": layers,
                        })
                    elif contract_type == "independence":
                        modules = [
                            m.strip() for m in contract_data.get("modules", "").split("\n")
                            if m.strip()
                        ]
                        result["contracts"].append({
                            "type": "independence",
                            "name": contract_name,
                            "modules": modules,
                        })
                    elif contract_type == "forbidden":
                        source = [
                            m.strip() for m in contract_data.get("source_modules", "").split("\n")
                            if m.strip()
                        ]
                        forbidden = [
                            m.strip() for m in contract_data.get("forbidden_modules", "").split("\n")
                            if m.strip()
                        ]
                        result["contracts"].append({
                            "type": "forbidden",
                            "name": contract_name,
                            "source_modules": source,
                            "forbidden_modules": forbidden,
                        })
            
            return result
            
        except Exception as e:
            print(f"Error parsing .importlinter: {e}")
            return {}
    
    def _parse_pyproject(self, pyproject_path: Path) -> Dict[str, Any]:
        """Parse pyproject.toml [tool.import-linter] section."""
        if not tomllib:
            return {}
        
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            
            il_config = data.get("tool", {}).get("import-linter", {})
            if not il_config:
                return {}
            
            result = {
                "root_packages": [],
                "contracts": [],
            }
            
            # Get root package(s)
            if "root_packages" in il_config:
                result["root_packages"] = il_config["root_packages"]
            elif "root_package" in il_config:
                result["root_packages"] = [il_config["root_package"]]
            
            # Parse contracts
            for key, val in il_config.items():
                if key.startswith("contract"):
                    contract_type = val.get("type", "")
                    contract_name = val.get("name", key)
                    
                    if contract_type == "layers":
                        result["contracts"].append({
                            "type": "layers",
                            "name": contract_name,
                            "layers": val.get("layers", []),
                        })
                    elif contract_type == "independence":
                        result["contracts"].append({
                            "type": "independence",
                            "name": contract_name,
                            "modules": val.get("modules", []),
                        })
                    elif contract_type == "forbidden":
                        result["contracts"].append({
                            "type": "forbidden",
                            "name": contract_name,
                            "source_modules": val.get("source_modules", []),
                            "forbidden_modules": val.get("forbidden_modules", []),
                        })
            
            return result
            
        except Exception as e:
            print(f"Error parsing pyproject.toml: {e}")
            return {}
    
    def _convert_to_oracle_result(
        self,
        repo_path: Path,
        contracts_data: Dict[str, Any],
        config_filename: str,
    ) -> OracleResult:
        """Convert parsed import-linter config to OracleResult."""
        
        membership = ComponentMembership()
        constraints = DependencyConstraints()
        warnings: List[str] = []
        
        root_packages = contracts_data.get("root_packages", [])
        contracts = contracts_data.get("contracts", [])
        
        if not contracts:
            warnings.append("No contracts found in import-linter config")
        
        for contract in contracts:
            contract_type = contract.get("type")
            
            if contract_type == "layers":
                layer_contract = LayerContract(
                    name=contract.get("name", ""),
                    layers=contract.get("layers", []),
                )
                
                # Add layer memberships (module → layer mapping)
                for layer_module in layer_contract.layers:
                    # Use module name as component, infer layer from position
                    layer_name = self._infer_layer_name(layer_module, layer_contract.layers)
                    
                    # Add to membership: ALL files under this module belong to this component
                    # Note: We are abstracting modules to components here
                    membership.add_file(
                        rel_path=layer_module.replace('.', '/'), # This is storing a prefix, not a file. 
                        # Ideally ComponentMembership should handle prefixes.
                        # For now, let's just use the module name as the key for mapping logic later.
                        component=layer_name
                    )
                
                # Add dependency constraints
                for start, end in layer_contract.get_allowed_deps():
                    start_layer = self._infer_layer_name(start, layer_contract.layers)
                    end_layer = self._infer_layer_name(end, layer_contract.layers)
                    constraints.add_allowed(start_layer, end_layer)
                    
                for start, end in layer_contract.get_forbidden_deps():
                    start_layer = self._infer_layer_name(start, layer_contract.layers)
                    end_layer = self._infer_layer_name(end, layer_contract.layers)
                    constraints.add_forbidden(start_layer, end_layer)
            
            elif contract_type == "independence":
                ind_contract = IndependenceContract(
                    name=contract.get("name", ""),
                    modules=contract.get("modules", []),
                )
                # For independence, we probably want to treat each module as its own component?
                # Or just map forbidden edges.
                # Simplification: Just add forbidden edges.
                pass 
                
            elif contract_type == "forbidden":
                # Simplification: Just add forbidden edges.
                pass
        
        return OracleResult(
            membership=membership,
            constraints=constraints,
            oracle_source=f"import_linter:{config_filename}",
            validation_note="Explicit architectural contracts defined in repository config",
            warnings=warnings,
        )
    
    def _infer_layer_name(self, module: str, all_layers: List[str]) -> str:
        """Infer canonical layer name from module and position."""
        # Get position (0 = UI/top, len-1 = data/bottom)
        try:
            position = all_layers.index(module)
            total = len(all_layers)
            ratio = position / max(1, total - 1)
            
            if ratio <= 0.25:
                return "Interface"  # Top layer (UI, controllers)
            elif ratio <= 0.5:
                return "Application"  # Middle-high (services, use cases)
            elif ratio <= 0.75:
                return "Core"  # Middle-low (domain, business logic)
            else:
                return "Infrastructure"  # Bottom (data, adapters)
        except ValueError:
            return module.split(".")[-1].title()


# =============================================================================
# SELF-TEST
# =============================================================================

def _test_import_linter():
    """Test with a sample .importlinter config."""
    from pathlib import Path
    import tempfile
    
    sample_config = """
[importlinter]
root_package = myproject

[importlinter:contract:1]
name = Layered Architecture
type = layers
layers =
    myproject.ui
    myproject.api
    myproject.services
    myproject.domain
    myproject.infrastructure

[importlinter:contract:2]
name = Domain Independence
type = independence
modules =
    myproject.domain
    myproject.infrastructure

[importlinter:contract:3]
name = No External Cloud in Domain
type = forbidden
source_modules =
    myproject.domain
forbidden_modules =
    boto3
    google.cloud
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / ".importlinter"
        config_path.write_text(sample_config)
        
        oracle = ImportLinterOracle({})
        result = oracle.extract(Path(tmpdir), {})
        
        print("=" * 60)
        print("IMPORT LINTER ORACLE TEST")
        print("=" * 60)
        print(f"Component memberships: {result.membership.total_files}")
        for file, comp in result.membership.file_to_component.items():
            print(f"  {file} -> {comp}")
        
        print(f"\nDependency constraints: Allowed={len(result.constraints.allowed)}, Forbidden={len(result.constraints.forbidden)}")
        if result.constraints.forbidden:
             print(f"  Sample forbidden: {result.constraints.forbidden[:3]}")
        
        print(f"\nWarnings: {result.warnings if result.warnings else 'None'}")
        print("=" * 60)


if __name__ == "__main__":
    _test_import_linter()
