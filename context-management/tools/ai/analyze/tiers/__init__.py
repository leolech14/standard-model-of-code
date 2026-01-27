"""
Tiers Package - Execution Tier System
=====================================

Standard Model Classification:
-----------------------------
D1_KIND:     ORG.PKG.O (Organizational Package)
D2_LAYER:    Application (tier orchestration)
D3_ROLE:     Controller (routes to appropriate tier)
D4_BOUNDARY: Internal (no direct external calls)
D5_STATE:    Stateless (routing logic is pure)
D6_EFFECT:   Pure (routing decision is deterministic)
D7_LIFECYCLE: Use (called during analysis routing)
D8_TRUST:    90 (well-defined tier boundaries)

Purpose Emergence: pi3 Organelle
    Each tier is a coherent unit that can function independently.
    The package provides the coordination layer.

Communication Theory:
    This package implements CHANNEL SELECTION - routing queries
    to the appropriate tier based on ACI analysis.

ACI Tiers (Adaptive Context Intelligence):
    INSTANT (0):     Cached truths for counts/stats (<100ms)
    RAG (1):         File Search for targeted lookups (~5s)
    LONG_CONTEXT (2): Full context Gemini reasoning (~60s)
    PERPLEXITY (3):  External web research (~30s)
    FLASH_DEEP (4):  Gemini 2.0 Flash with 2M context (~120s)
    HYBRID (5):      Internal + External synthesis (~90s)
"""

from enum import Enum
from typing import Optional, Dict, Any


class Tier(Enum):
    """
    ACI Execution Tiers.

    Each tier represents a different trade-off between:
    - Latency (how fast)
    - Cost (how expensive)
    - Depth (how thorough)
    - Scope (internal vs external)
    """
    INSTANT = "instant"         # Tier 0: Cached truths
    RAG = "rag"                 # Tier 1: File Search
    LONG_CONTEXT = "long_context"  # Tier 2: Full context
    PERPLEXITY = "perplexity"   # Tier 3: External research
    FLASH_DEEP = "flash_deep"   # Tier 4: 2M context
    HYBRID = "hybrid"           # Tier 5: Internal + External


def tier_from_string(tier_str: str) -> Optional[Tier]:
    """
    Convert string to Tier enum.

    Handles aliases:
    - "deep" -> FLASH_DEEP
    - "external" -> PERPLEXITY

    Args:
        tier_str: Tier name string

    Returns:
        Tier enum value or None if invalid
    """
    tier_str = tier_str.lower().strip()

    # Handle aliases
    aliases = {
        "deep": "flash_deep",
        "external": "perplexity",
        "web": "perplexity",
        "full": "long_context",
    }
    tier_str = aliases.get(tier_str, tier_str)

    try:
        return Tier(tier_str)
    except ValueError:
        return None


# Tier characteristics (for routing decisions)
TIER_CHARACTERISTICS = {
    Tier.INSTANT: {
        "latency_ms": 100,
        "cost_factor": 0.0,
        "requires_api": False,
        "requires_context": False,
        "description": "Cached truths - instant answers for counts and stats",
    },
    Tier.RAG: {
        "latency_ms": 5000,
        "cost_factor": 0.5,
        "requires_api": True,
        "requires_context": False,
        "description": "File Search - targeted lookups with citations",
    },
    Tier.LONG_CONTEXT: {
        "latency_ms": 60000,
        "cost_factor": 1.0,
        "requires_api": True,
        "requires_context": True,
        "description": "Full context - thorough reasoning over codebase",
    },
    Tier.PERPLEXITY: {
        "latency_ms": 30000,
        "cost_factor": 0.8,
        "requires_api": True,
        "requires_context": False,
        "description": "External research - web search and synthesis",
    },
    Tier.FLASH_DEEP: {
        "latency_ms": 120000,
        "cost_factor": 2.0,
        "requires_api": True,
        "requires_context": True,
        "description": "Flash Deep - 2M context for comprehensive analysis",
    },
    Tier.HYBRID: {
        "latency_ms": 90000,
        "cost_factor": 1.8,
        "requires_api": True,
        "requires_context": True,
        "description": "Hybrid - internal context + external evidence",
    },
}


__all__ = [
    "Tier",
    "tier_from_string",
    "TIER_CHARACTERISTICS",
]
