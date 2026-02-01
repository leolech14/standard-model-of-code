"""
Stage 0: Survey (Pre-Analysis Intelligence)

Performs pre-analysis scanning to detect vendor directories, minified files,
and estimate complexity before the main analysis begins.
"""

from typing import TYPE_CHECKING, Optional, List

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class SurveyStage(BaseStage):
    """
    Stage 0: Survey - Pre-Analysis Intelligence.

    Input: CodebaseState with target_path set
    Output: CodebaseState with survey results and exclusion paths

    Detects:
    - Vendor directories (node_modules, venv, etc.)
    - Minified files
    - Estimated complexity
    - Recommended exclusions
    """

    def __init__(self, skip: bool = False):
        """
        Initialize survey stage.

        Args:
            skip: If True, skip survey entirely
        """
        self._skip = skip

    @property
    def name(self) -> str:
        return "survey"

    @property
    def stage_number(self) -> Optional[int]:
        return 0

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have a target path."""
        return bool(state.target_path)

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Run pre-analysis survey.
        """
        from pathlib import Path

        if self._skip:
            print("   → Survey skipped")
            return state

        target = Path(state.target_path)
        if not target.is_dir():
            print("   → Survey skipped (single file)")
            return state

        import sys
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from survey import run_survey

            survey_result = run_survey(str(target))

            # Store survey results in metadata
            state.metadata['survey'] = {
                'total_files': survey_result.total_files,
                'source_files': survey_result.source_files,
                'estimated_nodes': survey_result.estimated_nodes,
                'scan_time_ms': survey_result.scan_time_ms,
                'directory_exclusions': survey_result.directory_exclusions,
                'minified_files': survey_result.minified_files,
                'warnings': survey_result.warnings,
            }

            # Store exclusion paths for subsequent stages
            state.metadata['exclude_paths'] = survey_result.recommended_excludes

            # Store CCI metrics if available
            if hasattr(survey_result, 'cci') and survey_result.cci:
                state.metadata['cci'] = {
                    'score': survey_result.cci.cci,
                    'verdict': survey_result.cci.verdict,
                    'sensitivity': survey_result.cci.sensitivity,
                    'specificity': survey_result.cci.specificity,
                    'precision': survey_result.cci.precision,
                }

            print(f"   → Scanned {survey_result.total_files:,} files in {survey_result.scan_time_ms:.0f}ms")
            print(f"   → Excluding {len(survey_result.recommended_excludes)} paths")
            print(f"   → Estimated {survey_result.estimated_nodes:,} nodes")

        except ImportError as e:
            print(f"   → Survey module not available: {e}")
        except Exception as e:
            print(f"   → Survey failed: {e}")

        return state
