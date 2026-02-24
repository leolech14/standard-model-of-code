# Collider - Standard Model of Code
# Core public API

# Survey Module (Phase 10: Adaptive Intelligence Layer)
from .survey import (
    run_survey,
    SurveyResult,
    ExclusionMatch,
    MinifiedFile,
    scan_for_exclusions,
    detect_minified_files,
    load_exclusion_config,
    generate_analysis_config,
)

# Primary analysis entry points
from .full_analysis import (
    run_full_analysis,
    run_pipeline_analysis,
)

__version__ = "4.0.0"

__all__ = [
    # Version
    "__version__",
    # Survey
    "run_survey",
    "SurveyResult",
    "ExclusionMatch",
    "MinifiedFile",
    "scan_for_exclusions",
    "detect_minified_files",
    "load_exclusion_config",
    "generate_analysis_config",
    # Analysis
    "run_full_analysis",
    "run_pipeline_analysis",
]
