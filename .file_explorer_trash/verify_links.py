#!/usr/bin/env python3
import os
import re
from pathlib import Path
import sys

def verify_links(root_dir):
    """
    Scans all .md files for broken internal links.
    """
    print("🔍 VERIFYING LINKS (Gate G3)...")
    root = Path(root_dir)
    md_files = list(root.glob("**/*.md"))
    
    broken_count = 0
    link_pattern = re.compile(r'\[.*?\]\((?!http|https|mailto|file)(.*?)\)')
    
    for md_file in md_files:
        content = md_file.read_text()
        links = link_pattern.findall(content)
        
        for link in links:
            # Handle anchor links
            clean_link = link.split('#')[0]
            if not clean_link: continue
            
            # Try relative path
            target = md_file.parent / clean_link
            if not target.exists():
                print(f"   ❌ Broken link in {md_file.relative_to(root)}: {link}")
                broken_count += 1
                
    if broken_count == 0:
        print("✅ No broken links found.")
        return True
    else:
        print(f"❌ Found {broken_count} broken links.")
        return False

if __name__ == "__main__":
    root_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = verify_links(root_path)
    # We don't exit with error yet to allow baseline measurement
    sys.exit(0)
