"""Domain verification orchestrator with three-tier output."""

import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

import sys
_AI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AI_DIR))

from _shared import (
    PROJECT_ROOT as _DEFAULT_ROOT,
    SEMANTIC_MODELS_PATH,
    create_client,
    create_developer_client,
    list_file_search_stores,
    get_or_create_store,
    index_files_to_store,
    list_local_files,
)

from .models import AuditReport
from .hypothesis import generate_hypotheses
from .verifier import verify_hypothesis


def load_semantic_models() -> dict:
    """Load semantic_models.yaml."""
    if not SEMANTIC_MODELS_PATH.exists():
        print(f"Error: Semantic models not found at {SEMANTIC_MODELS_PATH}")
        return {}
    with open(SEMANTIC_MODELS_PATH) as f:
        return yaml.safe_load(f) or {}


def _append_run_index(report: AuditReport, output_dir: Path) -> None:
    """Append compact record to run_index.jsonl."""
    record = {
        "_generated": report.generated,
        "domain": report.domain,
        "hypotheses_count": report.hypotheses_count,
        "verified_count": report.verified_count,
        "violation_count": report.violation_count,
        "timestamp": report.timestamp,
    }
    with open(output_dir / "run_index.jsonl", "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def verify_domain(
    domain: str,
    store_name: Optional[str] = None,
    output: Optional[str] = None,
    index: bool = False,
    candidate: Optional[str] = None,
    project_root: Optional[Path] = None,
    sync_gcs: bool = False,
) -> AuditReport:
    """Orchestrate full domain verification with three-tier output.

    Args:
        domain: Domain name from semantic_models.yaml (e.g., "atoms", "pipeline")
        store_name: File Search store name (default: collider-{domain})
        output: Optional explicit output file path
        index: If True, index files to store before verifying
        candidate: Explicit candidate file path (skips discovery)
        project_root: Override PROJECT_ROOT for testing
        sync_gcs: If True, attempt gsutil cp to GCS (requires billing)
    """
    root = project_root or _DEFAULT_ROOT
    models = load_semantic_models()

    if domain not in models:
        print(f"Error: Domain '{domain}' not found in semantic_models.yaml")
        available = list(models.keys())
        print(f"Available: {available}")
        return AuditReport(
            _generated=AuditReport.d6_header(),
            domain=domain,
            timestamp=datetime.now(timezone.utc).isoformat(),
            hypotheses_count=0,
        )

    domain_config = models[domain]
    store_name = store_name or f"collider-{domain}"

    # Initialize clients
    print("Initializing clients...")
    dev_client = create_developer_client()
    vertex_client, _ = create_client()

    # Optional indexing
    if index and dev_client:
        print(f"Indexing domain '{domain}'...")
        target_dir = None
        if domain == "pipeline":
            target_dir = root / "particle/src/core"
        elif domain == "theory":
            target_dir = root / "particle/docs/theory"
        if target_dir:
            store_res = get_or_create_store(dev_client, store_name)
            files = list_local_files(target_dir)
            index_files_to_store(dev_client, store_res, files, root)

    # Resolve store
    store_resource_name = None
    if not candidate and dev_client:
        print(f"Resolving store '{store_name}'...")
        stores = list_file_search_stores(dev_client)
        t_store = next((s for s in stores if s.display_name == store_name), None)
        if t_store:
            store_resource_name = t_store.name
            print(f"  Found store: {store_resource_name}")
        else:
            print(f"  Warning: Store '{store_name}' not found.")

    # Generate and verify hypotheses
    hypotheses = generate_hypotheses(domain_config)
    print(f"\nLoaded {len(hypotheses)} hypotheses for domain '{domain}'")

    results = []
    for h in hypotheses:
        print("-" * 60)
        res = verify_hypothesis(
            dev_client, vertex_client, h,
            store_resource_name, candidate_override=candidate,
            project_root=root,
        )
        results.append({"hypothesis": h.model_dump(), "result": res.model_dump()})
        time.sleep(1)

    # Build markdown report
    md = f"# Validated Semantic Map: {domain.upper()}\n\n"
    md += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    verified_count = 0
    violation_count = 0

    for item in results:
        h = item["hypothesis"]
        res = item["result"]
        md += f"## Concept: {h['concept']}\n> {h['description']}\n\n"
        if res["verified"]:
            verified_count += 1
            analysis_text = (
                res["analysis"].get("summary", str(res["analysis"]))
                if isinstance(res["analysis"], dict) else str(res["analysis"])
            )
            md += analysis_text + "\n\n"
            gr = res.get("guardrails", {})
            md += "### Semantic Guardrails (Antimatter Check)\n"
            if gr.get("compliant"):
                md += "**PASSED**: No liabilities detected.\n"
            else:
                md += "**DETECTED LIABILITIES**:\n"
                for v in gr.get("violations", []):
                    violation_count += 1
                    md += f"- **[{v.get('law_id')}]**: {v.get('reasoning')} (Severity: {v.get('severity')})\n"
            md += "\n"
        else:
            md += f"**Verification Failed**: {res.get('reason')}\n\n"

    # Build AuditReport
    report = AuditReport(
        _generated=AuditReport.d6_header(),
        domain=domain,
        timestamp=datetime.now(timezone.utc).isoformat(),
        hypotheses_count=len(hypotheses),
        verified_count=verified_count,
        violation_count=violation_count,
        results=results,
        markdown=md,
    )

    # --- Three-tier output ---
    socratic_dir = root / ".socratic"
    socratic_dir.mkdir(exist_ok=True)

    # Tier 1: Full JSON report
    (socratic_dir / "latest_report.json").write_text(
        report.model_dump_json(by_alias=True, indent=2)
    )

    # Tier 3: Markdown report
    (socratic_dir / "latest_report.md").write_text(md)

    # Longitudinal tracking
    _append_run_index(report, socratic_dir)

    # Legacy output path (backward compat)
    intelligence_dir = root / "wave/intelligence"
    intelligence_dir.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    legacy_path = intelligence_dir / f"socratic_audit_{domain}_{timestamp}.json"
    legacy_path.write_text(report.model_dump_json(by_alias=True, indent=2))

    # Optional GCS sync
    if sync_gcs and shutil.which("gsutil"):
        try:
            import subprocess
            subprocess.run(
                ["gsutil", "cp", str(legacy_path),
                 f"gs://elements-archive-2026/intelligence/{legacy_path.name}"],
                check=False, capture_output=True,
            )
        except Exception:
            pass

    # Explicit output file
    if output:
        Path(output).write_text(md)
        print(f"\nReport saved to: {output}")
    else:
        print(md)

    print(f"\nOutputs:")
    print(f"  Tier 1 (JSON): {socratic_dir / 'latest_report.json'}")
    print(f"  Tier 3 (MD):   {socratic_dir / 'latest_report.md'}")
    print(f"  Index:         {socratic_dir / 'run_index.jsonl'}")
    print(f"  Legacy:        {legacy_path}")

    return report
