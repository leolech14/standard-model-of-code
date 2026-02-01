#!/usr/bin/env python3
"""
🚀 SPECTROMETER V12 - God Class Antimatter Detector (Lite Version)
Immediate testing without external dependencies
===============================================

Usage:
    python3 god_class_lite_main.py https://github.com/spring-projects/spring-boot
    python3 god_class_lite_main.py /path/to/local/repo
    python3 god_class_lite_main.py .  # Analyze current directory
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def main():
    """Main execution"""
    print("="*100)
    print("🔬 SPECTROMETER V12 - God Class Antimatter Detector (Lite Version)")
    print("Universal Polyglot Analysis - No Dependencies Required")
    print("="*100)

    # Get target repository
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "."  # Default to current directory

    # For URL, would need git clone - skip for demo
    if target.startswith(('http://', 'https://')):
        print(f"📥 URL detected: {target}")
        print("⚠️  For demo, analyzing current directory instead")
        target = "."

    # Validate path exists
    if not os.path.exists(target):
        print(f"❌ Error: Path '{target}' does not exist")
        print("Usage: python3 god_class_lite_main.py <path_to_repo>")
        sys.exit(1)

    try:
        # Import detector
        sys.path.insert(0, 'core')
        from god_class_detector_lite import GodClassDetectorLite

        # Initialize detector
        detector = GodClassDetectorLite()

        # Show detector capabilities
        print(f"\n🎯 GOD CLASS DETECTOR CAPABILITIES")
        print("-" * 60)
        print(f"🔍 Supported Languages: Python, Java, TypeScript, Go, Rust, Kotlin, C#")
        print(f"📊 Risk Factors: Size, Method Count, Responsibility Overload")
        print(f"🌐 Touchpoints: Coordination, Business Logic, Data Access, UI, Infrastructure")
        print(f"⚡ Antimatter Threshold: >80% risk score")
        print(f"📈 Visualization: ASCII charts + JSON export")

        # Analyze repository
        print(f"\n🔍 STARTING GOD CLASS ANALYSIS")
        print("-" * 60)
        results = detector.analyze_repository(target)

        # Show summary results
        summary = results['summary']
        print(f"\n📊 ANALYSIS SUMMARY")
        print("-" * 60)
        print(f"📁 Languages Detected: {', '.join(summary['languages_detected'])}")
        print(f"📋 Total Classes Analyzed: {summary['total_classes_analyzed']}")
        print(f"⚠️  God Classes Found: {summary['god_classes_found']}")
        print(f"☢️  Antimatter Risk Classes: {summary['antimatter_risk_classes']}")
        print(f"📈 Average Risk Score: {summary['average_risk_score']:.1f}%")

        # Risk distribution
        risk_dist = results['risk_distribution']
        print(f"\n🎲 RISK DISTRIBUTION")
        print("-" * 60)
        print(f"🔴 Critical (>90%): {risk_dist['critical_risk']}")
        print(f"🟠 High (80-90%): {risk_dist['high_risk']}")
        print(f"🟡 Medium (60-80%): {risk_dist['medium_risk']}")
        print(f"🟢 Low (<60%): {risk_dist['low_risk']}")

        # ASCII Visualization
        detector.generate_ascii_visualization(results['god_classes'])

        # Show detailed God Classes
        god_classes = results['god_classes']
        if god_classes:
            print(f"\n🏆 DETAILED GOD CLASS ANALYSIS")
            print("-" * 100)
            print(f"{'Risk':<8} | {'Class Name':<30} | {'Language':<10} | {'LOC':<6} | {'Methods':<8} | {'Resp':<6} | {'Top Refactor'}")
            print("-" * 100)

            # Show only God Classes
            god_classes_only = [gc for gc in god_classes if gc.is_god_class]
            sorted_god_classes = sorted(god_classes_only,
                                      key=lambda x: x.antimatter_risk_score,
                                      reverse=True)

            for gc in sorted_god_classes:
                top_refactor = gc.suggested_refactors[0][:20] if gc.suggested_refactors else "None"
                print(f"{gc.antimatter_risk_score:.1f}%{'':<5} | {gc.class_name[:28]:<30} | {gc.language:<10} | "
                      f"{gc.lines_of_code:<6} | {gc.method_count:<8} | {gc.responsibility_count:<6} | {top_refactor}")

        # Show refactoring recommendations
        recommendations = results['recommendations']
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 60)

        if recommendations['priority_actions']:
            print(f"🚨 Priority Actions:")
            for action in recommendations['priority_actions']:
                print(f"   • {action}")

        if recommendations['architectural_patterns']:
            print(f"\n🏗️  Architectural Patterns to Apply:")
            for pattern in recommendations['architectural_patterns'][:5]:
                print(f"   • {pattern}")

        if recommendations['risk_mitigation']:
            print(f"\n🛡️  Risk Mitigation:")
            for mitigation in recommendations['risk_mitigation']:
                print(f"   • {mitigation}")

        # Save results to JSON
        output_dir = Path('god_class_output')
        output_dir.mkdir(exist_ok=True)

        results_path = output_dir / 'god_class_analysis_lite.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 Results saved to: {results_path}")

        # Example detailed refactor plan
        if god_classes_only:
            worst_class = sorted(god_classes_only, key=lambda x: x.antimatter_risk_score, reverse=True)[0]
            print(f"\n🔧 DETAILED REFACTOR PLAN: {worst_class.class_name}")
            print("-" * 60)
            print(f"📊 Current Metrics:")
            print(f"   • Lines of Code: {worst_class.lines_of_code}")
            print(f"   • Method Count: {worst_class.method_count}")
            print(f"   • Responsibility Overload: {worst_class.responsibility_count} touchpoints")
            print(f"   • Antimatter Risk: {worst_class.antimatter_risk_score:.1f}%")
            print(f"\n🎯 Touchpoint Analysis:")
            print(f"   • Coordination: {worst_class.coordination_touchpoints}")
            print(f"   • Business Logic: {worst_class.business_logic_touchpoints}")
            print(f"   • Data Access: {worst_class.data_access_touchpoints}")
            print(f"   • UI Interaction: {worst_class.ui_touchpoints}")
            print(f"   • Infrastructure: {worst_class.infrastructure_touchpoints}")
            print(f"\n🔧 Step-by-Step Refactoring:")
            for i, suggestion in enumerate(worst_class.suggested_refactors, 1):
                print(f"   {i}. {suggestion}")

            print(f"\n🎯 Expected Outcome:")
            print(f"   • Split into {max(2, len(worst_class.suggested_refactors))} focused classes")
            print(f"   • Reduce lines of code by ~60%")
            print(f"   • Single responsibility per class")
            print(f"   • Antimatter risk <30%")

        print(f"\n🎉 GOD CLASS ANALYSIS COMPLETE!")
        print("="*100)

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
