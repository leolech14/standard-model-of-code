#!/usr/bin/env python3
"""
Collider - Standard Model of Code (Backward Compatibility Module)
==================================================================

This module re-exports from the refactored proof package.
New code should import from src.tools.proof directly.

Old:
    from prove import run_proof

New:
    from proof import ProofPipeline, run_proof

Usage:
    python prove.py <path_to_code>
"""

import sys
from pathlib import Path

# Re-export everything from the new package for backward compatibility
from proof import (
    ProofPipeline,
    run_proof,
    ProofDocument,
    ProofDocumentBuilder,
    StageResult,
)

__all__ = [
    'ProofPipeline',
    'run_proof',
    'ProofDocument',
    'ProofDocumentBuilder',
    'StageResult',
]


# CLI for backward compatibility
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prove.py <path_to_code>")
        print()
        print("Example:")
        print("  python prove.py .")
        print("  python prove.py /path/to/repo")
        sys.exit(1)

    target = sys.argv[1]
    run_proof(target)
