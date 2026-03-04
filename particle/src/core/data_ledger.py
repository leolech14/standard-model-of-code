"""DataLedger — Non-linear pipeline data traffic tracking.

Stages publish data keys when they produce results. Consumers query
the ledger before extraction. The ledger provides a completion view
in the pipeline report.

Not an event bus. Not async. Just a tracking dict with publish/query.

    stage produces data  → ledger.publish(key, producer, status)
    consumer needs data  → ledger.is_available(key) / get_status(key)
    pipeline report      → ledger.to_dict() → data_availability section
"""

from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LedgerEntry:
    """A single publication record in the ledger."""

    key: str
    producer: str           # e.g. "Stage 6.9: API Drift Detection"
    status: str             # "ok" | "empty" | "skipped" | "failed"
    timestamp_ms: float     # monotonic ms since pipeline start
    summary: str = ""       # e.g. "42 drift items, score=3.3%"


# ---------------------------------------------------------------------------
# MANIFEST: static declaration of expected data keys → producer stages.
#
# Keys present here but not published = gap (stage didn't run).
# Keys published but not here = undeclared output (new stage, missing entry).
# ---------------------------------------------------------------------------

MANIFEST: Dict[str, str] = {
    # Phase 1: Discovery
    "smartignore":          "Stage -1: SmartIgnore",
    "survey":               "Stage 0: Survey",
    "contextome":           "Stage 0.8: Contextome Intelligence",
    "incremental":          "Stage 0.5: Incremental Detection",

    # Phase 2: Extraction
    "nodes":                "Stage 1: Base Analysis",
    "edges":                "Stage 1: Base Analysis",
    "standard_model":       "Stage 2: Standard Model Enrichment",
    "ecosystem":            "Stage 2.5: Ecosystem Discovery",
    "levels":               "Stage 2.6: Level Classification",
    "dimensions":           "Stage 2.7: Dimension Classification",

    # Phase 3: Enrichment
    "scope_analysis":       "Stage 2.8: Scope Analysis",
    "control_flow":         "Stage 2.9: Control Flow Metrics",
    "pattern_detection":    "Stage 2.10: Pattern Detection",
    "data_flow_enrichment": "Stage 2.11: Data Flow Analysis",

    # Phase 4: Analysis
    "purpose_field":        "Stage 3: Purpose Field",
    "organelle_purpose":    "Stage 3.5: Organelle Purpose",
    "system_purpose":       "Stage 3.6: System Purpose",
    "coherence":            "Stage 3.7: Purpose Coherence",
    "execution_flow":       "Stage 4: Execution Flow",
    "markov":               "Stage 5: Markov Transition Matrix",
    "knots":                "Stage 6: Knot/Cycle Detection",
    "graph_analytics":      "Stage 6.5: Graph Analytics",
    "statistical_metrics":  "Stage 6.6: Statistical Metrics",
    "semantic_analysis":    "Stage 6.7: Semantic Purpose Analysis",
    "codome":               "Stage 6.8: Codome Boundaries",
    "api_drift":            "Stage 6.9: API Drift Detection",

    # Phase 5: Intelligence
    "data_flow":            "Stage 7: Data Flow Analysis",
    "performance":          "Stage 8: Performance Prediction",
    "constraints":          "Stage 8.5: Constraint Validation",
    "purpose_intelligence": "Stage 8.6: Purpose Intelligence",

    # Phase 5→6 bridge
    "full_output":          "_assemble_output",

    # Phase 6: Synthesis
    "roadmap":              "Stage 9: Roadmap Evaluation",
    "topology":             "Stage 10: Visual Reasoning",
    "semantics":            "Stage 11: Semantic Cortex",
    "ai_insights":          "Stage 12: AI Insights",
    "manifest":             "Stage 13: Manifest Writer",
    "igt":                  "Stage 14: IGT Metrics",
    "db_persistence":       "Stage 15: Database Persistence",
    "vectorization":        "Stage 16: Semantic Vector Indexing",
    "trinity":              "Stage 17: Collider Trinity",
    "temporal":             "Stage 18: Temporal Analysis",
    "ideome":               "Stage 19: Ideome Synthesis",
    "chemistry":            "Stage 20: Data Chemistry",
    "color_encoding":       "Post-Stage 20: Color Encoding",

    # Phase 7: Output
    "insights":             "Stage 21: Insights Compilation",
    "output_gen":           "Stage 22: Output Generation",
}


class DataLedger:
    """Non-linear pipeline data traffic tracker.

    Provides publish/query semantics so any pipeline component can
    check whether a data key has been produced, and with what status.
    """

    def __init__(self, pipeline_start: Optional[float] = None):
        self._entries: Dict[str, LedgerEntry] = {}
        self._pipeline_start = pipeline_start or time.monotonic()

    def publish(
        self,
        key: str,
        producer: str,
        *,
        status: str = "ok",
        summary: str = "",
    ) -> None:
        """Record that *producer* has produced data for *key*."""
        elapsed_ms = (time.monotonic() - self._pipeline_start) * 1000
        self._entries[key] = LedgerEntry(
            key=key,
            producer=producer,
            status=status,
            timestamp_ms=round(elapsed_ms, 1),
            summary=summary,
        )

    def is_available(self, key: str) -> bool:
        """True only if *key* was published with status ``"ok"``."""
        entry = self._entries.get(key)
        return entry is not None and entry.status == "ok"

    def get_status(self, key: str) -> Optional[str]:
        """Return status string or None if never published."""
        entry = self._entries.get(key)
        return entry.status if entry else None

    def get_entry(self, key: str) -> Optional[LedgerEntry]:
        """Return full entry or None."""
        return self._entries.get(key)

    def missing_keys(self) -> List[str]:
        """MANIFEST keys that were never published."""
        return sorted(k for k in MANIFEST if k not in self._entries)

    def unexpected_keys(self) -> List[str]:
        """Published keys not declared in MANIFEST."""
        return sorted(k for k in self._entries if k not in MANIFEST)

    def to_dict(self) -> dict:
        """Serialize for pipeline_report.json ``data_availability`` section."""
        by_status = Counter(e.status for e in self._entries.values())
        missing = self.missing_keys()
        return {
            "total_expected": len(MANIFEST),
            "total_published": len(self._entries),
            "missing_count": len(missing),
            "missing_keys": missing,
            "by_status": dict(by_status),
            "entries": [
                {
                    "key": e.key,
                    "producer": e.producer,
                    "status": e.status,
                    "timestamp_ms": e.timestamp_ms,
                    "summary": e.summary,
                }
                for e in sorted(
                    self._entries.values(), key=lambda e: e.timestamp_ms
                )
            ],
        }

    def summary_line(self) -> str:
        """One-line summary for console output."""
        total = len(MANIFEST)
        published = len(self._entries)
        missing = self.missing_keys()
        if missing:
            names = ", ".join(missing[:5])
            extra = f" (+{len(missing) - 5} more)" if len(missing) > 5 else ""
            return f"Data: {published}/{total} keys published, {len(missing)} missing: {names}{extra}"
        return f"Data: {published}/{total} keys published (complete)"
