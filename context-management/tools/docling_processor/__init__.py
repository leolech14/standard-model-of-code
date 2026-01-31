"""
Docling Batch Processor - Production-ready PDF processing for academic papers.

Tool ID: T054
Status: Working

Features:
- 4-tier fallback for problematic PDFs
- Parcel/Waybill tracking for logistics
- HybridChunker integration for RAG
- Batch processing with resume capability

Usage:
    from context_management.tools.docling_processor import DoclingProcessor, DoclingConfig

    config = DoclingConfig.load()
    processor = DoclingProcessor(config)
    manifest = processor.process_batch()

CLI:
    python -m context_management.tools.docling_processor process
    python -m context_management.tools.docling_processor status
"""

__version__ = "1.0.0"
__tool_id__ = "T054"

from .config import DoclingConfig
from .processor import DoclingProcessor, validate_installation
from .output import DoclingResult, BatchManifest
from .fallback import FallbackHandler, FallbackStrategy
from .chunker import DoclingChunker

__all__ = [
    "DoclingConfig",
    "DoclingProcessor",
    "DoclingResult",
    "BatchManifest",
    "FallbackHandler",
    "FallbackStrategy",
    "DoclingChunker",
    "validate_installation",
]
