"""Socratic Semantic Validator — hypothesis-driven code verification."""

from .domain_runner import verify_domain
from .validator import SocraticValidator
from .hypothesis import generate_hypotheses
from .models import Hypothesis, VerificationResult, AuditReport

__all__ = [
    "verify_domain", "SocraticValidator", "generate_hypotheses",
    "Hypothesis", "VerificationResult", "AuditReport",
]
