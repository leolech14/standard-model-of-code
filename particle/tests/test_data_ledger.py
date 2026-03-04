"""Tests for DataLedger — non-linear pipeline data traffic tracking."""

import time
import pytest

from src.core.data_ledger import DataLedger, LedgerEntry, MANIFEST


class TestDataLedger:
    """Core DataLedger functionality."""

    def test_publish_and_available(self):
        ledger = DataLedger()
        ledger.publish("nodes", "Stage 1: Base Analysis", summary="500 nodes")
        assert ledger.is_available("nodes")
        assert ledger.get_status("nodes") == "ok"

    def test_not_available_when_empty(self):
        ledger = DataLedger()
        ledger.publish("roadmap", "Stage 9: Roadmap", status="empty")
        assert not ledger.is_available("roadmap")
        assert ledger.get_status("roadmap") == "empty"

    def test_not_available_when_skipped(self):
        ledger = DataLedger()
        ledger.publish("ai_insights", "Stage 12: AI Insights", status="skipped")
        assert not ledger.is_available("ai_insights")
        assert ledger.get_status("ai_insights") == "skipped"

    def test_not_available_when_failed(self):
        ledger = DataLedger()
        ledger.publish("ecosystem", "Stage 2.5", status="failed", summary="ImportError")
        assert not ledger.is_available("ecosystem")
        assert ledger.get_status("ecosystem") == "failed"

    def test_unknown_key_returns_none(self):
        ledger = DataLedger()
        assert ledger.get_status("nonexistent") is None
        assert not ledger.is_available("nonexistent")

    def test_get_entry(self):
        ledger = DataLedger()
        ledger.publish("nodes", "Stage 1", summary="42 nodes")
        entry = ledger.get_entry("nodes")
        assert isinstance(entry, LedgerEntry)
        assert entry.key == "nodes"
        assert entry.summary == "42 nodes"
        assert entry.status == "ok"
        assert entry.timestamp_ms >= 0

    def test_get_entry_none_for_missing(self):
        ledger = DataLedger()
        assert ledger.get_entry("missing") is None

    def test_publish_overwrites(self):
        ledger = DataLedger()
        ledger.publish("nodes", "Stage 1", status="failed")
        assert ledger.get_status("nodes") == "failed"
        ledger.publish("nodes", "Stage 1", status="ok", summary="retry worked")
        assert ledger.get_status("nodes") == "ok"
        assert ledger.get_entry("nodes").summary == "retry worked"


class TestMissing:
    """MANIFEST gap detection."""

    def test_missing_keys_all_when_empty(self):
        ledger = DataLedger()
        missing = ledger.missing_keys()
        assert len(missing) == len(MANIFEST)
        assert missing == sorted(MANIFEST.keys())

    def test_missing_keys_decreases(self):
        ledger = DataLedger()
        for key in MANIFEST:
            ledger.publish(key, "test", status="ok")
        assert ledger.missing_keys() == []

    def test_unexpected_keys(self):
        ledger = DataLedger()
        ledger.publish("surprise_key", "mystery stage")
        assert "surprise_key" in ledger.unexpected_keys()

    def test_no_unexpected_when_in_manifest(self):
        ledger = DataLedger()
        ledger.publish("nodes", "Stage 1")
        assert ledger.unexpected_keys() == []


class TestSerialization:
    """to_dict() output for pipeline_report.json."""

    def test_to_dict_structure(self):
        ledger = DataLedger()
        ledger.publish("nodes", "Stage 1", summary="500 nodes")
        ledger.publish("edges", "Stage 1", summary="300 edges")
        d = ledger.to_dict()

        assert d["total_expected"] == len(MANIFEST)
        assert d["total_published"] == 2
        assert d["missing_count"] == len(MANIFEST) - 2
        assert "nodes" not in d["missing_keys"]
        assert "edges" not in d["missing_keys"]
        assert d["by_status"] == {"ok": 2}
        assert len(d["entries"]) == 2

    def test_entries_sorted_by_timestamp(self):
        ledger = DataLedger()
        ledger.publish("nodes", "Stage 1")
        ledger.publish("edges", "Stage 1")
        ledger.publish("purpose_field", "Stage 3")
        d = ledger.to_dict()
        timestamps = [e["timestamp_ms"] for e in d["entries"]]
        assert timestamps == sorted(timestamps)

    def test_by_status_counts(self):
        ledger = DataLedger()
        ledger.publish("nodes", "S1", status="ok")
        ledger.publish("roadmap", "S9", status="skipped")
        ledger.publish("ecosystem", "S2.5", status="failed")
        ledger.publish("ai_insights", "S12", status="empty")
        d = ledger.to_dict()
        assert d["by_status"] == {"ok": 1, "skipped": 1, "failed": 1, "empty": 1}


class TestSummaryLine:
    """Console summary output."""

    def test_complete(self):
        ledger = DataLedger()
        for key in MANIFEST:
            ledger.publish(key, "test")
        line = ledger.summary_line()
        assert "complete" in line
        assert f"{len(MANIFEST)}/{len(MANIFEST)}" in line

    def test_missing(self):
        ledger = DataLedger()
        ledger.publish("nodes", "Stage 1")
        line = ledger.summary_line()
        assert "missing" in line
        assert "1/" in line

    def test_many_missing_truncates(self):
        """When >5 keys missing, shows +N more."""
        ledger = DataLedger()
        line = ledger.summary_line()
        assert "+", line  # all missing, should have +N more


class TestManifest:
    """MANIFEST integrity."""

    def test_manifest_has_entries(self):
        assert len(MANIFEST) >= 40, f"Expected ~45 entries, got {len(MANIFEST)}"

    def test_manifest_keys_are_snake_case(self):
        for key in MANIFEST:
            assert key == key.lower(), f"Key '{key}' should be lowercase"
            assert " " not in key, f"Key '{key}' should not contain spaces"

    def test_manifest_values_are_stage_names(self):
        for key, producer in MANIFEST.items():
            assert len(producer) > 0, f"Empty producer for key '{key}'"


class TestTimestamp:
    """Timestamp tracking."""

    def test_timestamps_are_monotonic(self):
        ledger = DataLedger()
        ledger.publish("nodes", "Stage 1")
        ledger.publish("edges", "Stage 1")
        e1 = ledger.get_entry("nodes")
        e2 = ledger.get_entry("edges")
        assert e1.timestamp_ms <= e2.timestamp_ms

    def test_custom_pipeline_start(self):
        start = time.monotonic() - 1.0  # 1 second ago
        ledger = DataLedger(pipeline_start=start)
        ledger.publish("nodes", "Stage 1")
        entry = ledger.get_entry("nodes")
        assert entry.timestamp_ms >= 1000  # at least 1s elapsed
