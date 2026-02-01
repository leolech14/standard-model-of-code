#!/usr/bin/env python3
"""
🚀 SPECTROMETER V12 - God Class Antimatter Detector
Universal polyglot analysis for God Classes with 3D visualization
==============================================================

Usage:
    python3 god_class_main.py https://github.com/spring-projects/spring-boot
    python3 god_class_main.py /path/to/local/repo
    python3 god_class_main.py .  # Analyze current directory
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def clone_repo_if_needed(target: str) -> str:
    """Clone repository if URL is provided"""
    if target.startswith(('http://', 'https://', 'git@')):
        print(f"📥 Cloning repository: {target}")

        # Create temp directory
        repo_name = target.split('/')[-1].replace('.git', '')
        clone_dir = f'temp_{repo_name}'

        # Remove existing temp directory
        if os.path.exists(clone_dir):
            subprocess.run(['rm', '-rf', clone_dir])

        # Clone repository
        result = subprocess.run(['git', 'clone', target, clone_dir],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Error cloning repository: {result.stderr}")
            sys.exit(1)

        print(f"✅ Repository cloned to: {clone_dir}")
        return clone_dir
    else:
        return target

def main():
    """Main execution"""
    print("="*100)
    print("🔬 SPECTROMETER V12 - God Class Antimatter Detector")
    print("Universal Polyglot Analysis with 3D Visualization")
    print("="*100)

    # Get target repository
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "."  # Default to current directory

    # Clone if URL provided
    repo_path = clone_repo_if_needed(target)

    # Validate path exists
    if not os.path.exists(repo_path):
        print(f"❌ Error: Path '{repo_path}' does not exist")
        print("Usage: python3 god_class_main.py <repo_url_or_path>")
        sys.exit(1)

    try:
        # Import detector
        sys.path.insert(0, 'core')
        from god_class_detector import GodClassDetector

        # Initialize detector
        detector = GodClassDetector()

        # Show detector capabilities
        print(f"\n🎯 GOD CLASS DETECTOR CAPABILITIES")
        print("-" * 60)
        print(f"🔍 Supported Languages: Python, Java, TypeScript, Go, Rust, Kotlin, C#")
        print(f"📊 Risk Factors: Size, Method Count, Responsibility Overload")
        print(f"🌐 Touchpoints: Coordination, Business Logic, Data Access, UI, Infrastructure")
        print(f"⚡ Antimatter Threshold: >80% risk score")
        print(f"📈 Visualization: 3D exploding nodes + risk distribution charts")

        # Analyze repository
        print(f"\n🔍 STARTING GOD CLASS ANALYSIS")
        print("-" * 60)
        results = detector.analyze_repository(repo_path)

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

        # Show top God Classes
        god_classes = results['god_classes']
        if god_classes:
            print(f"\n🏆 TOP 10 HIGHEST RISK GOD CLASSES")
            print("-" * 60)
            sorted_god_classes = sorted(god_classes,
                                      key=lambda x: x.antimatter_risk_score,
                                      reverse=True)[:10]

            print(f"{'Risk':<8} | {'Class Name':<30} | {'Language':<12} | {'LOC':<6} | {'Methods':<8} | {'Touchpoints':<12}")
            print("-" * 90)

            for gc in sorted_god_classes:
                print(f"{gc.antimatter_risk_score:.1f}%{'':<5} | {gc.class_name[:28]:<30} | {gc.language:<12} | "
                      f"{gc.lines_of_code:<6} | {gc.method_count:<8} | {gc.touchpoint_overload:.1f}%{'':<7}")

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

        # Generate visualizations
        if god_classes:
            print(f"\n📊 GENERATING VISUALIZATIONS")
            print("-" * 60)

            output_dir = Path('god_class_output')
            output_dir.mkdir(exist_ok=True)

            # 3D visualization
            viz_path = output_dir / 'god_class_3d_visualization.png'
            detector.generate_3d_visualization(god_classes, str(viz_path))

            # Save detailed results
            results_path = output_dir / 'god_class_analysis.json'
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            print(f"✅ Results saved to: {output_dir}")
            print(f"   • 3D Visualization: {viz_path}")
            print(f"   • Detailed Analysis: {results_path}")

        # Example refactor suggestions
        if god_classes:
            worst_class = sorted(god_classes, key=lambda x: x.antimatter_risk_score, reverse=True)[0]
            print(f"\n🔧 EXAMPLE REFACTOR: {worst_class.class_name}")
            print("-" * 60)
            print(f"Current Issues:")
            print(f"   • {worst_class.lines_of_code} lines of code (too large)")
            print(f"   • {worst_class.method_count} methods (too many responsibilities)")
            print(f"   • {worst_class.responsibility_count} different touchpoints")
            print(f"\nSuggested Refactoring:")
            for suggestion in worst_class.suggested_refactors[:3]:
                print(f"   • {suggestion}")

        print(f"\n🎉 GOD CLASS ANALYSIS COMPLETE!")
        print("="*100)

        # Cleanup if we cloned a repo
        if repo_path.startswith('temp_'):
            cleanup = input("\n🗑️  Remove temporary cloned repository? (y/N): ")
            if cleanup.lower() == 'y':
                subprocess.run(['rm', '-rf', repo_path])
                print(f"✅ Cleaned up: {repo_path}")

        return 0

    except ImportError as e:
        print(f"❌ Error: Missing dependencies: {e}")
        print("Please install: pip install matplotlib numpy")
        return 1
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
