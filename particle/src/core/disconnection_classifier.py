# Theory: L2_PRINCIPLES.md (Orphan Semantics Principle)
# Theory: ORPHAN_SEMANTICS.md (Type-aware disconnection taxonomy)
"""
Disconnection Taxonomy: Rich classification of why nodes appear disconnected.

Replaces lazy "orphan" label with 7-type taxonomy (see ORPHAN_TAXONOMY.md).
Extracted from full_analysis.py during audit refactoring (2026-02-24).
"""
from typing import Dict, Any, Optional

from src.core.igt_metrics import OrphanClassifier


def classify_disconnection(node: Dict[str, Any], in_deg: int, out_deg: int) -> Optional[Dict[str, Any]]:
    """
    Classify WHY a node appears disconnected in the dependency graph.

    Returns None if node is not disconnected (has both incoming and outgoing edges).
    Returns a dict with:
        - reachability_source: Why this node exists without standard edges
        - connection_gap: What kind of disconnection (isolated, no_incoming, no_outgoing)
        - isolation_confidence: How confident we are in this classification (0.0-1.0)
        - suggested_action: What to do about it (OK, CHECK, DELETE)

    This replaces the misleading "orphan" classification which conflated 7+ phenomena.
    """
    # Not disconnected - has both incoming and outgoing
    if in_deg > 0 and out_deg > 0:
        return None

    # Determine connection gap type
    if in_deg == 0 and out_deg == 0:
        connection_gap = 'isolated'
    elif in_deg == 0:
        connection_gap = 'no_incoming'
    else:
        connection_gap = 'no_outgoing'

    file_path = node.get('file_path', '')
    name = node.get('name', '')
    kind = node.get('kind', '')
    decorators = node.get('decorators', [])

    # Normalize file_path for pattern matching
    file_lower = file_path.lower()
    name_lower = name.lower()

    # 1. Test file detection (pytest, jest, unittest)
    if any(pattern in file_lower for pattern in ['test_', '_test.', '/tests/', 'conftest', 'spec.js', '.test.', '.spec.']):
        return {
            'reachability_source': 'test_entry',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.95,
            'suggested_action': 'OK - test framework invokes'
        }

    # 2. Entry point detection (__main__, CLI, scripts)
    if any([
        name_lower == 'main',
        name_lower == '__main__',
        'if __name__' in node.get('body_source', ''),
        kind == 'script',
        file_lower.endswith('cli.py'),
        file_lower.endswith('__main__.py'),
    ]):
        return {
            'reachability_source': 'entry_point',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.99,
            'suggested_action': 'OK - program entry point'
        }

    # 3. Framework-managed detection (decorators, dataclasses)
    framework_decorators = ['@dataclass', '@component', '@injectable', '@service', '@controller',
                           '@app.route', '@pytest.fixture', '@staticmethod', '@classmethod',
                           '@property', '@abstractmethod', '@override']
    if decorators:
        decorator_str = ' '.join(str(d).lower() for d in decorators)
        if any(fd.lower().lstrip('@') in decorator_str for fd in framework_decorators):
            return {
                'reachability_source': 'framework_managed',
                'connection_gap': connection_gap,
                'isolation_confidence': 0.90,
                'suggested_action': 'OK - framework instantiates'
            }

    # Also check for dataclass-like patterns in kind
    if kind in ['dataclass', 'namedtuple', 'TypedDict', 'Enum']:
        return {
            'reachability_source': 'framework_managed',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.90,
            'suggested_action': 'OK - instantiated at runtime'
        }

    # 4. Cross-language boundary (JS files analyzed but called from HTML/other)
    if any(file_lower.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte']):
        return {
            'reachability_source': 'cross_language',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.70,
            'suggested_action': 'CHECK - may have cross-language callers'
        }

    # 5. Config/schema files
    if any(pattern in file_lower for pattern in ['config', 'schema', 'settings', '.yaml', '.yml', '.json', '.toml']):
        return {
            'reachability_source': 'external_boundary',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.80,
            'suggested_action': 'OK - configuration/schema'
        }

    # 6. Dynamic dispatch patterns (reflection-like)
    body = node.get('body_source', '')
    if any(pattern in body for pattern in ['getattr(', 'eval(', 'exec(', '__getattr__', 'globals()[', 'locals()[']):
        return {
            'reachability_source': 'dynamic_target',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.60,
            'suggested_action': 'CHECK - may be called via reflection'
        }

    # 7. Public API detection (exported, __all__, public functions)
    if name and not name.startswith('_'):
        # Check if it looks like a public interface
        if kind in ['function', 'class', 'method'] and out_deg > 0:
            return {
                'reachability_source': 'external_boundary',
                'connection_gap': connection_gap,
                'isolation_confidence': 0.75,
                'suggested_action': 'CHECK - may be public API'
            }

    # 8. Default: Truly unreachable (likely dead code)
    # ENHANCED: Apply IGT Orphan Severity
    igt_severity = OrphanClassifier.classify_severity(name, node.get('type', 'file'), file_path)

    return {
        'reachability_source': 'unreachable',
        'connection_gap': connection_gap,
        'isolation_confidence': 0.85,
        'suggested_action': 'REVIEW - likely dead code',
        'igt_severity': igt_severity['score'],
        'igt_label': igt_severity['label'],
        'is_true_orphan': igt_severity['is_problem']
    }
