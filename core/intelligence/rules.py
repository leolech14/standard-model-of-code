"""
Standard Model Rules (The Physics)

This module defines the architectural laws that the Spectrometer enforces.
These are the "Invariants" of a healthy Standard Model codebase.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ArchitecturalRule:
    id: str
    name: str
    description: str
    severity: str  # "CRITICAL", "WARNING", "INFO"
    category: str  # "JURISDICTION", "PURITY", "SIZING"

class StandardModelPhysics:
    """
    Defines the immutable laws of the Standard Model.
    """
    
    # -------------------------------------------------------------------------
    # JURISDICTION LAWS (Layering & Dependencies)
    # -------------------------------------------------------------------------
    
    LAW_OF_GRAVITY = ArchitecturalRule(
        id="JUR-001",
        name="Law of Gravity (Layering)",
        description="Dependencies must flow DOWN: Data > Logic > App > Interface. A lower layer cannot import a higher layer.",
        severity="CRITICAL",
        category="JURISDICTION"
    )

    LAW_OF_ISOLATION = ArchitecturalRule(
        id="JUR-002",
        name="Law of Isolation (Horizontal)",
        description="Atoms in the same layer/continent should minimalize horizontal dependencies unless explicitly designed as a collaborative cluster.",
        severity="WARNING",
        category="JURISDICTION"
    )

    # -------------------------------------------------------------------------
    # PURITY LAWS (Behavior & Side Effects)
    # -------------------------------------------------------------------------

    LAW_OF_ATOMIC_PURITY = ArchitecturalRule(
        id="PUR-001",
        name="Law of Atomic Purity",
        description="Data Foundation atoms (Primitives, Structs) must be pure data holders. They cannot contain logic or side effects.",
        severity="CRITICAL",
        category="PURITY"
    )

    LAW_OF_FUNCTIONAL_HONESTY = ArchitecturalRule(
        id="PUR-002",
        name="Law of Functional Honesty",
        description="Functions labeled as 'pure' or 'computation' must not perform I/O or mutation.",
        severity="WARNING",
        category="PURITY"
    )

    # -------------------------------------------------------------------------
    # SIZING LAWS (Complexity & Size)
    # -------------------------------------------------------------------------

    LAW_OF_ATOMIC_SIZE = ArchitecturalRule(
        id="SIZ-001",
        name="Law of Atomic Size (God Class)",
        description="An Atom should not exceed responsible size limits (default: < 20 methods, < 300 LOC).",
        severity="WARNING",
        category="SIZING"
    )

    ALL_RULES = [
        LAW_OF_GRAVITY,
        LAW_OF_ISOLATION,
        LAW_OF_ATOMIC_PURITY,
        LAW_OF_FUNCTIONAL_HONESTY,
        LAW_OF_ATOMIC_SIZE
    ]
