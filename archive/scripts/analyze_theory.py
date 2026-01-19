#!/usr/bin/env python3
"""
Deep analysis of the Theory Canvas content
Extracts the Standard Model of Software Architecture concepts
"""

import json
import re
from collections import defaultdict

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_concepts_from_large_texts(nodes):
    """Extract key theoretical concepts from large text nodes."""
    concepts = {
        'impossible_patterns': [],
        'four_forces': [],
        'haiku_examples': [],
        'spectrometer_features': [],
        'key_theorems': []
    }

    # Pattern for the 42 impossible sub-hadrons
    impossible_pattern = r'(\w+::\w+)'

    for node in nodes:
        if len(node.get('text', '')) > 500:
            text = node.get('text', '')

            # Extract impossible patterns
            if 'impossíveis' in text or 'IMPOSSÍVEIS' in text:
                matches = re.findall(r'(\w+::\w+)', text)
                concepts['impossible_patterns'].extend(matches)

            # Extract the four forces mapping
            if 'Força forte' in text or 'Strong Force' in text:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'Responsabilidade' in line and i > 0:
                        concepts['four_forces'].append({
                            'force': 'Strong',
                            'software_dimension': 'Responsibility (Domain)',
                            'description': 'What the element DOES in the domain'
                        })
                    if 'Pureza' in line or 'Purity' in text:
                        concepts['four_forces'].append({
                            'force': 'Electromagnetic',
                            'software_dimension': 'Purity (side-effects)',
                            'description': 'Can or cannot touch the external world'
                        })
                    if 'Boundary' in line or 'camada' in line:
                        concepts['four_forces'].append({
                            'force': 'Weak',
                            'software_dimension': 'Boundary (layer)',
                            'description': 'Where the element lives in topology'
                        })
                    if 'Lifecycle' in line or 'temporalidade' in line:
                        concepts['four_forces'].append({
                            'force': 'Gravity',
                            'software_dimension': 'Lifecycle (temporal)',
                            'description': 'When the element exists and how it dies'
                        })

            # Extract HAIKU examples with statistics
            if 'HAIKU' in text and '%' in text:
                lines = text.split('\n')
                for line in lines:
                    if '::' in line and '%' in line:
                        # Extract pattern like "QueryHandler::FindById | 98.7%"
                        match = re.search(r'(\w+::\w+)\s*\|\s*([\d.]+)%', line)
                        if match:
                            concepts['haiku_examples'].append({
                                'pattern': match.group(1),
                                'frequency': float(match.group(2))
                            })

            # Extract Spectrometer v10 features
            if 'Spectrometer v10' in text:
                features = re.findall(r'-(.+?)\n', text)
                concepts['spectrometer_features'] = [f.strip() for f in features[:5]]

            # Extract key theorems
            if '10.9%' in text:
                concepts['key_theorems'].append('10.9% of theoretical space is antimatter (impossible patterns)')
            if '384-42' in text:
                concepts['key_theorems'].append('384 total sub-hadrons = 342 possible + 42 impossible')
            if 'CQRS' in text:
                concepts['key_theorems'].append('CQRS violation: Commands never return data, Queries never modify state')

    # Remove duplicates
    concepts['impossible_patterns'] = list(set(concepts['impossible_patterns']))

    return concepts

def generate_theory_summary():
    """Generate a comprehensive summary of the theory."""
    summary = """
# Standard Model of Software Architecture - v10

## Core Theory

The theory proposes that all software architecture can be modeled using:
- 11 fundamental laws (like physics laws)
- 12 quarks/continents (basic building blocks)
- 96 hadrons (complex patterns)
- 384 sub-hadrons (specific implementations)

## Key Discovery: 42 Impossible Patterns

From the 384 theoretical sub-hadrons, exactly 42 are impossible - they represent
architectural anti-patterns that violate fundamental laws:

1. CommandHandler::FindById - Violates CQRS (commands shouldn't return data)
2. QueryHandler::Save - Violates CQRS (queries shouldn't modify state)
3. Entity::Stateless - Entities must have identity and state
4. ValueObject::HasIdentity - Value objects defined by values, not ID
5. RepositoryImpl::PureFunction - Repositories have I/O, can't be pure
6. PureFunction::ExternalIO - Pure functions have no side effects
7. EventHandler::ReturnsValue - Event handlers are fire-and-forget
8. TestFunction::ModifiesProductionData - Tests touching production is catastrophic
9. APIHandler::InternalOnly - APIs must have external boundary
10. Service::GlobalState - Services in DDD/Clean are stateless

## The Four Forces of Software

1. **Strong Force** = Responsibility (Domain)
   - What the element DOES in the domain
   - 32 possible values: Create, Update, Delete, FindById, etc.

2. **Electromagnetic Force** = Purity (side-effects)
   - Can or cannot touch the external world
   - 4 possible values: Pure, Impure, Idempotent, ExternalIO

3. **Weak Force** = Boundary (layer)
   - Where the element lives in topology
   - 6 possible values: Domain, Application, Infra, Adapter, API, Test

4. **Gravity** = Lifecycle (temporal)
   - When the element exists and how it dies
   - 5 possible values: Singleton, Scoped, Transient, Ephemeral, Immortal

## Mathematical Properties

- Total theoretical space: 384 sub-hadrons
- Possible patterns: 342 (89.1%)
- Impossible patterns: 42 (10.9%)
- The 10.9% corresponds to the "antimatter" region of the theory

## Practical Applications

The Spectrometer v10 tool:
1. Analyzes code AST and symbolic scope
2. Maps each element to one of the 342 possible sub-hadrons
3. Detects the 42 impossible patterns as "black holes"
4. Provides architectural insights in minutes instead of hours

## Validation

- Tested on 28 repositories (10k-120k LOC, 5 languages)
- Reduced comprehension time from 4.2 hours to 6.8 minutes (-97.3%)
- Reduced dependency graph from 12,000+ nodes to average 214 nodes (-98.2%)
- 100% detection rate of CQRS/DDD violations in test cases
"""
    return summary

def extract_specific_patterns(nodes):
    """Extract specific HAIKU patterns mentioned in the text."""
    patterns = []

    for node in nodes:
        text = node.get('text', '')

        # Look for pattern examples
        if '::' in text:
            # Extract all pattern::subpattern combinations
            matches = re.findall(r'(\w+)::(\w+)', text)
            for parent, child in matches:
                patterns.append({
                    'parent': parent,
                    'child': child,
                    'full': f"{parent}::{child}",
                    'context': 'example' if 'exemplo' in text.lower() else 'theoretical'
                })

    # Get unique patterns
    unique_patterns = {}
    for p in patterns:
        key = p['full']
        if key not in unique_patterns:
            unique_patterns[key] = p

    return list(unique_patterns.values())

def main():
    # Load the canvas
    canvas = load_json('/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas')

    print("\n" + "="*80)
    print("STANDARD MODEL OF SOFTWARE ARCHITECTURE - DEEP ANALYSIS")
    print("="*80)

    # Get all text nodes
    text_nodes = [n for n in canvas['nodes'] if n.get('type') == 'text']

    # Extract concepts
    concepts = extract_concepts_from_large_texts(text_nodes)
    patterns = extract_specific_patterns(text_nodes)

    print("\n📊 THEORY STRUCTURE:")
    print(f"  • 11 Laws of Physics (fundamental constraints)")
    print(f"  • 12 Quarks/Continents (basic particles)")
    print(f"  • 96 Hadrons (composite particles)")
    print(f"  • 384 Sub-hadrons (342 possible + 42 impossible)")

    print("\n⚛️  THE FOUR FORCES MAPPING:")
    for force in concepts['four_forces']:
        print(f"  • {force['force']:<20} → {force['software_dimension']}")
        print(f"    {force['description']}")

    print(f"\n🚫 THE 42 IMPOSSIBLE PATTERNS (Architectural Antimatter):")
    for i, pattern in enumerate(concepts['impossible_patterns'][:10], 1):
        print(f"  {i:2d}. {pattern}")
    if len(concepts['impossible_patterns']) > 10:
        print(f"  ... and {len(concepts['impossible_patterns']) - 10} more")

    print(f"\n📈 HAIKU FREQUENCY EXAMPLES (from repository analysis):")
    sorted_haikus = sorted(concepts['haiku_examples'], key=lambda x: x['frequency'], reverse=True)
    for haiku in sorted_haikus[:8]:
        status = "Ubiquitous" if haiku['frequency'] > 90 else "Rare" if haiku['frequency'] < 1 else "Common"
        print(f"  • {haiku['pattern']:<30} | {haiku['frequency']:5.1f}% | {status}")

    print(f"\n🔬 KEY THEOREMS:")
    for i, theorem in enumerate(concepts['key_theorems'], 1):
        print(f"  {i}. {theorem}")

    print(f"\n🎯 SPECTROMETER v10 CAPABILITIES:")
    for feature in concepts['spectrometer_features'][:5]:
        if feature:
            print(f"  • {feature.strip('- ')}")

    print("\n" + "="*80)

    # Save detailed theory summary
    with open('/Users/lech/PROJECTS_all/PROJECT_elements/theory_summary.md', 'w', encoding='utf-8') as f:
        f.write(generate_theory_summary())

    print("✅ Detailed theory summary saved to: theory_summary.md")
    print("\n🎯 Analysis complete!")

if __name__ == "__main__":
    main()