import os
import csv
import time
from datetime import datetime

def get_file_info(filepath):
    """Get size and timestamp info for a file."""
    try:
        stat = os.stat(filepath)
        size_bytes = stat.st_size
        created_epoch = int(stat.st_ctime)
        created_iso = datetime.fromtimestamp(created_epoch).isoformat()
        modified_epoch = int(stat.st_mtime)
        modified_iso = datetime.fromtimestamp(modified_epoch).isoformat()
        return size_bytes, created_epoch, created_iso, modified_epoch, modified_iso
    except Exception as e:
        return None

def main():
    repo_root = "/Users/lech/PROJECTS_all/PROJECT_elements"
    output_file = os.path.join(repo_root, "project_elements_file_timestamps.csv")
    
    print(f"Scanning {repo_root}...")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['path', 'size_bytes', 'created_epoch', 'created_iso', 'modified_epoch', 'modified_iso'])
        
        file_count = 0
        for root, dirs, files in os.walk(repo_root):
            # Skip hidden directories like .git, .eval, node_modules etc if needed
            # For now, we'll keep it broad but maybe skip .git to avoid spam
            if '.git' in dirs:
                dirs.remove('.git')
            if 'node_modules' in dirs:
                dirs.remove('node_modules')
                
            for name in files:
                filepath = os.path.join(root, name)
                
                # specific excludes if any
                if name == ".DS_Store":
                    continue
                    
                info = get_file_info(filepath)
                if info:
                    row = [filepath] + list(info)
                    writer.writerow(row)
                    file_count += 1
                    
    print(f"Done. Wrote {file_count} files to {output_file}")

if __name__ == "__main__":
    main()
