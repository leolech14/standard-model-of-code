"""
Cryptographic Integrity & Provenance utilities.

Merkle root computation and refinery signatures for analysis provenance.
Extracted from full_analysis.py during audit refactoring (2026-02-24).
"""
import hashlib
from datetime import datetime, timezone
from typing import List


def calculate_merkle_root(items: List[str]) -> str:
    """
    Calculate a simple cryptographic root for a list of items.
    Ensures deterministic output via sorting.
    """
    if not items:
        return hashlib.sha256(b"").hexdigest()

    # Deterministic order
    sorted_items = sorted(items)

    # Simple binary-concatenation approach for Merkle-like root
    hashes = [hashlib.sha256(item.encode()).hexdigest() for item in sorted_items]

    while len(hashes) > 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])

        new_hashes = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i+1]
            new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
        hashes = new_hashes

    return hashes[0]


def generate_refinery_signature() -> str:
    """Generate a signature for the current refinery engine instance."""
    engine_id = "particle-v4.0.0-smoc"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return hashlib.sha256(f"{engine_id}-{timestamp}".encode()).hexdigest()[:16]
