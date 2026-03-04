"""Pipeline phases — extracted from full_analysis.py monolith.

Each phase exports a single ``run_<phase>(ctx)`` function that takes
a :class:`PipelineContext` and mutates it in place.
"""

from ._context import PipelineContext
from .discovery import run_discovery
from .extraction import run_extraction
from .enrichment import run_enrichment
from .analysis import run_analysis
from .intelligence import run_intelligence
from .synthesis import run_synthesis
from .output import run_output

__all__ = [
    'PipelineContext',
    'run_discovery',
    'run_extraction',
    'run_enrichment',
    'run_analysis',
    'run_intelligence',
    'run_synthesis',
    'run_output',
]
