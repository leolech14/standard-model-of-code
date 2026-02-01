"""
Base Executor - Abstract Tier Execution
=======================================

Standard Model Classification:
-----------------------------
D1_KIND:     ORG.CLS.A (Organizational Class - Abstract)
D2_LAYER:    Application (tier abstraction)
D3_ROLE:     Internal (base class, not directly used)
D4_BOUNDARY: Internal (no external calls in base)
D5_STATE:    Stateless (abstract, no state)
D6_EFFECT:   Pure (interface definition only)
D7_LIFECYCLE: Create (defines structure for subclasses)
D8_TRUST:    95 (simple interface)

Purpose: pi2 Molecular
    Defines the contract that all tier executors must implement.
    This enables polymorphic tier selection.
"""

import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass

from ..output import AnalyzeResult


@dataclass
class TierRequest:
    """
    Request to a tier executor.

    This is the input contract - all tiers receive the same structure.
    """
    query: str
    context: str = ""
    model: str = ""
    mode: str = "standard"
    sets: Optional[list] = None
    extra_context: str = ""
    system_prompt: str = ""


@dataclass
class TierResponse:
    """
    Response from a tier executor.

    This is the output contract - all tiers return the same structure.
    """
    text: str
    usage: Optional[Dict[str, int]] = None
    model: str = ""
    mode: str = ""
    tier: str = ""
    saved_path: str = ""
    success: bool = True
    error: str = ""


class BaseTierExecutor(ABC):
    """
    Abstract base class for tier executors.

    Each tier implements:
    - execute(): Main execution logic
    - can_handle(): Check if tier can handle request
    - get_info(): Tier metadata

    Communication Theory:
        Each executor is a CHANNEL with specific characteristics
        (latency, cost, scope). The routing layer selects the
        appropriate channel based on query analysis.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize executor with configuration.

        Args:
            config: Configuration dict (from AnalyzeConfig)
        """
        self.config = config or {}

    @abstractmethod
    def execute(self, request: TierRequest) -> TierResponse:
        """
        Execute the tier's analysis.

        Args:
            request: TierRequest with query and context

        Returns:
            TierResponse with results
        """
        pass

    @abstractmethod
    def can_handle(self, request: TierRequest) -> bool:
        """
        Check if this tier can handle the request.

        Used for fallback logic - if primary tier fails,
        check if alternative tier can handle.

        Args:
            request: TierRequest to check

        Returns:
            True if tier can handle this request
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """
        Get tier metadata.

        Returns:
            Dict with tier characteristics
        """
        return {
            "name": self.__class__.__name__,
            "tier": "unknown",
            "description": "Base tier executor",
        }

    def log(self, message: str, level: str = "info") -> None:
        """
        Log a message to stderr.

        All tier logs go to stderr to keep stdout clean for results.

        Args:
            message: Message to log
            level: Log level (info, warn, error)
        """
        tier_name = self.get_info().get("tier", "unknown").upper()
        prefix = f"[{tier_name}]"

        if level == "error":
            print(f"{prefix} ERROR: {message}", file=sys.stderr)
        elif level == "warn":
            print(f"{prefix} WARNING: {message}", file=sys.stderr)
        else:
            print(f"{prefix} {message}", file=sys.stderr)


def create_response_from_error(
    error: Exception,
    tier: str = "unknown",
    request: Optional[TierRequest] = None
) -> TierResponse:
    """
    Create a TierResponse from an error.

    Standardizes error handling across all tiers.

    Args:
        error: The exception that occurred
        tier: Tier name for logging
        request: Original request (for context)

    Returns:
        TierResponse with error details
    """
    return TierResponse(
        text="",
        tier=tier,
        success=False,
        error=str(error),
        mode=request.mode if request else "standard",
    )
