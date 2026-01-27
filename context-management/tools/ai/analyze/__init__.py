"""
Analyze Package - Modular AI Analysis Tool
==========================================

Architecture follows Standard Model of Code principles:
- Each module has single responsibility (RPBL Dimension 1: Low R)
- Tiers are separate execution channels (Communication Theory)
- Stone Tool outputs are explicit (Tool Theory)

Package Structure:
    analyze/
    ├── __init__.py       # This file - exports main entry points
    ├── cli.py            # CLI parsing (Boundary Atom)
    ├── config.py         # Configuration loading (Supplier Atom)
    ├── context.py        # Context building (pi2 Molecular)
    ├── clients.py        # API client creation (Connector Atom)
    ├── output.py         # Stone Tool output contract
    ├── session.py        # Session/turn logging
    ├── socratic.py       # Socratic validation
    ├── tiers/            # Execution tiers (pi3 Organelle)
    │   ├── base.py       # BaseExecutor abstraction
    │   ├── instant.py    # Tier 0: Cached truths
    │   ├── rag.py        # Tier 1: File Search
    │   ├── long_context.py # Tier 2: Full context
    │   ├── perplexity.py # Tier 3: External research
    │   ├── flash_deep.py # Tier 4: 2M context
    │   └── hybrid.py     # Tier 5: Internal + External
    ├── modes/            # Analysis modes (pi2 Molecular)
    │   ├── standard.py   # One-shot query
    │   ├── interactive.py # Chat mode
    │   └── insights.py   # JSON insights
    └── search/           # File Search subsystem
        ├── store.py      # Store management
        ├── indexer.py    # File indexing
        └── query.py      # Search execution

Usage:
    from analyze import run_analysis, AnalyzeConfig
    from analyze.tiers import get_tier_executor
    from analyze.output import AnalyzeResult
"""

__version__ = "4.0.0"  # Major version bump for modular architecture

# Core exports
from .config import AnalyzeConfig, load_config, PROJECT_ROOT
from .output import AnalyzeResult, ContextManifest

__all__ = [
    "AnalyzeConfig",
    "load_config",
    "PROJECT_ROOT",
    "AnalyzeResult",
    "ContextManifest",
]
