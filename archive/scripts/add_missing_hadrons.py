#!/usr/bin/env python3
"""
Add the 17 missing Hadrons to 1440_csv.csv.
This script generates rows for each missing Hadron across a subset of dimension combos.
"""

import csv
from itertools import product

# The 17 missing Hadrons with their metadata
MISSING_HADRONS = [
    # (continent, quark, hadron, example, detection_rule)
    ("Data Foundations", "Bits", "ParityBit", "__builtin_popcount(x) % 2", "popcount + mod 2"),
    ("Data Foundations", "Bits", "SignBit", "x >> 31", "arithmetic shift right 31"),
    ("Data Foundations", "Bytes", "MagicBytes", "b'\\x89PNG\\r\\n\\x1a\\n'", "starts with known magic"),
    ("Data Foundations", "Bytes", "PaddingBytes", "pad: [u8; 7]", "fixed-size padding"),
    ("Logic & Flow", "Control Structures", "GuardClause", "if (!user) throw", "early return + error"),
    ("Logic & Flow", "Functions", "SagaStep", "compensateDeleteUser", "saga/orchestration pattern"),
    ("Logic & Flow", "Functions", "Reducer", "reduce(acc, item)", "reduce/fold"),
    ("Organization", "Aggregates", "Projection", "handles events -> updates read model", "@EventHandler on read model"),
    ("Execution", "Executables", "Fiber", "Fiber.schedule { ... }", "Fiber keyword"),
    ("Execution", "Executables", "WebWorker", "new Worker('worker.js')", "new Worker"),
    ("Execution", "Executables", "ServiceWorker", "self.addEventListener('install')", "Service Worker scope"),
    ("Execution", "Executables", "ServerlessColdStart", "handler first run", "internal metric"),
    ("Execution", "Executables", "TracerProvider", "OpenTelemetry.sdk.trace", "OpenTelemetry init"),
    ("Execution", "Executables", "PluginLoader", "plugin.load('*.so')", "dynamic plugin load"),
    ("Execution", "Executables", "PanicRecover", "defer recover()", "recover/defer"),
    ("Execution", "Executables", "ABTestRouter", "abtest.variant('exp-123')", "A/B test routing"),
    ("Execution", "Executables", "CanaryDeployTrigger", "if canary_rollout", "canary condition"),
]

# Dimension values (subset for manageable row count)
RESPONSIBILITIES = ["Create", "Read", "Update", "Delete"]
PURITIES = ["Pure", "Impure", "Idempotent", "ExternalIO"]
BOUNDARIES = ["Domain", "Application", "Infrastructure"]
LIFECYCLES = ["Singleton", "Scoped", "Transient"]

def generate_rows():
    """Generate CSV rows for missing Hadrons."""
    rows = []
    
    for continent, quark, hadron, example, rule in MISSING_HADRONS:
        for resp, purity, boundary, lifecycle in product(RESPONSIBILITIES, PURITIES, BOUNDARIES, LIFECYCLES):
            # Determine if impossible (simplified heuristic)
            is_impossible = "False"
            impossible_reason = ""
            
            # Some impossible combos
            if lifecycle == "Immutable" and resp in ["Create", "Update", "Delete"]:
                is_impossible = "True"
                impossible_reason = "Immutable cannot have mutating operations"
            
            # Build visual_3d based on continent
            shape_map = {
                "Data Foundations": "tetrahedron",
                "Logic & Flow": "octahedron", 
                "Organization": "dodecahedron",
                "Execution": "icosahedron"
            }
            base_shape = shape_map.get(continent, "sphere")
            visual = f"{base_shape}_crystalline+dynamic"
            
            # Emergence rarity (placeholder)
            emergence = "25.0%"
            
            # Build touchpoints
            touchpoints = "mutation,deterministic"
            
            row = {
                "responsibility": resp,
                "purity": purity,
                "boundary": boundary,
                "lifecycle": lifecycle,
                "base_hadron": hadron,
                "quark_parent": quark,
                "touchpoints": touchpoints,
                "is_impossible": is_impossible,
                "impossible_reason": impossible_reason,
                "visual_3d": visual,
                "emergence_rarity_2025": emergence,
                "continente_cor": continent,
                "particula_fundamental": quark,
                "hadron_subtipo": hadron,
                "forma_3d_base_variacao": f"{base_shape} + glow",
                "exemplo_real_linguagem_neutro": example,
                "regra_detecao": rule
            }
            rows.append(row)
    
    return rows

def main():
    # Read existing CSV
    csv_path = "1440_csv.csv"
    
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        existing_rows = list(reader)
        fieldnames = reader.fieldnames
    
    print(f"Existing rows: {len(existing_rows)}")
    
    # Get existing hadron types
    existing_hadrons = set(row['hadron_subtipo'] for row in existing_rows)
    print(f"Existing unique hadrons: {len(existing_hadrons)}")
    
    # Generate new rows
    new_rows = generate_rows()
    
    # Filter to only truly missing hadrons
    new_rows = [r for r in new_rows if r['hadron_subtipo'] not in existing_hadrons]
    print(f"New rows to add: {len(new_rows)}")
    
    # Append to CSV
    all_rows = existing_rows + new_rows
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"Total rows after update: {len(all_rows)}")
    
    # Verify
    final_hadrons = set(row['hadron_subtipo'] for row in all_rows)
    print(f"Final unique hadrons: {len(final_hadrons)}")

if __name__ == "__main__":
    main()
