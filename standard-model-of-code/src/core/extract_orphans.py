
import sys
import json
import os

def extract_orphans():
    try:
        # Load JSON from stdin
        data = json.load(sys.stdin)
        
        # safely get orphans list
        orphans = data.get('execution_flow', {}).get('orphans', [])
        
        # Generate Markdown content
        lines = []
        lines.append('# Analysis Report: Orphaned Code Candidates')
        lines.append(f'\n**Total Count:** {len(orphans)}\n')
        lines.append('The following files/nodes were identified as unreachable from any known entry point (Executables or Tests).')
        lines.append('These are high-confidence candidates for deletion, but manual review is always recommended.\n')
        lines.append('## Orphan List')
        
        for o in sorted(orphans):
            lines.append(f'- `{o}`')
            
        # Write to file
        output_path = '../orphans_report.md'
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
            
        print(f"Successfully wrote {len(orphans)} orphans to {os.path.abspath(output_path)}")
        
    except Exception as e:
        print(f"Error extracting orphans: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    extract_orphans()
