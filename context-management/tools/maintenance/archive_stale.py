#!/usr/bin/env python3
"""
🧟 ZOMBIE CODE ARCHIVER
=======================
Automated cleanup tool that moves "Stale Code" (untouched > 30 days) 
from the active source tree to the archive.

Usage:
    python3 archive_stale_files.py [--dry-run] [--days 30]

Logic:
1. Reads `project_elements_file_timestamps.csv`.
2. Filters for files in 'standard-model-of-code/src' (Active).
3. Checks if Modification Time > 30 days ago.
4. Quarantines them to `archive/zombie_code/<YYYY-MM-DD>/`.
"""

import csv
import os
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
CSV_PATH = Path("project_elements_file_timestamps.csv")
ARCHIVE_ROOT = Path("archive/zombie_code")
ACTIVE_ROOTS = ["standard-model-of-code/src"]

def parse_args():
    parser = argparse.ArgumentParser(description="Archive stale files.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without moving files")
    parser.add_argument("--days", type=int, default=30, help="Days of inactivity to consider stale (default: 30)")
    parser.add_argument("--force", action="store_true", help="Execute moves (opposite of dry-run, but explicit)")
    return parser.parse_args()

def is_active_path(path_str):
    p = Path(path_str)
    try:
        rel = p.relative_to(os.getcwd())
    except ValueError:
        # If absolute path is not relative to CWD, try to match textually
        if str(os.getcwd()) in str(p):
            rel = Path(str(p).replace(str(os.getcwd()) + "/", ""))
        else:
            return False

    for root in ACTIVE_ROOTS:
        if str(rel).startswith(root):
            return True
    return False

def main():
    args = parse_args()
    
    # Safety default: Dry run unless force is specified, OR if user didn't specify dry-run but script defaults to active?
    # To differ from standard rm, let's make it SAFE by default.
    # Actually, standard unix tools do active unless --dry-run. Let's follow that but print loud warnings.
    dry_run = args.dry_run
    
    print(f"🧟 ZOMBIE ARCHIVER (Threshold: {args.days} days)")
    if dry_run:
        print("🛡️  DRY RUN MODE: No files will be moved.")
    else:
        print("⚠️  LIVE MODE: Files will be moved to archive!")

    if not CSV_PATH.exists():
        print(f"❌ Error: CSV not found at {CSV_PATH}. Run update_timestamps.sh first.")
        exit(1)

    threshold_date = datetime.now() - timedelta(days=args.days)
    print(f"📅 Stale Threshold: {threshold_date.isoformat()}")

    candidates = []

    # 1. Read CSV
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fpath = row['path']
            
            # Check if active path
            if not is_active_path(fpath):
                continue

            # PROTECTION: detailed exclusions
            if fpath.endswith("__init__.py"):
                continue

                
            # Check modification time
            try:
                mtime_iso = row['modified_iso']
                # Handle varying ISO formats if needed, usually 'YYYY-MM-DDTHH:MM:SS'
                mtime = datetime.fromisoformat(mtime_iso)
                
                if mtime < threshold_date:
                    candidates.append({
                        'path': fpath,
                        'mtime': mtime,
                        'age': (datetime.now() - mtime).days
                    })
            except ValueError:
                continue

    # 2. Process Candidates
    print(f"\n🔍 Found {len(candidates)} stale candidates in active directories.")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    target_dir = ARCHIVE_ROOT / today_str
    
    if candidates and not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"📂 Archive Target: {target_dir}")

    count_moved = 0
    for cand in candidates:
        src = Path(cand['path'])
        
        # Double check existence
        if not src.exists():
            print(f"⚠️  Missing: {src.name} (already gone?)")
            continue
            
        dest = target_dir / src.name
        
        # Conflict resolution
        if dest.exists():
            dest = target_dir / f"{src.stem}_{int(datetime.now().timestamp())}{src.suffix}"

        icon = "🧟" if cand['age'] > 90 else "🕸️"
        print(f"{icon} {src.name:<40} (Age: {cand['age']}d) -> {dest}")

        if not dry_run:
            try:
                shutil.move(str(src), str(dest))
                count_moved += 1
            except Exception as e:
                print(f"❌ Failed to move {src.name}: {e}")

    if dry_run:
        print(f"\n🛡️  Dry run complete. Run without --dry-run to archive these {len(candidates)} files.")
    else:
        print(f"\n✅ Operation Cleanup Complete. {count_moved} files moved to quarantine.")

if __name__ == "__main__":
    main()
