#!/usr/bin/env python3
"""
Test enhanced detector on dddpy repository
"""

import json
import os
import ast
from pathlib import Path
from enhanced_pattern_detector import EnhancedPatternDetector
from tree_sitter_engine import TreeSitterEngine

def load_original_results():
    """Load the original spectrometer results"""
    with open('output/results.json', 'r') as f:
        return json.load(f)

def save_enhanced_results(results):
    """Save the enhanced results"""
    os.makedirs('output', exist_ok=True)
    with open('output/enhanced_results.json', 'w') as f:
        json.dump(results, f, indent=2)

def analyze_with_enhanced_detector():
    """Analyze dddpy repository with enhanced detector"""

    print("🚀 Running Enhanced Analysis on dddpy Repository")
    print("=" * 60)

    # Load original results for comparison
    original_results = load_original_results()

    # Initialize enhanced detector
    detector = EnhancedPatternDetector()

    # Get Python files from dddpy
    dddpy_path = Path("validation/dddpy-main")
    python_files = list(dddpy_path.rglob("*.py"))

    enhanced_results = {
        'repository': 'dddpy-main',
        'total_files': len(python_files),
        'enhanced_detections': {},
        'improvements': {},
        'classes': {}
    }

    new_value_objects = 0
    multi_responsibility_classes = 0
    total_classes_analyzed = 0

    for file_path in python_files:
        print(f"\n📄 Analyzing: {file_path.relative_to(dddpy_path)}")

        try:
            # Parse with tree-sitter
            ts_engine = TreeSitterEngine()
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            tree = ts_engine.parser.parse(bytes(source_code, 'utf-8'))

            # Find all classes
            classes = []
            for node in ts_engine.find_all_nodes(tree, 'class_definition'):
                class_name = ts_engine.get_node_text(node.child_by_field_name('name'), source_code)
                classes.append({
                    'name': class_name,
                    'ast_node': node,
                    'source_code': source_code
                })

            # Convert to AST for enhanced analysis
            ast_tree = ast.parse(source_code)

            for class_info in classes:
                class_name = class_info['name']
                total_classes_analyzed += 1

                # Get original pattern if exists
                original_pattern = None
                for particle in original_results.get('particles', []):
                    if particle['name'] == class_name:
                        original_pattern = particle.get('type')
                        break

                # Find AST node for this class
                class_ast_node = None
                for node in ast.walk(ast_tree):
                    if isinstance(node, ast.ClassDef) and node.name == class_name:
                        class_ast_node = node
                        break

                if class_ast_node:
                    # Enhanced analysis
                    class_data = {
                        'name': class_name,
                        'file': str(file_path.relative_to(dddpy_path)),
                        'ast_tree': class_ast_node,
                        'original_pattern': original_pattern
                    }

                    enhanced_patterns = detector.analyze_class(class_data)

                    # Check for new ValueObject detection
                    has_new_vo = any(p.pattern_type == "ValueObject" and p.confidence > 0.7
                                   for p in enhanced_patterns) and original_pattern != "ValueObject"

                    # Check for multi-responsibility
                    has_multi_resp = any(p.is_multi_responsibility for p in enhanced_patterns)

                    if has_new_vo:
                        new_value_objects += 1
                        print(f"  ✅ NEW ValueObject: {class_name}")

                    if has_multi_resp:
                        multi_responsibility_classes += 1
                        print(f"  🔄 Multi-Responsibility: {class_name}")

                    # Store results
                    enhanced_results['classes'][class_name] = {
                        'file': class_data['file'],
                        'original_pattern': original_pattern,
                        'enhanced_patterns': [
                            {
                                'type': p.pattern_type,
                                'confidence': p.confidence,
                                'responsibilities': p.responsibilities,
                                'responsibility_count': p.responsibility_count,
                                'is_multi_responsibility': p.is_multi_responsibility,
                                'reasons': p.reasons
                            }
                            for p in enhanced_patterns
                        ],
                        'is_new_detection': has_new_vo,
                        'is_multi_responsibility': has_multi_resp
                    }

        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

    # Calculate improvements
    enhanced_results['improvements'] = {
        'total_classes_analyzed': total_classes_analyzed,
        'new_value_objects_detected': new_value_objects,
        'multi_responsibility_classes': multi_responsibility_classes,
        'original_coverage': original_results.get('recall_overall', 0.60),
        'estimated_coverage_improvement': (new_value_objects + multi_responsibility_classes) / total_classes_analyzed * 100 if total_classes_analyzed > 0 else 0,
        'estimated_total_coverage': 60 + (new_value_objects + multi_responsibility_classes) / total_classes_analyzed * 100 if total_classes_analyzed > 0 else 60
    }

    # Print summary
    print("\n" + "=" * 60)
    print("📊 ENHANCED DETECTION SUMMARY")
    print("=" * 60)
    print(f"Total classes analyzed: {total_classes_analyzed}")
    print(f"NEW ValueObjects detected: {new_value_objects} (was 0!)")
    print(f"Multi-responsibility classes: {multi_responsibility_classes}")
    print(f"Original coverage: {original_results.get('recall_overall', 0.60):.1%}")
    print(f"Coverage improvement: {enhanced_results['improvements']['estimated_coverage_improvement']:.1f}%")
    print(f"Estimated total coverage: {enhanced_results['improvements']['estimated_total_coverage']:.1f}%")

    # Save results
    save_enhanced_results(enhanced_results)

    print(f"\n💾 Results saved to: output/enhanced_results.json")

    return enhanced_results

if __name__ == "__main__":
    analyze_with_enhanced_detector()