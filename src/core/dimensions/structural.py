"""
Structural Dimensions
=====================

Detectors for D1 (WHAT), D2 (LAYER), D3 (ROLE).
These dimensions define the structural identity of a code atom.
"""

from typing import Dict, Any


class StructuralDimensionDetector:
    """Detects structural dimensions D1, D2, D3."""

    # Atom type mapping
    ATOM_MAP = {
        "function": "FunctionDef",
        "method": "MethodDef",
        "class": "ClassDef",
        "module": "ModuleDef",
        "lambda": "LambdaExpr",
        "async_function": "AsyncFunctionDef",
        "async_method": "AsyncMethodDef",
    }

    def detect_d1_what(self, node: Dict[str, Any]) -> str:
        """
        D1: WHAT - The structural atom type.

        This is the AST node kind mapped to our 200+ atom taxonomy.
        Open world: new atoms can be added as discovered.

        Examples:
        - FunctionDef, ClassDef, IfStatement, ForLoop
        - Lambda, Comprehension, Decorator
        - ImportStatement, AssignmentExpression
        """
        # Use the raw AST kind if available
        if "ast_kind" in node:
            return node["ast_kind"]

        # Fallback to symbol kind
        kind = node.get("kind", "Unknown")
        return self.ATOM_MAP.get(kind, kind.title())

    def detect_d2_layer(self, node: Dict[str, Any]) -> str:
        """
        D2: LAYER - Architectural layer position.

        Values: Interface, Application, Core, Infrastructure, Test, Unknown
        """
        # Check if already classified
        if layer := node.get("layer"):
            return self._normalize_layer(layer)

        # Infer from file path
        file_path = node.get("file_path", "").lower()

        # Test layer (highest priority)
        if any(x in file_path for x in ["/test/", "/tests/", "test_", "_test.", "spec_"]):
            return "Test"

        # Interface/Presentation layer
        if any(x in file_path for x in ["/api/", "/controllers/", "/routes/", "/handlers/", "/views/"]):
            return "Interface"

        # Application layer
        if any(x in file_path for x in ["/application/", "/usecases/", "/services/", "/commands/", "/queries/"]):
            return "Application"

        # Core/Domain layer
        if any(x in file_path for x in ["/domain/", "/core/", "/entities/", "/models/", "/aggregates/"]):
            return "Core"

        # Infrastructure layer
        if any(x in file_path for x in ["/infrastructure/", "/infra/", "/adapters/", "/repositories/", "/gateways/"]):
            return "Infrastructure"

        # Fallback: infer from role
        return self._infer_layer_from_role(node.get("role", "Unknown"))

    def _normalize_layer(self, layer: str) -> str:
        """Normalize layer names to standard set."""
        layer_lower = layer.lower()

        if layer_lower in ["interface", "presentation", "ui"]:
            return "Interface"
        elif layer_lower in ["application", "app", "usecase"]:
            return "Application"
        elif layer_lower in ["core", "domain", "business"]:
            return "Core"
        elif layer_lower in ["infrastructure", "infra", "data"]:
            return "Infrastructure"
        elif layer_lower in ["test", "testing", "spec"]:
            return "Test"
        else:
            return "Unknown"

    def _infer_layer_from_role(self, role: str) -> str:
        """Infer layer from role when path inference fails."""
        if role in ["Controller", "Handler", "Route"]:
            return "Interface"
        elif role in ["UseCase", "ApplicationService", "Command", "Query"]:
            return "Application"
        elif role in ["Entity", "ValueObject", "AggregateRoot", "DomainService"]:
            return "Core"
        elif role in ["Repository", "Gateway", "Adapter", "Client"]:
            return "Infrastructure"
        elif role == "Test":
            return "Test"
        return "Unknown"

    def detect_d3_role(self, node: Dict[str, Any]) -> str:
        """
        D3: ROLE - Semantic purpose (the 33 canonical roles).

        This is already detected by particle_classifier.py.
        Just extract it from the node.

        Values:
        - Query, Command, Creator, Destroyer, Mutator
        - Repository, Service, Controller, Factory
        - Entity, ValueObject, DTO
        - Handler, Validator, Mapper
        - etc. (33 total)
        """
        return node.get("role", "Unknown")
