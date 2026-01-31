#!/usr/bin/env python3
"""
DoclingResult and BatchManifest - Output dataclasses for Docling processor.

Follows the Parcel/Waybill pattern from Refinery.
"""

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class DoclingResult:
    """Result from processing a single PDF."""

    # Identity
    pdf_path: Path
    ref_id: str  # "REF-001" or extracted from filename
    parcel_id: str = field(default_factory=lambda: f"pcl_{uuid.uuid4().hex[:12]}")

    # Status
    status: str = "pending"  # pending | processing | success | partial | failed
    strategy_used: str = "standard"  # standard | no_ocr | minimal | chunked

    # Output paths
    markdown_path: Optional[Path] = None
    json_path: Optional[Path] = None
    chunks_path: Optional[Path] = None

    # Metadata
    page_count: int = 0
    chunk_count: int = 0
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None

    # Waybill for logistics tracking
    waybill: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize waybill if not set."""
        if not self.waybill:
            self.waybill = {
                "parcel_id": self.parcel_id,
                "ref_id": self.ref_id,
                "route": []
            }

    def add_route_event(self, event: str, agent: str, context: Optional[Dict] = None):
        """Add an event to the waybill route."""
        self.waybill["route"].append({
            "event": event,
            "timestamp": int(time.time()),
            "agent": agent,
            "context": context or {}
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "pdf_path": str(self.pdf_path),
            "ref_id": self.ref_id,
            "parcel_id": self.parcel_id,
            "status": self.status,
            "strategy_used": self.strategy_used,
            "markdown_path": str(self.markdown_path) if self.markdown_path else None,
            "json_path": str(self.json_path) if self.json_path else None,
            "chunks_path": str(self.chunks_path) if self.chunks_path else None,
            "page_count": self.page_count,
            "chunk_count": self.chunk_count,
            "processing_time_seconds": self.processing_time_seconds,
            "error_message": self.error_message,
            "waybill": self.waybill
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DoclingResult":
        """Create from dictionary."""
        result = cls(
            pdf_path=Path(data["pdf_path"]),
            ref_id=data["ref_id"],
            parcel_id=data.get("parcel_id", f"pcl_{uuid.uuid4().hex[:12]}"),
            status=data.get("status", "pending"),
            strategy_used=data.get("strategy_used", "standard"),
            page_count=data.get("page_count", 0),
            chunk_count=data.get("chunk_count", 0),
            processing_time_seconds=data.get("processing_time_seconds", 0.0),
            error_message=data.get("error_message"),
            waybill=data.get("waybill", {})
        )

        if data.get("markdown_path"):
            result.markdown_path = Path(data["markdown_path"])
        if data.get("json_path"):
            result.json_path = Path(data["json_path"])
        if data.get("chunks_path"):
            result.chunks_path = Path(data["chunks_path"])

        return result


@dataclass
class BatchManifest:
    """Manifest for a batch processing run."""

    batch_id: str = field(default_factory=lambda: f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Counts
    total_files: int = 0
    successful: int = 0
    partial: int = 0
    failed: int = 0
    skipped: int = 0

    # Processing info
    config_used: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: float = 0.0

    # Results
    results: List[DoclingResult] = field(default_factory=list)

    def add_result(self, result: DoclingResult):
        """Add a result and update counts."""
        self.results.append(result)
        self.total_files = len(self.results)

        if result.status == "success":
            self.successful += 1
        elif result.status == "partial":
            self.partial += 1
        elif result.status == "failed":
            self.failed += 1
        elif result.status == "skipped":
            self.skipped += 1

    def summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            "batch_id": self.batch_id,
            "timestamp": self.timestamp,
            "total_files": self.total_files,
            "successful": self.successful,
            "partial": self.partial,
            "failed": self.failed,
            "skipped": self.skipped,
            "success_rate": self.successful / self.total_files if self.total_files > 0 else 0.0,
            "duration_seconds": self.duration_seconds
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "batch_id": self.batch_id,
            "timestamp": self.timestamp,
            "summary": self.summary(),
            "config_used": self.config_used,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "results": [r.to_dict() for r in self.results]
        }

    def save(self, output_dir: Path):
        """Save manifest to JSON file with atomic write."""
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / "manifest.json"
        temp_path = output_dir / "manifest.json.tmp"

        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2)

            # Verify JSON is valid
            with open(temp_path, 'r', encoding='utf-8') as f:
                json.load(f)

            # Atomic rename
            temp_path.rename(manifest_path)

        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise RuntimeError(f"Failed to save manifest: {e}") from e

    @classmethod
    def load(cls, manifest_path: Path) -> "BatchManifest":
        """Load manifest from JSON file."""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        manifest = cls(
            batch_id=data["batch_id"],
            timestamp=data["timestamp"],
            config_used=data.get("config_used", {}),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            duration_seconds=data.get("duration_seconds", 0.0)
        )

        for result_data in data.get("results", []):
            result = DoclingResult.from_dict(result_data)
            manifest.results.append(result)

            # Update counts
            if result.status == "success":
                manifest.successful += 1
            elif result.status == "partial":
                manifest.partial += 1
            elif result.status == "failed":
                manifest.failed += 1
            elif result.status == "skipped":
                manifest.skipped += 1

        manifest.total_files = len(manifest.results)
        return manifest

    def get_failed_refs(self) -> List[str]:
        """Get list of failed ref IDs for retry."""
        return [r.ref_id for r in self.results if r.status == "failed"]

    def get_partial_refs(self) -> List[str]:
        """Get list of partial ref IDs for potential retry."""
        return [r.ref_id for r in self.results if r.status == "partial"]
