#!/usr/bin/env python3
"""
Refinery Pipeline ("The Logistics Network")
===========================================

Orchestrates the flow of data parcels from Ingestion to Chunking.
Ensures that every step of the process is tracked via Waybills.

Phases:
1. Ingestion (corpus_inventory): Scans files, mints Parcel IDs.
2. Refinement (Refinery): Consumes Parcels, produces Chunk Sub-Parcels.
"""

import sys
import json
import logging
import uuid # Added for batch IDs
from pathlib import Path
from datetime import datetime

# Import subsystems
# Add 'tools' directory to sys.path to allow imports like 'ai.aci.refinery'
current_dir = Path(__file__).resolve().parent
tools_dir = current_dir.parent
sys.path.append(str(tools_dir))

# Import sibling
import refinery.corpus_inventory as corpus_inventory

# Import cousin
from ai.aci.refinery import Refinery
from ai.aci.semantic_finder import semantic_match, format_semantic_match

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("LogisticsPipeline")

def load_config(config_path: str) -> dict:
    """Load configuration from YAML."""
    path = Path(config_path)
    if not path.exists():
        logger.warning(f"⚠️ Config not found at {config_path}. Using defaults.")
        return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def run_pipeline(source_dir: str, query: str = None, config_path: str = None, dry_run: bool = False, max_files: int = 10):
    """
    Run the full logistics pipeline.
    """
    root_path = Path(source_dir).resolve()
    if root_path.is_file():
        root_path = root_path.parent
    logger.info(f"📦 Starting Logistics Pipeline for: {root_path}")

    # Load Config (Layer 2 - Parametric Control)
    config = {}
    if config_path:
        logger.info(f"⚙️ Loading Parametric Config from: {config_path}")
        config = load_config(config_path)

    # Merge Logic: CLI arg > Config File > Default
    p_config = config.get('pipeline', {})
    r_config = config.get('refinery', {})

    active_query = query or p_config.get('query')
    max_files = max_files or p_config.get('max_files', 10)
    context_depth = r_config.get('context_depth', 'medium')

    # Batch Identity (The "Room")
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    logger.info(f"🆔 BATCH ID: {batch_id} (Copresence Context)")
    logger.info(f"📊 CONFIG: query='{active_query}', max_files={max_files}, depth={context_depth}")

    # PHASE 0: ATTENTION SIGNAL
    match_signal = None
    if active_query:
        logger.info(f"🔍 ATTENTION SIGNAL: Analyzing query -> '{active_query}'")
        match_signal = semantic_match(active_query)
        logger.info(f"📊 SEMANTIC MATCH:\n{format_semantic_match(match_signal)}")

    # PHASE 1: INGESTION
    logger.info("--- PHASE 1: INGESTION (Minting Parcels) ---")
    inventory = corpus_inventory.scan_corpus(root_path, quick=False)

    total_files = inventory['summary']['total_files']
    logger.info(f"✅ Ingested {total_files} files with Waybills.")

    # PHASE 2: REFINEMENT
    logger.info("--- PHASE 2: REFINEMENT (Processing Parcels) ---")

    refinery = Refinery(config=config)
    all_chunks = []
    processed_count = 0

    for file_entry in inventory['files']:
        if processed_count >= max_files:
            break

        file_path = root_path / file_entry['path']
        parcel_id = file_entry.get('parcel_id')

        # Fundamental Check: No Parcel ID? No Processing.
        if not parcel_id:
            logger.error(f"❌ REJECTED {file_entry['path']}: No Parcel ID (Waybill Missing)")
            continue

        logger.info(f"Processing Parcel {parcel_id} ({file_entry['path']})...")

        chunks = refinery.process_file(
            str(file_path),
            use_cache=False,  # Force reprocessing to apply new logistics
            parent_parcel_id=parcel_id,
            batch_id=batch_id,
            semantic_match=match_signal
        )

        all_chunks.extend(chunks)
        processed_count += 1

    # EXPORT
    output_file = root_path / "context-management/intelligence/chunks/logistics_demo.json"
    refinery.export_to_json(all_chunks, str(output_file))

    logger.info(f"🏁 Pipeline Complete. Exported {len(all_chunks)} tracked chunks to {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Logistics Pipeline")
    parser.add_argument("directory", help="Directory to process")
    parser.add_argument("--query", help="Query to drive the attention mechanism gate")
    parser.add_argument("--config", help="Path to refinery_config.yaml")
    parser.add_argument("--max-files", type=int, default=10, help="Max files to process")

    args = parser.parse_args()

    run_pipeline(args.directory, query=args.query, config_path=args.config, max_files=args.max_files)
