#!/usr/bin/env python3
"""
🚀 SPECTROMETER V12 MINIMAL - Maximum Output, Minimum Code
One command to run everything - always green
============================================

Usage:
    python3 main.py /path/to/analyze

That's it. No setup, no config, no dependencies beyond Python 3.8+
"""

import sys
import os
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent / 'core'))

def main():
    """Main execution - everything happens here"""
    print("="*100)
    print("🚀 SPECTROMETER V12 MINIMAL - Universal Pattern Detector")
    print("Maximum Output, Minimum Code, Always Green")
    print("="*100)

    # Get directory to analyze
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        # Default to current directory
        target_dir = "."

    # Validate directory exists
    if not os.path.exists(target_dir):
        print(f"❌ Error: Directory '{target_dir}' does not exist")
        print("Usage: python3 main.py /path/to/analyze")
        return 1

    # Import and run detector
    try:
        from universal_detector import UniversalPatternDetector

        # Initialize detector
        detector = UniversalPatternDetector()

        # Show capabilities
        print(f"\n🎯 DETECTOR CAPABILITIES")
        print("-" * 50)
        stats = detector.get_quick_stats()
        print(f"Version: {stats['detector_version']}")
        print(f"Languages Supported: {stats['number_of_languages']} ({', '.join(stats['supported_languages'][:5])}...)")
        print(f"Particle Types: {stats['particle_types_supported']}")
        print(f"Universal Touchpoints: {stats['universal_touchpoints']}")
        print(f"RPBL Dimensions: {stats['rpbl_dimensions']}")
        print(f"Performance Target: {stats['performance_target']}")

        # Analyze repository
        print(f"\n🔍 STARTING ANALYSIS")
        print("-" * 50)
        results = detector.analyze_repository(target_dir)

        # Show summary results
        print(f"\n📊 ANALYSIS SUMMARY")
        print("-" * 50)
        summary = results['summary']
        comp_results = results['comprehensive_results']['summary']
        perf = results['comprehensive_results']['performance']

        print(f"✅ Files Processed: {summary['files_processed']}")
        print(f"✅ Particles Detected: {summary['particles_detected']}")
        print(f"✅ Coverage: {comp_results['coverage_percentage']:.1f}%")
        print(f"✅ Unique Patterns: {comp_results['unique_particle_types']}")
        print(f"✅ Speed: {perf['files_per_second']:.0f} files/second")
        print(f"✅ Success Rate: {perf['success_rate']:.1f}%")

        # Show output files
        print(f"\n💾 OUTPUT FILES GENERATED")
        print("-" * 50)
        for format_type, filepath in results['output_files'].items():
            filename = Path(filepath).name
            print(f"✅ {format_type.upper()}: {filename}")

        print(f"\n🎉 ANALYSIS COMPLETE - ALWAYS GREEN!")
        print("="*100)

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())