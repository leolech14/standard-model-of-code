#!/usr/bin/env python3
"""
Quick launcher for the Canonical Visualizer.

Usage:
    python visualize.py <analysis.json>
    python visualize.py output/learning/unified_analysis.json
"""

import sys
import webbrowser
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analytics import CanonicalVisualizer


def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <analysis.json> [output.html]")
        print("\nExamples:")
        print("  python visualize.py output/learning/unified_analysis.json")
        print("  python visualize.py unified_analysis.json my_viz.html")
        return

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    viz = CanonicalVisualizer()
    out = viz.generate(input_path, output_path)
    viz.print_report()

    # Auto-open in browser
    print(f"\nOpening: {out}")
    webbrowser.open(f"file://{out.absolute()}")


if __name__ == "__main__":
    main()
