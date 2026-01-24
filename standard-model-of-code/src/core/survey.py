"""
CODOME DEFINITION LAYER (Stage 0)
==================================

This module defines the ONTOLOGY of the target system before analysis begins.
It is not merely an optimization (exclusion); it is a DEFINITION.

"Before you measure a thing, you must define what the thing IS."

The Survey answers 5 fundamental questions:

1. IDENTITY: What IS this system?
   - Primary language (Python, TypeScript, Go...)
   - Dominant framework (Django, Next.js, FastAPI...)
   - Archetype (Monolith, Monorepo, Microservices, Library)

2. BOUNDARIES: Where does it START and END?
   - What is OURS vs VENDOR vs GENERATED?
   - Spatial boundaries (directories to include/exclude)

3. NATURE: What is the TEXTURE of this codebase?
   - Code vs Config vs Data ratios
   - File type distribution

4. POLLUTION: What VIOLATES the physics of this repo?
   - Vendor code in src/
   - Minified files without markers
   - Binary artifacts in source tree

5. ADAPTATION: How must the INSTRUMENTS be calibrated?
   - Which parsers to use
   - What thresholds apply
   - Expected patterns

Output: CodomeManifest - the complete ontological definition

Usage:
    from survey import run_survey, CodomeManifest

    manifest = run_survey("/path/to/repo")
    print(f"Identity: {manifest.identity}")
    print(f"Boundaries: {len(manifest.boundary_constraints)} exclusions")

See also:
    - docs/specs/CODOME_BOUNDARY_DEFINITION.md
    - docs/specs/CODOME_COMPLETENESS_INDEX.md
    - docs/specs/CODOME_HEALTH_INDEX.md

Phase: 10 (Adaptive Intelligence Layer)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os
import fnmatch
import yaml
import time


# ============================================================
# CONFIGURATION
# ============================================================

# Default patterns for exclusion detection
DEFAULT_DIRECTORY_PATTERNS = [
    "node_modules/",
    "vendor/",
    ".vendor/",
    ".repos_cache/",  # Test repository caches (calibration data)
    "lib/",
    "dist/",
    "build/",
    "out/",
    ".git/",
    "__pycache__/",
    ".venv/",
    "venv/",
    "coverage/",
    ".nyc_output/",
    ".next/",
    ".nuxt/",
]

DEFAULT_FILE_PATTERNS = [
    "*.min.js",
    "*.min.css",
    "*.bundle.js",
    "*.chunk.js",
    "*.generated.*",
    "*.pb.go",
    "*.pb.ts",
    "*.pb.js",
    "*_pb2.py",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
]

# Heuristics for minification detection
MINIFIED_THRESHOLDS = {
    "single_line_size_kb": 10,      # Single-line file > 10KB = likely minified
    "avg_line_length": 500,          # Avg line > 500 chars = likely minified
    "max_reasonable_line": 1000,     # Any line > 1000 chars = suspicious
    "whitespace_ratio_min": 0.05,    # Less than 5% whitespace = likely minified
}


# ============================================================
# DATA STRUCTURES - ONTOLOGICAL (The 5 Questions)
# ============================================================

# Q1: IDENTITY - What IS this system?
@dataclass
class SystemIdentity:
    """The fundamental identity of the codebase (Question 1).

    Archetype values: monolith, monorepo, microservices, library, cli, unknown
    """
    primary_language: str = "unknown"
    secondary_languages: list[str] = field(default_factory=list)
    dominant_framework: str = "unknown"
    archetype: str = "unknown"  # NOT topology! See terminology guide.
    confidence: float = 0.0

    def __str__(self) -> str:
        langs = f"{self.primary_language}"
        if self.secondary_languages:
            langs += f" (+{', '.join(self.secondary_languages)})"
        framework = f" / {self.dominant_framework}" if self.dominant_framework != "unknown" else ""
        return f"{langs}{framework} ({self.archetype})"


# Q3: NATURE - What is the TEXTURE?
@dataclass
class CodomeComposition:
    """The composition breakdown of the codebase (Question 3)."""
    source_files: int = 0
    config_files: int = 0
    data_files: int = 0
    doc_files: int = 0
    binary_files: int = 0
    other_files: int = 0

    @property
    def total(self) -> int:
        """Return total file count across all categories."""
        return (self.source_files + self.config_files + self.data_files +
                self.doc_files + self.binary_files + self.other_files)

    @property
    def source_ratio(self) -> float:
        """Return ratio of source files to total files (0.0 to 1.0)."""
        return self.source_files / self.total if self.total > 0 else 0.0

    def as_percentages(self) -> dict[str, float]:
        """Return file type distribution as percentages."""
        t = self.total or 1
        return {
            "source": self.source_files / t,
            "config": self.config_files / t,
            "data": self.data_files / t,
            "docs": self.doc_files / t,
            "binary": self.binary_files / t,
            "other": self.other_files / t,
        }


# Q4: POLLUTION - What shouldn't be here?
@dataclass
class PollutionAlert:
    """A detected pollution issue (Question 4)."""
    path: str
    pollution_type: str  # vendor_in_src, minified_unmarked, binary_in_source, etc.
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    recommendation: str


# ============================================================
# DATA STRUCTURES - DETECTION RESULTS
# ============================================================

@dataclass
class ExclusionMatch:
    """A single exclusion detection result."""
    path: str
    pattern: str
    reason: str
    confidence: float  # 0.0 - 1.0
    file_count: int = 0
    total_size_kb: float = 0.0


@dataclass
class MinifiedFile:
    """A detected minified file."""
    path: str
    reason: str
    size_kb: float
    line_count: int
    avg_line_length: float


@dataclass
class CCIMetrics:
    """Codome Completeness Index metrics.

    Measures how complete and accurate our code analysis is:
    - Sensitivity (Recall): What % of source code did we capture?
    - Specificity: What % of vendor code did we exclude?
    - Precision: What % of analyzed nodes are actually ours?
    - F2 Score: Recall-weighted harmonic mean (prioritizes completeness)

    See: docs/specs/CODOME_COMPLETENESS_INDEX.md
    """
    # Core classification counts
    true_positives: int = 0   # SOURCE correctly analyzed
    false_positives: int = 0  # VENDOR incorrectly analyzed
    true_negatives: int = 0   # VENDOR correctly excluded
    false_negatives: int = 0  # SOURCE incorrectly excluded

    # Derived metrics (calculated from counts)
    sensitivity: float = 0.0  # TP / (TP + FN) - Recall
    specificity: float = 0.0  # TN / (TN + FP)
    precision: float = 0.0    # TP / (TP + FP)
    f1_score: float = 0.0     # Harmonic mean
    f2_score: float = 0.0     # Recall-weighted (recommended)
    gmean: float = 0.0        # sqrt(Sensitivity * Specificity)

    # Overall score and interpretation
    cci: float = 0.0          # Primary CCI score (F2 * 100)
    verdict: str = "UNKNOWN"  # EXCELLENT/GOOD/FAIR/POOR


def calculate_cci(
    total_source_files: int,
    analyzed_source_files: int,
    total_vendor_files: int,
    analyzed_vendor_files: int,
) -> CCIMetrics:
    """Calculate Codome Completeness Index from classification results.

    Args:
        total_source_files: Ground truth count of source files
        analyzed_source_files: Source files we actually analyzed (TP)
        total_vendor_files: Ground truth count of vendor/generated files
        analyzed_vendor_files: Vendor files we incorrectly analyzed (FP)

    Returns:
        CCIMetrics with all calculated values
    """
    import math

    metrics = CCIMetrics()

    # Classification counts
    metrics.true_positives = analyzed_source_files
    metrics.false_positives = analyzed_vendor_files
    metrics.true_negatives = total_vendor_files - analyzed_vendor_files
    metrics.false_negatives = total_source_files - analyzed_source_files

    tp, fp, tn, fn = (
        metrics.true_positives,
        metrics.false_positives,
        metrics.true_negatives,
        metrics.false_negatives,
    )

    # Sensitivity (Recall) = TP / (TP + FN)
    if tp + fn > 0:
        metrics.sensitivity = tp / (tp + fn)

    # Specificity = TN / (TN + FP)
    if tn + fp > 0:
        metrics.specificity = tn / (tn + fp)

    # Precision = TP / (TP + FP)
    if tp + fp > 0:
        metrics.precision = tp / (tp + fp)

    # F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
    if metrics.precision + metrics.sensitivity > 0:
        metrics.f1_score = (
            2 * metrics.precision * metrics.sensitivity
        ) / (metrics.precision + metrics.sensitivity)

    # F2 Score = 5 * (Precision * Recall) / (4 * Precision + Recall)
    if 4 * metrics.precision + metrics.sensitivity > 0:
        metrics.f2_score = (
            5 * metrics.precision * metrics.sensitivity
        ) / (4 * metrics.precision + metrics.sensitivity)

    # G-Mean = sqrt(Sensitivity * Specificity)
    metrics.gmean = math.sqrt(metrics.sensitivity * metrics.specificity)

    # CCI = F2 * 100 (recommended metric)
    metrics.cci = metrics.f2_score * 100

    # Verdict
    if metrics.cci >= 95:
        metrics.verdict = "EXCELLENT"
    elif metrics.cci >= 85:
        metrics.verdict = "GOOD"
    elif metrics.cci >= 70:
        metrics.verdict = "FAIR"
    else:
        metrics.verdict = "POOR"

    return metrics


@dataclass
class SurveyResult:
    """Complete Codome Definition (CodomeManifest).

    This is the ontological definition of the codebase, answering:
    - Q1: IDENTITY (what is this system?)
    - Q2: BOUNDARIES (what's ours vs vendor?)
    - Q3: NATURE (code/config/data ratios)
    - Q4: POLLUTION (what shouldn't be here?)
    - Q5: ADAPTATION (pipeline configuration)
    """
    root_path: str
    scan_time_ms: float

    # Q1: IDENTITY - What IS this system?
    identity: SystemIdentity = field(default_factory=SystemIdentity)

    # Q3: NATURE - Composition breakdown
    composition: CodomeComposition = field(default_factory=CodomeComposition)

    # Q4: POLLUTION - Detected issues
    pollution_alerts: list[PollutionAlert] = field(default_factory=list)

    # Q2: BOUNDARIES - Spatial boundaries (legacy names kept for compatibility)
    directory_exclusions: list[ExclusionMatch] = field(default_factory=list)
    file_exclusions: list[ExclusionMatch] = field(default_factory=list)
    minified_files: list[MinifiedFile] = field(default_factory=list)

    # Counts (raw)
    total_files: int = 0
    total_dirs: int = 0
    total_size_kb: float = 0.0

    # Estimates (after exclusions)
    estimated_source_files: int = 0
    estimated_nodes: int = 0  # Rough estimate: ~75 nodes per source file

    # Q5: ADAPTATION - Pipeline configuration
    recommended_excludes: list[str] = field(default_factory=list)
    recommended_parsers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Codome Completeness Index (optional - populated after analysis comparison)
    cci: Optional[CCIMetrics] = None

    # Aliases for ontological access
    @property
    def boundary_constraints(self) -> list[str]:
        """Q2: Boundary constraints (alias for recommended_excludes)."""
        return self.recommended_excludes

    @property
    def exclusion_count(self) -> int:
        """Return total count of excluded directories, files, and minified artifacts."""
        return len(self.directory_exclusions) + len(self.file_exclusions) + len(self.minified_files)

    @property
    def signal_to_noise_ratio(self) -> float:
        """Ratio of source files to total files (higher = better)."""
        if self.total_files == 0:
            return 1.0
        return self.estimated_source_files / self.total_files

    @property
    def pollution_level(self) -> str:
        """Overall pollution assessment."""
        high_count = sum(1 for p in self.pollution_alerts if p.severity == "HIGH")
        medium_count = sum(1 for p in self.pollution_alerts if p.severity == "MEDIUM")
        if high_count > 0:
            return "HIGH"
        elif medium_count > 2:
            return "MEDIUM"
        elif len(self.pollution_alerts) > 0:
            return "LOW"
        return "CLEAN"

    @property
    def boundary_rigidity(self) -> str:
        """How rigid are the boundaries?"""
        if len(self.recommended_excludes) > 10:
            return "RIGID"
        elif len(self.recommended_excludes) > 3:
            return "MODERATE"
        elif len(self.recommended_excludes) > 0:
            return "PERMEABLE"
        return "OPEN"


# Alias for semantic clarity
CodomeManifest = SurveyResult


# ============================================================
# PATTERN DETECTION
# ============================================================

def path_matches_pattern(path: str, pattern: str) -> bool:
    """
    Check if a path matches an exclusion pattern.

    Supports:
    - Directory patterns: "vendor/" matches any path containing /vendor/
    - File patterns: "*.min.js" matches files ending in .min.js
    - Glob patterns: "**/*.generated.*" for recursive matching
    """
    path_lower = path.lower()
    pattern_lower = pattern.lower()

    # Directory pattern (ends with /)
    if pattern_lower.endswith('/'):
        dir_name = pattern_lower.rstrip('/')
        # Match /dirname/ anywhere in path
        return f"/{dir_name}/" in f"/{path_lower}/" or path_lower.startswith(f"{dir_name}/")

    # File pattern (contains *)
    if '*' in pattern:
        filename = os.path.basename(path)
        return fnmatch.fnmatch(filename.lower(), pattern_lower)

    # Exact match
    return path_lower == pattern_lower or path_lower.endswith(f"/{pattern_lower}")


def scan_for_exclusions(
    root: Path,
    dir_patterns: list[str] = None,
    file_patterns: list[str] = None,
    max_depth: int = 10
) -> tuple[list[ExclusionMatch], list[ExclusionMatch]]:
    """
    Scan directory for exclusion candidates.

    Returns:
        (directory_exclusions, file_exclusions)
    """
    dir_patterns = dir_patterns or DEFAULT_DIRECTORY_PATTERNS
    file_patterns = file_patterns or DEFAULT_FILE_PATTERNS

    dir_exclusions = []
    file_exclusions = []

    # Track already-matched directories to avoid duplicate counting
    matched_dirs = set()

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        depth = rel_dir.count(os.sep) if rel_dir != '.' else 0

        if depth > max_depth:
            dirnames.clear()  # Don't descend further
            continue

        # Check directory patterns
        for pattern in dir_patterns:
            if path_matches_pattern(rel_dir, pattern):
                if rel_dir not in matched_dirs:
                    matched_dirs.add(rel_dir)

                    # Count files and size in this directory
                    file_count = 0
                    total_size = 0
                    for dp, _, fns in os.walk(dirpath):
                        file_count += len(fns)
                        for fn in fns:
                            try:
                                total_size += os.path.getsize(os.path.join(dp, fn))
                            except OSError:
                                pass

                    dir_exclusions.append(ExclusionMatch(
                        path=rel_dir,
                        pattern=pattern,
                        reason=_get_pattern_reason(pattern),
                        confidence=1.0,
                        file_count=file_count,
                        total_size_kb=total_size / 1024
                    ))

                    # Don't descend into excluded directories
                    dirnames.clear()
                    break

        # Check file patterns (only if directory not excluded)
        if rel_dir not in matched_dirs:
            for filename in filenames:
                rel_path = os.path.join(rel_dir, filename) if rel_dir != '.' else filename
                for pattern in file_patterns:
                    if path_matches_pattern(filename, pattern):
                        try:
                            size = os.path.getsize(os.path.join(dirpath, filename)) / 1024
                        except OSError:
                            size = 0

                        file_exclusions.append(ExclusionMatch(
                            path=rel_path,
                            pattern=pattern,
                            reason=_get_pattern_reason(pattern),
                            confidence=0.95,
                            file_count=1,
                            total_size_kb=size
                        ))
                        break

    return dir_exclusions, file_exclusions


def _get_pattern_reason(pattern: str) -> str:
    """Get human-readable reason for a pattern."""
    reasons = {
        "node_modules/": "npm dependencies",
        "vendor/": "vendored dependencies",
        ".vendor/": "vendored dependencies",
        "dist/": "build output",
        "build/": "build output",
        "out/": "build output",
        ".git/": "git internals",
        "__pycache__/": "Python bytecode cache",
        ".venv/": "Python virtual environment",
        "venv/": "Python virtual environment",
        "coverage/": "test coverage data",
        ".nyc_output/": "test coverage data",
        ".next/": "Next.js build cache",
        ".nuxt/": "Nuxt.js build cache",
        "lib/": "library dependencies",
        "*.min.js": "minified JavaScript",
        "*.min.css": "minified CSS",
        "*.bundle.js": "bundled JavaScript",
        "*.chunk.js": "code-split chunk",
        "*.generated.*": "generated code",
        "*.pb.go": "protobuf generated (Go)",
        "*.pb.ts": "protobuf generated (TypeScript)",
        "*.pb.js": "protobuf generated (JavaScript)",
        "*_pb2.py": "protobuf generated (Python)",
        "*.lock": "lock file",
        "package-lock.json": "npm lock file",
        "yarn.lock": "yarn lock file",
        "pnpm-lock.yaml": "pnpm lock file",
    }
    return reasons.get(pattern, "matched exclusion pattern")


# ============================================================
# IDENTITY DETECTION (Q1: What IS this system?)
# ============================================================

# Language detection by file extension
LANGUAGE_EXTENSIONS = {
    # Primary languages
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".swift": "swift",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".scala": "scala",
    ".clj": "clojure",
    ".ex": "elixir",
    ".exs": "elixir",
    ".erl": "erlang",
    ".hs": "haskell",
    ".ml": "ocaml",
    ".lua": "lua",
    ".r": "r",
    ".R": "r",
    ".jl": "julia",
    ".dart": "dart",
    ".vue": "vue",
    ".svelte": "svelte",
}

# Framework detection markers
FRAMEWORK_MARKERS = {
    # Python frameworks
    ("requirements.txt", "django"): "django",
    ("requirements.txt", "flask"): "flask",
    ("requirements.txt", "fastapi"): "fastapi",
    ("pyproject.toml", "django"): "django",
    ("pyproject.toml", "flask"): "flask",
    ("pyproject.toml", "fastapi"): "fastapi",
    # JavaScript/TypeScript frameworks
    ("package.json", "next"): "nextjs",
    ("package.json", "react"): "react",
    ("package.json", "vue"): "vue",
    ("package.json", "angular"): "angular",
    ("package.json", "svelte"): "svelte",
    ("package.json", "express"): "express",
    ("package.json", "nestjs"): "nestjs",
    ("package.json", "nuxt"): "nuxt",
    # Go frameworks
    ("go.mod", "gin"): "gin",
    ("go.mod", "echo"): "echo",
    ("go.mod", "fiber"): "fiber",
    # Rust frameworks
    ("Cargo.toml", "actix"): "actix",
    ("Cargo.toml", "rocket"): "rocket",
    ("Cargo.toml", "axum"): "axum",
    # Ruby frameworks
    ("Gemfile", "rails"): "rails",
    ("Gemfile", "sinatra"): "sinatra",
}

# Archetype detection markers
ARCHETYPE_MARKERS = {
    # Monorepo markers
    "pnpm-workspace.yaml": "monorepo",
    "lerna.json": "monorepo",
    "nx.json": "monorepo",
    "turbo.json": "monorepo",
    "rush.json": "monorepo",
    # Library markers
    "setup.py": "library",
    "pyproject.toml": "library",  # weak - needs content check
    "Cargo.toml": "library",      # weak - needs content check
    # CLI markers
    "bin/": "cli",
    "cmd/": "cli",
}


def detect_identity(root: Path, exclude_dirs: list[str] = None) -> SystemIdentity:
    """Detect the fundamental identity of the codebase (Q1).

    Returns:
        SystemIdentity with language, framework, and archetype
    """
    exclude_dirs = exclude_dirs or DEFAULT_DIRECTORY_PATTERNS
    identity = SystemIdentity()

    # Count files by language extension
    lang_counts: dict[str, int] = {}
    total_code_files = 0

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)

        # Skip excluded directories
        skip = False
        for pattern in exclude_dirs:
            if path_matches_pattern(rel_dir, pattern):
                skip = True
                dirnames.clear()
                break
        if skip:
            continue

        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in LANGUAGE_EXTENSIONS:
                lang = LANGUAGE_EXTENSIONS[ext]
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
                total_code_files += 1

    # Determine primary and secondary languages
    if lang_counts:
        sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)
        identity.primary_language = sorted_langs[0][0]
        identity.secondary_languages = [l for l, _ in sorted_langs[1:4] if lang_counts[l] > total_code_files * 0.05]
        identity.confidence = sorted_langs[0][1] / total_code_files if total_code_files > 0 else 0.0

    # Detect framework from manifest files
    identity.dominant_framework = _detect_framework(root)

    # Detect archetype
    identity.archetype = _detect_archetype(root)

    return identity


def _detect_framework(root: Path) -> str:
    """Detect dominant framework from manifest files."""
    manifest_files = {
        "package.json": root / "package.json",
        "requirements.txt": root / "requirements.txt",
        "pyproject.toml": root / "pyproject.toml",
        "go.mod": root / "go.mod",
        "Cargo.toml": root / "Cargo.toml",
        "Gemfile": root / "Gemfile",
    }

    for manifest_name, manifest_path in manifest_files.items():
        if manifest_path.exists():
            try:
                content = manifest_path.read_text(encoding='utf-8', errors='ignore').lower()
                for (m_file, marker), framework in FRAMEWORK_MARKERS.items():
                    if m_file == manifest_name and marker in content:
                        return framework
            except (OSError, IOError):
                continue

    return "unknown"


def _detect_archetype(root: Path) -> str:
    """Detect project archetype (organizational structure)."""
    # Check for explicit monorepo markers
    for marker, archetype in ARCHETYPE_MARKERS.items():
        if marker.endswith('/'):
            if (root / marker.rstrip('/')).is_dir():
                return archetype
        else:
            if (root / marker).exists():
                # Strong monorepo markers
                if archetype == "monorepo":
                    return "monorepo"

    # Check for packages/ or apps/ directories (monorepo indicator)
    if (root / "packages").is_dir() or (root / "apps").is_dir():
        return "monorepo"

    # Check for microservices pattern (multiple service directories)
    service_dirs = [d for d in root.iterdir() if d.is_dir() and
                    any(d.name.endswith(s) for s in ['-service', '-api', '-worker', '-gateway'])]
    if len(service_dirs) >= 3:
        return "microservices"

    # Check for library indicators
    if (root / "setup.py").exists() or (root / "setup.cfg").exists():
        return "library"

    # Check pyproject.toml for library vs application
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            if "[project]" in content or "[tool.poetry]" in content:
                # Has package definition - likely a library
                if "dependencies" in content and "scripts" not in content:
                    return "library"
        except (OSError, IOError):
            pass

    # Check for CLI indicators
    if (root / "bin").is_dir() or (root / "cmd").is_dir():
        return "cli"

    # Default to monolith
    return "monolith"


# ============================================================
# COMPOSITION DETECTION (Q3: What is the TEXTURE?)
# ============================================================

# File type classification
SOURCE_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java', '.kt',
                     '.swift', '.rb', '.php', '.cs', '.cpp', '.c', '.h', '.hpp', '.scala',
                     '.clj', '.ex', '.exs', '.erl', '.hs', '.ml', '.lua', '.r', '.jl',
                     '.dart', '.vue', '.svelte'}
CONFIG_EXTENSIONS = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env',
                     '.xml', '.properties'}
DATA_EXTENSIONS = {'.csv', '.sql', '.graphql', '.gql', '.prisma', '.proto'}
DOC_EXTENSIONS = {'.md', '.rst', '.txt', '.adoc', '.org'}
BINARY_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp', '.bmp',
                     '.woff', '.woff2', '.ttf', '.eot', '.otf', '.mp3', '.mp4', '.wav',
                     '.pdf', '.zip', '.tar', '.gz', '.wasm', '.so', '.dll', '.exe'}


def detect_composition(root: Path, exclude_dirs: list[str] = None) -> CodomeComposition:
    """Detect the composition breakdown of the codebase (Q3).

    Returns:
        CodomeComposition with file type counts
    """
    exclude_dirs = exclude_dirs or DEFAULT_DIRECTORY_PATTERNS
    composition = CodomeComposition()

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)

        # Skip excluded directories
        skip = False
        for pattern in exclude_dirs:
            if path_matches_pattern(rel_dir, pattern):
                skip = True
                dirnames.clear()
                break
        if skip:
            continue

        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()

            if ext in SOURCE_EXTENSIONS:
                composition.source_files += 1
            elif ext in CONFIG_EXTENSIONS:
                composition.config_files += 1
            elif ext in DATA_EXTENSIONS:
                composition.data_files += 1
            elif ext in DOC_EXTENSIONS:
                composition.doc_files += 1
            elif ext in BINARY_EXTENSIONS:
                composition.binary_files += 1
            else:
                composition.other_files += 1

    return composition


# ============================================================
# POLLUTION DETECTION (Q4: What VIOLATES the physics?)
# ============================================================

def detect_pollution(
    root: Path,
    exclude_dirs: list[str] = None,
    minified_files: list[MinifiedFile] = None
) -> list[PollutionAlert]:
    """Detect pollution issues in the codebase (Q4).

    Pollution types:
    - vendor_in_src: Vendor code in source directories
    - minified_unmarked: Minified files without .min. marker
    - binary_in_source: Binary files in source directories
    - generated_unmarked: Generated code without markers
    - orphaned_config: Config files with no matching code

    Returns:
        List of PollutionAlert objects
    """
    exclude_dirs = exclude_dirs or DEFAULT_DIRECTORY_PATTERNS
    alerts: list[PollutionAlert] = []

    # Check for minified files without markers (already detected)
    if minified_files:
        for mf in minified_files:
            if '.min.' not in mf.path and '.bundle.' not in mf.path:
                alerts.append(PollutionAlert(
                    path=mf.path,
                    pollution_type="minified_unmarked",
                    severity="MEDIUM",
                    description=f"Minified file without .min. marker: {mf.reason}",
                    recommendation="Rename to include .min. or exclude from analysis"
                ))

    # Check for vendor patterns in source directories
    vendor_in_src_patterns = [
        ("jquery", "jQuery library"),
        ("lodash", "Lodash library"),
        ("underscore", "Underscore library"),
        ("moment", "Moment.js library"),
        ("axios", "Axios library"),
        ("d3.v", "D3.js library"),
    ]

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)

        # Skip excluded directories
        skip = False
        for pattern in exclude_dirs:
            if path_matches_pattern(rel_dir, pattern):
                skip = True
                dirnames.clear()
                break
        if skip:
            continue

        # Only check in source-like directories
        if not any(src in rel_dir for src in ['src', 'lib', 'app', 'core']):
            continue

        for filename in filenames:
            rel_path = os.path.join(rel_dir, filename) if rel_dir != '.' else filename
            filename_lower = filename.lower()

            # Check for vendor patterns in filename
            for pattern, desc in vendor_in_src_patterns:
                if pattern in filename_lower:
                    alerts.append(PollutionAlert(
                        path=rel_path,
                        pollution_type="vendor_in_src",
                        severity="HIGH",
                        description=f"{desc} found in source directory",
                        recommendation="Move to vendor/ or node_modules/, or install via package manager"
                    ))
                    break

            # Check for binary files in source directories
            ext = os.path.splitext(filename)[1].lower()
            if ext in BINARY_EXTENSIONS:
                alerts.append(PollutionAlert(
                    path=rel_path,
                    pollution_type="binary_in_source",
                    severity="LOW",
                    description=f"Binary file ({ext}) in source directory",
                    recommendation="Move to assets/ or public/ directory"
                ))

    return alerts


# ============================================================
# MINIFICATION DETECTION
# ============================================================

def detect_minified_files(
    root: Path,
    extensions: list[str] = None,
    exclude_dirs: list[str] = None
) -> list[MinifiedFile]:
    """
    Detect minified files using heuristics.

    Heuristics:
    1. Single-line file > 10KB
    2. Average line length > 500 characters
    3. Very low whitespace ratio
    """
    extensions = extensions or ['.js', '.css', '.ts']
    exclude_dirs = exclude_dirs or DEFAULT_DIRECTORY_PATTERNS

    minified = []

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)

        # Skip excluded directories
        skip = False
        for pattern in exclude_dirs:
            if path_matches_pattern(rel_dir, pattern):
                skip = True
                dirnames.clear()
                break
        if skip:
            continue

        for filename in filenames:
            # Skip already-marked minified files
            if '.min.' in filename or '.bundle.' in filename:
                continue

            # Check extension
            ext = os.path.splitext(filename)[1].lower()
            if ext not in extensions:
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.join(rel_dir, filename) if rel_dir != '.' else filename

            result = _check_minified(filepath)
            if result:
                minified.append(MinifiedFile(
                    path=rel_path,
                    reason=result['reason'],
                    size_kb=result['size_kb'],
                    line_count=result['line_count'],
                    avg_line_length=result['avg_line_length']
                ))

    return minified


def _check_minified(filepath: str) -> Optional[dict]:
    """
    Check if a file appears to be minified.

    Returns dict with details if minified, None otherwise.
    """
    try:
        size_bytes = os.path.getsize(filepath)
        size_kb = size_bytes / 1024

        # Small files are unlikely to be problematically minified
        if size_kb < 5:
            return None

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(500_000)  # Read first 500KB max

        lines = content.split('\n')
        line_count = len(lines)

        # Single line file > threshold
        if line_count <= 2 and size_kb > MINIFIED_THRESHOLDS['single_line_size_kb']:
            return {
                'reason': f"Single-line file ({size_kb:.1f}KB)",
                'size_kb': size_kb,
                'line_count': line_count,
                'avg_line_length': len(content) / max(line_count, 1)
            }

        # Average line length check
        avg_line_len = len(content) / max(line_count, 1)
        if avg_line_len > MINIFIED_THRESHOLDS['avg_line_length']:
            return {
                'reason': f"Very long lines (avg {avg_line_len:.0f} chars)",
                'size_kb': size_kb,
                'line_count': line_count,
                'avg_line_length': avg_line_len
            }

        # Whitespace ratio check (for larger files)
        if size_kb > 20:
            whitespace_count = sum(1 for c in content if c in ' \t\n')
            whitespace_ratio = whitespace_count / len(content) if content else 0
            if whitespace_ratio < MINIFIED_THRESHOLDS['whitespace_ratio_min']:
                return {
                    'reason': f"Low whitespace ({whitespace_ratio*100:.1f}%)",
                    'size_kb': size_kb,
                    'line_count': line_count,
                    'avg_line_length': avg_line_len
                }

        return None

    except (OSError, IOError):
        return None


# ============================================================
# MAIN SURVEY FUNCTION
# ============================================================

def run_survey(
    path: str,
    dir_patterns: list[str] = None,
    file_patterns: list[str] = None,
    detect_minified: bool = True
) -> SurveyResult:
    """
    Run a complete Codome Definition survey of a directory.

    This is the ONTOLOGICAL phase - it defines WHAT the codome IS before
    any analysis begins. It answers 5 fundamental questions:

    Q1. IDENTITY: What IS this system? (language, framework, archetype)
    Q2. BOUNDARIES: Where does it START and END? (exclusions)
    Q3. NATURE: What is the TEXTURE? (composition breakdown)
    Q4. POLLUTION: What VIOLATES the physics? (misplaced files)
    Q5. ADAPTATION: How must the INSTRUMENTS be calibrated? (parsers, thresholds)

    Args:
        path: Directory to survey
        dir_patterns: Directory exclusion patterns (default: DEFAULT_DIRECTORY_PATTERNS)
        file_patterns: File exclusion patterns (default: DEFAULT_FILE_PATTERNS)
        detect_minified: Whether to run minification detection heuristics

    Returns:
        SurveyResult (CodomeManifest) with complete ontological definition
    """
    start_time = time.time()
    root = Path(path).resolve()

    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root}")

    # Initialize result
    result = SurveyResult(
        root_path=str(root),
        scan_time_ms=0
    )

    # Count totals first (quick pass)
    for dirpath, dirnames, filenames in os.walk(root):
        result.total_dirs += len(dirnames)
        result.total_files += len(filenames)
        for fn in filenames:
            try:
                result.total_size_kb += os.path.getsize(os.path.join(dirpath, fn)) / 1024
            except OSError:
                pass

    # Q2: BOUNDARIES - Scan for pattern-based exclusions
    dir_exclusions, file_exclusions = scan_for_exclusions(
        root, dir_patterns, file_patterns
    )
    result.directory_exclusions = dir_exclusions
    result.file_exclusions = file_exclusions

    # Detect minified files (part of Q2)
    if detect_minified:
        excluded_dirs = [e.path for e in dir_exclusions]
        result.minified_files = detect_minified_files(
            root,
            exclude_dirs=excluded_dirs + (dir_patterns or DEFAULT_DIRECTORY_PATTERNS)
        )

    # Build exclusion list for other detection functions
    all_exclude_dirs = (dir_patterns or DEFAULT_DIRECTORY_PATTERNS) + [e.path for e in dir_exclusions]

    # Q1: IDENTITY - What IS this system?
    result.identity = detect_identity(root, all_exclude_dirs)

    # Q3: NATURE - Composition breakdown
    result.composition = detect_composition(root, all_exclude_dirs)

    # Q4: POLLUTION - Detect issues
    result.pollution_alerts = detect_pollution(root, all_exclude_dirs, result.minified_files)

    # Q5: ADAPTATION - Determine recommended parsers
    result.recommended_parsers = _get_recommended_parsers(result.identity)

    # Calculate estimates
    excluded_file_count = sum(e.file_count for e in dir_exclusions)
    excluded_file_count += len(file_exclusions)
    excluded_file_count += len(result.minified_files)

    result.estimated_source_files = max(0, result.total_files - excluded_file_count)
    result.estimated_nodes = result.estimated_source_files * 75  # Rough estimate

    # Build recommendations (Q2 boundary constraints)
    result.recommended_excludes = []
    for excl in dir_exclusions:
        result.recommended_excludes.append(excl.path)
    for excl in file_exclusions:
        result.recommended_excludes.append(excl.path)
    for mf in result.minified_files:
        result.recommended_excludes.append(mf.path)

    # Calculate Codome Completeness Index (CCI)
    # Model: Are we capturing source code while excluding non-source?
    #
    # Ground truth from composition detection:
    #   SOURCE = composition.source_files (code files: .py, .js, .ts, etc.)
    #   NON-SOURCE = total_files - source_files (config, docs, vendor, etc.)
    #
    # Our analysis plan:
    #   WILL_ANALYZE = estimated_source_files (after exclusions)
    #   WILL_EXCLUDE = excluded_file_count
    #
    # Classification:
    #   TP = source files we're keeping (min of detected source and what we analyze)
    #   FN = source files we might be excluding
    #   TN = non-source files we correctly exclude
    #   FP = non-source files we incorrectly include
    #
    source_detected = result.composition.source_files
    non_source_detected = result.total_files - source_detected

    # Conservative estimate: assume exclusions are accurate
    # TP = source we keep (can't exceed detected source)
    tp = min(result.estimated_source_files, source_detected)
    # FN = source we lose to exclusions
    fn = max(0, source_detected - result.estimated_source_files)
    # TN = non-source correctly excluded
    tn = min(excluded_file_count, non_source_detected)
    # FP = non-source incorrectly included (spillover into analysis)
    fp = max(0, result.estimated_source_files - source_detected)

    # Only calculate CCI if we have meaningful data
    if source_detected > 0 or excluded_file_count > 0:
        result.cci = calculate_cci(
            total_source_files=source_detected if source_detected > 0 else 1,
            analyzed_source_files=tp,
            total_vendor_files=non_source_detected if non_source_detected > 0 else 1,
            analyzed_vendor_files=fp
        )

    # Add warnings
    if result.estimated_nodes > 10000:
        result.warnings.append(
            f"Large codebase: estimated {result.estimated_nodes:,} nodes. "
            "Consider using --exclude to focus on specific directories."
        )

    if len(result.minified_files) > 0:
        total_minified_kb = sum(mf.size_kb for mf in result.minified_files)
        result.warnings.append(
            f"Found {len(result.minified_files)} minified files ({total_minified_kb:.0f}KB). "
            "These will be excluded by default."
        )

    if result.pollution_level == "HIGH":
        result.warnings.append(
            f"High pollution detected: {len(result.pollution_alerts)} issues found. "
            "Review pollution alerts before analysis."
        )

    result.scan_time_ms = (time.time() - start_time) * 1000
    return result


def _get_recommended_parsers(identity: SystemIdentity) -> list[str]:
    """Determine recommended parsers based on identity (Q5)."""
    parsers = []

    lang_to_parser = {
        "python": "tree-sitter-python",
        "javascript": "tree-sitter-javascript",
        "typescript": "tree-sitter-typescript",
        "go": "tree-sitter-go",
        "rust": "tree-sitter-rust",
        "java": "tree-sitter-java",
        "ruby": "tree-sitter-ruby",
        "php": "tree-sitter-php",
        "csharp": "tree-sitter-c-sharp",
        "cpp": "tree-sitter-cpp",
        "c": "tree-sitter-c",
    }

    if identity.primary_language in lang_to_parser:
        parsers.append(lang_to_parser[identity.primary_language])

    for lang in identity.secondary_languages:
        if lang in lang_to_parser and lang_to_parser[lang] not in parsers:
            parsers.append(lang_to_parser[lang])

    return parsers


# ============================================================
# CONFIG FILE SUPPORT
# ============================================================

def load_exclusion_config(config_path: str = None) -> dict:
    """
    Load exclusion configuration from YAML file.

    If no path provided, looks for:
    1. .collider/exclusions.yaml in current directory
    2. Built-in defaults
    """
    if config_path:
        path = Path(config_path)
    else:
        # Look for config in current directory
        path = Path('.collider/exclusions.yaml')
        if not path.exists():
            path = Path('collider.yaml')

    if path.exists():
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    # Return defaults
    return {
        'version': '1.0',
        'directory_patterns': DEFAULT_DIRECTORY_PATTERNS,
        'file_patterns': DEFAULT_FILE_PATTERNS,
    }


def generate_analysis_config(survey_result: SurveyResult) -> dict:
    """
    Generate an analysis configuration from survey results.

    This config can be passed to Collider's full analysis.
    """
    return {
        'version': '1.0',
        'generated_from': 'survey',
        'root_path': survey_result.root_path,
        'exclude_paths': survey_result.recommended_excludes,
        'estimated_nodes': survey_result.estimated_nodes,
        'warnings': survey_result.warnings,
        'survey_stats': {
            'total_files': survey_result.total_files,
            'excluded_files': survey_result.total_files - survey_result.estimated_source_files,
            'signal_to_noise_ratio': survey_result.signal_to_noise_ratio,
            'scan_time_ms': survey_result.scan_time_ms,
        }
    }


# ============================================================
# CLI SUPPORT (for ./collider survey command)
# ============================================================

def print_survey_report(result: SurveyResult, verbose: bool = False):
    """Print a human-readable Codome Definition report.

    This outputs a POSITIVE DEFINITION of the codome, not just exclusions.
    The report answers the 5 ontological questions.
    """
    print("\n" + "=" * 60)
    print("CODOME DEFINITION REPORT (Stage 0)")
    print("=" * 60)
    print(f"Path: {result.root_path}")
    print(f"Scan time: {result.scan_time_ms:.0f}ms")
    print()

    # Q1: IDENTITY - What IS this system?
    print("Q1: IDENTITY - What IS this system?")
    print("-" * 40)
    print(f"  System: {result.identity}")
    print(f"  Primary language:  {result.identity.primary_language}")
    if result.identity.secondary_languages:
        print(f"  Secondary:         {', '.join(result.identity.secondary_languages)}")
    print(f"  Framework:         {result.identity.dominant_framework}")
    print(f"  Archetype:         {result.identity.archetype}")
    print(f"  Confidence:        {result.identity.confidence:.0%}")
    print()

    # Q2: BOUNDARIES - Where does it START and END?
    print("Q2: BOUNDARIES - Where does it START and END?")
    print("-" * 40)
    print(f"  Total files:       {result.total_files:,}")
    print(f"  Total dirs:        {result.total_dirs:,}")
    print(f"  Total size:        {result.total_size_kb/1024:.1f}MB")
    print()
    print(f"  Included (OURS):   {result.estimated_source_files:,} files")
    excluded = result.total_files - result.estimated_source_files
    print(f"  Excluded (THEIRS): {excluded:,} files")
    print(f"  Boundary rigidity: {result.boundary_rigidity}")
    if verbose and result.directory_exclusions:
        print()
        print("  Exclusion details:")
        for excl in result.directory_exclusions[:5]:
            print(f"    - {excl.path} ({excl.reason})")
        if len(result.directory_exclusions) > 5:
            print(f"    ... and {len(result.directory_exclusions) - 5} more")
    print()

    # Q3: NATURE - What is the TEXTURE?
    print("Q3: NATURE - What is the TEXTURE?")
    print("-" * 40)
    comp = result.composition
    pcts = comp.as_percentages()
    print(f"  Source files:  {comp.source_files:>5,} ({pcts['source']:>5.1%})")
    print(f"  Config files:  {comp.config_files:>5,} ({pcts['config']:>5.1%})")
    print(f"  Data files:    {comp.data_files:>5,} ({pcts['data']:>5.1%})")
    print(f"  Doc files:     {comp.doc_files:>5,} ({pcts['docs']:>5.1%})")
    print(f"  Binary files:  {comp.binary_files:>5,} ({pcts['binary']:>5.1%})")
    print(f"  Other:         {comp.other_files:>5,} ({pcts['other']:>5.1%})")
    print(f"  Signal ratio:  {comp.source_ratio:.1%}")
    print()

    # Q4: POLLUTION - What VIOLATES the physics?
    print("Q4: POLLUTION - What VIOLATES the physics?")
    print("-" * 40)
    print(f"  Pollution level: {result.pollution_level}")
    print(f"  Issues found:    {len(result.pollution_alerts)}")
    if result.pollution_alerts:
        for alert in result.pollution_alerts[:3]:
            severity_icon = {"HIGH": "!!!", "MEDIUM": "!!", "LOW": "!"}.get(alert.severity, "?")
            print(f"    [{severity_icon}] {alert.pollution_type}: {alert.path}")
            if verbose:
                print(f"        {alert.description}")
                print(f"        -> {alert.recommendation}")
        if len(result.pollution_alerts) > 3:
            print(f"    ... and {len(result.pollution_alerts) - 3} more issues")
    print()

    # Q5: ADAPTATION - How must the INSTRUMENTS be calibrated?
    print("Q5: ADAPTATION - How must the INSTRUMENTS be calibrated?")
    print("-" * 40)
    if result.recommended_parsers:
        print(f"  Parsers: {', '.join(result.recommended_parsers)}")
    print(f"  Est. nodes:        {result.estimated_nodes:,}")
    print(f"  Signal/Noise:      {result.signal_to_noise_ratio:.1%}")
    print()

    # Warnings
    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  [!] {warning}")
        print()

    # CCI Metrics (if available)
    if result.cci:
        cci = result.cci
        print("CODOME COMPLETENESS INDEX (CCI):")
        print("-" * 40)
        print(f"  CCI Score:     {cci.cci:.1f}% ({cci.verdict})")
        print(f"  Sensitivity:   {cci.sensitivity:.1%}  (Recall - found all source?)")
        print(f"  Specificity:   {cci.specificity:.1%}  (Excluded vendor?)")
        print(f"  Precision:     {cci.precision:.1%}  (No noise?)")
        print(f"  F2 Score:      {cci.f2_score:.3f}  (Completeness-weighted)")
        if verbose:
            print(f"  F1 Score:      {cci.f1_score:.3f}  (Balanced)")
            print(f"  G-Mean:        {cci.gmean:.3f}  (Geometric)")
            print(f"  TP={cci.true_positives}, FP={cci.false_positives}, "
                  f"TN={cci.true_negatives}, FN={cci.false_negatives}")
        print()

    # Summary verdict
    print("=" * 60)
    print("CODOME DEFINITION COMPLETE")
    print(f"  This is a {result.identity.archetype.upper()} codebase")
    print(f"  Primary: {result.identity.primary_language}")
    if result.identity.dominant_framework != "unknown":
        print(f"  Framework: {result.identity.dominant_framework}")
    print(f"  {result.estimated_source_files:,} source files ready for analysis")
    print("=" * 60)


if __name__ == '__main__':
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    verbose = '-v' in sys.argv or '--verbose' in sys.argv

    result = run_survey(path)
    print_survey_report(result, verbose=verbose)
