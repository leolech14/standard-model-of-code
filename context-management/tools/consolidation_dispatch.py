#!/usr/bin/env python3
import json
import sys
import argparse
from pathlib import Path
from couriers.courier_link_fixer import LinkFixerCourier
from couriers.courier_archivist import ArchivistCourier

def run_consolidation_dispatch(input_json: str, output_json: str, courier_type: str = "all"):
    """
    Consolidation Dispatcher: Orchestrates multiple couriers for project cleanup.
    """
    print(f"🚛 CONSOLIDATION DISPATCHER: Loading parcels from {input_json}...")

    with open(input_json, 'r') as f:
        data = json.load(f)

    nodes = data.get('nodes', [])
    processed_nodes = []

    # Instantiate Couriers
    couriers = []
    if courier_type in ["link_fixer", "all"]:
        couriers.append(LinkFixerCourier())
    if courier_type in ["archivist", "all"]:
        couriers.append(ArchivistCourier())

    print(f"📦 FOUND: {len(nodes)} parcels.")
    print(f"👷 DRAFTED: {[c.agent_id for c in couriers]}")

    work_count = 0
    for node in nodes:
        active_node = node

        # Consolidation Logic:
        # 1. Links: Process all nodes
        # 2. Archivist: Process definitions (h2/h3)

        for courier in couriers:
            if isinstance(courier, ArchivistCourier) and node.get('chunk_type') not in ['h2', 'h3']:
                continue

            print(f"   Executing {courier.agent_id} on Parcel {node.get('waybill', {}).get('parcel_id')}...")
            active_node = courier.run(active_node)
            work_count += 1

        processed_nodes.append(active_node)

    # Save Manifest
    data['nodes'] = processed_nodes
    with open(output_json, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ CONSOLIDATION COMPLETE. {work_count} tasks executed by Couriers.")
    print(f"📄 Manifesto saved to {output_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidation Dispatcher")
    parser.add_argument("input", help="Input JSON (Parcels)")
    parser.add_argument("output", help="Output JSON (Consolidated)")
    parser.add_argument("--type", default="all", help="Courier type to run (link_fixer, archivist, all)")

    args = parser.parse_args()
    run_consolidation_dispatch(args.input, args.output, args.type)
