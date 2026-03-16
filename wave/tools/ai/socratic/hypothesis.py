"""Hypothesis generation from semantic_models.yaml domain definitions."""

from typing import Dict, List
from .models import Hypothesis


def generate_hypotheses(domain_config: Dict) -> List[Hypothesis]:
    """Convert domain definitions into testable hypotheses.

    Args:
        domain_config: A domain entry from semantic_models.yaml
            with 'definitions' dict and optional 'scope' string.

    Returns:
        List of Hypothesis objects, one per concept in the domain.
    """
    hypotheses = []
    definitions = domain_config.get("definitions", {})
    domain_scope = domain_config.get("scope", "")

    for concept, details in definitions.items():
        desc = details.get("description", "No description")
        invariants = details.get("invariants", [])
        anchors = details.get("anchors", [])

        claim = f"Hypothesis: The concept '{concept}' is implemented according to strict invariants."

        hypotheses.append(Hypothesis(
            concept=concept,
            claim=claim,
            description=desc,
            invariants=invariants,
            anchors=anchors,
            scope=domain_scope,
        ))

    return hypotheses
