#!/usr/bin/env python3
"""
FILE RELOCATION CANDIDATES FINDER
=================================
Identifies clusters of files that might be better relocated.
"""

import csv
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
METADATA_CSV = PROJECT_ROOT / "context-management/output/file_metadata_audit.csv"

def load_metadata():
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

def analyze_clusters(files):
    clusters = {}
    
    # 1. ROOT LEVEL FILES (potential clutter)
    root_files = [f for f in files if f['path'].count('/') == 1]
    clusters['root_clutter'] = {
        'title': '📁 Root Level Files (Potential Clutter)',
        'description': 'Files at project root that might belong in subdirectories',
        'suggestion': 'Move to appropriate subdirectory based on purpose',
        'files': sorted([f['path'] for f in root_files if f['extension'] not in ['.md', '.gitignore', '']])
    }
    
    # 2. DOCS IN CODE DIRECTORIES
    docs_in_code = [f for f in files 
                    if '/src/' in f['path'] and f['category'] == 'Doc']
    clusters['docs_in_code'] = {
        'title': '📄 Documentation in Source Directories',
        'description': 'Markdown/doc files found inside src/ folders',
        'suggestion': 'Move to docs/ directory or context-management/docs/',
        'files': sorted([f['path'] for f in docs_in_code])
    }
    
    # 3. CODE IN DOCS DIRECTORIES
    code_in_docs = [f for f in files 
                    if '/docs/' in f['path'] and f['category'] == 'Code']
    clusters['code_in_docs'] = {
        'title': '💻 Code Files in Documentation Directories',
        'description': 'Python/JS/etc files found inside docs/ folders',
        'suggestion': 'Move to src/ or tools/ directory',
        'files': sorted([f['path'] for f in code_in_docs])
    }
    
    # 4. ORPHANED .agent DIRECTORIES
    agent_files = [f for f in files if '/.agent/' in f['path']]
    clusters['orphan_agent'] = {
        'title': '🤖 Agent Configuration Files',
        'description': '.agent/ directories scattered across project',
        'suggestion': 'Consider consolidating under context-management/.agent/',
        'files': sorted(set(['/'.join(f['path'].split('/')[:-1]) for f in agent_files]))
    }
    
    # 5. DUPLICATE FILENAMES (potential consolidation)
    filename_counts = defaultdict(list)
    for f in files:
        if f['filename'] and f['extension'] in ['.py', '.md', '.js']:
            filename_counts[f['filename']].append(f['path'])
    
    duplicates = {k: v for k, v in filename_counts.items() 
                  if len(v) > 1 and k not in ['README.md', '__init__.py', 'index.js', 'setup.py']}
    clusters['duplicates'] = {
        'title': '🔄 Duplicate Filenames',
        'description': 'Files with same name in multiple locations',
        'suggestion': 'Review for redundancy or naming conflicts',
        'files': {name: paths for name, paths in sorted(duplicates.items())[:15]}
    }
    
    # 6. LARGE FILES (potential archive candidates)
    large_files = sorted([f for f in files if f['size_bytes'] > 500_000], 
                         key=lambda x: x['size_bytes'], reverse=True)[:20]
    clusters['large_files'] = {
        'title': '📦 Large Files (>500KB)',
        'description': 'Heavy files that might bloat version control',
        'suggestion': 'Consider LFS, compression, or archiving',
        'files': [(f['path'], f'{f["size_bytes"]/1024/1024:.2f} MB') for f in large_files]
    }
    
    # 7. LEGACY/ARCHIVE CANDIDATES (outside archive/)
    legacy_patterns = ['old', 'backup', 'deprecated', 'legacy', '_old', '.bak', 'copy']
    legacy_candidates = [f for f in files 
                         if any(p in f['path'].lower() for p in legacy_patterns)
                         and '/archive/' not in f['path']]
    clusters['legacy_outside_archive'] = {
        'title': '🗃️ Legacy Files Outside Archive',
        'description': 'Files with legacy/backup patterns not in archive/',
        'suggestion': 'Move to archive/ directory',
        'files': sorted([f['path'] for f in legacy_candidates])[:30]
    }
    
    # 8. VENV/NODE_MODULES still in tree
    venv_files = [f for f in files if 'venv/' in f['path'] or 'node_modules/' in f['path']]
    clusters['venv_pollution'] = {
        'title': '🚫 Virtual Environment Pollution',
        'description': 'venv/node_modules files tracked (should be excluded)',
        'suggestion': 'Add to .gitignore and remove from tracking',
        'count': len(venv_files),
        'sample_paths': sorted(set([f['path'].split('/')[0] + '/' + f['path'].split('/')[1] 
                                     for f in venv_files if len(f['path'].split('/')) > 1]))[:10]
    }
    
    # 9. SCATTERED CONFIGS
    config_files = [f for f in files 
                    if f['filename'] in ['config.yaml', 'config.json', 'settings.py', '.env']]
    clusters['scattered_configs'] = {
        'title': '⚙️ Scattered Configuration Files',
        'description': 'Config files in various locations',
        'suggestion': 'Consider consolidating under context-management/config/',
        'files': sorted([f['path'] for f in config_files])
    }
    
    # 10. OUTPUT FILES (should be in output/)
    output_candidates = [f for f in files 
                         if ('output' in f['filename'].lower() or 
                             'result' in f['filename'].lower() or
                             f['extension'] in ['.csv', '.html'])
                         and '/output/' not in f['path']]
    clusters['output_scattered'] = {
        'title': '📊 Output Files Outside output/',
        'description': 'Generated files (CSV, HTML) not in dedicated output directory',
        'suggestion': 'Move to context-management/output/ or project-specific output/',
        'files': sorted([f['path'] for f in output_candidates])[:20]
    }
    
    return clusters

def print_report(clusters):
    print("=" * 70)
    print("FILE RELOCATION CANDIDATES REPORT")
    print("=" * 70)
    
    for key, cluster in clusters.items():
        print(f"\n### {cluster['title']}")
        print(f"*{cluster['description']}*")
        print(f"**Suggestion**: {cluster['suggestion']}")
        
        if 'count' in cluster:
            print(f"**Count**: {cluster['count']} files")
            if 'sample_paths' in cluster:
                for p in cluster['sample_paths']:
                    print(f"  - {p}")
        elif isinstance(cluster.get('files'), dict):
            for name, paths in cluster['files'].items():
                print(f"\n**{name}**:")
                for p in paths[:3]:
                    print(f"  - {p}")
                if len(paths) > 3:
                    print(f"  - ...and {len(paths)-3} more")
        elif isinstance(cluster.get('files'), list):
            if cluster['files']:
                for item in cluster['files'][:10]:
                    if isinstance(item, tuple):
                        print(f"  - {item[0]} ({item[1]})")
                    else:
                        print(f"  - {item}")
                if len(cluster['files']) > 10:
                    print(f"  - ...and {len(cluster['files'])-10} more")
            else:
                print("  (none found)")

def main():
    print("Loading metadata...")
    files = load_metadata()
    print(f"Analyzing {len(files)} files...")
    
    clusters = analyze_clusters(files)
    print_report(clusters)

if __name__ == "__main__":
    main()
