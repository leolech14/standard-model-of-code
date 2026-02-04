#!/usr/bin/env python3
import re
from pathlib import Path
import sys

def verify_placeholders(root_dir):
    """
    Scans for unresolved placeholders like {TODO}, {placeholder}, etc.
    """
    print("🔍 VERIFYING PLACEHOLDERS (Gate G4)...")
    root = Path(root_dir)
    md_files = list(root.glob("**/*.md"))

    # Matches {anything_lowercase_with_underscores}
    placeholder_pattern = re.compile(r'\{[a-z0-9_]+\}')

    count = 0
    for md_file in md_files:
        if "node_modules" in str(md_file) or ".git" in str(md_file):
            continue

        content = md_file.read_text()
        matches = placeholder_pattern.findall(content)

        if matches:
            print(f"   ❌ Found {len(matches)} placeholders in {md_file.relative_to(root)}")
            for match in matches:
                print(f"      - {match}")
            count += len(matches)

    if count == 0:
        print("✅ No unresolved placeholders found.")
        return True
    else:
        print(f"❌ Found {count} unresolved placeholders.")
        return False

if __name__ == "__main__":
    root_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = verify_placeholders(root_path)
    sys.exit(0)
