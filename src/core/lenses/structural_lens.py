"""
Structural Lens
===============

Interrogates code atoms for structural properties:
- R1: IDENTITY - What is it called?
- R2: ONTOLOGY - What exists here?
- R4: COMPOSITION - How is it structured?
"""

from typing import Dict, Any, List
from pathlib import Path


class StructuralLens:
    """
    Reveals structural properties of code atoms.

    Handles identity, ontology, and composition questions.
    """

    # ==================== R1: IDENTITY ====================

    def lens_r1_identity(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        R1: IDENTITY - What is it called?

        Reveals: Name, path, signature, unique identifiers
        """
        name = node.get("name", "Unknown")
        file_path = node.get("file_path", "")
        start_line = node.get("start_line", 0)
        signature = node.get("signature", "")

        qualified_name = f"{Path(file_path).stem}:{start_line}:{name}" if file_path else name
        module_path = self._extract_module_path(file_path)
        semantic_id = node.get("id", f"{module_path}.{name}")

        return {
            "name": name,
            "qualified_name": qualified_name,
            "file_path": file_path,
            "module_path": module_path,
            "line_number": start_line,
            "signature": signature,
            "semantic_id": semantic_id,
            "unique_reference": f"{file_path}:{start_line}" if file_path else name,
        }

    def _extract_module_path(self, file_path: str) -> str:
        """Convert file path to Python module path."""
        if not file_path:
            return ""

        path = Path(file_path)
        parts = path.parts

        module_parts = []
        capture = False
        for part in parts:
            if part in ["src", "lib", "package", "app"]:
                capture = True
                continue
            if capture and part != "__pycache__":
                module_parts.append(part)

        if not module_parts:
            module_parts = list(parts)

        if module_parts and module_parts[-1].endswith('.py'):
            module_parts = list(module_parts[:-1]) + [module_parts[-1][:-3]]

        return ".".join(module_parts)

    # ==================== R2: ONTOLOGY ====================

    def lens_r2_ontology(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        R2: ONTOLOGY - What exists here?

        Reveals: Entity type, properties, attributes
        """
        kind = node.get("kind", "unknown")
        params = node.get("params", [])
        return_type = node.get("return_type", "")
        decorators = node.get("decorators", [])
        base_classes = node.get("base_classes", [])
        complexity = node.get("complexity", 0)
        loc = node.get("lines_of_code", 0)

        entity_category = self._categorize_entity(kind)

        properties = {
            "is_async": "async" in kind.lower(),
            "is_static": "static" in node.get("modifiers", []),
            "is_private": node.get("name", "").startswith("_"),
            "has_decorators": len(decorators) > 0,
            "has_inheritance": len(base_classes) > 0,
        }

        return {
            "entity_type": kind,
            "entity_category": entity_category,
            "parameter_count": len(params),
            "parameters": params,
            "return_type": return_type,
            "decorators": decorators,
            "base_classes": base_classes,
            "complexity": complexity,
            "lines_of_code": loc,
            "properties": properties,
        }

    def _categorize_entity(self, kind: str) -> str:
        """Categorize entity into high-level groups."""
        kind_lower = kind.lower()

        if "class" in kind_lower:
            return "container"
        elif "function" in kind_lower or "method" in kind_lower:
            return "callable"
        elif "module" in kind_lower:
            return "namespace"
        elif "variable" in kind_lower or "constant" in kind_lower:
            return "data"
        else:
            return "other"

    # ==================== R4: COMPOSITION ====================

    def lens_r4_composition(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        R4: COMPOSITION - How is it structured?

        Reveals: Parts, container, nesting, internal structure
        """
        parent = node.get("parent", "")
        children = node.get("children", [])
        body_source = node.get("body_source", "")

        nesting_depth = self._calculate_nesting_depth(
            node.get("file_path", ""),
            node.get("start_line", 0)
        )
        internal_counts = self._count_internal_elements(body_source)

        return {
            "parent": parent,
            "children": children,
            "child_count": len(children),
            "nesting_depth": nesting_depth,
            "has_body": len(body_source) > 0,
            "internal_functions": internal_counts.get("functions", 0),
            "internal_classes": internal_counts.get("classes", 0),
            "internal_statements": internal_counts.get("statements", 0),
        }

    def _calculate_nesting_depth(self, file_path: str, line: int) -> int:
        """Calculate how deeply nested this node is."""
        return 0  # Would need full AST context

    def _count_internal_elements(self, body: str) -> Dict[str, int]:
        """Count internal functions, classes, etc."""
        if not body:
            return {"functions": 0, "classes": 0, "statements": 0}

        return {
            "functions": body.count("def "),
            "classes": body.count("class "),
            "statements": len([
                l for l in body.split("\n")
                if l.strip() and not l.strip().startswith("#")
            ]),
        }

    # ==================== COMBINED ====================

    def interrogate(self, node: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Interrogate a node through all structural lenses.

        Returns dict with R1, R2, R4 results.
        """
        return {
            "R1_IDENTITY": self.lens_r1_identity(node),
            "R2_ONTOLOGY": self.lens_r2_ontology(node),
            "R4_COMPOSITION": self.lens_r4_composition(node),
        }
