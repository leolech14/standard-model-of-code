#!/usr/bin/env python3
"""
LOL (List of Lists) Sync - Real-time Inventory Manager
=======================================================
SMoC Role: Management/Inventory/D | daemon | orchestrator

Maintains a CSV inventory of all PROJECT_elements entities with:
1. Real-time sync from filesystem
2. Deterministic auto-categorization
3. Inbox for new/uncategorized items

Output: .agent/intelligence/LOL.csv

Usage:
  python lol_sync.py                    # One-shot sync
  python lol_sync.py --watch            # Daemon mode (continuous)
  python lol_sync.py --inbox            # Show inbox (uncategorized)
  python lol_sync.py --export           # Export to CSV only
  python lol_sync.py --stats            # Show statistics
"""

import csv
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
CSV_PATH = REPO_ROOT / ".agent" / "intelligence" / "LOL.csv"
INBOX_PATH = REPO_ROOT / ".agent" / "intelligence" / "LOL_INBOX.csv"

# ============================================================================
# CLASSIFICATION RULES (Deterministic)
# ============================================================================

class Domain(Enum):
    PARTICLE = "particle"    # Collider, code analysis
    WAVE = "wave"            # Context, AI tools
    OBSERVER = "observer"    # .agent, task registry
    META = "meta"            # LOL (List of Lists) itself, truths
    UNKNOWN = "unknown"

class Category(Enum):
    SOURCE = "source"        # Application source code
    TOOL = "tool"            # Executable tools
    CONFIG = "config"        # Configuration files
    SCHEMA = "schema"        # Schema definitions
    TEST = "test"            # Test files
    DOC = "doc"              # Documentation
    DATA = "data"            # Data files
    VENDOR = "vendor"        # Third-party code
    UNKNOWN = "unknown"

class IntelModel(Enum):
    D = "D"      # Deterministic
    H = "H"      # Hybrid
    AI = "AI"    # AI-Required
    E = "E"      # Ensemble
    NA = "N/A"   # Not applicable

# Domain classification rules (path patterns) - ORDER MATTERS (first match wins)
DOMAIN_RULES = [
    # Particle domain (Collider + outputs)
    ("standard-model-of-code/", Domain.PARTICLE),
    ("architecture_report/", Domain.PARTICLE),
    ("collider_output", Domain.PARTICLE),  # collider outputs
    ("evolution_report/", Domain.PARTICLE),
    ("roadmap_report/", Domain.PARTICLE),
    ("temporal_dashboard/", Domain.PARTICLE),

    # Wave domain (Context/AI)
    ("context-management/", Domain.WAVE),

    # Observer domain (Agent)
    (".agent/", Domain.OBSERVER),

    # Meta domain (project-level config and docs)
    ("LOL", Domain.META),
    (".claude/", Domain.META),
    (".gemini/", Domain.META),
    (".vscode/", Domain.META),
    ("assets/", Domain.META),
    ("related/", Domain.META),  # related projects
    # Root-level files
    ("CLAUDE.md", Domain.META),
    ("GEMINI.md", Domain.META),
    ("README.md", Domain.META),
    ("ARCHITECTURE", Domain.META),
    ("PROJECT_MAP", Domain.META),
    ("AGENTS.md", Domain.META),
    ("QUICK_START.md", Domain.META),
    ("DEEP_GHOSTS_REPORT.md", Domain.META),
    ("AGENTKNOWLEDGEDUMP.md", Domain.META),
    (".gitignore", Domain.META),
    (".pre-commit", Domain.META),
    ("Dockerfile", Domain.META),
    ("commitlint", Domain.META),
    ("cloud-entrypoint", Domain.META),
    ("project_elements_file_timestamps.csv", Domain.META),
    ("flash-ui", Domain.META),
]

# Fallback domain rule for root-level files
def classify_domain(path: str) -> Domain:
    """Classify domain based on path patterns."""
    for pattern, domain in DOMAIN_RULES:
        if pattern in path:
            return domain
    # Fallback: root-level files without / are META
    if "/" not in path:
        return Domain.META
    return Domain.UNKNOWN

# Category classification rules (path patterns + extensions) - ORDER MATTERS
# NOTE: Paths don't have leading slashes, so use "tools/" not "/tools/"
CATEGORY_RULES = [
    # Excluded patterns (OS files)
    (lambda p: p == ".DS_Store" or "/.DS_Store" in p or p.endswith(".DS_Store"), Category.DATA),

    # Tools (executables) - note: no leading slash in pattern
    (lambda p: "tools/" in p and p.endswith(".py"), Category.TOOL),
    (lambda p: "tools/" in p and p.endswith(".sh"), Category.TOOL),
    (lambda p: "tools/" in p and Path(p).suffix == "" and Path(p).name != "tools", Category.TOOL),  # bare executables like "bare"
    (lambda p: p.endswith("cli.py"), Category.TOOL),
    (lambda p: "scripts/" in p and p.endswith((".py", ".sh")), Category.TOOL),
    (lambda p: "hooks/" in p, Category.TOOL),  # git hooks
    (lambda p: p.endswith("-entrypoint.sh"), Category.TOOL),
    (lambda p: p.endswith(".sh") and "/" not in p, Category.TOOL),  # root shell scripts
    (lambda p: p.endswith(".sh") and ("check" in p or "coverage" in p), Category.TOOL),  # checker scripts
    # Root-level bare executables
    (lambda p: "/" not in p and Path(p).suffix == "" and p in ("concierge", "pe", "collider"), Category.TOOL),

    # Tests
    (lambda p: "tests/" in p or "test_" in p or "_test.py" in p, Category.TEST),
    (lambda p: "test" in Path(p).stem.lower() and p.endswith(".py"), Category.TEST),
    (lambda p: "fixtures/" in p, Category.TEST),
    (lambda p: "specs/" in p and "_spec" in p, Category.TEST),

    # Schema (formal definitions)
    (lambda p: "schema/" in p, Category.SCHEMA),
    (lambda p: ".schema." in p, Category.SCHEMA),
    (lambda p: "ATOMS_TIER" in p, Category.SCHEMA),
    (lambda p: "roles.json" in p, Category.SCHEMA),
    (lambda p: p.endswith(".scm"), Category.SCHEMA),  # Tree-sitter queries
    (lambda p: "patterns/" in p and p.endswith((".yaml", ".json")), Category.SCHEMA),  # pattern definitions
    (lambda p: "canonical_types.json" in p, Category.SCHEMA),
    (lambda p: "universal_patterns.json" in p, Category.SCHEMA),

    # Data (outputs, logs, generated, media, binaries)
    (lambda p: p.endswith((".jsonl", ".log")), Category.DATA),
    (lambda p: "_logs/" in p, Category.DATA),
    (lambda p: "research/" in p and p.endswith(".json"), Category.DATA),
    (lambda p: "unified_analysis.json" in p, Category.DATA),
    (lambda p: "architecture_report/" in p, Category.DATA),
    (lambda p: p.startswith("assets/") or "/assets/" in p, Category.DATA),  # all assets are data
    (lambda p: p.endswith((".png", ".jpg", ".jpeg", ".pdf", ".svg", ".gif", ".zip", ".ico", ".txt")), Category.DATA),
    (lambda p: p.endswith(".html") and ("report" in p.lower() or "output" in p.lower() or "_report/" in p), Category.DATA),
    (lambda p: p.endswith(".csv"), Category.DATA),
    (lambda p: "_data.json" in p or "data.json" in p.split("/")[-1], Category.DATA),  # *_data.json files
    (lambda p: ".checkpoint.json" in p, Category.DATA),  # checkpoint files
    (lambda p: "collider_output" in p and p.endswith(".json"), Category.DATA),  # collider JSON outputs
    (lambda p: "evolution_report/" in p, Category.DATA),
    (lambda p: "roadmap_report/" in p, Category.DATA),
    (lambda p: "test-results/" in p, Category.DATA),  # test screenshots/results
    # Binary/media data
    (lambda p: p.endswith((".blend", ".woff", ".woff2", ".ttf", ".eot")), Category.DATA),  # 3D, fonts
    (lambda p: p.endswith((".css", ".min.css")) and "libs/" in p, Category.DATA),  # vendor CSS
    (lambda p: p.endswith(".legacy"), Category.DATA),  # archived files
    (lambda p: ".bandit_output.json" in p, Category.DATA),  # security scan output
    (lambda p: ".coverage" in p and not p.endswith(".coveragerc"), Category.DATA),  # coverage data
    (lambda p: "egg-info/" in p or "PKG-INFO" in p, Category.DATA),  # build artifacts
    (lambda p: "/data/" in p and p.endswith(".json"), Category.DATA),  # data/*.json
    (lambda p: "/output/" in p and p.endswith(".json"), Category.DATA),  # output/*.json
    (lambda p: "reference_datasets/" in p, Category.DATA),  # reference data
    (lambda p: "registry/" in p and p.endswith(".json"), Category.DATA),  # registry data
    (lambda p: "tokens/" in p and p.endswith(".json"), Category.DATA),  # design tokens
    (lambda p: "batch_grade/" in p and p.endswith(".json"), Category.DATA),  # batch grading results
    (lambda p: "roadmaps/" in p and p.endswith(".json"), Category.DATA),  # roadmap data
    (lambda p: "grades_" in p and p.endswith(".json"), Category.DATA),  # grading outputs
    # Intelligence outputs (observer domain)
    (lambda p: "intelligence/" in p and p.endswith((".json", ".txt", ".html", ".jsonl")), Category.DATA),
    (lambda p: "_reports/" in p, Category.DATA),
    (lambda p: "_scans/" in p, Category.DATA),
    (lambda p: "chunks/" in p, Category.DATA),
    (lambda p: "triage_reports/" in p, Category.DATA),
    (lambda p: "confidence_reports/" in p, Category.DATA),
    (lambda p: "sessions/" in p and p.endswith(".json"), Category.DATA),
    (lambda p: "raw/" in p and p.endswith(".json"), Category.DATA),

    # Config (settings, dotfiles, build configs)
    (lambda p: "config/" in p, Category.CONFIG),
    (lambda p: p.endswith((".yaml", ".yml")) and "patterns/" not in p and "research/" not in p, Category.CONFIG),
    (lambda p: "settings" in p.lower() and p.endswith(".json"), Category.CONFIG),
    (lambda p: "config" in p.lower() and p.endswith((".json", ".yaml", ".toml")), Category.CONFIG),
    (lambda p: ".pre-commit" in p, Category.CONFIG),
    (lambda p: "commitlint" in p, Category.CONFIG),
    (lambda p: p.endswith(".gitignore") or "/.gitignore" in p, Category.CONFIG),
    (lambda p: "Dockerfile" in p, Category.CONFIG),
    (lambda p: ".vscode/" in p, Category.CONFIG),
    (lambda p: p.endswith("package.json") or p.endswith("package-lock.json"), Category.CONFIG),
    (lambda p: p.endswith("tsconfig.json"), Category.CONFIG),
    (lambda p: p.endswith("setup.sh"), Category.TOOL),  # setup scripts are tools
    # Dotfile configs
    (lambda p: p.endswith((".coveragerc", ".dockerignore", ".editorconfig", ".colliderignore")), Category.CONFIG),
    (lambda p: p.endswith((".env", ".env.example", ".env.local")), Category.CONFIG),
    (lambda p: p.endswith((".ini", ".toml", ".cfg")), Category.CONFIG),
    (lambda p: "CODEOWNERS" in p, Category.CONFIG),
    (lambda p: "MANIFEST.in" in p, Category.CONFIG),
    (lambda p: p.endswith("Makefile") or "/Makefile" in p, Category.CONFIG),
    (lambda p: p.endswith(".plist") or p.endswith(".plist.example"), Category.CONFIG),
    (lambda p: "requirements" in p and p.endswith((".txt", ".lock")), Category.CONFIG),
    (lambda p: p.endswith("pyproject.toml") or p.endswith("pytest.ini"), Category.CONFIG),

    # Documentation
    (lambda p: p.endswith(".md"), Category.DOC),
    (lambda p: p.endswith(".mmd"), Category.DOC),  # Mermaid diagrams
    (lambda p: "docs/" in p, Category.DOC),

    # Vendor (third-party)
    (lambda p: "vendor/" in p, Category.VENDOR),
    (lambda p: "node_modules" in p, Category.VENDOR),
    (lambda p: ".min.js" in p, Category.VENDOR),

    # Source (default for code files)
    (lambda p: p.endswith((".py", ".js", ".ts", ".jsx", ".tsx")), Category.SOURCE),
    (lambda p: p.endswith(".html") and "viz/" in p, Category.SOURCE),
    (lambda p: p.endswith(".css") and "libs/" not in p, Category.SOURCE),  # CSS source files
    (lambda p: p.endswith(".html"), Category.SOURCE),  # fallback for HTML
    # Special executables
    (lambda p: p == "standard-model-of-code/collider", Category.TOOL),  # main CLI
]

# Intelligence model rules (for tools only)
INTEL_RULES = {
    # AI-Required tools
    "perplexity_research.py": IntelModel.AI,
    "precision_fetcher.py": IntelModel.AI,
    "insights_generator.py": IntelModel.AI,

    # Ensemble tools
    "centripetal_scan.py": IntelModel.E,

    # Hybrid tools (use AI optionally)
    "analyze.py": IntelModel.H,
    "tier_orchestrator.py": IntelModel.H,
    "industrial_triage.py": IntelModel.H,
    "autopilot.py": IntelModel.H,
    "enrichment_orchestrator.py": IntelModel.H,

    # Everything else is Deterministic by default
}

# Exclusions
EXCLUDED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", ".tools_venv",
    "archive", ".archive", ".collider", "dist", "build", "artifacts",
    ".mypy_cache", ".pytest_cache", "benchmarks", "llm-threads", "_archive",
}

EXCLUDED_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dylib", ".egg-info", ".whl",
    ".log", ".tmp", ".bak", ".swp", ".swo", ".DS_Store",
}


# ============================================================================
# DATA MODEL
# ============================================================================

@dataclass
class Entity:
    """A single inventoried entity."""
    path: str
    extension: str
    domain: str
    category: str
    intel_model: str
    size_bytes: int
    modified: str
    hash_short: str
    status: str  # tracked, new, deleted, modified

    def to_dict(self):
        return asdict(self)


# ============================================================================
# CLASSIFICATION ENGINE
# ============================================================================

# Note: classify_domain is defined above near DOMAIN_RULES for locality

def classify_category(path: str) -> Category:
    """Deterministically classify category from path."""
    for rule, category in CATEGORY_RULES:
        if callable(rule) and rule(path):
            return category
        elif isinstance(rule, str) and rule in path:
            return category
    return Category.UNKNOWN


def classify_intel_model(path: str, category: Category) -> IntelModel:
    """Classify intelligence model (only for tools)."""
    if category != Category.TOOL:
        return IntelModel.NA

    filename = Path(path).name
    return INTEL_RULES.get(filename, IntelModel.D)


def compute_hash(filepath: Path) -> str:
    """Compute short hash of file content."""
    try:
        content = filepath.read_bytes()
        return hashlib.sha256(content).hexdigest()[:8]
    except:
        return "????????"


def scan_entity(filepath: Path) -> Optional[Entity]:
    """Scan a single file and create Entity."""
    try:
        rel_path = str(filepath.relative_to(REPO_ROOT))

        # Skip excluded
        if any(part in EXCLUDED_DIRS for part in filepath.parts):
            return None
        if filepath.suffix in EXCLUDED_EXTENSIONS:
            return None
        if not filepath.is_file():
            return None

        stat = filepath.stat()
        domain = classify_domain(rel_path)
        category = classify_category(rel_path)
        intel = classify_intel_model(rel_path, category)

        return Entity(
            path=rel_path,
            extension=filepath.suffix,
            domain=domain.value,
            category=category.value,
            intel_model=intel.value,
            size_bytes=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            hash_short=compute_hash(filepath),
            status="tracked",
        )
    except Exception as e:
        return None


# ============================================================================
# CSV MANAGEMENT
# ============================================================================

def load_csv(path: Path) -> dict[str, Entity]:
    """Load existing CSV into dict keyed by path."""
    entities = {}
    if not path.exists():
        return entities

    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entities[row['path']] = Entity(**row)

    return entities


def save_csv(entities: dict[str, Entity], path: Path):
    """Save entities dict to CSV."""
    if not entities:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(Entity.__dataclass_fields__.keys())

    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entity in sorted(entities.values(), key=lambda e: e.path):
            writer.writerow(entity.to_dict())


# ============================================================================
# SYNC ENGINE
# ============================================================================

def full_scan() -> dict[str, Entity]:
    """Scan entire repository and return entities."""
    entities = {}

    for filepath in REPO_ROOT.rglob("*"):
        entity = scan_entity(filepath)
        if entity:
            entities[entity.path] = entity

    return entities


def sync_inventory() -> tuple[dict, dict, dict]:
    """
    Sync CSV with filesystem.
    Returns: (current, added, removed)
    """
    # Load existing
    existing = load_csv(CSV_PATH)

    # Scan current
    current = full_scan()

    # Compute diffs
    existing_paths = set(existing.keys())
    current_paths = set(current.keys())

    added_paths = current_paths - existing_paths
    removed_paths = existing_paths - current_paths
    common_paths = existing_paths & current_paths

    # Build result
    added = {p: current[p] for p in added_paths}
    removed = {p: existing[p] for p in removed_paths}

    # Mark status
    for path in added_paths:
        current[path].status = "new"

    for path in removed_paths:
        existing[path].status = "deleted"
        current[path] = existing[path]  # Keep deleted in inventory

    # Check for modifications
    for path in common_paths:
        if current[path].hash_short != existing[path].hash_short:
            current[path].status = "modified"
        else:
            current[path].status = "tracked"

    return current, added, removed


def save_inbox(added: dict[str, Entity]):
    """Save new/uncategorized items to inbox."""
    inbox = {}

    for path, entity in added.items():
        if entity.category == "unknown" or entity.domain == "unknown":
            inbox[path] = entity

    if inbox:
        save_csv(inbox, INBOX_PATH)
        print(f"  {len(inbox)} items added to inbox (need categorization)")


# ============================================================================
# CLI
# ============================================================================

def print_stats(entities: dict[str, Entity]):
    """Print inventory statistics."""
    print("\n" + "=" * 60)
    print("LOL (List of Lists) INVENTORY STATISTICS")
    print("=" * 60)

    # By domain
    domains = {}
    for e in entities.values():
        domains[e.domain] = domains.get(e.domain, 0) + 1

    print("\n## By Domain")
    for d in sorted(domains.keys()):
        print(f"  {d:12} {domains[d]:4}")

    # By category
    categories = {}
    for e in entities.values():
        categories[e.category] = categories.get(e.category, 0) + 1

    print("\n## By Category")
    for c in sorted(categories.keys()):
        print(f"  {c:12} {categories[c]:4}")

    # By extension
    extensions = {}
    for e in entities.values():
        extensions[e.extension] = extensions.get(e.extension, 0) + 1

    print("\n## By Extension (top 10)")
    for ext, count in sorted(extensions.items(), key=lambda x: -x[1])[:10]:
        print(f"  {ext or '(none)':12} {count:4}")

    # By intel model (tools only)
    intel = {}
    for e in entities.values():
        if e.category == "tool":
            intel[e.intel_model] = intel.get(e.intel_model, 0) + 1

    if intel:
        print("\n## Tool Intelligence Models")
        for i in sorted(intel.keys()):
            print(f"  {i:12} {intel[i]:4}")

    # Totals
    total_size = sum(int(e.size_bytes) for e in entities.values())
    print(f"\n## Totals")
    print(f"  Entities:   {len(entities)}")
    print(f"  Total size: {total_size / 1024 / 1024:.1f} MB")
    print("=" * 60)


def watch_mode():
    """Daemon mode - continuously sync."""
    print("LOL (List of Lists) Sync - Watch Mode")
    print("Press Ctrl+C to stop\n")

    last_scan = None

    while True:
        try:
            current, added, removed = sync_inventory()

            if added or removed:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Changes detected:")

                if added:
                    print(f"  + {len(added)} new")
                    for p in list(added.keys())[:5]:
                        print(f"    + {p}")
                    if len(added) > 5:
                        print(f"    ... and {len(added) - 5} more")

                if removed:
                    print(f"  - {len(removed)} removed")
                    for p in list(removed.keys())[:5]:
                        print(f"    - {p}")

                # Save
                save_csv(current, CSV_PATH)
                save_inbox(added)
                print(f"  Saved to {CSV_PATH}")

            last_scan = current
            time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            print("\nStopping watch mode.")
            break


def main():
    if "--watch" in sys.argv:
        watch_mode()
        return

    if "--stats" in sys.argv:
        entities = load_csv(CSV_PATH)
        if not entities:
            print("No inventory found. Run without --stats first.")
            return
        print_stats(entities)
        return

    if "--inbox" in sys.argv:
        inbox = load_csv(INBOX_PATH)
        if not inbox:
            print("Inbox is empty.")
        else:
            print(f"INBOX ({len(inbox)} items):")
            for path, entity in inbox.items():
                print(f"  [{entity.domain}/{entity.category}] {path}")
        return

    # Default: one-shot sync
    print("LOL (List of Lists) Sync - Scanning repository...")

    current, added, removed = sync_inventory()

    print(f"\nResults:")
    print(f"  Total entities: {len(current)}")
    print(f"  New:            {len(added)}")
    print(f"  Removed:        {len(removed)}")

    # Filter out deleted from save
    to_save = {p: e for p, e in current.items() if e.status != "deleted"}

    save_csv(to_save, CSV_PATH)
    save_inbox(added)

    print(f"\nSaved to: {CSV_PATH}")

    if "--export" not in sys.argv:
        print_stats(to_save)


if __name__ == "__main__":
    main()
