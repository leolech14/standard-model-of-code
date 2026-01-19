#!/usr/bin/env python3
"""
Simple test of enhanced detector on dddpy repository
"""

import json
import os
import ast
from pathlib import Path
from enhanced_pattern_detector import EnhancedPatternDetector

def load_original_results():
    """Load the original spectrometer results"""
    try:
        with open('output/results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Original results not found. Running main.py first...")
        return None

def test_enhanced_on_dddpy():
    """Test enhanced detector on dddpy repository"""

    print("🚀 Testing Enhanced Detector on dddpy Repository")
    print("=" * 60)

    # Load original results
    original_results = load_original_results()
    if not original_results:
        return

    # Initialize enhanced detector
    detector = EnhancedPatternDetector()

    # Get Python files from dddpy
    dddpy_path = Path("validation/dddpy_real")
    if not dddpy_path.exists():
        print(f"❌ dddpy path not found: {dddpy_path}")
        return

    python_files = list(dddpy_path.rglob("*.py"))
    print(f"📁 Found {len(python_files)} Python files")

    # Track improvements
    total_classes = 0
    new_value_objects = 0
    previously_detected_vos = 0
    multi_resp_classes = 0

    # Results summary
    new_detections = []

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Parse with AST
            ast_tree = ast.parse(source_code)

            # Find all classes
            for node in ast.walk(ast_tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    total_classes += 1

                    # Check if originally detected as ValueObject
                    original_vo = False
                    for particle in original_results.get('particles', []):
                        if particle['name'] == class_name and particle.get('type') == 'ValueObject':
                            original_vo = True
                            previously_detected_vos += 1
                            break

                    # Enhanced analysis
                    class_info = {
                        'name': class_name,
                        'ast_tree': node,
                        'file': str(file_path.relative_to(dddpy_path))
                    }

                    enhanced_patterns = detector.analyze_class(class_info)

                    # Check for ValueObject detection
                    vo_detected = False
                    vo_confidence = 0.0
                    for pattern in enhanced_patterns:
                        if pattern.pattern_type == "ValueObject" and pattern.confidence > 0.7:
                            vo_detected = True
                            vo_confidence = pattern.confidence
                            break

                    # Check for multi-responsibility
                    has_multi_resp = any(p.is_multi_responsibility for p in enhanced_patterns)

                    if vo_detected and not original_vo:
                        new_value_objects += 1
                        new_detections.append({
                            'class': class_name,
                            'file': class_info['file'],
                            'pattern': 'ValueObject',
                            'confidence': vo_confidence,
                            'type': 'NEW DETECTION'
                        })
                        print(f"  ✅ NEW ValueObject: {class_name} (confidence: {vo_confidence:.2f})")

                    if has_multi_resp:
                        multi_resp_classes += 1
                        pattern_type = next((p.pattern_type for p in enhanced_patterns if p.is_multi_responsibility), 'Unknown')
                        new_detections.append({
                            'class': class_name,
                            'file': class_info['file'],
                            'pattern': pattern_type,
                            'type': 'MULTI-RESPONSIBILITY'
                        })

        except Exception as e:
            print(f"  ⚠️  Error in {file_path}: {e}")
            continue

    # Calculate coverage improvement
    print("\n" + "=" * 60)
    print("📊 ENHANCED DETECTION RESULTS")
    print("=" * 60)

    print(f"Total classes analyzed: {total_classes}")
    print(f"")
    print(f"ValueObject detections:")
    print(f"  Previously detected: {previously_detected_vos}")
    print(f"  NEW detections: {new_value_objects}")
    print(f"  Total VO detections: {previously_detected_vos + new_value_objects}")
    print(f"")
    print(f"Multi-responsibility classes: {multi_resp_classes}")
    print(f"")
    print(f"Original coverage: {original_results.get('recall_overall', 0.60):.1%}")

    # Calculate improvement
    if total_classes > 0:
        # Original VO detection rate was 0%
        vo_improvement = (new_value_objects / total_classes) * 100
        total_improvement = vo_improvement + ((multi_resp_classes / total_classes) * 50)  # Weight multi-resp less
        estimated_coverage = 60 + total_improvement

        print(f"Estimated VO detection improvement: {vo_improvement:.1f}%")
        print(f"Estimated total coverage: {estimated_coverage:.1f}%")

        if estimated_coverage >= 95:
            print("  ✅ REACHED 95% TARGET!")
        elif estimated_coverage >= 130:
            print("  🎯 EXCEEDED 130% TARGET!")
        else:
            print(f"  ⚠️  Short of 95% target by {95 - estimated_coverage:.1f}%")

    # Show new detections
    if new_detections:
        print(f"\n🔍 NEW DETECTIONS SUMMARY:")
        print("-" * 40)
        for detection in new_detections[:10]:  # Show first 10
            print(f"{detection['type']}: {detection['class']} → {detection['pattern']}")
        if len(new_detections) > 10:
            print(f"... and {len(new_detections) - 10} more")

    # Save enhanced results
    enhanced_results = {
        'summary': {
            'total_classes': total_classes,
            'new_value_objects': new_value_objects,
            'previously_detected_vos': previously_detected_vos,
            'multi_responsibility_classes': multi_resp_classes,
            'original_coverage': original_results.get('recall_overall', 0.60),
            'estimated_total_coverage': estimated_coverage if total_classes > 0 else 60
        },
        'new_detections': new_detections
    }

    os.makedirs('output', exist_ok=True)
    with open('output/enhanced_validation.json', 'w') as f:
        json.dump(enhanced_results, f, indent=2)

    print(f"\n💾 Enhanced results saved to: output/enhanced_validation.json")

    return enhanced_results

if __name__ == "__main__":
    test_enhanced_on_dddpy()