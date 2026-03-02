"""
SMART IGNORE - Sequential Discovery Protocol
=============================================

Progressive codebase reconnaissance that maps directory structure
in coordinated phases, classifying signal vs noise BEFORE any parsing.

Unlike the Survey (which walks everything then filters), SmartIgnore
explores incrementally: shallow first, then deeper only where signal
warrants it.

Three phases:
    Phase 1: RECON       (depth=1)  Classify top-level directories
    Phase 2: SIGNAL SCAN (depth=2+) Targeted exploration of unknowns
    Phase 3: DECISION               Generate .smartignore manifest

Output:
    SmartIgnoreManifest - structured decisions fed to Survey + Analysis
    .smartignore file   - human-readable, cacheable, reusable

Usage:
    from smart_ignore import SmartIgnore

    si = SmartIgnore("/path/to/repo")
    manifest = si.discover()
    print(manifest.summary())

Phase: 11 (Pre-Survey Intelligence)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os
import time
import json
import fnmatch


# ============================================================
# CLASSIFICATION VOCABULARY
# ============================================================

class DirClass:
    """Directory classification constants."""
    CODE = "CODE"            # Primary source -- always explore deep
    VENDOR = "VENDOR"        # Third-party deps -- always skip
    BUILD = "BUILD"          # Build/compile output -- always skip
    CACHE = "CACHE"          # Caches, bytecode -- always skip
    DATA = "DATA"            # Data files, assets -- skip unless small
    DOCS = "DOCS"            # Documentation -- explore shallow
    GENERATED = "GENERATED"  # Auto-generated code -- skip
    TEST = "TEST"            # Test directories -- explore
    CONFIG = "CONFIG"        # Configuration -- include
    INFRA = "INFRA"          # CI/CD, Docker, etc. -- include shallow
    ARCHIVE = "ARCHIVE"      # Old/archived code -- skip
    UNKNOWN = "UNKNOWN"      # Can't classify -- explore next phase


class Decision:
    """What to do with a directory."""
    EXPLORE = "EXPLORE"          # Full deep analysis
    SKIP = "SKIP"                # Exclude from analysis
    SHALLOW = "SHALLOW"          # Include but limit depth
    EXPLORE_NEXT = "EXPLORE_NEXT"  # Needs deeper scan to decide


# ============================================================
# CLASSIFICATION RULES
# ============================================================

# Instant classification by directory name (no filesystem access needed)
NAME_CLASSIFICATIONS = {
    # VENDOR
    "node_modules": (DirClass.VENDOR, "npm dependencies"),
    "vendor": (DirClass.VENDOR, "vendored dependencies"),
    ".vendor": (DirClass.VENDOR, "vendored dependencies"),
    "bower_components": (DirClass.VENDOR, "bower dependencies"),
    "jspm_packages": (DirClass.VENDOR, "jspm dependencies"),
    "packages": (DirClass.VENDOR, "vendored packages"),  # Go, etc.
    ".repos_cache": (DirClass.VENDOR, "cached repositories"),

    # BUILD
    "dist": (DirClass.BUILD, "build output"),
    "build": (DirClass.BUILD, "build output"),
    "out": (DirClass.BUILD, "build output"),
    "output": (DirClass.BUILD, "build output"),
    "target": (DirClass.BUILD, "build output (Java/Rust)"),
    "_build": (DirClass.BUILD, "build output"),
    ".output": (DirClass.BUILD, "build output"),

    # CACHE
    ".git": (DirClass.CACHE, "git internals"),
    "__pycache__": (DirClass.CACHE, "Python bytecode"),
    ".cache": (DirClass.CACHE, "cache directory"),
    ".pytest_cache": (DirClass.CACHE, "pytest cache"),
    ".mypy_cache": (DirClass.CACHE, "mypy cache"),
    ".ruff_cache": (DirClass.CACHE, "ruff cache"),
    ".tox": (DirClass.CACHE, "tox environments"),
    ".nox": (DirClass.CACHE, "nox environments"),
    ".next": (DirClass.CACHE, "Next.js build cache"),
    ".nuxt": (DirClass.CACHE, "Nuxt.js build cache"),
    ".parcel-cache": (DirClass.CACHE, "Parcel bundler cache"),
    ".turbo": (DirClass.CACHE, "Turborepo cache"),
    ".nx": (DirClass.CACHE, "Nx cache"),
    ".nyc_output": (DirClass.CACHE, "NYC coverage data"),
    "coverage": (DirClass.CACHE, "test coverage data"),
    ".coverage": (DirClass.CACHE, "coverage data"),
    ".eggs": (DirClass.CACHE, "Python egg cache"),
    "*.egg-info": (DirClass.CACHE, "Python egg info"),

    # VENV (special vendor -- Python environments)
    ".venv": (DirClass.VENDOR, "Python virtual environment"),
    "venv": (DirClass.VENDOR, "Python virtual environment"),
    "env": (DirClass.VENDOR, "Python virtual environment"),
    ".env": (DirClass.CONFIG, "environment config"),  # ambiguous but common

    # DATA
    "data": (DirClass.DATA, "data directory"),
    "datasets": (DirClass.DATA, "datasets"),
    "fixtures": (DirClass.DATA, "test fixtures / data"),
    "samples": (DirClass.DATA, "sample data"),
    "migrations": (DirClass.DATA, "database migrations"),

    # DOCS
    "docs": (DirClass.DOCS, "documentation"),
    "doc": (DirClass.DOCS, "documentation"),
    "documentation": (DirClass.DOCS, "documentation"),
    "wiki": (DirClass.DOCS, "wiki pages"),

    # TEST
    "tests": (DirClass.TEST, "test suite"),
    "test": (DirClass.TEST, "test suite"),
    "__tests__": (DirClass.TEST, "test suite (Jest)"),
    "spec": (DirClass.TEST, "test specifications"),
    "specs": (DirClass.TEST, "test specifications"),
    "e2e": (DirClass.TEST, "end-to-end tests"),
    "integration": (DirClass.TEST, "integration tests"),

    # CONFIG
    ".github": (DirClass.INFRA, "GitHub config"),
    ".gitlab": (DirClass.INFRA, "GitLab config"),
    ".circleci": (DirClass.INFRA, "CircleCI config"),
    ".husky": (DirClass.CONFIG, "git hooks"),
    ".vscode": (DirClass.CONFIG, "VS Code settings"),
    ".idea": (DirClass.CONFIG, "IntelliJ settings"),
    ".claude": (DirClass.CONFIG, "Claude settings"),

    # INFRA
    "docker": (DirClass.INFRA, "Docker configuration"),
    "k8s": (DirClass.INFRA, "Kubernetes manifests"),
    "kubernetes": (DirClass.INFRA, "Kubernetes manifests"),
    "terraform": (DirClass.INFRA, "Terraform IaC"),
    "helm": (DirClass.INFRA, "Helm charts"),
    "deploy": (DirClass.INFRA, "deployment config"),
    ".terraform": (DirClass.CACHE, "Terraform cache"),

    # ARCHIVE
    "archive": (DirClass.ARCHIVE, "archived code"),
    ".archive": (DirClass.ARCHIVE, "archived code"),
    "archived": (DirClass.ARCHIVE, "archived code"),
    "old": (DirClass.ARCHIVE, "old code"),
    "deprecated": (DirClass.ARCHIVE, "deprecated code"),
    "legacy": (DirClass.ARCHIVE, "legacy code"),
    "experiments": (DirClass.ARCHIVE, "experimental code"),

    # GENERATED
    "generated": (DirClass.GENERATED, "generated code"),
    "auto-generated": (DirClass.GENERATED, "auto-generated code"),
    "codegen": (DirClass.GENERATED, "code generation output"),
    "proto": (DirClass.GENERATED, "protobuf definitions/generated"),
}

# File extension -> classification (for signal density calculation)
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java',
    '.kt', '.kts', '.rb', '.php', '.cs', '.c', '.cpp', '.h', '.hpp',
    '.swift', '.m', '.scala', '.clj', '.ex', '.exs', '.erl', '.hs',
    '.lua', '.r', '.R', '.jl', '.dart', '.vue', '.svelte',
}

CONFIG_EXTENSIONS = {
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.env', '.properties', '.xml', '.plist',
}

DOC_EXTENSIONS = {
    '.md', '.rst', '.txt', '.adoc', '.org', '.tex',
}

DATA_EXTENSIONS = {
    '.csv', '.tsv', '.parquet', '.arrow', '.sqlite', '.db',
    '.sql', '.jsonl', '.ndjson', '.avro', '.feather',
}

# Framework marker files -> hints about directory purpose
FRAMEWORK_MARKERS = {
    "package.json": "node_project",
    "setup.py": "python_project",
    "pyproject.toml": "python_project",
    "setup.cfg": "python_project",
    "go.mod": "go_project",
    "Cargo.toml": "rust_project",
    "pom.xml": "java_project",
    "build.gradle": "java_project",
    "Gemfile": "ruby_project",
    "composer.json": "php_project",
    "Makefile": "build_system",
    "CMakeLists.txt": "cmake_project",
    "Dockerfile": "containerized",
    "docker-compose.yml": "containerized",
    ".gitignore": "git_tracked",
    "requirements.txt": "python_deps",
    "Pipfile": "python_deps",
    "tsconfig.json": "typescript_project",
    "jest.config.js": "test_config",
    "pytest.ini": "test_config",
    "conftest.py": "test_config",
}


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class DirectorySignal:
    """Classification result for a single directory."""
    path: str                          # Relative path from root
    name: str                          # Directory basename
    depth: int                         # Distance from root (0 = top-level)
    classification: str = DirClass.UNKNOWN
    confidence: float = 0.0            # 0.0 to 1.0
    reason: str = ""                   # Human-readable explanation
    decision: str = Decision.EXPLORE_NEXT  # What to do
    phase: int = 0                     # Which phase classified this

    # Filesystem stats (populated during scan)
    file_count: int = 0
    dir_count: int = 0
    total_size_kb: float = 0.0

    # Signal analysis (populated in Phase 2)
    code_files: int = 0
    config_files: int = 0
    doc_files: int = 0
    data_files: int = 0
    other_files: int = 0
    code_density: float = 0.0          # code_files / total files
    extensions: dict = field(default_factory=dict)   # {".py": 5, ...}
    markers: list = field(default_factory=list)      # ["package.json", ...]


@dataclass
class SmartIgnoreManifest:
    """Complete output of the sequential discovery protocol."""
    root_path: str
    timestamp: str = ""
    discovery_time_ms: float = 0.0

    # Phase results
    phase1_dirs: int = 0               # Directories classified in Phase 1
    phase2_dirs: int = 0               # Directories explored in Phase 2
    total_dirs_scanned: int = 0

    # Decisions
    signals: list = field(default_factory=list)  # List[DirectorySignal]

    # Aggregated decisions
    explore_paths: list = field(default_factory=list)    # Full deep analysis
    skip_paths: list = field(default_factory=list)       # Excluded
    shallow_paths: list = field(default_factory=list)    # Limited depth

    # Stats
    estimated_files_to_analyze: int = 0
    estimated_files_skipped: int = 0
    skip_ratio: float = 0.0            # files_skipped / total

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            f"SmartIgnore Discovery: {self.root_path}",
            f"  Time: {self.discovery_time_ms:.0f}ms",
            f"  Scanned: {self.total_dirs_scanned} directories",
            f"  Phase 1 (name): {self.phase1_dirs} classified",
            f"  Phase 2 (signal): {self.phase2_dirs} explored",
            f"  Decisions:",
            f"    EXPLORE:  {len(self.explore_paths)} dirs (full analysis)",
            f"    SHALLOW:  {len(self.shallow_paths)} dirs (limited)",
            f"    SKIP:     {len(self.skip_paths)} dirs (excluded)",
            f"  Files: ~{self.estimated_files_to_analyze} to analyze, "
            f"~{self.estimated_files_skipped} skipped ({self.skip_ratio:.0%})",
        ]
        return "\n".join(lines)


# ============================================================
# SMART IGNORE ENGINE
# ============================================================

class SmartIgnore:
    """Sequential discovery protocol for intelligent codebase exploration.

    Explores a repository in coordinated phases, making decisions at
    each depth level before going deeper. Produces a SmartIgnoreManifest
    that feeds into the Survey and Analysis pipeline.

    Design principle: never process information you don't need.
    """

    def __init__(self, root_path: str, max_phase2_depth: int = 3):
        self.root = Path(root_path).resolve()
        self.max_phase2_depth = max_phase2_depth
        self.signals: dict[str, DirectorySignal] = {}  # path -> signal

    def discover(self) -> SmartIgnoreManifest:
        """Run the full sequential discovery protocol.

        Returns SmartIgnoreManifest with classified directories.
        """
        start = time.time()
        manifest = SmartIgnoreManifest(
            root_path=str(self.root),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )

        # Phase 1: Classify top-level directories by name
        self._phase1_recon()
        manifest.phase1_dirs = sum(
            1 for s in self.signals.values()
            if s.phase == 1 and s.classification != DirClass.UNKNOWN
        )

        # Phase 2: Signal scan on UNKNOWN/ambiguous directories
        self._phase2_signal_scan()
        manifest.phase2_dirs = sum(
            1 for s in self.signals.values() if s.phase == 2
        )

        # Phase 3: Make final decisions
        self._phase3_decide()

        # Build manifest
        manifest.signals = list(self.signals.values())
        manifest.total_dirs_scanned = len(self.signals)

        for sig in self.signals.values():
            if sig.decision == Decision.EXPLORE:
                manifest.explore_paths.append(sig.path)
                manifest.estimated_files_to_analyze += sig.file_count
            elif sig.decision == Decision.SKIP:
                manifest.skip_paths.append(sig.path)
                manifest.estimated_files_skipped += sig.file_count
            elif sig.decision == Decision.SHALLOW:
                manifest.shallow_paths.append(sig.path)
                manifest.estimated_files_to_analyze += sig.file_count

        total = manifest.estimated_files_to_analyze + manifest.estimated_files_skipped
        manifest.skip_ratio = manifest.estimated_files_skipped / total if total > 0 else 0.0

        manifest.discovery_time_ms = (time.time() - start) * 1000
        return manifest

    # ----------------------------------------------------------
    # PHASE 1: RECON (depth=1, name-based classification)
    # ----------------------------------------------------------

    def _phase1_recon(self):
        """Classify top-level directories by name alone.

        Uses os.scandir for speed (no recursion, no stat calls beyond
        what scandir provides for free).
        """
        try:
            entries = list(os.scandir(self.root))
        except PermissionError:
            return

        for entry in entries:
            if not entry.is_dir(follow_symlinks=False):
                continue

            name = entry.name
            rel_path = name  # top-level, so relative path = name

            signal = DirectorySignal(
                path=rel_path,
                name=name,
                depth=0,
                phase=1,
            )

            # Try name-based classification
            classification = self._classify_by_name(name)
            if classification:
                cls, reason = classification
                signal.classification = cls
                signal.reason = reason
                signal.confidence = 0.95  # name match = high confidence
                signal.decision = self._class_to_decision(cls)
            else:
                signal.classification = DirClass.UNKNOWN
                signal.reason = "no name match"
                signal.confidence = 0.0
                signal.decision = Decision.EXPLORE_NEXT

            # Quick file/dir count (non-recursive, just immediate children)
            try:
                children = list(os.scandir(entry.path))
                signal.file_count = sum(1 for c in children if c.is_file(follow_symlinks=False))
                signal.dir_count = sum(1 for c in children if c.is_dir(follow_symlinks=False))
            except PermissionError:
                pass

            self.signals[rel_path] = signal

    # ----------------------------------------------------------
    # PHASE 2: SIGNAL SCAN (targeted exploration of unknowns)
    # ----------------------------------------------------------

    def _phase2_signal_scan(self):
        """Explore directories that Phase 1 couldn't classify.

        For each UNKNOWN directory, scan its contents to calculate
        code density, detect framework markers, and classify by signal.
        """
        unknowns = [
            s for s in self.signals.values()
            if s.decision == Decision.EXPLORE_NEXT
        ]

        for parent_signal in unknowns:
            self._scan_directory_signal(
                self.root / parent_signal.path,
                parent_signal.path,
                current_depth=1,
            )

    def _scan_directory_signal(self, abs_path: Path, rel_path: str, current_depth: int):
        """Calculate signal density for a directory.

        Counts files by type, detects markers, computes code density.
        Recurses into subdirectories up to max_phase2_depth.
        """
        if current_depth > self.max_phase2_depth:
            return

        signal = self.signals.get(rel_path)
        if signal is None:
            signal = DirectorySignal(
                path=rel_path,
                name=abs_path.name,
                depth=current_depth,
                phase=2,
            )
            self.signals[rel_path] = signal
        else:
            signal.phase = 2

        # Scan immediate contents
        extensions = {}
        markers = []
        code_files = 0
        config_files = 0
        doc_files = 0
        data_files = 0
        other_files = 0
        total_size = 0

        try:
            entries = list(os.scandir(abs_path))
        except PermissionError:
            signal.classification = DirClass.UNKNOWN
            signal.reason = "permission denied"
            signal.confidence = 0.5
            signal.decision = Decision.SKIP
            return

        subdirs = []
        for entry in entries:
            if entry.is_file(follow_symlinks=False):
                ext = Path(entry.name).suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1

                if ext in CODE_EXTENSIONS:
                    code_files += 1
                elif ext in CONFIG_EXTENSIONS:
                    config_files += 1
                elif ext in DOC_EXTENSIONS:
                    doc_files += 1
                elif ext in DATA_EXTENSIONS:
                    data_files += 1
                else:
                    other_files += 1

                # Detect framework markers
                if entry.name in FRAMEWORK_MARKERS:
                    markers.append(entry.name)

                try:
                    total_size += entry.stat(follow_symlinks=False).st_size
                except OSError:
                    pass

            elif entry.is_dir(follow_symlinks=False):
                subdirs.append(entry)

        total_files = code_files + config_files + doc_files + data_files + other_files

        signal.code_files = code_files
        signal.config_files = config_files
        signal.doc_files = doc_files
        signal.data_files = data_files
        signal.other_files = other_files
        signal.file_count = total_files
        signal.dir_count = len(subdirs)
        signal.total_size_kb = total_size / 1024
        signal.extensions = extensions
        signal.markers = markers
        signal.code_density = code_files / total_files if total_files > 0 else 0.0

        # Classify by signal
        self._classify_by_signal(signal)

        # Recurse into subdirectories that need exploration
        for subdir in subdirs:
            sub_name = subdir.name
            sub_rel = f"{rel_path}/{sub_name}"

            # Try name-based classification first (fast path)
            name_cls = self._classify_by_name(sub_name)
            if name_cls:
                cls, reason = name_cls
                sub_signal = DirectorySignal(
                    path=sub_rel,
                    name=sub_name,
                    depth=current_depth + 1,
                    classification=cls,
                    reason=reason,
                    confidence=0.95,
                    decision=self._class_to_decision(cls),
                    phase=2,
                )
                # Quick count for skip estimation
                try:
                    sub_children = list(os.scandir(subdir.path))
                    sub_signal.file_count = sum(1 for c in sub_children if c.is_file(follow_symlinks=False))
                    sub_signal.dir_count = sum(1 for c in sub_children if c.is_dir(follow_symlinks=False))
                except PermissionError:
                    pass
                self.signals[sub_rel] = sub_signal
            else:
                # Need deeper scan
                self._scan_directory_signal(
                    abs_path / sub_name,
                    sub_rel,
                    current_depth + 1,
                )

    def _classify_by_signal(self, signal: DirectorySignal):
        """Classify a directory based on its content signal."""
        density = signal.code_density
        total = signal.file_count

        if total == 0:
            signal.classification = DirClass.UNKNOWN
            signal.reason = "empty directory"
            signal.confidence = 0.8
            signal.decision = Decision.SKIP
            return

        # High code density -> CODE
        if density >= 0.5:
            signal.classification = DirClass.CODE
            signal.reason = f"{density:.0%} code density ({signal.code_files}/{total} files)"
            signal.confidence = min(0.9, 0.5 + density * 0.4)
            signal.decision = Decision.EXPLORE
            return

        # Mostly docs
        if signal.doc_files > 0 and signal.doc_files / total >= 0.5:
            signal.classification = DirClass.DOCS
            signal.reason = f"{signal.doc_files}/{total} documentation files"
            signal.confidence = 0.8
            signal.decision = Decision.SHALLOW
            return

        # Mostly data
        if signal.data_files > 0 and signal.data_files / total >= 0.5:
            signal.classification = DirClass.DATA
            signal.reason = f"{signal.data_files}/{total} data files"
            signal.confidence = 0.8
            signal.decision = Decision.SKIP
            return

        # Mostly config
        if signal.config_files > 0 and signal.config_files / total >= 0.6:
            signal.classification = DirClass.CONFIG
            signal.reason = f"{signal.config_files}/{total} config files"
            signal.confidence = 0.7
            signal.decision = Decision.SHALLOW
            return

        # Low code density but has some code -> include
        if density > 0:
            signal.classification = DirClass.CODE
            signal.reason = f"low code density ({density:.0%}) but has {signal.code_files} source files"
            signal.confidence = 0.6
            signal.decision = Decision.EXPLORE
            return

        # No code at all
        signal.classification = DirClass.DATA
        signal.reason = f"0% code density, {total} non-code files"
        signal.confidence = 0.7
        signal.decision = Decision.SKIP

    # ----------------------------------------------------------
    # PHASE 3: FINAL DECISIONS
    # ----------------------------------------------------------

    def _phase3_decide(self):
        """Finalize decisions, resolve conflicts, propagate parents."""
        # Ensure any remaining EXPLORE_NEXT gets a decision
        for signal in self.signals.values():
            if signal.decision == Decision.EXPLORE_NEXT:
                # Default: if we still don't know, explore it
                signal.decision = Decision.EXPLORE
                signal.reason = signal.reason or "unclassified, included by default"
                signal.confidence = max(signal.confidence, 0.3)

    # ----------------------------------------------------------
    # HELPERS
    # ----------------------------------------------------------

    @staticmethod
    def _classify_by_name(name: str) -> Optional[tuple[str, str]]:
        """Try to classify a directory by name alone.

        Returns (classification, reason) or None.
        """
        lower = name.lower()

        # Direct match
        if lower in NAME_CLASSIFICATIONS:
            return NAME_CLASSIFICATIONS[lower]

        # Glob-style patterns (e.g., *.egg-info)
        for pattern, (cls, reason) in NAME_CLASSIFICATIONS.items():
            if '*' in pattern and fnmatch.fnmatch(lower, pattern):
                return (cls, reason)

        # Heuristic: dotfile directories that look like caches
        if lower.startswith('.') and lower.endswith('_cache'):
            return (DirClass.CACHE, f"cache directory ({name})")

        # Heuristic: directories starting with _ often archival
        if lower.startswith('_') and lower not in ('_build', '__tests__', '__pycache__'):
            # Don't auto-classify, let signal scan decide
            return None

        return None

    @staticmethod
    def _class_to_decision(cls: str) -> str:
        """Map a classification to a default decision."""
        return {
            DirClass.CODE: Decision.EXPLORE,
            DirClass.VENDOR: Decision.SKIP,
            DirClass.BUILD: Decision.SKIP,
            DirClass.CACHE: Decision.SKIP,
            DirClass.DATA: Decision.SKIP,
            DirClass.DOCS: Decision.SHALLOW,
            DirClass.GENERATED: Decision.SKIP,
            DirClass.TEST: Decision.EXPLORE,
            DirClass.CONFIG: Decision.SHALLOW,
            DirClass.INFRA: Decision.SHALLOW,
            DirClass.ARCHIVE: Decision.SKIP,
            DirClass.UNKNOWN: Decision.EXPLORE_NEXT,
        }.get(cls, Decision.EXPLORE_NEXT)

    # ----------------------------------------------------------
    # OUTPUT: .smartignore FILE
    # ----------------------------------------------------------

    def write_smartignore(self, manifest: SmartIgnoreManifest, output_path: Optional[str] = None) -> str:
        """Write a .smartignore file from a manifest.

        The file is human-readable, cacheable, and can be loaded
        by the Survey and Analysis pipeline.

        Returns the path to the written file.
        """
        if output_path is None:
            output_path = str(self.root / ".smartignore")

        lines = [
            "# .smartignore - Auto-generated by Collider Sequential Discovery",
            f"# Generated: {manifest.timestamp}",
            f"# Root: {manifest.root_path}",
            f"# Discovery: {manifest.discovery_time_ms:.0f}ms, "
            f"{manifest.total_dirs_scanned} dirs scanned",
            f"# Skip ratio: {manifest.skip_ratio:.0%} "
            f"(~{manifest.estimated_files_skipped} files excluded)",
            "#",
            "# Format: path/ # CLASSIFICATION: reason",
            "# Lines starting with ! are INCLUDE overrides",
            "#",
            "",
        ]

        # Group by decision
        skips = sorted(
            [s for s in manifest.signals if s.decision == Decision.SKIP],
            key=lambda s: s.path
        )
        shallows = sorted(
            [s for s in manifest.signals if s.decision == Decision.SHALLOW],
            key=lambda s: s.path
        )
        explores = sorted(
            [s for s in manifest.signals if s.decision == Decision.EXPLORE],
            key=lambda s: s.path
        )

        if skips:
            lines.append("# ── SKIP (excluded from analysis) ──")
            for s in skips:
                files_note = f"{s.file_count} files" if s.file_count > 0 else "empty"
                lines.append(f"{s.path}/  # {s.classification}: {s.reason} ({files_note})")
            lines.append("")

        if shallows:
            lines.append("# ── SHALLOW (limited depth analysis) ──")
            for s in shallows:
                files_note = f"{s.file_count} files" if s.file_count > 0 else "empty"
                lines.append(f"~{s.path}/  # {s.classification}: {s.reason} ({files_note})")
            lines.append("")

        if explores:
            lines.append("# ── EXPLORE (full deep analysis) ──")
            for s in explores:
                density = f"{s.code_density:.0%} code" if s.code_density > 0 else "unscanned"
                lines.append(f"!{s.path}/  # {s.classification}: {s.reason} ({density})")
            lines.append("")

        content = "\n".join(lines)

        with open(output_path, 'w') as f:
            f.write(content)

        return output_path

    # ----------------------------------------------------------
    # OUTPUT: JSON (for pipeline consumption)
    # ----------------------------------------------------------

    def manifest_to_dict(self, manifest: SmartIgnoreManifest) -> dict:
        """Convert manifest to a dictionary for JSON serialization."""
        return {
            "smartignore_version": "1.0.0",
            "root_path": manifest.root_path,
            "timestamp": manifest.timestamp,
            "discovery_time_ms": round(manifest.discovery_time_ms, 1),
            "total_dirs_scanned": manifest.total_dirs_scanned,
            "phase1_classified": manifest.phase1_dirs,
            "phase2_explored": manifest.phase2_dirs,
            "decisions": {
                "explore": manifest.explore_paths,
                "shallow": manifest.shallow_paths,
                "skip": manifest.skip_paths,
            },
            "estimates": {
                "files_to_analyze": manifest.estimated_files_to_analyze,
                "files_skipped": manifest.estimated_files_skipped,
                "skip_ratio": round(manifest.skip_ratio, 3),
            },
            "signals": [
                {
                    "path": s.path,
                    "classification": s.classification,
                    "decision": s.decision,
                    "confidence": round(s.confidence, 2),
                    "reason": s.reason,
                    "code_density": round(s.code_density, 2),
                    "file_count": s.file_count,
                    "phase": s.phase,
                }
                for s in manifest.signals
            ],
        }


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def run_smart_ignore(root_path: str, write_file: bool = True) -> SmartIgnoreManifest:
    """Run SmartIgnore discovery and optionally write .smartignore file.

    This is the main entry point for the pipeline.
    """
    si = SmartIgnore(root_path)
    manifest = si.discover()

    if write_file:
        si.write_smartignore(manifest)

    return manifest


def load_smartignore(path: str) -> list[str]:
    """Load skip paths from an existing .smartignore file.

    Returns list of paths to exclude (compatible with survey exclude_paths).
    """
    skip_paths = []
    smartignore_path = Path(path)

    if not smartignore_path.exists():
        return skip_paths

    with open(smartignore_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            # Skip EXPLORE lines (! prefix)
            if line.startswith('!'):
                continue
            # Skip SHALLOW lines (~ prefix) -- they're included
            if line.startswith('~'):
                continue
            # Extract path (before the # comment)
            path_part = line.split('#')[0].strip().rstrip('/')
            if path_part:
                skip_paths.append(path_part)

    return skip_paths
