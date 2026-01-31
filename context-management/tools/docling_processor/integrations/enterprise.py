"""
Enterprise Patterns for Docling Processor

Production-ready patterns: circuit breakers, retry logic, monitoring, distributed processing.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set, Optional, Callable, Any
from enum import Enum
from collections import deque
import threading

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Failures before opening
    recovery_timeout: int = 60          # Seconds before half-open
    success_threshold: int = 2          # Successes to close from half-open
    timeout_seconds: int = 300          # Request timeout


@dataclass
class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.

    Prevents cascading failures by stopping requests to failing services.

    Usage:
        breaker = CircuitBreaker()

        if breaker.can_execute("doc_001"):
            try:
                result = process_document("doc_001")
                breaker.record_success("doc_001")
            except Exception as e:
                breaker.record_failure("doc_001", str(e))
    """
    config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    _states: Dict[str, CircuitState] = field(default_factory=dict)
    _failures: Dict[str, int] = field(default_factory=dict)
    _successes: Dict[str, int] = field(default_factory=dict)
    _last_failure_time: Dict[str, datetime] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def can_execute(self, resource_id: str) -> bool:
        """Check if request should proceed."""
        with self._lock:
            state = self._states.get(resource_id, CircuitState.CLOSED)

            if state == CircuitState.CLOSED:
                return True

            if state == CircuitState.OPEN:
                # Check if recovery timeout elapsed
                last_failure = self._last_failure_time.get(resource_id)
                if last_failure:
                    elapsed = (datetime.now() - last_failure).total_seconds()
                    if elapsed >= self.config.recovery_timeout:
                        self._states[resource_id] = CircuitState.HALF_OPEN
                        self._successes[resource_id] = 0
                        logger.info(f"Circuit half-open for {resource_id}")
                        return True
                return False

            # HALF_OPEN - allow test requests
            return True

    def record_success(self, resource_id: str):
        """Record successful execution."""
        with self._lock:
            state = self._states.get(resource_id, CircuitState.CLOSED)

            if state == CircuitState.HALF_OPEN:
                self._successes[resource_id] = self._successes.get(resource_id, 0) + 1
                if self._successes[resource_id] >= self.config.success_threshold:
                    self._states[resource_id] = CircuitState.CLOSED
                    self._failures[resource_id] = 0
                    logger.info(f"Circuit closed for {resource_id}")

            elif state == CircuitState.CLOSED:
                # Reset failures on success
                self._failures[resource_id] = 0

    def record_failure(self, resource_id: str, error: str = ""):
        """Record failed execution."""
        with self._lock:
            state = self._states.get(resource_id, CircuitState.CLOSED)

            self._failures[resource_id] = self._failures.get(resource_id, 0) + 1
            self._last_failure_time[resource_id] = datetime.now()

            if state == CircuitState.HALF_OPEN:
                # Immediately open on failure during recovery
                self._states[resource_id] = CircuitState.OPEN
                logger.warning(f"Circuit re-opened for {resource_id}: {error}")

            elif state == CircuitState.CLOSED:
                if self._failures[resource_id] >= self.config.failure_threshold:
                    self._states[resource_id] = CircuitState.OPEN
                    logger.warning(f"Circuit opened for {resource_id}: {error}")

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        with self._lock:
            return {
                "states": {k: v.value for k, v in self._states.items()},
                "failures": dict(self._failures),
                "open_circuits": [k for k, v in self._states.items()
                                   if v == CircuitState.OPEN],
            }


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_retries: int = 3
    initial_delay: float = 1.0        # Seconds
    max_delay: float = 60.0           # Seconds
    exponential_base: float = 2.0
    jitter: float = 0.1               # Random jitter factor


class RetryHandler:
    """
    Exponential backoff retry handler.

    Usage:
        retry = RetryHandler()

        @retry.with_retry
        def process_document(path):
            return docling.convert(path)
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()

    def with_retry(self, func: Callable) -> Callable:
        """Decorator for retry logic."""
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = self.config.initial_delay

            for attempt in range(self.config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < self.config.max_retries:
                        # Add jitter
                        import random
                        jittered_delay = delay * (1 + random.uniform(-self.config.jitter, self.config.jitter))
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {jittered_delay:.1f}s"
                        )
                        time.sleep(jittered_delay)
                        delay = min(delay * self.config.exponential_base, self.config.max_delay)

            raise last_exception

        return wrapper


@dataclass
class ProcessingMetrics:
    """Metrics for monitoring document processing."""
    documents_processed: int = 0
    documents_failed: int = 0
    documents_skipped: int = 0
    total_pages: int = 0
    total_chunks: int = 0
    total_processing_time: float = 0.0
    errors: List[Dict[str, str]] = field(default_factory=list)
    _latencies: deque = field(default_factory=lambda: deque(maxlen=1000))

    def record_success(self, doc_id: str, pages: int, chunks: int, duration: float):
        """Record successful processing."""
        self.documents_processed += 1
        self.total_pages += pages
        self.total_chunks += chunks
        self.total_processing_time += duration
        self._latencies.append(duration)

    def record_failure(self, doc_id: str, error: str):
        """Record failed processing."""
        self.documents_failed += 1
        self.errors.append({
            "doc_id": doc_id,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })

    def record_skip(self, doc_id: str, reason: str):
        """Record skipped document."""
        self.documents_skipped += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        latencies = list(self._latencies)
        sorted_latencies = sorted(latencies) if latencies else [0]

        return {
            "documents_processed": self.documents_processed,
            "documents_failed": self.documents_failed,
            "documents_skipped": self.documents_skipped,
            "total_pages": self.total_pages,
            "total_chunks": self.total_chunks,
            "avg_processing_time": (
                self.total_processing_time / self.documents_processed
                if self.documents_processed > 0 else 0
            ),
            "p50_latency": sorted_latencies[len(sorted_latencies) // 2] if sorted_latencies else 0,
            "p95_latency": sorted_latencies[int(len(sorted_latencies) * 0.95)] if len(sorted_latencies) > 1 else 0,
            "p99_latency": sorted_latencies[int(len(sorted_latencies) * 0.99)] if len(sorted_latencies) > 1 else 0,
            "error_rate": (
                self.documents_failed / (self.documents_processed + self.documents_failed)
                if (self.documents_processed + self.documents_failed) > 0 else 0
            ),
            "recent_errors": self.errors[-10:],  # Last 10 errors
        }


@dataclass
class ProgressTracker:
    """
    Persistent progress tracking for resume capability.

    Usage:
        tracker = ProgressTracker("./progress.json")

        for doc in documents:
            if tracker.is_processed(doc):
                continue
            process(doc)
            tracker.mark_processed(doc)
            tracker.save()
    """
    progress_file: Path
    processed: Set[str] = field(default_factory=set)
    failed: Set[str] = field(default_factory=set)
    skipped: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.progress_file, str):
            self.progress_file = Path(self.progress_file)
        self.load()

    def load(self):
        """Load progress from file."""
        if self.progress_file.exists():
            try:
                data = json.loads(self.progress_file.read_text())
                self.processed = set(data.get("processed", []))
                self.failed = set(data.get("failed", []))
                self.skipped = set(data.get("skipped", []))
                self.metadata = data.get("metadata", {})
                logger.info(
                    f"Loaded progress: {len(self.processed)} processed, "
                    f"{len(self.failed)} failed"
                )
            except Exception as e:
                logger.warning(f"Could not load progress: {e}")

    def save(self):
        """Save progress to file."""
        data = {
            "processed": list(self.processed),
            "failed": list(self.failed),
            "skipped": list(self.skipped),
            "metadata": self.metadata,
            "last_updated": datetime.now().isoformat(),
        }
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.progress_file.write_text(json.dumps(data, indent=2))

    def is_processed(self, doc_id: str) -> bool:
        """Check if document was already processed."""
        return doc_id in self.processed

    def is_failed(self, doc_id: str) -> bool:
        """Check if document previously failed."""
        return doc_id in self.failed

    def mark_processed(self, doc_id: str):
        """Mark document as processed."""
        self.processed.add(doc_id)
        self.failed.discard(doc_id)

    def mark_failed(self, doc_id: str):
        """Mark document as failed."""
        self.failed.add(doc_id)

    def mark_skipped(self, doc_id: str):
        """Mark document as skipped."""
        self.skipped.add(doc_id)

    def get_pending(self, all_docs: List[str]) -> List[str]:
        """Get documents not yet processed."""
        return [d for d in all_docs
                if d not in self.processed and d not in self.skipped]


class BatchOrchestrator:
    """
    Orchestrator for enterprise batch processing.

    Combines circuit breaker, retry, metrics, and progress tracking.

    Usage:
        orchestrator = BatchOrchestrator(
            progress_file="./progress.json",
            metrics_callback=lambda m: print(m.get_stats())
        )

        results = orchestrator.process_batch(
            documents=["doc1.pdf", "doc2.pdf"],
            processor_fn=your_processor_function
        )
    """

    def __init__(
        self,
        progress_file: str = "processing_progress.json",
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        metrics_callback: Optional[Callable[[ProcessingMetrics], None]] = None,
        checkpoint_interval: int = 10,
    ):
        self.tracker = ProgressTracker(Path(progress_file))
        self.circuit_breaker = CircuitBreaker(
            config=circuit_breaker_config or CircuitBreakerConfig()
        )
        self.retry_handler = RetryHandler(retry_config)
        self.metrics = ProcessingMetrics()
        self.metrics_callback = metrics_callback
        self.checkpoint_interval = checkpoint_interval

    def process_batch(
        self,
        documents: List[str],
        processor_fn: Callable[[str], Dict[str, Any]],
        skip_failed: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a batch of documents with enterprise patterns.

        Args:
            documents: List of document paths/IDs
            processor_fn: Function that processes a single document
            skip_failed: Skip previously failed documents

        Returns:
            Processing results summary
        """
        pending = self.tracker.get_pending(documents)
        if skip_failed:
            pending = [d for d in pending if not self.tracker.is_failed(d)]

        logger.info(f"Processing {len(pending)} documents ({len(documents) - len(pending)} already done)")

        results = {"successful": [], "failed": [], "skipped": []}

        for i, doc_id in enumerate(pending):
            # Circuit breaker check
            if not self.circuit_breaker.can_execute(doc_id):
                self.metrics.record_skip(doc_id, "circuit_open")
                self.tracker.mark_skipped(doc_id)
                results["skipped"].append(doc_id)
                continue

            # Process with retry
            start_time = time.time()
            try:
                result = self.retry_handler.with_retry(processor_fn)(doc_id)
                duration = time.time() - start_time

                self.circuit_breaker.record_success(doc_id)
                self.metrics.record_success(
                    doc_id,
                    pages=result.get("pages", 0),
                    chunks=result.get("chunks", 0),
                    duration=duration
                )
                self.tracker.mark_processed(doc_id)
                results["successful"].append(doc_id)

            except Exception as e:
                error_str = str(e)
                self.circuit_breaker.record_failure(doc_id, error_str)
                self.metrics.record_failure(doc_id, error_str)
                self.tracker.mark_failed(doc_id)
                results["failed"].append(doc_id)
                logger.error(f"Failed to process {doc_id}: {error_str}")

            # Checkpoint
            if (i + 1) % self.checkpoint_interval == 0:
                self.tracker.save()
                if self.metrics_callback:
                    self.metrics_callback(self.metrics)
                logger.info(f"Checkpoint: {i + 1}/{len(pending)} processed")

        # Final save
        self.tracker.save()

        return {
            "summary": self.metrics.get_stats(),
            "results": results,
            "circuit_breaker": self.circuit_breaker.get_status(),
        }
