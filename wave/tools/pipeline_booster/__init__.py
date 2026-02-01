"""
Pipeline Booster - Universal Compute Acceleration

Seamlessly upgrade any pipeline to use GPU/cloud compute.

Usage:
    from pipeline_booster import boost

    @boost(gpu=True)
    def my_slow_function(data):
        # Your existing code
        return process(data)

    # Automatically runs on best available compute
    result = my_slow_function(data)
"""

from .core import boost, BoostConfig, ComputeBackend
from .providers import get_provider, list_providers

__version__ = "0.1.0"

__all__ = [
    "boost",
    "BoostConfig",
    "ComputeBackend",
    "get_provider",
    "list_providers",
]
