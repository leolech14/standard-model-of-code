#!/usr/bin/env python3
"""
🔬 Auto Pattern Discovery Engine

Deterministic pattern discovery applied during pipeline execution.
Discovers and exposes naming patterns that can become new atom types.
"""

from typing import Dict, List, Tuple, Counter
from collections import Counter, defaultdict
import re


class AutoPatternDiscovery:
    """Automatic pattern discovery for unknown particles."""
    
    # Prefix patterns to detect
    PREFIX_ROLES = {
        'test_': 'Test',
        'get_': 'Query',
        'set_': 'Command',
        'add_': 'Command',
        'remove_': 'Command',
        'delete_': 'Command',
        'update_': 'Command',
        'create_': 'Factory',
        'build_': 'Factory',
        'make_': 'Factory',
        'find_': 'Query',
        'fetch_': 'Query',
        'load_': 'Query',
        'save_': 'Command',
        'is_': 'Specification',
        'has_': 'Specification',
        'can_': 'Specification',
        'should_': 'Specification',
        'validate_': 'Validator',
        'check_': 'Validator',
        'parse_': 'Utility',
        'format_': 'Utility',
        'convert_': 'Mapper',
        'transform_': 'Mapper',
        'to_': 'Mapper', 
        'from_': 'Factory',
        'as_': 'Mapper',
        'handle_': 'EventHandler',
        'on_': 'EventHandler',
        'do_': 'Command',
        'run_': 'Command',
        'execute_': 'UseCase',
        'process_': 'Service',
        'render_': 'Utility',
        'init_': 'Service',
        'setup_': 'Service',
        'teardown_': 'Service',
        'cleanup_': 'Service',
    }
    
    # Suffix patterns
    SUFFIX_ROLES = {
        '_handler': 'EventHandler',
        '_callback': 'EventHandler',
        '_hook': 'EventHandler',
        '_validator': 'Validator',
        '_factory': 'Factory',
        '_builder': 'Builder',
        '_service': 'Service',
        '_helper': 'Utility',
        '_util': 'Utility',
        '_utils': 'Utility',
        '_manager': 'Service',
        '_processor': 'Service',
        '_parser': 'Utility',
        '_serializer': 'Mapper',
        '_deserializer': 'Mapper',
        '_converter': 'Mapper',
        '_adapter': 'Adapter',
        '_decorator': 'Utility',
        '_wrapper': 'Utility',
        '_mixin': 'Utility',
        '_test': 'Test',
        '_spec': 'Specification',
    }
    
    # Dunder methods
    DUNDER_ROLES = {
        '__init__': 'Lifecycle',
        '__new__': 'Factory',
        '__del__': 'Lifecycle',
        '__str__': 'Utility',
        '__repr__': 'Utility',
        '__eq__': 'Specification',
        '__ne__': 'Specification',
        '__lt__': 'Specification',
        '__le__': 'Specification',
        '__gt__': 'Specification',
        '__ge__': 'Specification',
        '__hash__': 'Utility',
        '__bool__': 'Specification',
        '__len__': 'Query',
        '__iter__': 'Iterator',
        '__next__': 'Iterator',
        '__getitem__': 'Query',
        '__setitem__': 'Command',
        '__delitem__': 'Command',
        '__contains__': 'Specification',
        '__call__': 'Command',
        '__enter__': 'Lifecycle',
        '__exit__': 'Lifecycle',
        '__getattr__': 'Query',
        '__setattr__': 'Command',
    }

    def __init__(self):
        self.discovered_patterns: Dict[str, int] = Counter()
        self.unknown_names: List[str] = []
    
    def classify_by_pattern(self, name: str) -> Tuple[str, float]:
        """
        Deterministically classify a function/method name by pattern.
        Returns (type, confidence).
        """
        if not name:
            return ('Unknown', 0.0)
        
        # Get the short name (last part after dot)
        short = name.split('.')[-1] if '.' in name else name
        short_lower = short.lower()
        
        # 1. Check dunder methods (highest confidence)
        if short_lower.startswith('__') and short_lower.endswith('__'):
            for dunder, role in self.DUNDER_ROLES.items():
                if short_lower == dunder:
                    return (role, 95.0)
            # Unknown dunder
            return ('Utility', 70.0)
        
        # 2. Check prefix patterns
        for prefix, role in self.PREFIX_ROLES.items():
            if short_lower.startswith(prefix):
                self.discovered_patterns[f'prefix:{prefix}'] += 1
                return (role, 85.0)
        
        # 3. Check suffix patterns
        for suffix, role in self.SUFFIX_ROLES.items():
            if short_lower.endswith(suffix):
                self.discovered_patterns[f'suffix:{suffix}'] += 1
                return (role, 85.0)
        
        # 4. Private methods (single underscore prefix)
        if short_lower.startswith('_') and not short_lower.startswith('__'):
            self.discovered_patterns['_private'] += 1
            return ('Internal', 70.0)
        
        # 5. Record as unknown for pattern analysis
        self.unknown_names.append(short_lower)
        return ('Unknown', 30.0)
    
    def get_pattern_report(self) -> Dict:
        """Generate report of discovered patterns."""
        # Analyze remaining unknown names for new patterns
        token_freq = Counter()
        for name in self.unknown_names:
            tokens = re.findall(r'[a-z]+', name)
            for token in tokens:
                if len(token) > 2:
                    token_freq[token] += 1
        
        return {
            'total_classified': sum(self.discovered_patterns.values()),
            'total_unknown': len(self.unknown_names),
            'top_patterns': self.discovered_patterns.most_common(20),
            'suggested_new_patterns': token_freq.most_common(10),
            'coverage': sum(self.discovered_patterns.values()) / 
                       (sum(self.discovered_patterns.values()) + len(self.unknown_names)) * 100
                       if (sum(self.discovered_patterns.values()) + len(self.unknown_names)) > 0 else 0
        }


def apply_auto_discovery(particles: List[Dict]) -> List[Dict]:
    """
    Apply auto pattern discovery to particles during pipeline.
    Modifies particles in place to update Unknown types.
    """
    discovery = AutoPatternDiscovery()
    updated = 0
    
    for particle in particles:
        if particle.get('type') == 'Unknown':
            name = particle.get('name', '')
            new_type, confidence = discovery.classify_by_pattern(name)
            
            if new_type != 'Unknown':
                particle['type'] = new_type
                particle['confidence'] = confidence
                particle['discovery_method'] = 'auto_pattern'
                updated += 1
    
    # Generate report
    report = discovery.get_pattern_report()
    report['particles_updated'] = updated
    
    return particles, report


if __name__ == '__main__':
    # Test
    test_names = [
        'test_user_login',
        'get_user_by_id',
        '__init__',
        '_private_method',
        'UserFactory',
        'handle_request',
        'some_random_function',
    ]
    
    discovery = AutoPatternDiscovery()
    for name in test_names:
        role, conf = discovery.classify_by_pattern(name)
        print(f'{name} -> {role} ({conf}%)')
    
    print()
    print('Report:', discovery.get_pattern_report())
