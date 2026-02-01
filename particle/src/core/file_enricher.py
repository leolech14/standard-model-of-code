"""
FILE ENRICHER - Metadata Extraction for Visualization

Gathers comprehensive file metadata for the Collider visualization system.
This is LAYER 1 (Python) - the source of truth for all file metadata.

Metadata Dimensions:
- Physical: size_bytes, line_count, blank_lines
- Temporal: modified_ts, created_ts, age_days
- Structural: token_count, complexity_score, comment_ratio
- Categorical: extension, format_category, purpose
- Git: commits, authors, last_author (optional)

Usage:
    from src.core.file_enricher import FileEnricher

    enricher = FileEnricher(root_path="/path/to/repo")
    metadata = enricher.enrich_file("src/core/atom_classifier.py")

    # Or enrich all file boundaries at once
    enriched_boundaries = enricher.enrich_boundaries(file_boundaries)
"""

import os
import stat
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib


class FileEnricher:
    """
    Extracts comprehensive metadata from files for visualization.
    """

    # Format categories by extension
    FORMAT_CATEGORIES = {
        # Code
        '.py': 'code', '.js': 'code', '.ts': 'code', '.tsx': 'code', '.jsx': 'code',
        '.java': 'code', '.c': 'code', '.cpp': 'code', '.h': 'code', '.hpp': 'code',
        '.go': 'code', '.rs': 'code', '.rb': 'code', '.php': 'code', '.swift': 'code',
        '.kt': 'code', '.scala': 'code', '.cs': 'code', '.m': 'code', '.mm': 'code',
        '.lua': 'code', '.r': 'code', '.jl': 'code', '.ex': 'code', '.exs': 'code',

        # Config
        '.json': 'config', '.yaml': 'config', '.yml': 'config', '.toml': 'config',
        '.ini': 'config', '.cfg': 'config', '.conf': 'config', '.env': 'config',
        '.xml': 'config', '.plist': 'config', '.properties': 'config',

        # Documentation
        '.md': 'doc', '.rst': 'doc', '.txt': 'doc', '.adoc': 'doc',
        '.html': 'doc', '.htm': 'doc',

        # Data
        '.csv': 'data', '.tsv': 'data', '.parquet': 'data', '.avro': 'data',
        '.sql': 'data', '.db': 'data', '.sqlite': 'data',

        # Style
        '.css': 'style', '.scss': 'style', '.sass': 'style', '.less': 'style',

        # Shell/Scripts
        '.sh': 'script', '.bash': 'script', '.zsh': 'script', '.fish': 'script',
        '.ps1': 'script', '.bat': 'script', '.cmd': 'script',

        # Build
        '.dockerfile': 'build', '.makefile': 'build', '.cmake': 'build',
    }

    # Purpose detection patterns
    PURPOSE_PATTERNS = {
        'test': ['test', 'spec', 'mock', 'fixture', 'conftest'],
        'config': ['config', 'settings', 'env', 'setup'],
        'model': ['model', 'entity', 'schema', 'dto'],
        'service': ['service', 'manager', 'handler', 'processor'],
        'controller': ['controller', 'api', 'route', 'endpoint', 'view'],
        'utility': ['util', 'helper', 'common', 'shared', 'lib'],
        'interface': ['interface', 'abstract', 'base', 'protocol'],
        'data': ['data', 'fixture', 'seed', 'migration'],
    }

    def __init__(self, root_path: str = ".", enable_git: bool = True):
        """
        Initialize enricher.

        Args:
            root_path: Root directory of the repository
            enable_git: Whether to gather git metadata (slower)
        """
        self.root_path = Path(root_path).resolve()
        self.enable_git = enable_git
        self._git_available = self._check_git()
        self._git_cache: Dict[str, Dict] = {}

    def _check_git(self) -> bool:
        """Check if git is available and repo is initialized."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def enrich_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract all metadata for a single file.

        Args:
            file_path: Path to file (absolute or relative to root)

        Returns:
            Dictionary of metadata fields
        """
        # Resolve path
        if os.path.isabs(file_path):
            full_path = Path(file_path)
        else:
            full_path = self.root_path / file_path

        if not full_path.exists():
            return self._empty_metadata(file_path)

        metadata = {
            'file': str(file_path),
            'file_name': full_path.name,
        }

        # Physical metadata
        metadata.update(self._get_physical_metadata(full_path))

        # Temporal metadata
        metadata.update(self._get_temporal_metadata(full_path))

        # Structural metadata
        metadata.update(self._get_structural_metadata(full_path))

        # Categorical metadata
        metadata.update(self._get_categorical_metadata(full_path))

        # Git metadata (optional)
        if self.enable_git and self._git_available:
            metadata.update(self._get_git_metadata(full_path))

        return metadata

    def _get_physical_metadata(self, path: Path) -> Dict[str, Any]:
        """Get file size and physical properties."""
        try:
            stat_info = path.stat()
            return {
                'size_bytes': stat_info.st_size,
                'size_kb': round(stat_info.st_size / 1024, 2),
                'is_empty': stat_info.st_size == 0,
            }
        except Exception:
            return {'size_bytes': 0, 'size_kb': 0, 'is_empty': True}

    def _get_temporal_metadata(self, path: Path) -> Dict[str, Any]:
        """Get timestamps and age."""
        try:
            stat_info = path.stat()
            modified_ts = stat_info.st_mtime

            # Try to get birth time (creation time)
            try:
                created_ts = stat_info.st_birthtime
            except AttributeError:
                created_ts = stat_info.st_ctime  # Fallback to ctime

            now = datetime.now().timestamp()
            age_days = int((now - modified_ts) / 86400)

            return {
                'modified_ts': int(modified_ts),
                'created_ts': int(created_ts),
                'modified_date': datetime.fromtimestamp(modified_ts).isoformat()[:10],
                'age_days': age_days,
                'is_stale': age_days > 365,  # Not modified in a year
                'is_recent': age_days < 7,   # Modified in last week
            }
        except Exception:
            return {
                'modified_ts': 0, 'created_ts': 0, 'modified_date': '',
                'age_days': 0, 'is_stale': False, 'is_recent': False
            }

    def _get_structural_metadata(self, path: Path) -> Dict[str, Any]:
        """Get line counts, token estimates, and complexity hints."""
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            line_count = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())

            # Estimate token count (rough: ~4 chars per token for code)
            char_count = len(content)
            token_estimate = char_count // 4

            # Count comment lines (basic heuristic)
            ext = path.suffix.lower()
            comment_lines = self._count_comment_lines(lines, ext)

            # Code ratio (non-blank, non-comment)
            code_lines = line_count - blank_lines - comment_lines
            code_ratio = code_lines / max(1, line_count)

            # Complexity hint: count control flow keywords
            complexity_keywords = ['if', 'else', 'elif', 'for', 'while', 'try', 'except', 'catch', 'switch', 'case']
            complexity_count = sum(content.lower().count(f' {kw} ') + content.lower().count(f'\t{kw} ') for kw in complexity_keywords)
            complexity_density = complexity_count / max(1, code_lines) * 100

            return {
                'line_count': line_count,
                'blank_lines': blank_lines,
                'comment_lines': comment_lines,
                'code_lines': code_lines,
                'code_ratio': round(code_ratio, 2),
                'char_count': char_count,
                'token_estimate': token_estimate,
                'complexity_count': complexity_count,
                'complexity_density': round(complexity_density, 2),
            }
        except Exception:
            return {
                'line_count': 0, 'blank_lines': 0, 'comment_lines': 0,
                'code_lines': 0, 'code_ratio': 0, 'char_count': 0,
                'token_estimate': 0, 'complexity_count': 0, 'complexity_density': 0
            }

    def _count_comment_lines(self, lines: List[str], ext: str) -> int:
        """Count comment lines based on file extension."""
        comment_prefixes = {
            '.py': '#',
            '.js': '//', '.ts': '//', '.tsx': '//', '.jsx': '//',
            '.java': '//', '.c': '//', '.cpp': '//', '.go': '//', '.rs': '//',
            '.rb': '#', '.sh': '#', '.bash': '#', '.yaml': '#', '.yml': '#',
        }
        prefix = comment_prefixes.get(ext, '#')

        count = 0
        in_multiline = False

        for line in lines:
            stripped = line.strip()

            # Multi-line comments
            if '"""' in stripped or "'''" in stripped:
                in_multiline = not in_multiline
                count += 1
            elif in_multiline:
                count += 1
            elif '/*' in stripped:
                in_multiline = True
                count += 1
            elif '*/' in stripped:
                in_multiline = False
                count += 1
            elif stripped.startswith(prefix):
                count += 1

        return count

    def _get_categorical_metadata(self, path: Path) -> Dict[str, Any]:
        """Get extension, format category, and inferred purpose."""
        ext = path.suffix.lower()
        name_lower = path.name.lower()

        # Format category
        format_category = self.FORMAT_CATEGORIES.get(ext, 'other')

        # Special cases
        if 'dockerfile' in name_lower:
            format_category = 'build'
        elif 'makefile' in name_lower:
            format_category = 'build'
        elif name_lower.startswith('.'):
            format_category = 'config'

        # Infer purpose from name
        purpose = 'general'
        for category, patterns in self.PURPOSE_PATTERNS.items():
            if any(p in name_lower for p in patterns):
                purpose = category
                break

        # Also check parent directory
        parent_lower = path.parent.name.lower()
        if purpose == 'general':
            for category, patterns in self.PURPOSE_PATTERNS.items():
                if any(p in parent_lower for p in patterns):
                    purpose = category
                    break

        return {
            'extension': ext,
            'format_category': format_category,
            'purpose': purpose,
            'is_test': purpose == 'test',
            'is_config': format_category == 'config' or purpose == 'config',
        }

    def _get_git_metadata(self, path: Path) -> Dict[str, Any]:
        """Get git history metadata (commits, authors)."""
        rel_path = str(path.relative_to(self.root_path))

        if rel_path in self._git_cache:
            return self._git_cache[rel_path]

        metadata = {
            'git_commits': 0,
            'git_authors': [],
            'git_last_author': '',
            'git_first_commit_days': 0,
        }

        try:
            # Get commit count
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD', '--', rel_path],
                cwd=self.root_path,
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                metadata['git_commits'] = int(result.stdout.strip())

            # Get authors
            result = subprocess.run(
                ['git', 'log', '--format=%an', '--', rel_path],
                cwd=self.root_path,
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                authors = list(set(result.stdout.strip().split('\n')))
                authors = [a for a in authors if a]
                metadata['git_authors'] = authors[:5]  # Top 5
                if authors:
                    metadata['git_last_author'] = authors[0]

            # Get first commit date
            result = subprocess.run(
                ['git', 'log', '--reverse', '--format=%ct', '-1', '--', rel_path],
                cwd=self.root_path,
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                first_ts = int(result.stdout.strip())
                age_days = int((datetime.now().timestamp() - first_ts) / 86400)
                metadata['git_first_commit_days'] = age_days

        except Exception:
            pass

        self._git_cache[rel_path] = metadata
        return metadata

    def _empty_metadata(self, file_path: str) -> Dict[str, Any]:
        """Return empty metadata for missing files."""
        return {
            'file': file_path,
            'file_name': Path(file_path).name,
            'size_bytes': 0, 'size_kb': 0, 'is_empty': True,
            'modified_ts': 0, 'created_ts': 0, 'age_days': 0,
            'line_count': 0, 'token_estimate': 0,
            'extension': Path(file_path).suffix.lower(),
            'format_category': 'unknown',
            'purpose': 'unknown',
        }

    def enrich_boundaries(self, file_boundaries: List[Dict]) -> List[Dict]:
        """
        Enrich a list of file boundaries with metadata.

        Args:
            file_boundaries: List of boundary dicts with 'file' key

        Returns:
            Enriched boundaries with all metadata fields
        """
        enriched = []
        for boundary in file_boundaries:
            file_path = boundary.get('file') or boundary.get('file_path', '')
            if not file_path:
                enriched.append(boundary)
                continue

            metadata = self.enrich_file(file_path)
            # Merge: original boundary + enriched metadata
            merged = {**metadata, **boundary}  # boundary takes precedence for existing keys
            enriched.append(merged)

        return enriched


def enrich_file_boundaries(file_boundaries: List[Dict], root_path: str = ".", enable_git: bool = True) -> List[Dict]:
    """
    Convenience function to enrich file boundaries.

    Args:
        file_boundaries: List of boundary dicts
        root_path: Repository root
        enable_git: Whether to gather git metadata

    Returns:
        Enriched boundaries
    """
    enricher = FileEnricher(root_path=root_path, enable_git=enable_git)
    return enricher.enrich_boundaries(file_boundaries)
