#!/usr/bin/env python3
"""
SUBDIVISION STABILITY ANALYZER

Measures the "optimal subdivision count" hypothesis:
- At each level of the filesystem, how many immediate children?
- Is there a stable pattern (e.g., 5-7 children per directory)?
- Do directories with too many children indicate organization problems?

Theory:
  If human cognition limits comprehension to ~7 items (Miller's Law),
  then well-organized systems should have ~5-7 subdivisions at each level.

Usage:
    python measure_subdivision_stability.py
    python measure_subdivision_stability.py --path particle/
    python measure_subdivision_stability.py --visualize

Output:
    subdivision_analysis.json - Complete data
    subdivision_analysis.md - Human-readable report
    subdivision_histogram.txt - ASCII visualization
"""

import os
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from statistics import mean, median, stdev

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.pytest_cache', '.mypy_cache'}

class SubdivisionAnalyzer:
    """Analyze subdivision patterns across filesystem hierarchy."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.data = []

    def analyze(self):
        """Walk filesystem and measure subdivisions."""
        for root, dirs, files in os.walk(self.repo_root):
            # Filter excluded directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            root_path = Path(root)
            depth = len(root_path.relative_to(self.repo_root).parts)

            immediate_children = len(dirs) + len(files)
            immediate_dirs = len(dirs)
            immediate_files = len(files)

            if immediate_children > 0:  # Only count non-empty directories
                self.data.append({
                    'path': str(root_path.relative_to(self.repo_root)),
                    'depth': depth,
                    'total_children': immediate_children,
                    'subdirs': immediate_dirs,
                    'files': immediate_files,
                })

        print(f"Analyzed {len(self.data)} directories")

    def compute_statistics(self):
        """Compute summary statistics."""
        if not self.data:
            return {}

        counts = [d['total_children'] for d in self.data]
        dir_counts = [d['subdirs'] for d in self.data]

        by_depth = defaultdict(list)
        for d in self.data:
            by_depth[d['depth']].append(d['total_children'])

        return {
            'total_directories': len(self.data),
            'overall': {
                'mean': round(mean(counts), 2),
                'median': median(counts),
                'mode': Counter(counts).most_common(1)[0][0] if counts else 0,
                'stdev': round(stdev(counts), 2) if len(counts) > 1 else 0,
                'min': min(counts),
                'max': max(counts),
            },
            'subdirs_only': {
                'mean': round(mean(dir_counts), 2),
                'median': median(dir_counts),
                'mode': Counter(dir_counts).most_common(1)[0][0] if dir_counts else 0,
            },
            'by_depth': {
                depth: {
                    'mean': round(mean(counts), 2),
                    'median': median(counts),
                    'count': len(counts)
                }
                for depth, counts in sorted(by_depth.items())
            },
            'distribution': dict(Counter(counts).most_common(20)),
            'outliers_high': [d for d in self.data if d['total_children'] > 12],  # >12 = too many
            'optimal_range': [d for d in self.data if 4 <= d['total_children'] <= 9],  # 4-9 = optimal
        }

    def find_unstable_directories(self, stats):
        """Find directories that violate optimal subdivision."""
        outliers = []

        for d in self.data:
            count = d['total_children']

            # Too many children (> 12)
            if count > 12:
                outliers.append({
                    'path': d['path'],
                    'count': count,
                    'issue': 'TOO_MANY',
                    'severity': 'HIGH' if count > 20 else 'MEDIUM',
                    'recommendation': 'Consider creating subdirectories to group related items'
                })

            # Singleton directory (1 child)
            elif count == 1 and d['subdirs'] == 1:
                outliers.append({
                    'path': d['path'],
                    'count': count,
                    'issue': 'SINGLETON',
                    'severity': 'LOW',
                    'recommendation': 'Consider flattening (merge parent and child)'
                })

        return outliers

    def generate_report(self, output_dir: Path):
        """Generate analysis reports."""
        output_dir.mkdir(parents=True, exist_ok=True)

        stats = self.compute_statistics()
        outliers = self.find_unstable_directories(stats)

        # JSON report
        report = {
            'generated': '2026-01-28',
            'repo_root': str(self.repo_root),
            'statistics': stats,
            'outliers': outliers,
            'hypothesis_test': {
                'miller_law_range': [5, 9],  # 7 ± 2
                'observed_median': stats['overall']['median'],
                'observed_mode': stats['overall']['mode'],
                'in_optimal_range': 5 <= stats['overall']['median'] <= 9,
                'optimal_range_pct': len(stats['optimal_range']) / len(self.data) * 100,
            }
        }

        json_path = output_dir / 'subdivision_analysis.json'
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Markdown report
        md_path = output_dir / 'subdivision_analysis.md'
        with open(md_path, 'w') as f:
            f.write("# Subdivision Stability Analysis\n\n")
            f.write(f"**Generated:** 2026-01-28\n")
            f.write(f"**Repo:** {self.repo_root}\n\n")

            f.write("## Summary Statistics\n\n")
            f.write(f"- **Total directories:** {stats['total_directories']}\n")
            f.write(f"- **Mean children per directory:** {stats['overall']['mean']}\n")
            f.write(f"- **Median children:** {stats['overall']['median']}\n")
            f.write(f"- **Mode (most common):** {stats['overall']['mode']}\n\n")

            f.write("## Hypothesis Test: Optimal Range = 5-9 (Miller's Law)\n\n")
            f.write(f"- **Observed median:** {stats['overall']['median']}\n")
            f.write(f"- **In optimal range?** {report['hypothesis_test']['in_optimal_range']}\n")
            f.write(f"- **% directories in optimal range:** {report['hypothesis_test']['optimal_range_pct']:.1f}%\n\n")

            f.write("## Distribution\n\n")
            f.write("| Children | Directories |\n")
            f.write("|----------|-------------|\n")
            for count, freq in sorted(stats['distribution'].items()):
                f.write(f"| {count:2d} | {freq:4d} |\n")

            f.write("\n## Outliers (Too Many Children)\n\n")
            for outlier in sorted(outliers, key=lambda x: x['count'], reverse=True)[:20]:
                if outlier['issue'] == 'TOO_MANY':
                    f.write(f"- **{outlier['count']}** children | {outlier['path']}\n")

        print(f"✅ Generated reports in {output_dir}/")
        print(f"   Median subdivision: {stats['overall']['median']}")
        print(f"   In optimal range (5-9)? {report['hypothesis_test']['in_optimal_range']}")


def main():
    parser = argparse.ArgumentParser(description='Measure subdivision stability')
    parser.add_argument('--path', type=str, default='.',
                        help='Path to analyze (default: repo root)')
    parser.add_argument('--output', '-o', type=str, default='./.subdivision_analysis',
                        help='Output directory')
    args = parser.parse_args()

    repo_path = Path(args.path).resolve()
    print(f"Analyzing: {repo_path}")

    analyzer = SubdivisionAnalyzer(repo_path)
    analyzer.analyze()
    analyzer.generate_report(Path(args.output))


if __name__ == "__main__":
    main()
