#!/usr/bin/env python3
"""
Audit Pack Validator

Validates that a research audit pack has valid provenance and complete artifacts.
Prevents accidental "paper over" of missing or mock audits.

Usage:
    python tools/research/validate_audit_pack.py artifacts/atom-research/2026-01-22/
    python tools/research/validate_audit_pack.py artifacts/atom-research/2026-01-22/ --strict
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# Project root = standard-model-of-code/ (two levels up from this script)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def to_project_relative(path: Path) -> str:
    """Convert a path to project-root-relative POSIX string."""
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        # Path is not inside PROJECT_ROOT, return as-is
        return path.as_posix()


class ValidationError:
    """A single validation error."""
    def __init__(self, file: str, field: str, message: str, severity: str = "ERROR"):
        self.file = file
        self.field = field
        self.message = message
        self.severity = severity  # ERROR, WARNING

    def __str__(self):
        return f"[{self.severity}] {self.file}: {self.field} - {self.message}"


def load_yaml_frontmatter(filepath: Path) -> dict[str, Any] | None:
    """Extract YAML frontmatter from a markdown file."""
    try:
        content = filepath.read_text()
    except Exception as e:
        return None

    # Match YAML frontmatter between --- markers
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def compute_file_hash(filepath: Path) -> str | None:
    """Compute SHA256 hash of a file."""
    try:
        content = filepath.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except Exception:
        return None


def validate_audit_artifact(
    artifact_path: Path,
    prompt_base_dir: Path,
    errors: list[ValidationError],
) -> bool:
    """Validate a single audit artifact (.md file with YAML frontmatter)."""
    filename = artifact_path.name

    # Load frontmatter
    frontmatter = load_yaml_frontmatter(artifact_path)
    if frontmatter is None:
        errors.append(ValidationError(
            filename, "frontmatter", "Could not parse YAML frontmatter"
        ))
        return False

    # Check for audit_metadata
    metadata = frontmatter.get("audit_metadata")
    if metadata is None:
        errors.append(ValidationError(
            filename, "audit_metadata", "Missing audit_metadata block"
        ))
        return False

    # Required fields
    required_fields = ["model", "status", "date_utc"]
    for field in required_fields:
        if field not in metadata:
            errors.append(ValidationError(
                filename, f"audit_metadata.{field}", f"Missing required field"
            ))

    # Check status is COMPLETED
    status = metadata.get("status")
    if status != "COMPLETED":
        errors.append(ValidationError(
            filename, "audit_metadata.status",
            f"Status is '{status}', expected 'COMPLETED'"
        ))

    # Validate prompt hash if present
    prompt_hash = metadata.get("prompt_hash")
    prompt_file = metadata.get("prompt_file")

    if prompt_hash and prompt_file:
        # Resolve prompt file path (try multiple locations)
        prompt_path = None
        candidates = [
            prompt_base_dir / Path(prompt_file).name,  # Just filename in prompt dir
            prompt_base_dir / prompt_file,  # Full relative path
            artifact_path.parent.parent.parent.parent / prompt_file,  # From project root
            Path(prompt_file),  # As-is
        ]
        for candidate in candidates:
            if candidate.exists():
                prompt_path = candidate
                break

        if prompt_path and prompt_path.exists():
            computed_hash = compute_file_hash(prompt_path)
            # Extract hash value (may be prefixed with "sha256:")
            expected_hash = prompt_hash.replace("sha256:", "")

            if computed_hash != expected_hash:
                errors.append(ValidationError(
                    filename, "prompt_hash",
                    f"Hash mismatch: file={computed_hash[:16]}... expected={expected_hash[:16]}..."
                ))
        else:
            errors.append(ValidationError(
                filename, "prompt_file",
                f"Referenced prompt file not found: {prompt_file}"
            ))
    elif prompt_hash and not prompt_file:
        errors.append(ValidationError(
            filename, "prompt_file",
            "prompt_hash present but prompt_file missing (cannot verify)",
            severity="WARNING"
        ))

    return True


def validate_decision_record(
    decision_path: Path,
    audit_dir: Path,
    errors: list[ValidationError],
) -> bool:
    """Validate a decision record."""
    filename = decision_path.name

    frontmatter = load_yaml_frontmatter(decision_path)
    if frontmatter is None:
        errors.append(ValidationError(
            filename, "frontmatter", "Could not parse YAML frontmatter"
        ))
        return False

    # Check decision semantics
    decision = frontmatter.get("decision", {})
    promote = decision.get("promote")
    outcome = decision.get("outcome")
    claim_to = frontmatter.get("claim_level_to")
    claim_from = frontmatter.get("claim_level_from")

    # If blocked, claim_level_to should equal claim_level_from
    if outcome == "BLOCKED" and claim_to != claim_from:
        errors.append(ValidationError(
            filename, "claim_level_to",
            f"Outcome is BLOCKED but claim_level_to ({claim_to}) != claim_level_from ({claim_from})",
            severity="WARNING"
        ))

    # If promote is true, all hard gates must be true
    hard_gates = frontmatter.get("hard_gates", {})
    if promote:
        for gate, value in hard_gates.items():
            if not value:
                errors.append(ValidationError(
                    filename, f"hard_gates.{gate}",
                    f"promote=true but {gate}={value}"
                ))

    # Verify referenced audit artifacts exist
    ai_audits = frontmatter.get("ai_audits", {})
    for audit_name, audit_info in ai_audits.items():
        if isinstance(audit_info, dict):
            audit_path_str = audit_info.get("path", "")
        else:
            audit_path_str = audit_info

        if audit_path_str:
            # Try to resolve the path (multiple locations)
            audit_file = None
            candidates = [
                decision_path.parent / Path(audit_path_str).name,  # Same directory
                decision_path.parent.parent.parent.parent / audit_path_str,  # Project root
                Path(audit_path_str),  # As-is
            ]
            for candidate in candidates:
                if candidate.exists():
                    audit_file = candidate
                    break

            if audit_file is None:
                errors.append(ValidationError(
                    filename, f"ai_audits.{audit_name}",
                    f"Referenced audit file not found: {audit_path_str}"
                ))

    # Check falsification semantics
    falsification = frontmatter.get("falsification", {})
    falsifier_found = falsification.get("falsifier_found", False)
    falsifier_resolved = falsification.get("resolved", True)
    g3 = hard_gates.get("G3_falsification_clear", True)

    # G3 should be false only if falsifier found AND not resolved
    if falsifier_found and not falsifier_resolved and g3:
        errors.append(ValidationError(
            filename, "hard_gates.G3_falsification_clear",
            "G3=true but falsifier_found=true and resolved=false"
        ))

    return True


def validate_metrics_recompute(
    pack_dir: Path,
    errors: list[ValidationError],
) -> bool:
    """
    Recompute metrics from coverage.json files and compare to results.json.
    This prevents hand-edited results from going undetected.
    """
    repos_dir = pack_dir / "repos"
    results_file = pack_dir / "results.json"

    if not repos_dir.exists():
        errors.append(ValidationError(
            "repos/", "directory", "repos directory missing"
        ))
        return False

    if not results_file.exists():
        errors.append(ValidationError(
            "results.json", "existence", "results.json missing"
        ))
        return False

    # Load results.json
    try:
        with open(results_file) as f:
            results = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(ValidationError(
            "results.json", "json", f"Invalid JSON: {e}"
        ))
        return False

    results_by_name = {r.get("name"): r for r in results}

    # Scan repos directory
    repo_dirs = [d for d in repos_dir.iterdir() if d.is_dir()]
    coverage_count = 0

    for repo_dir in repo_dirs:
        repo_name = repo_dir.name

        # Find coverage.json
        coverage_files = list(repo_dir.glob("*/coverage.json"))
        if not coverage_files:
            errors.append(ValidationError(
                f"repos/{repo_name}/", "coverage.json",
                "No coverage.json found"
            ))
            continue

        coverage_file = coverage_files[0]
        coverage_count += 1

        try:
            with open(coverage_file) as f:
                coverage = json.load(f)
        except json.JSONDecodeError:
            errors.append(ValidationError(
                str(coverage_file), "json", "Invalid JSON"
            ))
            continue

        metrics = coverage.get("metrics", {})

        # Check if repo exists in results.json
        if repo_name not in results_by_name:
            errors.append(ValidationError(
                "results.json", f"repo.{repo_name}",
                f"Repo '{repo_name}' in repos/ but missing from results.json"
            ))
            continue

        result = results_by_name[repo_name]

        # Compare key metrics
        for field, coverage_key in [
            ("n_nodes", "n_nodes"),
            ("top_4_mass", "top_4_mass"),
            ("unknown_rate", "unknown_rate"),
        ]:
            coverage_val = metrics.get(coverage_key)
            result_val = result.get(field)

            if coverage_val is None:
                continue

            # Allow small float tolerance
            if isinstance(coverage_val, float) and isinstance(result_val, float):
                if abs(coverage_val - result_val) > 0.01:
                    errors.append(ValidationError(
                        "results.json", f"{repo_name}.{field}",
                        f"Mismatch: coverage.json={coverage_val}, results.json={result_val}"
                    ))
            elif coverage_val != result_val:
                errors.append(ValidationError(
                    "results.json", f"{repo_name}.{field}",
                    f"Mismatch: coverage.json={coverage_val}, results.json={result_val}"
                ))

    # Check for extra repos in results.json not in repos/
    repo_names_on_disk = {d.name for d in repo_dirs}
    for name in results_by_name:
        if name not in repo_names_on_disk:
            errors.append(ValidationError(
                "results.json", f"repo.{name}",
                f"Repo '{name}' in results.json but not in repos/"
            ))

    # Check counts match
    if len(results) != coverage_count:
        errors.append(ValidationError(
            "results.json", "count",
            f"Count mismatch: results.json={len(results)}, coverage.json files={coverage_count}",
            severity="WARNING"
        ))

    return True


def validate_manifest_completeness(
    pack_dir: Path,
    errors: list[ValidationError],
) -> bool:
    """
    Validate that MANIFEST.sha256 exists and covers all required files.

    Required surface:
    - core: corpus.yaml, results.json, summary.md, summary.csv
    - audits: all *.md files in ai-audit/
    - prompts: all files referenced by prompt_file in audits
    - coverage: coverage.json for each repo in repos/
    """
    manifest_file = pack_dir / "MANIFEST.sha256"

    if not manifest_file.exists():
        errors.append(ValidationError(
            "MANIFEST.sha256", "existence",
            "Manifest file missing (run seal not created)",
            severity="WARNING"
        ))
        return False

    # Parse manifest to get sealed files
    sealed_files: set[str] = set()
    try:
        content = manifest_file.read_text()
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                sealed_files.add(parts[1])
    except Exception as e:
        errors.append(ValidationError(
            "MANIFEST.sha256", "parse", f"Failed to parse manifest: {e}"
        ))
        return False

    # Check required core files (use project-relative paths for comparison)
    core_files = ["corpus.yaml", "results.json", "summary.md", "summary.csv"]
    for core in core_files:
        expected_path = to_project_relative(pack_dir / core)
        if expected_path not in sealed_files:
            errors.append(ValidationError(
                "MANIFEST.sha256", f"core.{core}",
                f"Required file not in manifest: {core}"
            ))

    # Check all audit files are sealed
    audit_dir = pack_dir / "ai-audit"
    if audit_dir.exists():
        for audit_file in audit_dir.glob("*.md"):
            expected_path = to_project_relative(audit_file)
            if expected_path not in sealed_files:
                errors.append(ValidationError(
                    "MANIFEST.sha256", f"audit.{audit_file.name}",
                    f"Audit file not in manifest: {audit_file.name}"
                ))

    # Check all coverage.json files are sealed
    repos_dir = pack_dir / "repos"
    if repos_dir.exists():
        for coverage_file in repos_dir.glob("*/*/coverage.json"):
            expected_path = to_project_relative(coverage_file)
            if expected_path not in sealed_files:
                errors.append(ValidationError(
                    "MANIFEST.sha256", f"coverage.{coverage_file.parent.parent.name}",
                    f"Coverage file not in manifest: {coverage_file}"
                ))

    # Check prompt files referenced by audits are sealed
    if audit_dir.exists():
        for audit_file in audit_dir.glob("*.md"):
            if audit_file.name.startswith("decision_"):
                continue
            frontmatter = load_yaml_frontmatter(audit_file)
            if frontmatter:
                metadata = frontmatter.get("audit_metadata", {})
                prompt_file = metadata.get("prompt_file")
                if prompt_file:
                    # Check if prompt file is in manifest (try various path forms)
                    prompt_sealed = any(
                        prompt_file in f or Path(prompt_file).name in f
                        for f in sealed_files
                    )
                    if not prompt_sealed:
                        errors.append(ValidationError(
                            "MANIFEST.sha256", f"prompt.{Path(prompt_file).name}",
                            f"Prompt file not in manifest: {prompt_file}",
                            severity="WARNING"
                        ))

    # Check for unsealed files in pack (strict mode: no extra files allowed)
    # This ensures the pack behaves like a real evidence ledger
    pack_extensions = {"*.md", "*.json", "*.csv", "*.yaml", "*.yml"}
    for pattern in pack_extensions:
        for pack_file in pack_dir.rglob(pattern):
            # Skip the manifest itself
            if pack_file.name == "MANIFEST.sha256":
                continue
            relative_path = to_project_relative(pack_file)
            if relative_path not in sealed_files:
                errors.append(ValidationError(
                    "MANIFEST.sha256", f"unsealed.{pack_file.name}",
                    f"File in pack not sealed in manifest: {relative_path}",
                    severity="WARNING"
                ))

    return True


def validate_audit_pack(pack_dir: Path, strict: bool = False) -> tuple[bool, list[ValidationError]]:
    """
    Validate an entire audit pack directory.

    Expected structure:
        pack_dir/
        ├── ai-audit/
        │   ├── gemini_finding_1.md
        │   ├── perplexity_finding_1.md
        │   ├── adversarial_finding_1.md
        │   └── decision_finding_1.md
        ├── corpus.yaml
        ├── results.json
        └── summary.md
    """
    errors: list[ValidationError] = []

    # Check directory exists
    if not pack_dir.exists():
        errors.append(ValidationError(
            str(pack_dir), "directory", "Audit pack directory does not exist"
        ))
        return False, errors

    # Check required files
    required_files = ["corpus.yaml", "results.json", "summary.md"]
    for req in required_files:
        if not (pack_dir / req).exists():
            errors.append(ValidationError(
                req, "existence", "Required file missing"
            ))

    # Check ai-audit directory
    audit_dir = pack_dir / "ai-audit"
    if not audit_dir.exists():
        errors.append(ValidationError(
            "ai-audit/", "directory", "ai-audit directory missing"
        ))
        return False, errors

    # Find prompt base directory (relative to project root)
    prompt_base = pack_dir.parent.parent.parent / "tools" / "research" / "prompts"
    if not prompt_base.exists():
        prompt_base = pack_dir.parent.parent.parent / "tools" / "research"

    # Validate each audit artifact
    audit_files = list(audit_dir.glob("*.md"))
    decision_files = [f for f in audit_files if f.name.startswith("decision_")]
    other_audits = [f for f in audit_files if not f.name.startswith("decision_")]

    if not other_audits:
        errors.append(ValidationError(
            "ai-audit/", "audits", "No audit artifacts found"
        ))

    if not decision_files:
        errors.append(ValidationError(
            "ai-audit/", "decision", "No decision record found"
        ))

    # Validate audit artifacts
    for audit_file in other_audits:
        validate_audit_artifact(audit_file, prompt_base, errors)

    # Validate decision records
    for decision_file in decision_files:
        validate_decision_record(decision_file, audit_dir, errors)

    # Validate metrics recompute (results.json vs coverage.json)
    validate_metrics_recompute(pack_dir, errors)

    # Validate manifest completeness (if manifest exists)
    validate_manifest_completeness(pack_dir, errors)

    # Count errors vs warnings
    error_count = sum(1 for e in errors if e.severity == "ERROR")
    warning_count = sum(1 for e in errors if e.severity == "WARNING")

    # In strict mode, warnings also fail
    if strict:
        valid = len(errors) == 0
    else:
        valid = error_count == 0

    return valid, errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate research audit pack provenance and completeness"
    )
    parser.add_argument(
        "pack_dir",
        type=Path,
        help="Path to audit pack directory (e.g., artifacts/atom-research/2026-01-22/)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of text",
    )

    args = parser.parse_args()

    valid, errors = validate_audit_pack(args.pack_dir, strict=args.strict)

    if args.json:
        output = {
            "valid": valid,
            "error_count": sum(1 for e in errors if e.severity == "ERROR"),
            "warning_count": sum(1 for e in errors if e.severity == "WARNING"),
            "errors": [
                {"file": e.file, "field": e.field, "message": e.message, "severity": e.severity}
                for e in errors
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Validating: {args.pack_dir}")
        print("=" * 60)

        if errors:
            for error in errors:
                print(error)
            print()

        error_count = sum(1 for e in errors if e.severity == "ERROR")
        warning_count = sum(1 for e in errors if e.severity == "WARNING")

        print(f"Errors: {error_count}, Warnings: {warning_count}")

        if valid:
            print("\n[PASS] Audit pack is valid")
        else:
            print("\n[FAIL] Audit pack validation failed")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
