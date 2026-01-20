#!/usr/bin/env python3
"""
ANALYTICS ENGINE
================

Statistical analysis algorithms for the "Nerd Layer" of code analysis.

Implements:
- Shannon Entropy: Measures classification diversity
- Cyclomatic Complexity: Measures branch/decision complexity
- Halstead Metrics: Measures code volume, difficulty, effort

Usage:
    from analytics_engine import (
        shannon_entropy,
        cyclomatic_complexity,
        halstead_metrics,
        compute_all_metrics
    )
"""

import ast
import math
from collections import Counter
from typing import Dict, List, Any, Optional


# =============================================================================
# SHANNON ENTROPY
# =============================================================================

def shannon_entropy(data: List[str]) -> float:
    """
    Calculate Shannon Entropy from a list of categorical values.
    
    H = -Σ p(x) * log₂(p(x))
    
    Args:
        data: List of category values (e.g., roles, layers, boundaries)
        
    Returns:
        Entropy value (0 = uniform, higher = more concentrated)
        
    Interpretation:
        - High entropy: Diverse distribution (many different categories)
        - Low entropy: Homogeneous distribution (few categories dominate)
    """
    if not data:
        return 0.0
    
    counts = Counter(data)
    total = len(data)
    probabilities = [count / total for count in counts.values()]
    
    entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
    return round(entropy, 4)


def entropy_normalized(data: List[str]) -> float:
    """
    Normalized entropy (0-1 scale).
    
    Returns:
        0 = completely uniform (one category)
        1 = maximum diversity (all categories equally distributed)
    """
    if not data:
        return 0.0
    
    n_categories = len(set(data))
    if n_categories <= 1:
        return 0.0
    
    max_entropy = math.log2(n_categories)
    actual_entropy = shannon_entropy(data)
    
    return round(actual_entropy / max_entropy, 4) if max_entropy > 0 else 0.0


# =============================================================================
# CYCLOMATIC COMPLEXITY
# =============================================================================

def cyclomatic_complexity(body_source: str) -> int:
    """
    Calculate Cyclomatic Complexity from source code.
    
    CC = Number of decision points + 1
    
    Decision points: if, for, while, try/except, and/or, match/case
    
    Args:
        body_source: Python source code string
        
    Returns:
        Cyclomatic complexity score (1 = linear, higher = more complex)
        
    Interpretation:
        1-4: Low complexity (good)
        5-7: Moderate complexity
        8-10: High complexity (consider refactoring)
        11+: Very high complexity (refactor required)
    """
    if not body_source:
        return 1
    
    try:
        tree = ast.parse(body_source)
    except SyntaxError:
        return 1  # Conservative fallback
    
    complexity = 1  # Entry point
    
    for node in ast.walk(tree):
        # Control flow statements
        if isinstance(node, (ast.If, ast.For, ast.While)):
            complexity += 1
        elif isinstance(node, ast.Try):
            complexity += 1
        elif isinstance(node, ast.ExceptHandler):
            complexity += 1
        # Boolean operators add paths
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, (ast.And, ast.Or)):
                complexity += len(node.values) - 1
        # Match/case (Python 3.10+)
        elif hasattr(ast, 'Match') and isinstance(node, ast.Match):
            complexity += len(node.cases)
        # Comprehensions have implicit loops
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            complexity += 1
    
    return complexity


# =============================================================================
# HALSTEAD METRICS
# =============================================================================

def halstead_metrics(body_source: str) -> Dict[str, float]:
    """
    Calculate Halstead metrics from source code.
    
    Formulas:
        n1 = distinct operators
        n2 = distinct operands
        N1 = total operators
        N2 = total operands
        N = N1 + N2 (program length)
        n = n1 + n2 (vocabulary)
        V = N * log₂(n) (volume)
        D = (n1/2) * (N2/n2) (difficulty)
        E = D * V (effort)
        T = E / 18 (time to program, seconds)
        B = V / 3000 (delivered bugs estimate)
    
    Args:
        body_source: Python source code string
        
    Returns:
        Dict with volume, difficulty, effort, time, bugs
        
    Interpretation:
        - Volume: Size of implementation (higher = more code)
        - Difficulty: How hard to understand (higher = harder)
        - Effort: Mental effort to implement (higher = more work)
        - Time: Estimated seconds to implement
        - Bugs: Estimated bugs delivered (higher = more bugs expected)
    """
    if not body_source:
        return {'volume': 0, 'difficulty': 0, 'effort': 0, 'time': 0, 'bugs': 0}
    
    try:
        tree = ast.parse(body_source)
    except SyntaxError:
        return {'volume': 0, 'difficulty': 0, 'effort': 0, 'time': 0, 'bugs': 0}
    
    operators = []
    operands = []
    
    # AST node types considered as operators
    operator_types = (
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
        ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd,
        ast.FloorDiv, ast.And, ast.Or, ast.Eq, ast.NotEq, ast.Lt,
        ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn,
        ast.Not, ast.Invert, ast.UAdd, ast.USub,
    )
    
    for node in ast.walk(tree):
        # Operators: functions, keywords, operations
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            operators.append('def')
        elif isinstance(node, ast.ClassDef):
            operators.append('class')
        elif isinstance(node, (ast.If, ast.IfExp)):
            operators.append('if')
        elif isinstance(node, ast.For):
            operators.append('for')
        elif isinstance(node, ast.While):
            operators.append('while')
        elif isinstance(node, ast.Return):
            operators.append('return')
        elif isinstance(node, ast.Call):
            operators.append('()')
        elif isinstance(node, ast.Assign):
            operators.append('=')
        elif isinstance(node, ast.AugAssign):
            operators.append(type(node.op).__name__)
        elif isinstance(node, ast.BinOp):
            operators.append(type(node.op).__name__)
        elif isinstance(node, ast.Compare):
            for op in node.ops:
                operators.append(type(op).__name__)
        elif isinstance(node, ast.BoolOp):
            operators.append(type(node.op).__name__)
        elif isinstance(node, ast.UnaryOp):
            operators.append(type(node.op).__name__)
        
        # Operands: names and constants
        if isinstance(node, ast.Name):
            operands.append(node.id)
        elif isinstance(node, ast.Constant):
            operands.append(str(node.value))
    
    n1 = len(set(operators))  # Distinct operators
    n2 = len(set(operands))   # Distinct operands
    N1 = len(operators)       # Total operators
    N2 = len(operands)        # Total operands
    
    N = N1 + N2  # Program length
    n = n1 + n2  # Vocabulary
    
    if n == 0 or n2 == 0:
        return {'volume': 0, 'difficulty': 0, 'effort': 0, 'time': 0, 'bugs': 0}
    
    V = N * math.log2(n)                    # Volume
    D = (n1 / 2) * (N2 / n2) if n2 > 0 else 0  # Difficulty
    E = D * V                                # Effort
    T = E / 18                               # Time (Stroud number = 18)
    B = V / 3000                             # Bugs
    
    return {
        'volume': round(V, 2),
        'difficulty': round(D, 2),
        'effort': round(E, 2),
        'time': round(T, 2),
        'bugs': round(B, 4),
    }


# =============================================================================
# UNIFIED INTERFACE
# =============================================================================

def compute_node_metrics(node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute all metrics for a single node.
    
    Args:
        node: Node dict with 'body_source' field
        
    Returns:
        Dict with cyclomatic and halstead metrics
    """
    body = node.get('body_source', '') or node.get('body', '') or ''
    
    return {
        'cyclomatic': cyclomatic_complexity(body),
        'halstead': halstead_metrics(body),
    }


def compute_codebase_entropy(nodes: List[Dict], field: str = 'role') -> Dict[str, float]:
    """
    Compute entropy statistics for a field across all nodes.
    
    Args:
        nodes: List of node dicts
        field: Field to analyze ('role', 'layer', 'boundary', etc.)
        
    Returns:
        Dict with entropy, normalized_entropy, distribution
    """
    values = [n.get(field, 'unknown') for n in nodes if n.get(field)]
    
    return {
        'entropy': shannon_entropy(values),
        'normalized': entropy_normalized(values),
        'distribution': dict(Counter(values)),
    }


def compute_all_metrics(nodes: List[Dict]) -> Dict[str, Any]:
    """
    Compute all statistical metrics for a codebase.
    
    Args:
        nodes: List of node dicts with body_source
        
    Returns:
        Dict with:
        - entropy: By field (role, layer, boundary, state, lifecycle)
        - complexity: Aggregate cyclomatic stats
        - halstead: Aggregate halstead stats
    """
    # Entropy by classification field
    entropy_fields = ['role', 'layer', 'boundary', 'state', 'lifecycle']
    entropy_stats = {
        field: compute_codebase_entropy(nodes, field)
        for field in entropy_fields
    }
    
    # Cyclomatic complexity
    cc_values = []
    for node in nodes:
        body = node.get('body_source', '') or ''
        if body:
            cc_values.append(cyclomatic_complexity(body))
    
    complexity_stats = {
        'avg': round(sum(cc_values) / len(cc_values), 2) if cc_values else 0,
        'max': max(cc_values) if cc_values else 0,
        'high_complexity_count': sum(1 for cc in cc_values if cc > 10),
    }
    
    # Halstead aggregate
    halstead_totals = {'volume': 0, 'difficulty': 0, 'effort': 0, 'bugs': 0}
    halstead_count = 0
    
    for node in nodes:
        body = node.get('body_source', '') or ''
        if body:
            h = halstead_metrics(body)
            for key in halstead_totals:
                halstead_totals[key] += h.get(key, 0)
            halstead_count += 1
    
    halstead_stats = {
        'total_volume': round(halstead_totals['volume'], 2),
        'avg_difficulty': round(halstead_totals['difficulty'] / halstead_count, 2) if halstead_count else 0,
        'total_effort': round(halstead_totals['effort'], 2),
        'estimated_bugs': round(halstead_totals['bugs'], 2),
    }
    
    return {
        'entropy': entropy_stats,
        'complexity': complexity_stats,
        'halstead': halstead_stats,
    }


if __name__ == "__main__":
    # Demo
    test_code = '''
def process_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
        elif item < 0:
            result.append(item * -1)
        else:
            result.append(0)
    return result
'''
    
    print("Analytics Engine Demo")
    print("=" * 60)
    
    print(f"\nCyclomatic Complexity: {cyclomatic_complexity(test_code)}")
    print(f"  (1=linear, 5-7=moderate, 10+=high)")
    
    h = halstead_metrics(test_code)
    print(f"\nHalstead Metrics:")
    print(f"  Volume: {h['volume']}")
    print(f"  Difficulty: {h['difficulty']}")
    print(f"  Effort: {h['effort']}")
    print(f"  Est. Bugs: {h['bugs']}")
    
    # Entropy demo
    roles = ['Query', 'Query', 'Command', 'Service', 'Query', 'Repository']
    print(f"\nShannon Entropy (roles): {shannon_entropy(roles)}")
    print(f"Normalized Entropy: {entropy_normalized(roles)}")
