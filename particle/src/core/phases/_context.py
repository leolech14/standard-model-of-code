"""Pipeline execution context — shared state across all phases."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from src.core.data_ledger import DataLedger


@dataclass
class PipelineContext:
    """Mutable state threaded through all pipeline phases.

    Each phase reads/writes attributes on this object instead of using
    local variables in the monolith.  Fields are grouped by lifecycle:
    immutable inputs first, then progressively-populated intermediates.
    """

    # ── Immutable inputs ─────────────────────────────────────────────
    target: Path
    output_dir: Path
    options: Dict[str, Any]
    quiet: bool
    batch_id: str
    start_time: float

    # ── Observability ────────────────────────────────────────────────
    perf_manager: Any          # PerformanceManager
    guard: Any                 # _PipelineCrashGuard
    data_ledger: DataLedger = field(default_factory=DataLedger)

    # ── Mutable graph state ──────────────────────────────────────────
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)

    # ── Accumulated output dict ──────────────────────────────────────
    # Built by _assemble_output(), consumed by synthesis & output phases
    full_output: Dict[str, Any] = field(default_factory=dict)

    # ── Cross-phase intermediates (populated progressively) ──────────
    exclude_paths: List[str] = field(default_factory=list)
    skip_files: Set[str] = field(default_factory=set)
    smartignore_manifest: Any = None
    survey_result: Any = None
    contextome_result: Any = None
    delta_tracker: Any = None
    delta_result: Any = None
    db_manager: Any = None

    # ── Analysis results needed across phases ────────────────────────
    purpose_field: Any = None
    exec_flow: Any = None
    markov: Optional[Dict] = None
    knots: Optional[Dict] = None
    graph_analytics: Optional[Dict] = None
    semantic_analysis: Optional[Dict] = None
    statistical_metrics: Optional[Dict] = None
    data_flow: Optional[Dict] = None
    perf_summary: Optional[Dict] = None
    constraint_report: Optional[Dict] = None
    codebase_intelligence: Optional[Dict] = None
    codome_result: Optional[Dict] = None
    ecosystem_discovery: Any = None
    ecosystem_discovery_status: str = "not_run"
    ecosystem_discovery_error: str = ""
    nx_graph_full: Any = None   # NetworkX graph built in Stage 6.5, reused in 6.7
    ts_cache: Any = None        # TreeSitterCache, initialized before enrichment

    # ── Stage 1 unified outputs (needed for full_output assembly) ────
    unified_stats: Optional[Dict] = None
    unified_classification: Optional[Dict] = None
    unified_auto_discovery: Optional[Dict] = None
    unified_dependencies: Optional[Dict] = None
    unified_architecture: Optional[Dict] = None
    unified_llm_enrichment: Optional[Dict] = None
    unified_warnings: Optional[List] = None
    unified_recommendations: Optional[List] = None

    # ── Purpose analysis intermediates ───────────────────────────────
    file_purposes: Optional[Dict] = None
    orphan_analysis: Optional[List] = field(default_factory=list)

    # ── API Drift Detection ────────────────────────────────────────────
    endpoint_catalog: Any = None       # EndpointCatalog from api_route_extractor
    consumer_report: Any = None        # APIConsumerReport from frontend_api_detector
    api_drift_report: Any = None       # APIDriftReport from api_drift_analyzer

    # ── Logistics (Phase 28) ─────────────────────────────────────────
    refinery_signature: str = ""
    merkle_root: str = "UNSET"

    # ── Meta-envelope (identity for cross-run analysis) ──────────────
    meta_envelope: Optional[Dict] = None

    # ── Output file paths ────────────────────────────────────────────
    unified_json: Any = None
    viz_file: Any = None
    report_path: Any = None
    db_run_id: Any = None
