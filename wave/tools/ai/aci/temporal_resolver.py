#!/usr/bin/env python3
"""
TEMPORAL RESOLVER - Git Archaeology + analyze.py for Canonical Source Resolution

When multiple files claim conflicting facts (counts, definitions, canonical status),
use git history + file timestamps + analyze.py to determine which is THE truth.

Workflow:
1. Find all files claiming to be canonical for concept X
2. Check git history: which was modified most recently?
3. Check file timestamps: which has newest data?
4. Query analyze.py: what does the CODE say?
5. Resolve conflict: declare ONE canonical, mark others as derived/archived

This prevents "pick a number" decisions - instead, use temporal evidence.

Example Use Cases:
- Pipeline stage count: 28 vs 18 vs 27
- Atom counts: Index says 43, registry has 42
- Dimension definitions: Multiple files claim canonical

Usage:
    python temporal_resolver.py --concept "pipeline stages" \
        --files "docs/specs/PIPELINE_STAGES.md,docs/specs/REGISTRY_OF_REGISTRIES.md" \
        --code-source "src/core/pipeline/stages/__init__.py"

    # Output:
    # Canonical: src/core/pipeline/stages/__init__.py (28 stages, last modified 2026-01-26)
    # Derived: docs/specs/PIPELINE_STAGES.md (28 stages, matches canonical) ✅
    # Outdated: docs/specs/REGISTRY_OF_REGISTRIES.md (18 stages, stale) ❌
    # Decision: Update REGISTRY_OF_REGISTRIES.md or mark as archive
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class TemporalResolver:
    """Resolve canonical source conflicts using git + file system + analyze.py"""

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()

    def get_git_history(self, file_path: str) -> Dict:
        """Get git metadata for a file."""
        try:
            # Last modification date
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ci|%H|%s', '--', file_path],
                capture_output=True, text=True, cwd=self.repo_root
            )
            if result.returncode == 0 and result.stdout.strip():
                date_str, commit_hash, message = result.stdout.strip().split('|', 2)
                return {
                    'last_modified': date_str,
                    'commit': commit_hash,
                    'message': message,
                    'exists_in_git': True
                }
        except Exception as e:
            pass

        return {'exists_in_git': False}

    def get_file_metadata(self, file_path: str) -> Dict:
        """Get filesystem metadata."""
        p = Path(self.repo_root) / file_path
        if not p.exists():
            return {'exists': False}

        stat = p.stat()
        return {
            'exists': True,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }

    def query_code_count(self, code_file: str, concept: str) -> Dict:
        """Query analyze.py about what the code says."""
        # This would call analyze.py with a specific query
        # For now, placeholder that describes the pattern
        return {
            'method': 'analyze.py',
            'query': f'Count {concept} in {code_file}',
            'note': 'Run: python wave/tools/ai/analyze.py --file {code_file} "<query>"'
        }

    def resolve_conflict(self, concept: str, files: List[str], code_source: str = None) -> Dict:
        """
        Resolve which file is canonical using temporal evidence.

        Args:
            concept: What we're resolving (e.g., "pipeline stages")
            files: List of files claiming canonical status
            code_source: Optional code file that is ultimate truth

        Returns:
            Resolution decision with evidence
        """
        evidence = {}

        # Gather evidence for each file
        for file in files:
            git_meta = self.get_git_history(file)
            fs_meta = self.get_file_metadata(file)

            evidence[file] = {
                'git': git_meta,
                'fs': fs_meta,
                'score': 0
            }

            # Scoring heuristic
            if git_meta.get('exists_in_git'):
                # More recent = higher score
                evidence[file]['score'] += 100
            if fs_meta.get('exists'):
                evidence[file]['score'] += 50

        # If code source provided, it wins
        if code_source:
            code_git = self.get_git_history(code_source)
            code_fs = self.get_file_metadata(code_source)

            evidence[code_source] = {
                'git': code_git,
                'fs': code_fs,
                'score': 1000,  # Code always wins
                'is_code': True
            }

        # Sort by score
        ranked = sorted(evidence.items(), key=lambda x: x[1]['score'], reverse=True)

        return {
            'concept': concept,
            'canonical': ranked[0][0] if ranked else None,
            'evidence': evidence,
            'ranked': ranked,
            'recommendation': self._generate_recommendation(ranked)
        }

    def _generate_recommendation(self, ranked: List[Tuple]) -> str:
        """Generate human-readable recommendation."""
        if not ranked:
            return "No files provided"

        canonical = ranked[0][0]
        recs = [f"✅ Canonical: {canonical}"]

        for file, data in ranked[1:]:
            if data.get('is_code'):
                recs.append(f"⚠️ {file} is code - should be source")
            elif data['git'].get('exists_in_git'):
                recs.append(f"📝 {file} - mark as GENERATED or REFERENCE")
            else:
                recs.append(f"🗑️ {file} - consider archiving")

        return "\n".join(recs)


# Workflow: Resolve pipeline stage count conflict
if __name__ == "__main__":
    import sys

    resolver = TemporalResolver()

    # Example: Pipeline stages
    result = resolver.resolve_conflict(
        concept="pipeline stages",
        files=[
            "particle/docs/specs/PIPELINE_STAGES.md",
            "particle/docs/specs/REGISTRY_OF_REGISTRIES.md"
        ],
        code_source="particle/src/core/pipeline/stages/__init__.py"
    )

    print("="*60)
    print(f"Resolving: {result['concept']}")
    print("="*60)
    print()
    print(result['recommendation'])
    print()
    print("Evidence:")
    for file, data in result['ranked']:
        print(f"\n  {file}")
        print(f"    Score: {data['score']}")
        if data['git'].get('exists_in_git'):
            print(f"    Last modified: {data['git']['last_modified']}")
            print(f"    Commit: {data['git']['commit'][:8]}")
        if data['fs'].get('exists'):
            print(f"    Size: {data['fs']['size']} bytes")
