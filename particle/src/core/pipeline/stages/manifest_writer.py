"""
Stage 13: Manifest Writer

Records provenance and integrity information before output generation.
This is the foundation for "MEASURED CODOME" - treating analysis output
as a first-class scientific measurement with reproducibility.

Captures:
- Input identity: git commit, file inventory hash
- Pipeline identity: stage versions, config
- Environment identity: Python version, key tool versions
- Timing: start/end timestamps
- Checksums: SHA-256 of all input files
"""

from typing import TYPE_CHECKING, Optional, Dict, Any, List
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class ManifestWriterStage(BaseStage):
    """
    Stage 13: Manifest Writer.

    Input: CodebaseState with complete analysis
    Output: CodebaseState with manifest in metadata

    The manifest enables:
    - Reproducibility verification
    - Drift detection (code vs tool vs environment)
    - Artifact integrity checking
    - Run comparison and diffing
    """

    @property
    def name(self) -> str:
        return "manifest_writer"

    @property
    def stage_number(self) -> Optional[int]:
        return 11  # 11.5 - after semantic_cortex, before output_generation

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes to record."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Generate manifest with provenance and integrity data.
        """
        target_path = Path(state.metadata.get('target_path', '.'))

        manifest = {
            "schema_version": "manifest.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),

            # Input identity
            "input": self._capture_input_identity(target_path, state),

            # Pipeline identity
            "pipeline": self._capture_pipeline_identity(state),

            # Environment identity
            "environment": self._capture_environment(),

            # Analysis summary (for quick lookup)
            "summary": self._capture_summary(state),

            # File checksums (for integrity)
            "checksums": self._compute_checksums(target_path, state),
        }

        # Store in state metadata
        state.metadata['manifest'] = manifest

        # Count stats for logging
        file_count = len(manifest.get('checksums', {}).get('files', {}))
        print(f"   → Manifest: {file_count} files hashed, provenance captured")

        return state

    def _capture_input_identity(self, target_path: Path, state: "CodebaseState") -> Dict[str, Any]:
        """Capture git commit, dirty state, and file inventory."""
        git_info = self._get_git_info(target_path)

        # Get analyzed file list
        analyzed_files = set()
        for node in state.nodes.values():
            fp = node.get('file_path', '')
            if fp and not fp.startswith('__codome__'):
                analyzed_files.add(fp)

        return {
            "root": str(target_path.resolve()),
            "git_commit": git_info.get('commit'),
            "git_branch": git_info.get('branch'),
            "git_dirty": git_info.get('dirty', True),
            "analyzed_file_count": len(analyzed_files),
            # Hash of sorted file list for quick comparison
            "inventory_hash": self._hash_strings(sorted(analyzed_files)),
        }

    def _capture_pipeline_identity(self, state: "CodebaseState") -> Dict[str, Any]:
        """Capture pipeline version and configuration."""
        return {
            "collider_version": self._get_collider_version(),
            "stage_count": len(state.metadata.get('stages_executed', [])),
            "stages_executed": state.metadata.get('stages_executed', []),
            "config": {
                "ai_insights": state.metadata.get('ai_insights', False),
                "deterministic": True,  # Always deterministic for now
            },
        }

    def _capture_environment(self) -> Dict[str, Any]:
        """Capture Python version and key dependencies."""
        import sys
        import platform

        deps = {}
        for pkg in ['tree_sitter', 'networkx', 'numpy', 'chardet']:
            try:
                mod = __import__(pkg)
                deps[pkg] = getattr(mod, '__version__', 'unknown')
            except ImportError:
                deps[pkg] = None

        return {
            "python_version": sys.version.split()[0],
            "platform": platform.system(),
            "platform_version": platform.release(),
            "dependencies": deps,
        }

    def _capture_summary(self, state: "CodebaseState") -> Dict[str, Any]:
        """Quick summary stats for manifest header."""
        return {
            "total_nodes": len(state.nodes),
            "total_edges": len(state.edges),
            "file_count": len(set(n.get('file_path', '') for n in state.nodes.values())),
            "codome_boundary_nodes": len([n for n in state.nodes.values()
                                          if n.get('is_codome_boundary')]),
        }

    def _compute_checksums(self, target_path: Path, state: "CodebaseState") -> Dict[str, Any]:
        """Compute SHA-256 checksums for analyzed files."""
        checksums = {}
        errors = []

        # Get unique files from nodes
        files = set()
        for node in state.nodes.values():
            fp = node.get('file_path', '')
            if fp and not fp.startswith('__codome__'):
                files.add(fp)

        for rel_path in sorted(files):
            try:
                full_path = target_path / rel_path
                if full_path.exists() and full_path.is_file():
                    checksums[rel_path] = self._sha256_file(full_path)
            except Exception as e:
                errors.append(f"{rel_path}: {e}")

        # Compute merkle root (hash of all hashes) for quick comparison
        all_hashes = [checksums[k] for k in sorted(checksums.keys())]
        merkle_root = self._hash_strings(all_hashes) if all_hashes else None

        return {
            "algorithm": "sha256",
            "merkle_root": merkle_root,
            "file_count": len(checksums),
            "files": checksums,
            "errors": errors if errors else None,
        }

    def _get_git_info(self, path: Path) -> Dict[str, Any]:
        """Get git commit, branch, and dirty state."""
        try:
            # Get commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=path, capture_output=True, text=True, timeout=5
            )
            commit = result.stdout.strip() if result.returncode == 0 else None

            # Get branch name
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=path, capture_output=True, text=True, timeout=5
            )
            branch = result.stdout.strip() if result.returncode == 0 else None

            # Check if dirty
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=path, capture_output=True, text=True, timeout=5
            )
            dirty = bool(result.stdout.strip()) if result.returncode == 0 else True

            return {'commit': commit, 'branch': branch, 'dirty': dirty}
        except Exception:
            return {'commit': None, 'branch': None, 'dirty': True}

    def _get_collider_version(self) -> str:
        """Get collider version from cli.py or fallback."""
        try:
            cli_path = Path(__file__).parent.parent.parent.parent.parent / 'cli.py'
            if cli_path.exists():
                content = cli_path.read_text()
                for line in content.split('\n'):
                    if '__version__' in line and '=' in line:
                        return line.split('=')[1].strip().strip('"\'')
        except Exception:
            pass
        return "unknown"

    def _sha256_file(self, path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()

    def _hash_strings(self, strings: List[str]) -> str:
        """Hash a list of strings (for inventory/merkle)."""
        h = hashlib.sha256()
        for s in strings:
            h.update(s.encode('utf-8'))
        return h.hexdigest()
