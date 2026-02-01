#!/usr/bin/env python3
"""
FallbackHandler - 4-tier progressive degradation for Docling processing.

Strategies (in order of attempt):
1. standard  - Full OCR + table structure recognition
2. no_ocr    - Tables only (for text-native PDFs)
3. minimal   - No OCR, no tables (basic text extraction)
4. chunked   - Process in 20-page chunks with minimal settings
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Any, Dict

logger = logging.getLogger(__name__)


class FallbackStrategy(Enum):
    """Processing strategies in order of fallback."""
    STANDARD = "standard"
    NO_OCR = "no_ocr"
    MINIMAL = "minimal"
    CHUNKED = "chunked"


# Strategy order for fallback progression
FALLBACK_ORDER = [
    FallbackStrategy.STANDARD,
    FallbackStrategy.NO_OCR,
    FallbackStrategy.MINIMAL,
    FallbackStrategy.CHUNKED
]


@dataclass
class FallbackResult:
    """Result of a fallback attempt."""
    success: bool
    strategy: FallbackStrategy
    result: Optional[Any] = None
    error: Optional[str] = None
    attempts: int = 0


class FallbackHandler:
    """
    Manages progressive fallback strategies for PDF processing.

    Usage:
        handler = FallbackHandler(enabled=True, max_retries=3)
        result = handler.try_with_fallback(
            pdf_path,
            process_func=lambda path, opts: docling_convert(path, **opts),
            get_options_func=lambda strategy: get_docling_options(strategy)
        )
    """

    def __init__(self, enabled: bool = True, max_retries: int = 3):
        self.enabled = enabled
        self.max_retries = max_retries
        self._current_strategy_index = 0

    def get_strategy_options(self, strategy: FallbackStrategy) -> Dict[str, Any]:
        """
        Get Docling options for a given strategy.

        Returns dict suitable for DocumentConverter initialization.
        """
        if strategy == FallbackStrategy.STANDARD:
            return {
                "do_ocr": True,
                "do_table_structure": True,
                "artifacts_path": None,  # Use default model cache
            }
        elif strategy == FallbackStrategy.NO_OCR:
            return {
                "do_ocr": False,
                "do_table_structure": True,
                "artifacts_path": None,
            }
        elif strategy == FallbackStrategy.MINIMAL:
            return {
                "do_ocr": False,
                "do_table_structure": False,
                "artifacts_path": None,
            }
        elif strategy == FallbackStrategy.CHUNKED:
            # Note: page_range is set dynamically per chunk in processor.py
            # This returns base options; chunked processing iterates all pages
            return {
                "do_ocr": False,
                "do_table_structure": False,
                "artifacts_path": None,
                "chunked_mode": True,  # Signal to processor to use iterative chunking
            }
        else:
            return self.get_strategy_options(FallbackStrategy.STANDARD)

    def try_with_fallback(
        self,
        pdf_path: str,
        process_func: Callable[[str, Dict], Any],
        start_strategy: Optional[FallbackStrategy] = None
    ) -> FallbackResult:
        """
        Try to process a PDF with progressive fallback.

        Args:
            pdf_path: Path to PDF file
            process_func: Function(path, options_dict) -> result
            start_strategy: Optional strategy to start from (for resume)

        Returns:
            FallbackResult with success status and result/error
        """
        if not self.enabled:
            # No fallback - try once with standard
            opts = self.get_strategy_options(FallbackStrategy.STANDARD)
            try:
                result = process_func(pdf_path, opts)
                return FallbackResult(
                    success=True,
                    strategy=FallbackStrategy.STANDARD,
                    result=result,
                    attempts=1
                )
            except Exception as e:
                return FallbackResult(
                    success=False,
                    strategy=FallbackStrategy.STANDARD,
                    error=str(e),
                    attempts=1
                )

        # Determine starting index
        start_index = 0
        if start_strategy:
            try:
                start_index = FALLBACK_ORDER.index(start_strategy)
            except ValueError:
                start_index = 0

        attempts = 0
        last_error = None

        for i, strategy in enumerate(FALLBACK_ORDER[start_index:], start=start_index):
            if attempts >= self.max_retries:
                break

            attempts += 1
            opts = self.get_strategy_options(strategy)

            logger.info(f"Trying strategy {strategy.value} for {pdf_path}")

            try:
                result = process_func(pdf_path, opts)
                logger.info(f"Success with strategy {strategy.value}")
                return FallbackResult(
                    success=True,
                    strategy=strategy,
                    result=result,
                    attempts=attempts
                )
            except MemoryError as e:
                last_error = f"MemoryError: {e}"
                logger.warning(f"Memory error with {strategy.value}, falling back...")
                continue
            except TimeoutError as e:
                last_error = f"TimeoutError: {e}"
                logger.warning(f"Timeout with {strategy.value}, falling back...")
                continue
            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                logger.warning(f"Error with {strategy.value}: {e}")

                # Some errors should not trigger fallback
                if "file not found" in str(e).lower():
                    return FallbackResult(
                        success=False,
                        strategy=strategy,
                        error=last_error,
                        attempts=attempts
                    )
                if "permission denied" in str(e).lower():
                    return FallbackResult(
                        success=False,
                        strategy=strategy,
                        error=last_error,
                        attempts=attempts
                    )

                continue

        # All strategies failed
        return FallbackResult(
            success=False,
            strategy=FALLBACK_ORDER[-1],  # Last attempted
            error=last_error or "All fallback strategies failed",
            attempts=attempts
        )

    def should_use_chunked(self, page_count: int, threshold: int = 100) -> bool:
        """Check if chunked processing is recommended based on page count."""
        return page_count > threshold

    def get_page_ranges(self, total_pages: int, chunk_size: int = 20) -> list:
        """
        Split a document into page ranges for chunked processing.

        Returns list of (start, end) tuples (1-indexed).
        """
        ranges = []
        for start in range(1, total_pages + 1, chunk_size):
            end = min(start + chunk_size - 1, total_pages)
            ranges.append((start, end))
        return ranges


def create_fallback_handler(config) -> FallbackHandler:
    """Create FallbackHandler from DoclingConfig."""
    return FallbackHandler(
        enabled=config.enable_fallbacks,
        max_retries=config.max_fallback_retries
    )
