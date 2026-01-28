# Survey

> **Mirror**: [`survey.py`](../../../src/core/survey.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture
### Classes
- **`SystemIdentity`**: No docstring
- **`CodomeComposition`**: No docstring
- **`PollutionAlert`**: No docstring
- **`ExclusionMatch`**: No docstring
- **`MinifiedFile`**: No docstring
- **`CCIMetrics`**: No docstring
- **`SurveyResult`**: No docstring

### Functions
- **`calculate_cci`**: Calculate Codome Completeness Index from classification results.
- **`path_matches_pattern`**: Check if a path matches an exclusion pattern.
- **`scan_for_exclusions`**: Scan directory for exclusion candidates.
- **`_get_pattern_reason`**: Get human-readable reason for a pattern.
- **`detect_identity`**: Detect the fundamental identity of the codebase (Q1).
- **`_detect_framework`**: Detect dominant framework from manifest files.
- **`_detect_archetype`**: Detect project archetype (organizational structure).
- **`detect_composition`**: Detect the composition breakdown of the codebase (Q3).
- **`detect_pollution`**: Detect pollution issues in the codebase (Q4).
- **`detect_minified_files`**: Detect minified files using heuristics.
- **`_check_minified`**: Check if a file appears to be minified.
- **`run_survey`**: Run a complete Codome Definition survey of a directory.
- **`_get_recommended_parsers`**: Determine recommended parsers based on identity (Q5).
- **`load_exclusion_config`**: Load exclusion configuration from YAML file.
- **`generate_analysis_config`**: Generate an analysis configuration from survey results.
- **`print_survey_report`**: Print a human-readable Codome Definition report.
