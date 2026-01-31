#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from couriers.courier_archivist import ArchivistCourier

def run_dispatch(input_json: str, output_json: str):
    """
    Reads Refinery Parcels, Dispatches Couriers, Saves Result.
    """
    print(f"🚚 DISPATCHER: Loading parcels from {input_json}...")

    with open(input_json, 'r') as f:
        data = json.load(f)

    nodes = data.get('nodes', [])
    processed_nodes = []

    # Instantiate Worker
    archivist = ArchivistCourier()

    print(f"📦 FOUND: {len(nodes)} parcels.")

    work_count = 0
    for node in nodes:
        # Filter: Only work on parcels that look like definitions (h2/h3 in our markdown dump context)
        # In code context, this would filter by AST type.
        if node.get('chunk_type') in ['h2', 'h3']:
            print(f"   Drafting Archivist for Parcel {node.get('waybill', {}).get('parcel_id')}...")

            # RUN THE COURIER
            updated_node = archivist.run(node)

            processed_nodes.append(updated_node)
            work_count += 1
        else:
            processed_nodes.append(node)

    # Save Manifest
    data['nodes'] = processed_nodes
    with open(output_json, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ DISPATCH COMPLETE. {work_count} parcels processed.")
    print(f"📄 Manifesto saved to {output_json}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: dispatch.py <input.json> <output.json>")
        sys.exit(1)
    run_dispatch(sys.argv[1], sys.argv[2])
