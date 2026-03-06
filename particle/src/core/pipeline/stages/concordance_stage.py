# Theory: L1_DEFINITIONS.md SS3.5 (Concordance Health)
# Theory: L0_AXIOMS.md A3 (Purpose Conservation)
"""
Stage 8.7: Concordance Validation

Validates declared architectural boundaries match actual directory structure.
Computes concordance Health(k) per region and overall alignment score.

Health(k) = |CONCORDANT| / (|CONCORDANT| + |DISCORDANT| + |UNVOICED| + |UNREALIZED|)

This stage bridges the wave/particle boundary — it wraps wave/tools/ai/boundary_analyzer.py
to integrate concordance metrics into the Collider pipeline output.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class ConcordanceStage(BaseStage):
    """
    Stage 8.7: Concordance Validation.

    Input: CodebaseState with enriched nodes and edges
    Output: CodebaseState with concordance health metrics

    Computes:
    - Health(k) per declared boundary region
    - Overall concordance health (mean of regions)
    - Alignment score (0-100)
    - Boundary issues (DISCORDANT, UNVOICED, UNREALIZED states)
    """

    @property
    def name(self) -> str:
        return "concordance"

    @property
    def stage_number(self) -> Optional[int]:
        return 8  # Phase 4: Intelligence (8.7)

    def validate_input(self, state: "CodebaseState") -> bool:
        """Concordance analysis only requires a valid target path."""
        return bool(state.target_path)

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Run boundary analysis, store concordance metrics, and track drift.

        Uses BoundaryAnalyzer from wave/tools/ai/ to validate
        declared boundaries against actual directory structure.

        Drift tracking (L0 A3): saves snapshot after each run and
        compares against previous snapshot to detect concordance drift.
        """
        import sys
        from pathlib import Path

        # Resolve project root (6 levels up from stages/)
        # stages/ -> pipeline/ -> core/ -> src/ -> particle/ -> PROJECT_ROOT
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
        wave_ai_path = project_root / "wave" / "tools" / "ai"

        if str(wave_ai_path) not in sys.path:
            sys.path.insert(0, str(wave_ai_path))

        try:
            from boundary_analyzer import (
                BoundaryAnalyzer, save_snapshot, compute_drift
            )

            # Use target_path as analysis root, fallback to project root
            analysis_root = Path(state.target_path)
            if not analysis_root.is_dir():
                analysis_root = project_root

            analyzer = BoundaryAnalyzer(analysis_root)
            report = analyzer.analyze()

            # Compute drift against previous snapshot (before saving current)
            drift_result = compute_drift(report, analysis_root)

            # Save concordance snapshot for future drift comparison
            try:
                save_snapshot(report, analysis_root)
            except Exception as snap_err:
                print(f"   \u2192 Snapshot save warning: {snap_err}")

            # Store full report in metadata
            report_dict = report.to_dict()
            if drift_result:
                report_dict['drift'] = drift_result
            state.metadata['concordance'] = report_dict

            # Print summary
            health_pct = report.overall_health * 100
            issue_count = len(report.issues)
            alignment = report.alignment_score

            drift_str = ""
            if drift_result:
                max_h = drift_result.get("max_health_drift", 0)
                alert_count = len(drift_result.get("alerts", []))
                drift_str = f", drift: {max_h:.4f}"
                if alert_count > 0:
                    drift_str += f" [{alert_count} alerts]"

            print(f"   \u2192 Concordance Health: {health_pct:.1f}%  "
                  f"({issue_count} issues, alignment: {alignment:.0f}/100{drift_str})")

        except ImportError as e:
            print(f"   \u2192 Concordance stage skipped (import): {e}")
        except Exception as e:
            print(f"   \u2192 Concordance stage skipped: {e}")

        return state
