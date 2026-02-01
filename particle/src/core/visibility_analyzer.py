"""
Visibility Analyzer for Wave-Particle Symmetry.
Determines public/private/protected visibility of Python symbols.

This module implements Python visibility conventions:
1. If __all__ is defined, ONLY those names are public
2. __dunder__ names = special (magic methods)
3. __name (double underscore prefix) = private (name-mangled)
4. _name (single underscore prefix) = protected
5. Default (no prefix) = public
"""
import ast
import warnings
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from enum import Enum


class Visibility(Enum):
    """Symbol visibility levels following Python conventions."""
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    SPECIAL = "special"  # dunder methods


@dataclass
class SymbolVisibility:
    """Metadata for a single symbol's visibility."""
    name: str
    qualified_name: str
    visibility: Visibility
    line_number: int
    is_in_all: bool = False


class VisibilityAnalyzer:
    """Analyzes Python source code to determine symbol visibility.

    Usage:
        analyzer = VisibilityAnalyzer(source_code, "module.name")
        visibility_map = analyzer.analyze()
        public_api = analyzer.get_public_exports()
    """

    def __init__(self, source_code: str, module_path: str = ""):
        """Initialize the visibility analyzer.

        Args:
            source_code: Python source code to analyze
            module_path: Optional module path for qualified names
        """
        self.source_code = source_code
        self.module_path = module_path
        self.tree: Optional[ast.AST] = None
        self._all_declaration: Optional[Set[str]] = None
        self._symbols: Dict[str, SymbolVisibility] = {}

        # Parse AST with error handling
        try:
            self.tree = ast.parse(source_code)
            self._all_declaration = self._extract_all_declaration()
        except SyntaxError as e:
            warnings.warn(f"Failed to parse source code: {e}")
            self.tree = None
        except UnicodeDecodeError as e:
            warnings.warn(f"Encoding error in source code: {e}")
            self.tree = None

    def analyze(self) -> Dict[str, SymbolVisibility]:
        """Analyze all symbols and return visibility mapping.

        Returns:
            Dict mapping symbol qualified names to SymbolVisibility objects.
            Returns empty dict if source is unparseable.
        """
        if self.tree is None:
            return {}

        self._symbols = {}
        self._visit_node(self.tree, parent_class=None)
        return self._symbols

    def get_public_exports(self) -> List[str]:
        """Get list of public API symbols.

        Returns:
            List of symbol names that are part of the public API.
        """
        if not self._symbols:
            self.analyze()

        return [
            symbol.name
            for symbol in self._symbols.values()
            if symbol.visibility == Visibility.PUBLIC
        ]

    def _extract_all_declaration(self) -> Optional[Set[str]]:
        """Extract __all__ declaration from module if present.

        Returns:
            Set of names in __all__, or None if not defined.
        """
        if self.tree is None:
            return None

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        # Extract list/tuple of strings
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            names = set()
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    names.add(elt.value)
                                # Python 3.7 compatibility (ast.Str removed in 3.12+)
                                elif hasattr(ast, 'Str') and isinstance(elt, getattr(ast, 'Str', type(None))):
                                    names.add(getattr(elt, 's', ''))
                            return names
        return None

    def _determine_visibility(self, name: str, is_in_all: bool) -> Visibility:
        """Apply visibility rules to determine symbol visibility.

        Args:
            name: Symbol name
            is_in_all: Whether symbol is listed in __all__

        Returns:
            Visibility level
        """
        # Rule 1: __all__ takes precedence
        if self._all_declaration is not None:
            if is_in_all:
                return Visibility.PUBLIC
            else:
                # Not in __all__ means explicitly not exported
                return Visibility.PRIVATE

        # Rule 2: __dunder__ = special
        if name.startswith("__") and name.endswith("__"):
            return Visibility.SPECIAL

        # Rule 3: __name = private (name mangling)
        if name.startswith("__") and not name.endswith("__"):
            return Visibility.PRIVATE

        # Rule 4: _name = protected
        if name.startswith("_") and not name.startswith("__"):
            return Visibility.PROTECTED

        # Rule 5: Default = public
        return Visibility.PUBLIC

    def _visit_node(self, node: ast.AST, parent_class: Optional[str] = None):
        """Recursively visit AST nodes to extract symbol definitions.

        Args:
            node: AST node to visit
            parent_class: Name of parent class if inside a class definition
        """
        for child in ast.iter_child_nodes(node):
            # Function definitions
            if isinstance(child, ast.FunctionDef) or isinstance(child, ast.AsyncFunctionDef):
                name = child.name
                qualified_name = f"{parent_class}.{name}" if parent_class else name
                is_in_all = self._all_declaration is not None and name in self._all_declaration

                self._symbols[qualified_name] = SymbolVisibility(
                    name=name,
                    qualified_name=qualified_name,
                    visibility=self._determine_visibility(name, is_in_all),
                    line_number=child.lineno,
                    is_in_all=is_in_all
                )

            # Class definitions
            elif isinstance(child, ast.ClassDef):
                name = child.name
                qualified_name = f"{parent_class}.{name}" if parent_class else name
                is_in_all = self._all_declaration is not None and name in self._all_declaration

                self._symbols[qualified_name] = SymbolVisibility(
                    name=name,
                    qualified_name=qualified_name,
                    visibility=self._determine_visibility(name, is_in_all),
                    line_number=child.lineno,
                    is_in_all=is_in_all
                )

                # Recurse into class to find methods
                self._visit_node(child, parent_class=qualified_name)

            # Module-level variable assignments
            elif isinstance(child, ast.Assign) and parent_class is None:
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        # Skip __all__ itself
                        if name == "__all__":
                            continue

                        is_in_all = self._all_declaration is not None and name in self._all_declaration

                        self._symbols[name] = SymbolVisibility(
                            name=name,
                            qualified_name=name,
                            visibility=self._determine_visibility(name, is_in_all),
                            line_number=child.lineno,
                            is_in_all=is_in_all
                        )
