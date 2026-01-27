"""
Classification Package - Universal Code Classification
========================================================

Provides semantic classification of code particles.

Exports:
    - UniversalClassifier: Main classifier (pattern + path + naming)
    - ClassifierPlugin: Hub-connected service wrapper
"""

from .universal_classifier import UniversalClassifier
from .classifier_plugin import ClassifierPlugin, get_classifier_from_hub

__all__ = [
    'UniversalClassifier',
    'ClassifierPlugin',
    'get_classifier_from_hub',
]
