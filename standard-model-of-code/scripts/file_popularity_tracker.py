#!/usr/bin/env python3
"""
FILE POPULARITY TRACKER - Omniscience About Repo Activity

Extends TDJ (Timestamp Daily Journal) with usage analytics to identify:
- Dead files (created but never modified)
- Popular files (frequently modified)
- Session patterns (when work happens)
- File lifetime (age without changes)
- Popularity score (modification frequency)

This is the "Big City" solution: When the repo gets too large to know everything,
this tool tells you what's actually being used vs what's forgotten.

Input:
    project_elements_file_timestamps.csv (from generate_repo_timestamps.py)

Output:
    file_popularity_report.json - Structured popularity metrics
    file_popularity_report.md - Human-readable insights
    dead_files.txt - Files created but never modified (candidates for archive)
    popular_files.txt - Top 50 most-modified files

Usage:
    python file_popularity_tracker.py
    python file_popularity_tracker.py --output /tmp/popularity/
    python file_popularity_tracker.py --dead-only  # Just list dead files

Integration:
    - Feeds to analyze.py as context (what files are actually used)
    - Feeds to graph visualization (node size = popularity)
    - Triggers for auto-archival (dead files > 90 days old)
"""

import csv
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

class FilePopularityTracker:
    """Analyze file usage patterns from timestamp journal."""

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.files = []
        self.load_data()

    def load_data(self):
        """Load timestamp CSV."""
        with open(self.csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.files.append({
                    'path': row['path'],
                    'size': int(row['size_bytes']),
                    'created': datetime.fromisoformat(row['birth_iso']),
                    'modified': datetime.fromisoformat(row['modified_iso']),
                    'created_epoch': int(row['birth_epoch']),
                    'modified_epoch': int(row['modified_epoch']),
                })

        print(f"Loaded {len(self.files)} files")

    def identify_dead_files(self) -> list:
        """Find files created but NEVER modified (dead code)."""
        dead = []
        for f in self.files:
            # If creation == modification (within 1 second tolerance)
            if abs(f['created_epoch'] - f['modified_epoch']) <= 1:
                age_days = (datetime.now() - f['created']).days
                dead.append({
                    'path': f['path'],
                    'age_days': age_days,
                    'size': f['size'],
                    'created': f['created'].isoformat()
                })
        return dead

    def compute_popularity(self) -> list:
        """Compute popularity score based on modification frequency."""
        now = datetime.now()
        scored = []

        for f in self.files:
            age_days = (now - f['created']).days
            days_since_mod = (now - f['modified']).days

            # Avoid division by zero
            if age_days < 1:
                age_days = 1

            # Popularity heuristic:
            # - Recency: recently modified = higher score
            # - Frequency proxy: (age - days_since_mod) / age
            #   If modified recently relative to age = active file
            recency_score = max(0, 1 - (days_since_mod / max(age_days, 1)))

            # Lifetime activity: created != modified suggests it's been touched
            is_active = abs(f['created_epoch'] - f['modified_epoch']) > 1

            popularity = recency_score * 100 if is_active else 0

            scored.append({
                'path': f['path'],
                'popularity': round(popularity, 2),
                'age_days': age_days,
                'days_since_mod': days_since_mod,
                'size': f['size'],
                'is_dead': not is_active
            })

        return sorted(scored, key=lambda x: x['popularity'], reverse=True)

    def analyze_sessions(self) -> dict:
        """Identify session patterns from modification timestamps."""
        # Group modifications by date
        by_date = defaultdict(int)
        by_hour = Counter()

        for f in self.files:
            date_str = f['modified'].date().isoformat()
            by_date[date_str] += 1

            hour = f['modified'].hour
            by_hour[hour] += 1

        # Find peak activity day
        peak_day = max(by_date.items(), key=lambda x: x[1]) if by_date else (None, 0)

        return {
            'total_days_active': len(by_date),
            'peak_day': peak_day[0],
            'peak_day_files': peak_day[1],
            'by_hour': dict(by_hour.most_common(24)),
            'recent_7_days': {k: v for k, v in sorted(by_date.items())[-7:]}
        }

    def generate_report(self, output_dir: Path):
        """Generate all outputs."""
        output_dir.mkdir(parents=True, exist_ok=True)

        dead = self.identify_dead_files()
        popular = self.compute_popularity()
        sessions = self.analyze_sessions()

        # JSON report
        report = {
            'generated': datetime.now().isoformat(),
            'total_files': len(self.files),
            'dead_files': len(dead),
            'dead_percentage': round(len(dead) / len(self.files) * 100, 2),
            'top_10_popular': popular[:10],
            'bottom_10_inactive': popular[-10:],
            'session_patterns': sessions,
        }

        json_path = output_dir / 'file_popularity_report.json'
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Dead files list
        dead_path = output_dir / 'dead_files.txt'
        with open(dead_path, 'w') as f:
            f.write(f"# Dead Files (created but never modified): {len(dead)}\n")
            f.write(f"# Total files: {len(self.files)}\n")
            f.write(f"# Dead percentage: {report['dead_percentage']}%\n\n")
            for d in sorted(dead, key=lambda x: x['age_days'], reverse=True):
                f.write(f"{d['age_days']:4d} days | {d['size']:8d} bytes | {d['path']}\n")

        # Popular files list
        pop_path = output_dir / 'popular_files.txt'
        with open(pop_path, 'w') as f:
            f.write(f"# Top 50 Most Popular Files (by modification recency)\n\n")
            for p in popular[:50]:
                if p['popularity'] > 0:
                    f.write(f"{p['popularity']:6.2f} | {p['days_since_mod']:4d} days ago | {p['path']}\n")

        # Markdown report
        md_path = output_dir / 'file_popularity_report.md'
        with open(md_path, 'w') as f:
            f.write("# File Popularity Report\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Total files:** {len(self.files)}\n\n")
            f.write(f"**Dead files:** {len(dead)} ({report['dead_percentage']}%)\n\n")
            f.write(f"**Peak activity:** {sessions['peak_day']} ({sessions['peak_day_files']} files)\n\n")

            f.write("## Top 20 Popular Files\n\n")
            for p in popular[:20]:
                if p['popularity'] > 0:
                    f.write(f"- **{p['popularity']:.1f}** - {p['path']} ({p['days_since_mod']} days ago)\n")

            f.write("\n## Session Patterns\n\n")
            f.write(f"Active days: {sessions['total_days_active']}\n\n")
            f.write("Recent 7 days:\n")
            for date, count in sessions['recent_7_days'].items():
                f.write(f"- {date}: {count} files\n")

            f.write("\n## Dead File Candidates (Top 20 Oldest)\n\n")
            for d in dead[:20]:
                f.write(f"- **{d['age_days']} days** - {d['path']}\n")

        print(f"✅ Generated reports in {output_dir}/")
        print(f"   - {json_path.name}")
        print(f"   - {md_path.name}")
        print(f"   - {dead_path.name}")
        print(f"   - {pop_path.name}")


def main():
    parser = argparse.ArgumentParser(description='Analyze file popularity from TDJ')
    parser.add_argument('--csv', type=str, default='project_elements_file_timestamps.csv',
                        help='Input CSV from generate_repo_timestamps.py')
    parser.add_argument('--output', '-o', type=str, default='./.file_popularity',
                        help='Output directory')
    parser.add_argument('--dead-only', action='store_true',
                        help='Only list dead files')
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ CSV not found: {csv_path}")
        print(f"Run: python standard-model-of-code/scripts/generate_repo_timestamps.py")
        return 1

    tracker = FilePopularityTracker(csv_path)

    if args.dead_only:
        dead = tracker.identify_dead_files()
        print(f"\nDead Files ({len(dead)}):")
        for d in sorted(dead, key=lambda x: x['age_days'], reverse=True)[:50]:
            print(f"  {d['age_days']:4d} days | {d['path']}")
        return 0

    output_dir = Path(args.output)
    tracker.generate_report(output_dir)
    return 0


if __name__ == "__main__":
    exit(main())
