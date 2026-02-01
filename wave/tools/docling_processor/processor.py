#!/usr/bin/env python3
"""
DoclingProcessor - Main engine for batch PDF processing.

Features:
- Batch processing with progress tracking
- 4-tier fallback for problematic PDFs
- Waybill tracking for each parcel
- Resume capability from manifest
- Integration with Refinery chunking
"""

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from tqdm import tqdm

from .config import DoclingConfig
from .output import DoclingResult, BatchManifest
from .fallback import FallbackHandler, FallbackStrategy, create_fallback_handler
from .chunker import DoclingChunker, create_chunker

logger = logging.getLogger(__name__)


class DoclingProcessor:
    """
    Main PDF processing engine using IBM Docling.

    Usage:
        config = DoclingConfig.load()
        processor = DoclingProcessor(config)

        # Single file
        result = processor.process_single(Path("paper.pdf"))

        # Batch
        manifest = processor.process_batch()
    """

    def __init__(self, config: DoclingConfig):
        self.config = config
        self.fallback_handler = create_fallback_handler(config)
        self.chunker = create_chunker(config) if config.enable_chunking else None

        # Set OMP threads for performance
        os.environ['OMP_NUM_THREADS'] = str(config.omp_num_threads)

        # Lazy load Docling converter
        self._converter = None

    def _get_converter(self, options: Dict[str, Any] = None):
        """
        Lazy-load the Docling DocumentConverter with given options.

        Caches converter for reuse when options match.
        """
        try:
            from docling.document_converter import DocumentConverter, PdfFormatOption
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.datamodel.base_models import InputFormat
        except ImportError as e:
            raise RuntimeError(f"Docling not installed properly: {e}")

        options = options or {}

        # Configure pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = options.get('do_ocr', self.config.enable_ocr)
        pipeline_options.do_table_structure = options.get('do_table_structure', self.config.enable_table_structure)

        # Create converter with format options
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )

        return converter

    def extract_ref_id(self, pdf_path: Path) -> str:
        """
        Extract reference ID from filename.

        Handles formats:
        - REF-001_Author_Year_Title.pdf
        - AUTHOR_YEAR_Title.pdf
        - Anything else -> generate from filename
        """
        stem = pdf_path.stem

        # Check for REF-XXX pattern
        ref_match = re.match(r'(REF-\d+)', stem)
        if ref_match:
            return ref_match.group(1)

        # Check for AUTHOR_YEAR pattern
        author_year_match = re.match(r'([A-Z]+)_(\d{4})', stem)
        if author_year_match:
            return f"{author_year_match.group(1)}_{author_year_match.group(2)}"

        # Fallback: use sanitized filename
        clean = re.sub(r'[^\w\-]', '_', stem)[:30]
        return clean

    def process_single(
        self,
        pdf_path: Path,
        batch_id: Optional[str] = None
    ) -> DoclingResult:
        """
        Process a single PDF file.

        Args:
            pdf_path: Path to PDF file
            batch_id: Optional batch ID for waybill tracking

        Returns:
            DoclingResult with processing outcome
        """
        ref_id = self.extract_ref_id(pdf_path)
        parcel_id = f"pcl_{uuid.uuid4().hex[:12]}"

        result = DoclingResult(
            pdf_path=pdf_path,
            ref_id=ref_id,
            parcel_id=parcel_id
        )
        result.add_route_event("processing_started", "docling.processor.py", {
            "batch_id": batch_id
        })

        start_time = time.time()

        # Check page count limit
        if self.config.max_page_limit > 0:
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(pdf_path))
                page_count = len(reader.pages)
                if page_count > self.config.max_page_limit:
                    result.status = "failed"
                    result.error_message = f"Skipped: {page_count} pages exceeds limit of {self.config.max_page_limit}"
                    result.page_count = page_count
                    result.processing_time_seconds = time.time() - start_time
                    result.add_route_event("skipped_page_limit", "docling.processor.py", {
                        "page_count": page_count,
                        "limit": self.config.max_page_limit
                    })
                    logger.warning(f"Skipping {pdf_path}: {page_count} pages exceeds limit {self.config.max_page_limit}")
                    return result
            except Exception as e:
                logger.warning(f"Could not check page count for {pdf_path}: {e}")

        # Define the processing function for fallback handler
        def process_with_options(path: str, opts: Dict) -> Any:
            # Handle chunked mode - process all pages in chunks
            if opts.get('chunked_mode'):
                return self._process_chunked(path, opts)

            converter = self._get_converter(opts)
            doc_result = converter.convert(path)
            return doc_result.document

        try:
            # Use fallback handler
            fallback_result = self.fallback_handler.try_with_fallback(
                str(pdf_path),
                process_with_options
            )

            result.processing_time_seconds = time.time() - start_time

            if not fallback_result.success:
                result.status = "failed"
                result.error_message = fallback_result.error
                result.add_route_event("processing_failed", "docling.processor.py", {
                    "error": fallback_result.error,
                    "attempts": fallback_result.attempts
                })
                return result

            # Success or partial
            docling_doc = fallback_result.result
            result.strategy_used = fallback_result.strategy.value

            # Determine if partial (fallback was used)
            if fallback_result.strategy != FallbackStrategy.STANDARD:
                result.status = "partial"
            else:
                result.status = "success"

            # Get page count
            if hasattr(docling_doc, 'pages'):
                result.page_count = len(docling_doc.pages)

            # Export outputs
            self._export_result(result, docling_doc, batch_id)

            result.add_route_event("processing_completed", "docling.processor.py", {
                "strategy": result.strategy_used,
                "page_count": result.page_count,
                "chunk_count": result.chunk_count
            })

            return result

        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)
            result.processing_time_seconds = time.time() - start_time
            result.add_route_event("processing_error", "docling.processor.py", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            logger.error(f"Failed to process {pdf_path}: {e}")
            return result

    def _export_result(
        self,
        result: DoclingResult,
        docling_doc: Any,
        batch_id: Optional[str] = None
    ):
        """Export processed document to configured formats."""
        # Determine output directory
        if batch_id:
            output_dir = self.config.output_dir / batch_id / result.status
        else:
            output_dir = self.config.output_dir / "single" / result.ref_id

        output_dir.mkdir(parents=True, exist_ok=True)

        # Export markdown
        if self.config.export_markdown:
            try:
                md_content = docling_doc.export_to_markdown()
                md_path = output_dir / f"{result.ref_id}.md"
                self._atomic_write(md_path, md_content)
                result.markdown_path = md_path
            except Exception as e:
                logger.warning(f"Failed to export markdown for {result.ref_id}: {e}")

        # Export JSON (DocTags)
        if self.config.export_json:
            try:
                json_content = docling_doc.export_to_dict()
                json_path = output_dir / f"{result.ref_id}.json"
                self._atomic_write(json_path, json.dumps(json_content, indent=2))
                result.json_path = json_path
            except Exception as e:
                logger.warning(f"Failed to export JSON for {result.ref_id}: {e}")

        # Generate chunks
        if self.config.export_chunks and self.chunker and result.markdown_path:
            try:
                md_content = result.markdown_path.read_text(encoding='utf-8')
                chunks = self.chunker.chunk_markdown(
                    md_content,
                    str(result.pdf_path),
                    result.ref_id,
                    result.parcel_id,
                    batch_id
                )
                result.chunk_count = len(chunks)

                # Save chunks
                chunks_path = output_dir / f"{result.ref_id}_chunks.json"
                chunks_data = {
                    "ref_id": result.ref_id,
                    "parcel_id": result.parcel_id,
                    "chunk_count": len(chunks),
                    "chunks": [c.to_dict() for c in chunks]
                }
                self._atomic_write(chunks_path, json.dumps(chunks_data, indent=2))
                result.chunks_path = chunks_path

            except Exception as e:
                logger.warning(f"Failed to generate chunks for {result.ref_id}: {e}")

    def _atomic_write(self, path: Path, content: str):
        """Write file atomically (temp → verify → rename)."""
        temp_path = path.with_suffix(path.suffix + '.tmp')

        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Verify write succeeded
            with open(temp_path, 'r', encoding='utf-8') as f:
                _ = f.read()

            # Atomic rename
            temp_path.rename(path)

        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise

    def _process_chunked(self, path: str, opts: Dict) -> Any:
        """
        Process a large PDF in chunks, iterating through all pages.

        This is used when all other strategies fail, processing 20 pages
        at a time with minimal settings to handle problematic PDFs.
        """
        try:
            from pypdf import PdfReader
        except ImportError:
            try:
                from PyPDF2 import PdfReader
            except ImportError:
                logger.error("Neither pypdf nor PyPDF2 available for chunked processing")
                raise ImportError("pypdf or PyPDF2 required for chunked processing")

        reader = PdfReader(path)
        total_pages = len(reader.pages)
        chunk_size = 20

        logger.info(f"Chunked processing: {total_pages} pages in {chunk_size}-page chunks")

        # Remove chunked_mode flag for converter
        converter_opts = {k: v for k, v in opts.items() if k != 'chunked_mode'}

        combined_markdown = []
        combined_pages = []

        for start_page in range(0, total_pages, chunk_size):
            end_page = min(start_page + chunk_size, total_pages)
            logger.info(f"Processing pages {start_page + 1}-{end_page}")

            try:
                converter = self._get_converter(converter_opts)
                # Docling uses 0-indexed page ranges
                doc_result = converter.convert(path, page_range=(start_page, end_page))

                if doc_result.document:
                    md = doc_result.document.export_to_markdown()
                    combined_markdown.append(f"\n\n<!-- Pages {start_page + 1}-{end_page} -->\n\n{md}")

                    if hasattr(doc_result.document, 'pages'):
                        combined_pages.extend(doc_result.document.pages)

            except Exception as e:
                logger.warning(f"Chunk {start_page + 1}-{end_page} failed: {e}")
                combined_markdown.append(f"\n\n<!-- Pages {start_page + 1}-{end_page}: FAILED -->\n\n")

        # Create a combined result object
        class CombinedDocument:
            def __init__(self, markdown: str, pages: list):
                self._markdown = markdown
                self.pages = pages

            def export_to_markdown(self):
                return self._markdown

            def export_to_dict(self):
                return {"combined": True, "page_count": len(self.pages)}

        return CombinedDocument('\n'.join(combined_markdown), combined_pages)

    def process_batch(
        self,
        pdf_paths: Optional[List[Path]] = None,
        resume_from: Optional[str] = None
    ) -> BatchManifest:
        """
        Process a batch of PDFs.

        Args:
            pdf_paths: List of PDF paths (default: scan input_dir)
            resume_from: Batch ID to resume from (loads previous manifest)

        Returns:
            BatchManifest with all results
        """
        # Initialize manifest
        if resume_from:
            manifest = self._load_resume_manifest(resume_from)
            processed_refs = {r.ref_id for r in manifest.results}
        else:
            manifest = BatchManifest()
            manifest.config_used = self.config.to_dict()
            manifest.start_time = datetime.now().isoformat()
            processed_refs = set()

        # Get PDF list
        if pdf_paths is None:
            pdf_paths = list(self.config.input_dir.glob("*.pdf"))

        # Filter already processed
        pdf_paths = [p for p in pdf_paths if self.extract_ref_id(p) not in processed_refs]

        logger.info(f"Processing {len(pdf_paths)} PDFs (batch: {manifest.batch_id})")

        # Create batch output directory
        batch_dir = self.config.output_dir / manifest.batch_id
        batch_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (batch_dir / "successful").mkdir(exist_ok=True)
        (batch_dir / "partial").mkdir(exist_ok=True)
        (batch_dir / "failed").mkdir(exist_ok=True)
        (batch_dir / "metadata").mkdir(exist_ok=True)

        # Process with progress bar
        checkpoint_count = 0

        for pdf_path in tqdm(pdf_paths, desc="Processing PDFs"):
            try:
                result = self.process_single(pdf_path, manifest.batch_id)
                manifest.add_result(result)

                # Save waybill
                waybill_path = batch_dir / "metadata" / f"{result.ref_id}_waybill.json"
                self._atomic_write(waybill_path, json.dumps(result.waybill, indent=2))

                checkpoint_count += 1

                # Checkpoint every batch_size files
                if checkpoint_count >= self.config.batch_size:
                    manifest.save(batch_dir)
                    checkpoint_count = 0
                    logger.info(f"Checkpoint saved: {manifest.successful}/{manifest.total_files} successful")

            except Exception as e:
                if self.config.continue_on_error:
                    logger.error(f"Error processing {pdf_path}: {e}")
                    # Create failed result
                    result = DoclingResult(
                        pdf_path=pdf_path,
                        ref_id=self.extract_ref_id(pdf_path),
                        status="failed",
                        error_message=str(e)
                    )
                    manifest.add_result(result)
                else:
                    raise

        # Finalize
        manifest.end_time = datetime.now().isoformat()
        if manifest.start_time:
            start = datetime.fromisoformat(manifest.start_time)
            end = datetime.fromisoformat(manifest.end_time)
            manifest.duration_seconds = (end - start).total_seconds()

        # Save final manifest
        manifest.save(batch_dir)

        # Create/update "latest" symlink
        latest_link = self.config.output_dir / "latest"
        if latest_link.is_symlink():
            latest_link.unlink()
        elif latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(batch_dir.name)

        logger.info(f"Batch complete: {manifest.summary()}")
        return manifest

    def _load_resume_manifest(self, batch_id: str) -> BatchManifest:
        """Load manifest for resume."""
        if batch_id == "latest":
            latest_link = self.config.output_dir / "latest"
            if latest_link.is_symlink():
                batch_id = latest_link.resolve().name

        manifest_path = self.config.output_dir / batch_id / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"No manifest found at {manifest_path}")

        return BatchManifest.load(manifest_path)

    def get_status(self) -> Dict[str, Any]:
        """Get processing status for all batches."""
        batches = []

        for batch_dir in self.config.output_dir.iterdir():
            if not batch_dir.is_dir() or batch_dir.name == "latest":
                continue

            manifest_path = batch_dir / "manifest.json"
            if manifest_path.exists():
                try:
                    manifest = BatchManifest.load(manifest_path)
                    batches.append(manifest.summary())
                except Exception as e:
                    batches.append({
                        "batch_id": batch_dir.name,
                        "error": str(e)
                    })

        return {
            "total_batches": len(batches),
            "batches": batches,
            "input_dir": str(self.config.input_dir),
            "output_dir": str(self.config.output_dir),
            "pdf_count": len(list(self.config.input_dir.glob("*.pdf")))
        }


def validate_installation() -> Tuple[bool, str]:
    """Validate Docling installation."""
    issues = []
    warnings = []

    try:
        import docling
        _ = docling
    except ImportError:
        issues.append("docling package not installed")

    try:
        from docling.document_converter import DocumentConverter
        _ = DocumentConverter
    except ImportError:
        issues.append("docling.document_converter not available")

    try:
        import docling_ibm_models
        _ = docling_ibm_models
    except ImportError:
        issues.append("docling-ibm-models not installed")

    try:
        from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
        _ = HybridChunker
    except ImportError:
        warnings.append("HybridChunker not available (will use fallback chunking)")

    if issues:
        return False, "; ".join(issues)

    msg = "All core dependencies available"
    if warnings:
        msg += f" (warnings: {'; '.join(warnings)})"
    return True, msg
