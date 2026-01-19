#!/usr/bin/env python3
"""
ANALYSIS SETS COVERAGE REPORT
=============================
Analyzes the curated file sets and generates comprehensive metrics.
"""

import csv
import yaml
import fnmatch
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
METADATA_CSV = PROJECT_ROOT / "context-management/output/file_metadata_audit.csv"
SETS_CONFIG = PROJECT_ROOT / "context-management/config/analysis_sets.yaml"

# Approximate tokens per byte (rough estimate for code/text)
TOKENS_PER_BYTE = 0.25  # ~4 chars per token on average

def load_metadata():
    """Load file metadata from CSV."""
    files = []
    with open(METADATA_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            files.append({
                'path': row['Path'],
                'filename': row['Filename'],
                'extension': row['Extension'],
                'category': row['Category'],
                'size_bytes': int(row['SizeBytes']),
                'lines': int(row['LineCount']) if row['LineCount'] else 0
            })
    return files

def load_sets_config():
    """Load analysis sets configuration."""
    with open(SETS_CONFIG) as f:
        return yaml.safe_load(f)

def match_file_to_sets(file_path, sets_config):
    """Check which sets a file belongs to."""
    matched = []
    for set_name, set_def in sets_config.get('analysis_sets', {}).items():
        for pattern in set_def.get('patterns', []):
            # Normalize paths for matching
            rel_path = file_path.lstrip('/')
            if fnmatch.fnmatch(rel_path, pattern):
                matched.append(set_name)
                break
    return matched

def calculate_metrics(files, sets_config):
    """Calculate metrics for all sets."""
    # Total metrics
    total_files = len(files)
    total_size = sum(f['size_bytes'] for f in files)
    total_lines = sum(f['lines'] for f in files)
    
    # Per-set metrics
    set_metrics = {}
    for set_name, set_def in sets_config.get('analysis_sets', {}).items():
        set_metrics[set_name] = {
            'description': set_def.get('description', ''),
            'patterns': set_def.get('patterns', []),
            'files': [],
            'file_count': 0,
            'size_bytes': 0,
            'lines': 0,
            'extensions': defaultdict(int),
            'categories': defaultdict(int)
        }
    
    # Match files to sets
    for file in files:
        matched_sets = match_file_to_sets(file['path'], sets_config)
        for set_name in matched_sets:
            if set_name in set_metrics:
                set_metrics[set_name]['files'].append(file['path'])
                set_metrics[set_name]['file_count'] += 1
                set_metrics[set_name]['size_bytes'] += file['size_bytes']
                set_metrics[set_name]['lines'] += file['lines']
                set_metrics[set_name]['extensions'][file['extension']] += 1
                set_metrics[set_name]['categories'][file['category']] += 1
    
    # Calculate derived metrics
    for set_name, metrics in set_metrics.items():
        metrics['coverage_pct'] = (metrics['file_count'] / total_files * 100) if total_files > 0 else 0
        metrics['size_pct'] = (metrics['size_bytes'] / total_size * 100) if total_size > 0 else 0
        metrics['estimated_tokens'] = int(metrics['size_bytes'] * TOKENS_PER_BYTE)
        metrics['size_mb'] = metrics['size_bytes'] / (1024 * 1024)
        
        # Top extensions
        metrics['top_extensions'] = sorted(
            metrics['extensions'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
    
    return {
        'total': {
            'file_count': total_files,
            'size_bytes': total_size,
            'size_mb': total_size / (1024 * 1024),
            'lines': total_lines,
            'estimated_tokens': int(total_size * TOKENS_PER_BYTE)
        },
        'sets': set_metrics
    }

def generate_report(metrics):
    """Generate markdown report."""
    report = []
    report.append("# Analysis Sets Coverage Report")
    report.append(f"\n**Generated**: {Path(__file__).name}")
    report.append(f"\n**Source**: `{METADATA_CSV.name}` ({metrics['total']['file_count']:,} files)")
    
    # Summary Table
    report.append("\n## Summary\n")
    report.append("| Set | Files | Size | Coverage | Est. Tokens | Fits in 1M? |")
    report.append("|-----|-------|------|----------|-------------|-------------|")
    
    for set_name, m in sorted(metrics['sets'].items()):
        fits = "✅ Yes" if m['estimated_tokens'] < 1_000_000 else "❌ No"
        report.append(
            f"| **{set_name}** | {m['file_count']:,} | {m['size_mb']:.2f} MB | "
            f"{m['coverage_pct']:.1f}% | {m['estimated_tokens']:,} | {fits} |"
        )
    
    # Total
    t = metrics['total']
    report.append(
        f"| **TOTAL** | {t['file_count']:,} | {t['size_mb']:.2f} MB | 100% | "
        f"{t['estimated_tokens']:,} | ❌ No |"
    )
    
    # Per-Set Details
    report.append("\n## Set Details\n")
    for set_name, m in sorted(metrics['sets'].items()):
        report.append(f"### {set_name.upper()}")
        report.append(f"*{m['description']}*\n")
        report.append(f"- **Patterns**: `{', '.join(m['patterns'])}`")
        report.append(f"- **Files**: {m['file_count']:,}")
        report.append(f"- **Size**: {m['size_mb']:.2f} MB ({m['size_pct']:.1f}% of total)")
        report.append(f"- **Lines**: {m['lines']:,}")
        report.append(f"- **Est. Tokens**: {m['estimated_tokens']:,}")
        
        if m['top_extensions']:
            exts = ", ".join([f"`{ext}` ({count})" for ext, count in m['top_extensions']])
            report.append(f"- **Top Extensions**: {exts}")
        
        report.append("")
    
    return "\n".join(report)

def main():
    print("Loading metadata...")
    files = load_metadata()
    
    print("Loading sets configuration...")
    sets_config = load_sets_config()
    
    print("Calculating metrics...")
    metrics = calculate_metrics(files, sets_config)
    
    print("\n" + "="*60)
    report = generate_report(metrics)
    print(report)
    
    # Save report
    output_path = PROJECT_ROOT / "context-management/output/analysis_sets_report.md"
    with open(output_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {output_path}")

if __name__ == "__main__":
    main()
