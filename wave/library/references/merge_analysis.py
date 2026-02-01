#!/usr/bin/env python3
"""Merge LLM analysis JSON into metadata stub."""

import json
import sys
from pathlib import Path
from datetime import datetime

REFS_DIR = Path(__file__).parent
METADATA_DIR = REFS_DIR / "metadata"


def merge_analysis(ref_id: str, analysis_file: Path) -> bool:
    """Merge analysis JSON into metadata stub."""
    meta_file = METADATA_DIR / f"{ref_id}.json"

    if not meta_file.exists():
        print(f"Error: {meta_file} not found")
        return False

    if not analysis_file.exists():
        print(f"Error: {analysis_file} not found")
        return False

    # Load both
    metadata = json.loads(meta_file.read_text())
    analysis = json.loads(analysis_file.read_text())

    # Merge analysis fields into metadata
    metadata.update({
        "summary": analysis.get("summary", metadata.get("summary")),
        "smoc_relevance_summary": analysis.get("smoc_relevance_summary", metadata.get("smoc_relevance_summary")),
        "key_smoc_concepts": analysis.get("key_smoc_concepts", []),
        "important_figures": analysis.get("important_figures", []),
        "important_equations": analysis.get("important_equations", []),
        "cross_references": analysis.get("cross_references", []),
        "gaps_or_extensions": analysis.get("gaps_or_extensions", metadata.get("gaps_or_extensions")),
        "priority_tier": analysis.get("priority_tier", metadata.get("priority_tier"))
    })

    # Update generation metadata
    metadata["generated_metadata"] = {
        "date": datetime.now().isoformat()[:10],
        "model": analysis.get("generated_by", "manual_analysis"),
        "analyst": "llm_enrichment"
    }

    # Save
    meta_file.write_text(json.dumps(metadata, indent=2) + "\n")

    print(f"✓ Merged analysis into {meta_file.name}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 merge_analysis.py <REF-ID> [analysis.json]")
        print("")
        print("If analysis.json not provided, uses metadata/<REF-ID>_analysis.json")
        return 1

    ref_id = sys.argv[1]

    if len(sys.argv) > 2:
        analysis_file = Path(sys.argv[2])
    else:
        analysis_file = METADATA_DIR / f"{ref_id}_analysis.json"

    success = merge_analysis(ref_id, analysis_file)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
