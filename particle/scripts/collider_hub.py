#!/usr/bin/env python3
"""Thin wrapper for the installable Collider Hub module."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.core.collider_hub import main


if __name__ == "__main__":
    raise SystemExit(main())
