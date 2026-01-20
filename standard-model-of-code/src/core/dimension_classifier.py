#!/usr/bin/env python3
"""
DIMENSION CLASSIFIER
====================

Classifies the 3 missing octahedral dimensions from the Standard Model theory:
- D4 BOUNDARY: Internal/Input/I-O/Output
- D5 STATE: Stateful/Stateless
- D7 LIFECYCLE: Create/Use/Destroy

Each node (atom) is classified using AST patterns and heuristics.

Usage:
    from dimension_classifier import DimensionClassifier
    
    classifier = DimensionClassifier()
    node['boundary'] = classifier.classify_boundary(node).value
    node['state'] = classifier.classify_state(node).value
    node['lifecycle'] = classifier.classify_lifecycle(node).value
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Any


class BoundaryType(Enum):
    """D4: Does this code cross I/O boundaries?"""
    INTERNAL = "internal"    # Pure computation, no I/O
    INPUT = "input"          # Reads from external (params, files, network, DB)
    OUTPUT = "output"        # Writes to external (returns, files, network, DB)
    IO = "io"                # Both reads and writes externally


class StateType(Enum):
    """D5: Does this code maintain state?"""
    STATELESS = "stateless"  # Pure function, no mutable state
    STATEFUL = "stateful"    # Has instance vars, globals, or closure state


class LifecyclePhase(Enum):
    """D7: What lifecycle phase is this code in?"""
    CREATE = "create"        # Initialization: __init__, factory, builder
    USE = "use"              # Normal operation: business logic  
    DESTROY = "destroy"      # Cleanup: __del__, close, dispose, cleanup


class DimensionClassifier:
    """
    Classifies code atoms across the 3 missing octahedral dimensions.
    Uses AST patterns and naming conventions for heuristic classification.
    """
    
    # I/O detection patterns
    IO_PATTERNS = {
        'input': [
            r'\bopen\s*\(',           # file open
            r'\bread\s*\(',           # file read
            r'\.get\s*\(',            # dict/request get
            r'\brequests?\.',         # HTTP requests
            r'\.query\s*\(',          # DB query
            r'\.find\s*\(',           # DB find
            r'\.select\s*\(',         # SQL select
            r'\binput\s*\(',          # user input
            r'os\.environ',           # env vars
            r'\.recv\s*\(',           # socket recv
            r'json\.load\s*\(',       # JSON load
            r'yaml\.load\s*\(',       # YAML load
            r'\bsys\.argv',           # CLI args
        ],
        'output': [
            r'\.write\s*\(',          # file write
            r'\bprint\s*\(',          # stdout
            r'\.send\s*\(',           # socket/network send
            r'\.post\s*\(',           # HTTP post
            r'\.put\s*\(',            # HTTP put
            r'\.delete\s*\(',         # HTTP delete
            r'\.insert\s*\(',         # DB insert
            r'\.update\s*\(',         # DB update
            r'\.save\s*\(',           # persistence save
            r'\.commit\s*\(',         # transaction commit
            r'json\.dump\s*\(',       # JSON dump
            r'logging\.',             # logging calls
        ],
    }
    
    # State detection patterns
    STATE_PATTERNS = [
        r'self\.\w+\s*=',             # instance variable assignment
        r'cls\.\w+\s*=',              # class variable assignment
        r'\bglobal\s+\w+',            # global declaration
        r'nonlocal\s+\w+',            # nonlocal (closure)
    ]
    
    # Lifecycle phase detection
    LIFECYCLE_PATTERNS = {
        'create': [
            r'^__init__$',            # Python constructor
            r'^__new__$',             # Python allocator
            r'^create',               # create_x
            r'^build',                # build_x  
            r'^make',                 # make_x
            r'^init',                 # init_x
            r'^setup',                # setup_x
            r'^construct',            # construct_x
            r'Factory$',              # xFactory class
            r'Builder$',              # xBuilder class
        ],
        'destroy': [
            r'^__del__$',             # Python destructor
            r'^__exit__$',            # Context manager exit
            r'^close$',               # close()
            r'^cleanup$',             # cleanup()
            r'^dispose$',             # dispose()
            r'^teardown',             # teardown_x
            r'^destroy',              # destroy_x
            r'^shutdown',             # shutdown_x
            r'^release',              # release_x
            r'^clear$',               # clear()
        ],
    }
    
    def __init__(self):
        # Compile regex patterns for performance
        self.input_regexes = [re.compile(p, re.IGNORECASE) for p in self.IO_PATTERNS['input']]
        self.output_regexes = [re.compile(p, re.IGNORECASE) for p in self.IO_PATTERNS['output']]
        self.state_regexes = [re.compile(p) for p in self.STATE_PATTERNS]
        self.create_regexes = [re.compile(p, re.IGNORECASE) for p in self.LIFECYCLE_PATTERNS['create']]
        self.destroy_regexes = [re.compile(p, re.IGNORECASE) for p in self.LIFECYCLE_PATTERNS['destroy']]
    
    def classify_boundary(self, node: Dict[str, Any]) -> BoundaryType:
        """
        Classify the I/O boundary type of a node.
        
        Args:
            node: Node dict with 'body_source', 'signature', etc.
            
        Returns:
            BoundaryType enum value
        """
        body = node.get('body_source', '') or node.get('body', '') or ''
        signature = node.get('signature', '') or ''
        combined = f"{signature}\n{body}"
        
        has_input = any(r.search(combined) for r in self.input_regexes)
        has_output = any(r.search(combined) for r in self.output_regexes)
        
        if has_input and has_output:
            return BoundaryType.IO
        elif has_input:
            return BoundaryType.INPUT
        elif has_output:
            return BoundaryType.OUTPUT
        else:
            return BoundaryType.INTERNAL
    
    def classify_state(self, node: Dict[str, Any]) -> StateType:
        """
        Classify whether a node maintains state.
        
        Args:
            node: Node dict with 'body_source', 'kind', etc.
            
        Returns:
            StateType enum value
        """
        body = node.get('body_source', '') or node.get('body', '') or ''
        kind = node.get('kind', 'function')
        name = node.get('name', '')
        
        # Classes are inherently stateful
        if kind == 'class':
            return StateType.STATEFUL
        
        # Check for state patterns in body
        for regex in self.state_regexes:
            if regex.search(body):
                return StateType.STATEFUL
        
        # Methods that modify self are stateful
        if 'self.' in body and '=' in body:
            # Simple check: self.x = ... pattern
            if re.search(r'self\.\w+\s*[+\-*/%]?=', body):
                return StateType.STATEFUL
        
        return StateType.STATELESS
    
    def classify_lifecycle(self, node: Dict[str, Any]) -> LifecyclePhase:
        """
        Classify the lifecycle phase of a node.
        
        Args:
            node: Node dict with 'name', etc.
            
        Returns:
            LifecyclePhase enum value
        """
        name = node.get('name', '')
        
        # Check create patterns
        for regex in self.create_regexes:
            if regex.search(name):
                return LifecyclePhase.CREATE
        
        # Check destroy patterns
        for regex in self.destroy_regexes:
            if regex.search(name):
                return LifecyclePhase.DESTROY
        
        # Default: normal operation
        return LifecyclePhase.USE
    
    def classify_all(self, node: Dict[str, Any]) -> Dict[str, str]:
        """
        Classify all 3 dimensions for a node.
        
        Returns:
            Dict with 'boundary', 'state', 'lifecycle' string values
        """
        return {
            'boundary': self.classify_boundary(node).value,
            'state': self.classify_state(node).value,
            'lifecycle': self.classify_lifecycle(node).value,
        }


def classify_all_dimensions(nodes: List[Dict[str, Any]]) -> int:
    """
    Classify all 3 missing dimensions for a list of nodes.
    Modifies nodes in-place.
    
    Args:
        nodes: List of node dicts
        
    Returns:
        Number of nodes classified
    """
    classifier = DimensionClassifier()
    count = 0
    
    for node in nodes:
        dims = classifier.classify_all(node)
        
        # Add to node
        node['boundary'] = dims['boundary']
        node['state'] = dims['state']
        node['lifecycle'] = dims['lifecycle']
        
        # Also add to dimensions sub-dict if it exists
        if 'dimensions' in node and isinstance(node['dimensions'], dict):
            node['dimensions']['boundary'] = dims['boundary']
            node['dimensions']['state'] = dims['state']
            node['dimensions']['lifecycle'] = dims['lifecycle']
        
        count += 1
    
    return count


if __name__ == "__main__":
    # Demo
    test_nodes = [
        {
            'name': '__init__',
            'kind': 'method',
            'body_source': 'self.data = []'
        },
        {
            'name': 'process',
            'kind': 'function',
            'body_source': 'result = compute(x); print(result); return result'
        },
        {
            'name': 'read_file',
            'kind': 'function',
            'body_source': 'with open(path) as f: return f.read()'
        },
        {
            'name': 'cleanup',
            'kind': 'function',
            'body_source': 'self.conn.close()'
        },
    ]
    
    classifier = DimensionClassifier()
    
    print("Dimension Classification Demo")
    print("=" * 60)
    
    for node in test_nodes:
        dims = classifier.classify_all(node)
        print(f"\n{node['name']}:")
        print(f"  Boundary:  {dims['boundary']}")
        print(f"  State:     {dims['state']}")
        print(f"  Lifecycle: {dims['lifecycle']}")
