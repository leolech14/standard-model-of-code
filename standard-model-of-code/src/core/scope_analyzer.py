#!/usr/bin/env python3
"""
SCOPE ANALYZER - Lexical scope analysis using tree-sitter AST.

Provides scope-aware analysis for:
- Variable binding resolution (ref → def)
- Unused definition detection (dead code)
- Variable shadowing detection (code smell)

Architecture:
- Per-file stateful traversal (O(n) not O(n²))
- Manual AST traversal (language-agnostic, robust)
- Visitor pattern compatible with EdgeExtractor

Usage:
    from src.core.scope_analyzer import analyze_scopes, find_unused_definitions

    scope_graph = analyze_scopes(tree, source, 'python')
    unused = find_unused_definitions(scope_graph)
    shadowed = find_shadowed_definitions(scope_graph)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class Definition:
    """A variable/function definition in a scope."""
    name: str
    node_id: int  # tree-sitter node id
    start_byte: int
    end_byte: int
    start_line: int
    end_line: int
    scope_id: int
    kind: str = 'variable'  # variable, function, parameter, class, import

    def __hash__(self):
        return hash((self.name, self.node_id, self.scope_id))


@dataclass
class Reference:
    """A reference to a name that needs resolution."""
    name: str
    node_id: int
    start_byte: int
    start_line: int
    scope_id: int
    resolved_def: Optional[Definition] = None

    def __hash__(self):
        return hash((self.name, self.node_id))


@dataclass
class Scope:
    """A lexical scope containing definitions."""
    id: int
    parent_id: Optional[int]
    start_byte: int
    end_byte: int
    start_line: int
    end_line: int
    kind: str  # module, function, class, block, comprehension
    inherits: bool = True  # False for class bodies (PEP 227)
    definitions: List[Definition] = field(default_factory=list)
    children: List[int] = field(default_factory=list)  # child scope ids


@dataclass
class ScopeGraph:
    """Complete scope analysis result for a file."""
    file_path: str
    language: str
    scopes: Dict[int, Scope] = field(default_factory=dict)
    definitions: Dict[int, Definition] = field(default_factory=dict)  # by node_id
    references: List[Reference] = field(default_factory=list)
    root_scope_id: int = 0

    def get_scope(self, scope_id: int) -> Optional[Scope]:
        return self.scopes.get(scope_id)

    def get_parent_scope(self, scope_id: int) -> Optional[Scope]:
        scope = self.scopes.get(scope_id)
        if scope and scope.parent_id is not None:
            return self.scopes.get(scope.parent_id)
        return None


# =============================================================================
# SCOPE-DEFINING NODE TYPES BY LANGUAGE
# =============================================================================

SCOPE_NODES = {
    'python': {
        'module': ('module', True),
        'function': ('function_definition', True),
        'async_function': ('function_definition', True),  # with async
        'class': ('class_definition', False),  # PEP 227: class scope doesn't inherit
        'lambda': ('lambda', True),
        'comprehension': ('list_comprehension', True),
        'dict_comprehension': ('dictionary_comprehension', True),
        'set_comprehension': ('set_comprehension', True),
        'generator': ('generator_expression', True),
    },
    'javascript': {
        'program': ('program', True),
        'function': ('function_declaration', True),
        'function_expr': ('function_expression', True),
        'arrow': ('arrow_function', True),
        'method': ('method_definition', True),
        'class': ('class_declaration', True),
        'block': ('statement_block', True),  # for let/const
        'for': ('for_statement', True),
        'for_in': ('for_in_statement', True),
        'catch': ('catch_clause', True),
    },
    'typescript': {
        'program': ('program', True),
        'function': ('function_declaration', True),
        'function_expr': ('function_expression', True),
        'arrow': ('arrow_function', True),
        'method': ('method_definition', True),
        'class': ('class_declaration', True),
        'block': ('statement_block', True),
        'for': ('for_statement', True),
        'for_in': ('for_in_statement', True),
        'catch': ('catch_clause', True),
    },
}

# Definition node types by language
DEFINITION_NODES = {
    'python': [
        'identifier',  # in assignment, parameter, for loop, etc.
    ],
    'javascript': [
        'identifier',  # in var/let/const, function name, parameter
    ],
    'typescript': [
        'identifier',
    ],
}


# =============================================================================
# CORE ANALYSIS FUNCTIONS
# =============================================================================

def analyze_scopes(tree, source: bytes, language: str, file_path: str = '') -> ScopeGraph:
    """
    Analyze scopes in a parsed tree.

    Args:
        tree: tree-sitter Tree object
        source: Source code as bytes
        language: Language name (python, javascript, typescript)
        file_path: Optional file path for reporting

    Returns:
        ScopeGraph with all scopes, definitions, and references
    """
    graph = ScopeGraph(file_path=file_path, language=language)

    scope_types = _get_scope_types(language)
    scope_stack: List[int] = []
    next_scope_id = 0

    # Create root scope from root node
    root = tree.root_node
    root_scope = Scope(
        id=next_scope_id,
        parent_id=None,
        start_byte=root.start_byte,
        end_byte=root.end_byte,
        start_line=root.start_point[0] + 1,
        end_line=root.end_point[0] + 1,
        kind='module' if language == 'python' else 'program',
        inherits=True,
    )
    graph.scopes[next_scope_id] = root_scope
    graph.root_scope_id = next_scope_id
    scope_stack.append(next_scope_id)
    next_scope_id += 1

    # Traverse tree
    cursor = tree.walk()

    def visit_node(node, depth=0):
        nonlocal next_scope_id

        node_type = node.type

        # Check if this node creates a new scope
        scope_info = scope_types.get(node_type)
        created_scope = False

        if scope_info:
            inherits = scope_info[1]
            parent_id = scope_stack[-1] if scope_stack else None

            new_scope = Scope(
                id=next_scope_id,
                parent_id=parent_id,
                start_byte=node.start_byte,
                end_byte=node.end_byte,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                kind=node_type,
                inherits=inherits,
            )
            graph.scopes[next_scope_id] = new_scope

            # Link to parent
            if parent_id is not None and parent_id in graph.scopes:
                graph.scopes[parent_id].children.append(next_scope_id)

            scope_stack.append(next_scope_id)
            next_scope_id += 1
            created_scope = True

        # Check for definitions
        _extract_definitions(node, graph, scope_stack, language, source)

        # Check for references (identifiers in expression context)
        _extract_references(node, graph, scope_stack, language)

        # Visit children
        for child in node.children:
            visit_node(child, depth + 1)

        # Pop scope if we created one
        if created_scope and scope_stack:
            scope_stack.pop()

    visit_node(root)

    # Resolve references
    _resolve_all_references(graph)

    return graph


def _get_scope_types(language: str) -> Dict[str, Tuple[str, bool]]:
    """Get scope-creating node types for a language."""
    lang_scopes = SCOPE_NODES.get(language, SCOPE_NODES.get('python', {}))
    # Invert to map node_type -> (name, inherits)
    return {v[0]: (k, v[1]) for k, v in lang_scopes.items()}


def _extract_definitions(node, graph: ScopeGraph, scope_stack: List[int],
                         language: str, source: bytes):
    """Extract definitions from a node based on context."""
    if not scope_stack:
        return

    current_scope_id = scope_stack[-1]

    # Python-specific definition extraction
    if language == 'python':
        _extract_python_definitions(node, graph, current_scope_id, source)
    elif language in ('javascript', 'typescript'):
        _extract_js_definitions(node, graph, current_scope_id, source)


def _extract_python_definitions(node, graph: ScopeGraph, scope_id: int, source: bytes):
    """Extract Python definitions."""
    parent = node.parent
    if not parent:
        return

    # Function/class name
    if node.type == 'identifier':
        if parent.type == 'function_definition' and _is_name_field(node, parent):
            _add_definition(node, graph, scope_id, 'function', source)
        elif parent.type == 'class_definition' and _is_name_field(node, parent):
            _add_definition(node, graph, scope_id, 'class', source)
        # Parameters
        elif parent.type in ('parameters', 'typed_parameter', 'default_parameter'):
            _add_definition(node, graph, scope_id, 'parameter', source)
        # Assignment target
        elif parent.type == 'assignment' and _is_left_side(node, parent):
            _add_definition(node, graph, scope_id, 'variable', source)
        # For loop variable
        elif parent.type == 'for_statement' and _is_left_side(node, parent):
            _add_definition(node, graph, scope_id, 'variable', source)
        # Import
        elif parent.type in ('import_statement', 'import_from_statement', 'aliased_import'):
            _add_definition(node, graph, scope_id, 'import', source)


def _extract_js_definitions(node, graph: ScopeGraph, scope_id: int, source: bytes):
    """Extract JavaScript/TypeScript definitions."""
    parent = node.parent
    if not parent:
        return

    if node.type == 'identifier':
        # Function name
        if parent.type == 'function_declaration' and _is_name_field(node, parent):
            _add_definition(node, graph, scope_id, 'function', source)
        # Class name
        elif parent.type == 'class_declaration' and _is_name_field(node, parent):
            _add_definition(node, graph, scope_id, 'class', source)
        # Variable declarator
        elif parent.type == 'variable_declarator' and _is_name_field(node, parent):
            _add_definition(node, graph, scope_id, 'variable', source)
        # Parameters
        elif parent.type == 'formal_parameters':
            _add_definition(node, graph, scope_id, 'parameter', source)
        # Import specifier
        elif parent.type in ('import_specifier', 'import_clause', 'namespace_import'):
            _add_definition(node, graph, scope_id, 'import', source)


def _is_name_field(node, parent) -> bool:
    """Check if node is the 'name' field of its parent."""
    # Try to get the 'name' field directly
    try:
        name_node = parent.child_by_field_name('name')
        if name_node and name_node.id == node.id:
            return True
    except (AttributeError, TypeError):
        pass

    # Fallback: first identifier child for function/class definitions
    if parent.type in ('function_definition', 'class_definition', 'function_declaration',
                       'class_declaration', 'variable_declarator'):
        for child in parent.children:
            if child.type == 'identifier':
                return child.id == node.id
    return False


def _is_left_side(node, parent) -> bool:
    """Check if node is on the left side of an assignment/for loop."""
    if parent.type == 'assignment':
        # Left side is before the '=' operator
        for child in parent.children:
            if child.type == '=':
                break
            if child.id == node.id or _contains_node(child, node):
                return True
    elif parent.type == 'for_statement':
        # Left side is the loop variable (before 'in')
        for child in parent.children:
            if child.type == 'in':
                break
            if child.id == node.id or _contains_node(child, node):
                return True
    return False


def _contains_node(container, target) -> bool:
    """Check if container node contains target node."""
    if container.id == target.id:
        return True
    for child in container.children:
        if _contains_node(child, target):
            return True
    return False


def _add_definition(node, graph: ScopeGraph, scope_id: int, kind: str, source: bytes):
    """Add a definition to the graph."""
    name = source[node.start_byte:node.end_byte].decode('utf8', errors='replace')

    definition = Definition(
        name=name,
        node_id=node.id,
        start_byte=node.start_byte,
        end_byte=node.end_byte,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        scope_id=scope_id,
        kind=kind,
    )

    graph.definitions[node.id] = definition

    if scope_id in graph.scopes:
        graph.scopes[scope_id].definitions.append(definition)


def _extract_references(node, graph: ScopeGraph, scope_stack: List[int], language: str):
    """Extract identifier references (not definitions)."""
    if not scope_stack or node.type != 'identifier':
        return

    # Skip if this is a definition (already processed)
    if node.id in graph.definitions:
        return

    parent = node.parent
    if not parent:
        return

    # Skip definition contexts
    if parent.type in ('function_definition', 'class_definition', 'function_declaration',
                       'class_declaration', 'variable_declarator', 'parameters',
                       'formal_parameters', 'typed_parameter', 'default_parameter',
                       'import_statement', 'import_from_statement', 'import_specifier'):
        return

    current_scope_id = scope_stack[-1]

    ref = Reference(
        name=node.text.decode('utf8', errors='replace') if node.text else '',
        node_id=node.id,
        start_byte=node.start_byte,
        start_line=node.start_point[0] + 1,
        scope_id=current_scope_id,
    )

    graph.references.append(ref)


def _resolve_all_references(graph: ScopeGraph):
    """Resolve all references to their definitions."""
    for ref in graph.references:
        ref.resolved_def = resolve_reference(ref, graph)


# =============================================================================
# RESOLUTION AND DETECTION FUNCTIONS
# =============================================================================

def resolve_reference(ref: Reference, graph: ScopeGraph) -> Optional[Definition]:
    """
    Resolve a reference to its definition.

    Algorithm (from tree-sitter-highlight):
    1. Start from reference's scope
    2. Walk scopes innermost → outermost
    3. For each scope, check definitions newest → oldest
    4. Match if: name matches AND ref.start_byte >= def.end_byte (defined before use)
    5. Stop if scope.inherits == False
    """
    current_scope_id = ref.scope_id

    while current_scope_id is not None:
        scope = graph.get_scope(current_scope_id)
        if not scope:
            break

        # Check definitions in this scope (reverse order = newest first)
        for definition in reversed(scope.definitions):
            if definition.name == ref.name:
                # Definition must be before reference (or same position for params)
                if ref.start_byte >= definition.start_byte:
                    return definition

        # Stop if scope doesn't inherit (class body in Python)
        if not scope.inherits:
            break

        current_scope_id = scope.parent_id

    return None


def find_unused_definitions(graph: ScopeGraph) -> List[Definition]:
    """
    Find definitions that are never referenced.

    Returns:
        List of unused Definition objects
    """
    # Collect all referenced definition node_ids
    referenced_ids: Set[int] = set()
    for ref in graph.references:
        if ref.resolved_def:
            referenced_ids.add(ref.resolved_def.node_id)

    # Find definitions not in referenced set
    unused = []
    for node_id, definition in graph.definitions.items():
        if node_id not in referenced_ids:
            # Skip certain kinds that are expected to be "unused" locally
            if definition.kind in ('import', 'class', 'function'):
                # These might be exported/used externally
                continue
            unused.append(definition)

    return unused


def find_shadowed_definitions(graph: ScopeGraph) -> List[Tuple[Definition, Definition]]:
    """
    Find definitions that shadow outer scope definitions.

    Returns:
        List of (inner_def, outer_def) pairs where inner shadows outer
    """
    shadowed_pairs = []

    for scope_id, scope in graph.scopes.items():
        if scope.parent_id is None:
            continue

        for inner_def in scope.definitions:
            # Look for same name in ancestor scopes
            outer_def = _find_in_ancestors(inner_def.name, scope.parent_id, graph)
            if outer_def:
                shadowed_pairs.append((inner_def, outer_def))

    return shadowed_pairs


def _find_in_ancestors(name: str, scope_id: Optional[int], graph: ScopeGraph) -> Optional[Definition]:
    """Find a definition with given name in ancestor scopes."""
    while scope_id is not None:
        scope = graph.get_scope(scope_id)
        if not scope:
            break

        for definition in scope.definitions:
            if definition.name == name:
                return definition

        if not scope.inherits:
            break

        scope_id = scope.parent_id

    return None


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_scope_summary(graph: ScopeGraph) -> dict:
    """Get summary statistics for a scope graph."""
    return {
        'total_scopes': len(graph.scopes),
        'total_definitions': len(graph.definitions),
        'total_references': len(graph.references),
        'resolved_references': sum(1 for r in graph.references if r.resolved_def),
        'unresolved_references': sum(1 for r in graph.references if not r.resolved_def),
        'unused_definitions': len(find_unused_definitions(graph)),
        'shadowed_pairs': len(find_shadowed_definitions(graph)),
    }


if __name__ == '__main__':
    # Test with a simple Python file
    import tree_sitter
    import tree_sitter_python

    code = b'''
def outer():
    x = 1
    def inner():
        x = 2  # shadows outer x
        y = 3  # unused
        print(x)
    inner()
'''

    parser = tree_sitter.Parser()
    parser.language = tree_sitter.Language(tree_sitter_python.language())
    tree = parser.parse(code)

    graph = analyze_scopes(tree, code, 'python', 'test.py')

    print("=" * 60)
    print("SCOPE ANALYSIS TEST")
    print("=" * 60)
    print(f"\nScopes: {len(graph.scopes)}")
    for sid, scope in graph.scopes.items():
        print(f"  [{sid}] {scope.kind} (lines {scope.start_line}-{scope.end_line})")
        for d in scope.definitions:
            print(f"       def: {d.name} ({d.kind})")

    print(f"\nReferences: {len(graph.references)}")
    for ref in graph.references:
        resolved = f"-> {ref.resolved_def.name}@L{ref.resolved_def.start_line}" if ref.resolved_def else "UNRESOLVED"
        print(f"  {ref.name}@L{ref.start_line} {resolved}")

    print(f"\nUnused definitions:")
    for d in find_unused_definitions(graph):
        print(f"  {d.name} at line {d.start_line}")

    print(f"\nShadowed definitions:")
    for inner, outer in find_shadowed_definitions(graph):
        print(f"  {inner.name}@L{inner.start_line} shadows {outer.name}@L{outer.start_line}")

    print(f"\nSummary: {get_scope_summary(graph)}")
