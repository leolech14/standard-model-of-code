#!/usr/bin/env python3
"""
sync_session_tasks.py - Sync ephemeral session tasks to persistent registry.

This tool bridges the gap between:
- Session Tasks (Claude TaskList - ephemeral)
- Registry Tasks (.agent/registry/ - persistent YAML)

Usage:
    # Export session tasks to inbox as opportunities
    ./sync_session_tasks.py export --tasks "18,19,20,21,22,23,24,25"

    # Import from a JSON file (exported from session)
    ./sync_session_tasks.py import session_tasks.json

    # Validate session tasks against registry
    ./sync_session_tasks.py validate session_tasks.json

    # Run enrichment after sync
    ./sync_session_tasks.py export --tasks "18,19" --enrich

Output:
    - New OPP-XXX.yaml files in .agent/registry/inbox/
    - Validation report with SYNCED/ORPHANED status
"""

import argparse
import json
import yaml
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional
from difflib import SequenceMatcher

# Paths
SCRIPT_DIR = Path(__file__).parent
AGENT_DIR = SCRIPT_DIR.parent
INBOX_DIR = AGENT_DIR / "registry" / "inbox"
ACTIVE_DIR = AGENT_DIR / "registry" / "active"
ARCHIVE_DIR = AGENT_DIR / "registry" / "archive"

# Ensure directories exist
INBOX_DIR.mkdir(parents=True, exist_ok=True)


def get_next_opp_id() -> str:
    """Get next available OPP-XXX ID."""
    existing = list(INBOX_DIR.glob("OPP-*.yaml"))
    if not existing:
        return "OPP-100"

    max_num = 0
    for f in existing:
        try:
            num = int(f.stem.split("-")[1])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass

    return f"OPP-{max_num + 1:03d}"


def load_registry_tasks() -> Dict[str, dict]:
    """Load all registry tasks (active + inbox)."""
    tasks = {}

    for yaml_dir in [ACTIVE_DIR, INBOX_DIR]:
        for yaml_file in yaml_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    content = f.read()
                    # Handle both YAML with frontmatter and pure YAML
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            data = yaml.safe_load(parts[2])
                        else:
                            data = yaml.safe_load(content)
                    else:
                        data = yaml.safe_load(content)

                    if data and isinstance(data, dict):
                        task_id = data.get('id', yaml_file.stem)
                        title = data.get('title', '')
                        tasks[task_id] = {
                            'title': title,
                            'file': str(yaml_file),
                            'status': data.get('status', 'UNKNOWN'),
                            'confidence': data.get('confidence', {})
                        }
            except Exception as e:
                print(f"WARNING: Failed to load {yaml_file}: {e}")

    return tasks


def find_similar_task(title: str, registry_tasks: Dict[str, dict], threshold: float = 0.6) -> Optional[str]:
    """Find if a similar task already exists in registry."""
    title_lower = title.lower()

    for task_id, task_data in registry_tasks.items():
        registry_title = task_data.get('title', '').lower()
        similarity = SequenceMatcher(None, title_lower, registry_title).ratio()
        if similarity >= threshold:
            return task_id

    return None


def session_task_to_yaml(task_id: int, subject: str, description: str = "") -> str:
    """Convert a session task to registry YAML format."""
    opp_id = get_next_opp_id()
    now = datetime.now(timezone.utc).isoformat()

    # Map session task to category based on keywords
    category = "GENERAL"
    subject_lower = subject.lower()
    if any(kw in subject_lower for kw in ["health", "pathogen", "purity", "metric"]):
        category = "HEALTH_MODEL"
    elif any(kw in subject_lower for kw in ["refactor", "cc=", "god function"]):
        category = "TECH_DEBT"
    elif any(kw in subject_lower for kw in ["cli", "command", "flag"]):
        category = "CLI"
    elif any(kw in subject_lower for kw in ["test", "regression", "validation"]):
        category = "TESTING"
    elif any(kw in subject_lower for kw in ["doc", "theory", "define"]):
        category = "DOCUMENTATION"

    yaml_content = f'''# {opp_id}: {subject}
# Imported from: Session Task #{task_id}
# Category: {category}

id: {opp_id}
title: "{subject}"
status: PENDING
category: {category}
source: "session_task_{task_id}"

description: |
  {description or subject}

created_at: "{now}"
updated_at: "{now}"

# Needs 4D confidence scoring
confidence:
  factual: 0.70
  alignment: 0.70
  current: 0.70
  onwards: 0.70
  overall: 0.70
  needs_review: true

tags:
  - session-import
  - needs-enrichment
'''
    return opp_id, yaml_content


def export_tasks(task_specs: List[str], enrich: bool = False, dry_run: bool = False):
    """
    Export session tasks to registry.

    task_specs: List of "id:subject" or just "id" strings
    """
    registry_tasks = load_registry_tasks()
    exported = []
    skipped = []

    print("\n" + "="*60)
    print("SESSION → REGISTRY SYNC")
    print("="*60)

    for spec in task_specs:
        # Parse spec (format: "18:Subject text" or just "18")
        if ':' in spec:
            parts = spec.split(':', 1)
            task_id = int(parts[0])
            subject = parts[1].strip()
        else:
            task_id = int(spec)
            subject = f"Session Task #{task_id}"

        # Check if already exists
        similar = find_similar_task(subject, registry_tasks)
        if similar:
            print(f"  SKIP #{task_id}: Similar to {similar}")
            skipped.append((task_id, similar))
            continue

        opp_id, yaml_content = session_task_to_yaml(task_id, subject)
        output_path = INBOX_DIR / f"{opp_id}.yaml"

        if dry_run:
            print(f"  [DRY] #{task_id} → {opp_id}")
        else:
            with open(output_path, 'w') as f:
                f.write(yaml_content)
            print(f"  OK: #{task_id} → {opp_id} ({output_path.name})")
            exported.append(opp_id)

    print(f"\nExported: {len(exported)}, Skipped: {len(skipped)}")

    if enrich and exported and not dry_run:
        print("\nRunning enrichment pipeline...")
        import subprocess
        enricher = SCRIPT_DIR / "enrichment_orchestrator.py"
        if enricher.exists():
            subprocess.run([sys.executable, str(enricher)])


def validate_file(json_path: str):
    """Validate session tasks JSON against registry."""
    with open(json_path, 'r') as f:
        session_tasks = json.load(f)

    registry_tasks = load_registry_tasks()

    print("\n" + "="*60)
    print("VALIDATION REPORT")
    print("="*60)

    synced = []
    orphaned = []

    for task in session_tasks:
        task_id = task.get('id', task.get('number', '?'))
        subject = task.get('subject', task.get('title', ''))
        status = task.get('status', 'pending')

        if status == 'completed':
            continue

        similar = find_similar_task(subject, registry_tasks, threshold=0.5)
        if similar:
            synced.append((task_id, subject, similar))
            print(f"  ✓ #{task_id} → {similar}")
        else:
            orphaned.append((task_id, subject))
            print(f"  ✗ #{task_id}: {subject[:50]}...")

    print(f"\nSYNCED: {len(synced)}, ORPHANED: {len(orphaned)}")

    if orphaned:
        print("\nOrphaned tasks need export:")
        for task_id, subject in orphaned:
            print(f'  {task_id}:"{subject}"')


def main():
    parser = argparse.ArgumentParser(description="Sync session tasks to registry")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Export command
    export_parser = subparsers.add_parser('export', help='Export tasks to registry')
    export_parser.add_argument('--tasks', '-t', required=True,
                              help='Task specs: "18:Subject,19:Subject" or "18,19,20"')
    export_parser.add_argument('--enrich', '-e', action='store_true',
                              help='Run enrichment pipeline after export')
    export_parser.add_argument('--dry-run', '-n', action='store_true')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate against registry')
    validate_parser.add_argument('json_file', help='Session tasks JSON file')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import from JSON file')
    import_parser.add_argument('json_file', help='Session tasks JSON file')
    import_parser.add_argument('--enrich', '-e', action='store_true')
    import_parser.add_argument('--dry-run', '-n', action='store_true')

    args = parser.parse_args()

    if args.command == 'export':
        task_specs = [t.strip() for t in args.tasks.split(',')]
        export_tasks(task_specs, args.enrich, args.dry_run)

    elif args.command == 'validate':
        validate_file(args.json_file)

    elif args.command == 'import':
        with open(args.json_file, 'r') as f:
            tasks = json.load(f)
        task_specs = []
        for t in tasks:
            if t.get('status') != 'completed':
                tid = t.get('id', t.get('number'))
                subject = t.get('subject', t.get('title', ''))
                task_specs.append(f"{tid}:{subject}")
        export_tasks(task_specs, args.enrich, args.dry_run)


if __name__ == "__main__":
    main()
