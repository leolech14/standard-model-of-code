"""
Behavioral Dimensions
=====================

Detectors for D4 (BOUNDARY), D5 (STATE), D6 (EFFECT).
These dimensions define the behavioral characteristics of a code atom.
"""

import ast
from typing import Dict, Any


class BehavioralDimensionDetector:
    """Detects behavioral dimensions D4, D5, D6."""

    def __init__(self):
        self.boundary_cache: Dict[str, str] = {}
        self.state_cache: Dict[str, str] = {}
        self.purity_cache: Dict[str, str] = {}

    def detect_d4_boundary(self, node: Dict[str, Any]) -> str:
        """
        D4: BOUNDARY - Does this node cross architectural boundaries?

        Values:
        - Internal: Stays within one layer
        - Input: Receives data from outside (API, user input, external service)
        - Output: Sends data outside (DB write, API call, file write)
        - I-O: Both input and output (bidirectional boundary crossing)
        """
        node_id = node.get("id", "")

        # Check cached boundary map
        if node_id in self.boundary_cache:
            return self.boundary_cache[node_id]

        # Analyze by name patterns
        name = node.get("name", "").lower()

        # Input patterns
        input_patterns = ["fetch", "get", "load", "read", "receive", "handle", "listen", "accept"]
        has_input = any(p in name for p in input_patterns)

        # Output patterns
        output_patterns = ["save", "store", "write", "send", "publish", "emit", "persist", "create", "update", "delete"]
        has_output = any(p in name for p in output_patterns)

        # Determine boundary type
        if has_input and has_output:
            return "I-O"
        elif has_input:
            return "Input"
        elif has_output:
            return "Output"

        # Check role for hints
        return self._infer_boundary_from_role(node.get("role", ""))

    def _infer_boundary_from_role(self, role: str) -> str:
        """Infer boundary type from role."""
        if role in ["Controller", "Handler", "Gateway", "Adapter"]:
            return "I-O"  # These typically bridge boundaries
        elif role in ["Repository", "Client"]:
            return "I-O"  # Read and write external data
        elif role in ["Query", "Finder", "Loader"]:
            return "Input"
        elif role in ["Command", "Creator", "Destroyer"]:
            return "Output"
        return "Internal"

    def detect_d5_state(self, node: Dict[str, Any]) -> str:
        """
        D5: STATE - Does this node maintain internal state?

        Values:
        - Stateful: Has mutable instance variables, modifies self
        - Stateless: Pure logic, no internal state
        """
        node_id = node.get("id", "")

        # Check cache
        if node_id in self.state_cache:
            return self.state_cache[node_id]

        # Analyze source code if available
        body_source = node.get("body_source", "")
        if body_source:
            result = self._analyze_statefulness(body_source, node.get("kind", ""))
            self.state_cache[node_id] = result
            return result

        # Fallback: infer from role/kind
        return self._infer_state_from_context(node)

    def _analyze_statefulness(self, source: str, kind: str) -> str:
        """Analyze source code to detect statefulness."""
        try:
            tree = ast.parse(source)
        except:
            return "Unknown"

        # For classes: check for __init__ with instance variables
        if kind == "class":
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                    # Has instance variable assignments
                    for stmt in ast.walk(node):
                        if isinstance(stmt, ast.Attribute) and isinstance(stmt.value, ast.Name) and stmt.value.id == "self":
                            return "Stateful"
                    return "Stateless"
            return "Stateful"  # Class without __init__ likely has state elsewhere

        # For functions: check for self mutations
        for node in ast.walk(tree):
            # self.x = ... (mutation)
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                        return "Stateful"

            # global/nonlocal (external state)
            if isinstance(node, (ast.Global, ast.Nonlocal)):
                return "Stateful"

        return "Stateless"

    def _infer_state_from_context(self, node: Dict[str, Any]) -> str:
        """Infer statefulness from role and kind."""
        role = node.get("role", "Unknown")
        kind = node.get("kind", "")

        # Classes are typically stateful
        if kind == "class":
            return "Stateful"

        # Stateful roles
        if role in ["Entity", "ValueObject", "AggregateRoot", "Repository", "Service", "Manager", "Cache"]:
            return "Stateful"

        # Stateless roles
        if role in ["Query", "Utility", "Formatter", "Validator", "Mapper", "Factory"]:
            return "Stateless"

        return "Unknown"

    def detect_d6_effect(self, node: Dict[str, Any]) -> str:
        """
        D6: EFFECT - What side effects does this node have?

        Values:
        - Pure: No side effects, deterministic
        - Read: Reads external state (DB query, file read, API GET)
        - Write: Modifies external state (DB write, file write, API POST)
        - ReadModify: Both reads and writes
        """
        node_id = node.get("id", "")

        # Check cached purity map
        if node_id in self.purity_cache:
            return self.purity_cache[node_id]

        # Analyze by name patterns
        name = node.get("name", "").lower()

        # Read patterns
        read_patterns = ["get", "fetch", "find", "load", "read", "query", "search", "list"]
        has_read = any(p in name for p in read_patterns)

        # Write patterns
        write_patterns = ["set", "save", "store", "write", "create", "update", "delete", "insert", "remove"]
        has_write = any(p in name for p in write_patterns)

        # Determine effect type
        if has_read and has_write:
            return "ReadModify"
        elif has_write:
            return "Write"
        elif has_read:
            return "Read"

        # Infer from role
        role = node.get("role", "")
        if role in ["Query", "Finder", "Loader", "Getter"]:
            return "Read"
        elif role in ["Command", "Creator", "Mutator", "Destroyer"]:
            return "Write"
        elif role in ["Repository", "Service"]:
            return "ReadModify"
        elif role in ["Utility", "Formatter", "Validator", "Mapper"]:
            return "Pure"

        # Check for pure function indicators
        if self._looks_pure(node):
            return "Pure"

        return "Unknown"

    def _looks_pure(self, node: Dict[str, Any]) -> bool:
        """Heuristic check if function looks pure."""
        name = node.get("name", "").lower()

        # Pure function name patterns
        pure_patterns = ["calculate", "compute", "format", "parse", "transform", "convert", "validate", "is", "has", "to"]
        if any(p in name for p in pure_patterns):
            return True

        # No parameters = likely not pure (unless constant)
        if not node.get("params") and node.get("kind") == "function":
            return False

        return False

    def load_boundary_results(self, boundary_map: Dict[str, str]):
        """Load results from boundary_detector.py"""
        self.boundary_cache = boundary_map

    def load_purity_results(self, purity_map: Dict[str, str]):
        """Load results from purity_detector.py"""
        self.purity_cache = purity_map
