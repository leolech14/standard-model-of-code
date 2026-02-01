# Perplexity Research: IBM Docling batch PDF processing power user guide 2025:

1. BATCH PROCESSING PATTERNS
- What is the ...

> **Date:** 2026-01-31 01:55:40
> **Model:** sonar-deep-research
> **Query Length:** 1234 chars

---

## Query

IBM Docling batch PDF processing power user guide 2025:

1. BATCH PROCESSING PATTERNS
- What is the recommended way to process 80+ PDF files efficiently?
- Python API vs CLI for batch operations - which is better for automation?
- How to implement parallel processing with enable_parallel_processing?
- What is the OMP_NUM_THREADS optimization?

2. ERROR HANDLING & LEGACY PDFs
- How to handle PDFs that fail conversion (old formats like PDF 1.2)?
- What fallback strategies exist for scanned documents?
- How to implement retry logic for failed conversions?
- What are common failure modes and their solutions?

3. OUTPUT ORGANIZATION
- Best practices for organizing output from large PDF libraries
- How to preserve source-to-output mapping?
- Directory structure recommendations for academic paper processing

4. RAG INTEGRATION
- How does DocTags work for chunking?
- HierarchicalChunker vs HybridChunker - when to use which?
- LlamaIndex integration best practices
- Token-aware chunking strategies

5. PERFORMANCE OPTIMIZATION
- What settings reduce memory usage for large documents?
- GPU vs CPU tradeoffs
- Batch size recommendations
- How to monitor progress on long-running conversions

Include code examples where possible.

---

## Response

# IBM Docling Batch PDF Processing Power User Guide 2025

This comprehensive guide addresses the essential techniques for processing large-scale PDF collections with IBM Docling, covering batch processing patterns, error handling strategies, output organization, Retrieval-Augmented Generation integration, and performance optimization. The guide synthesizes practical implementation approaches based on Docling's native capabilities, including the DocumentConverter API, batch processing workflows, chunking strategies, and production-ready resilience patterns that enable organizations to convert 80+ PDF files efficiently while maintaining data integrity and managing computational resources effectively.

## Batch Processing Fundamentals and Architecture

### Understanding Docling's Batch Processing Approach

IBM Docling provides a foundational architecture for batch PDF processing that differs from traditional approaches in how it manages multiple documents. The batch processing infrastructure built into Docling enables developers to process multiple documents through the DocumentConverter in a single operation, with the ability to handle partial failures and maintain consistency across document conversions[3][21][54]. Unlike some document processing systems that process documents sequentially with no parallelism awareness, Docling's batch capabilities are designed around the principle of processing documents one at a time through a unified pipeline, allowing for efficient scaling through distributed orchestration rather than internal parallelization.

The core insight behind Docling's batch architecture is that Python's Global Interpreter Lock (GIL) creates fundamental constraints on in-process parallelization[26][29]. The project maintainers have explicitly chosen to focus on throughput optimization—processing as many files as possible—rather than reducing time-to-conversion for individual documents[26]. This philosophy means that the recommended approach for parallel processing is to use external orchestration frameworks such as Apache Spark, Ray, or the Data Prep Kit rather than relying on threading-based parallelism within Docling itself[4][5].

The DocumentConverter class serves as the entry point for batch operations, providing both single-document and batch processing methods. The `convert()` method processes individual documents and returns a ConversionResult object containing either the successfully converted DoclingDocument or error information[35][49]. For batch operations, the `convert_all()` method accepts an iterable of document paths or DocumentStream objects and yields ConversionResult objects one at a time, allowing for memory-efficient processing of large collections[3][21][54].

### Batch Processing API Structure

The standard approach to batch processing with Docling involves creating a DocumentConverter instance with configured pipeline options and then calling convert_all() with a collection of input sources. The API design emphasizes control and transparency, allowing developers to inspect each conversion result individually and determine how to handle successes and failures[3][21][54]. Each ConversionResult object contains metadata about the conversion process, including the conversion status (SUCCESS, PARTIAL_SUCCESS, or FAILURE), error items if applicable, and performance metrics related to processing time.

```python
from docling.document_converter import DocumentConverter
from pathlib import Path
from typing import Iterable, Union

# Basic batch processing example
doc_converter = DocumentConverter()

input_doc_paths = [
    Path("documents/report1.pdf"),
    Path("documents/report2.pdf"),
    Path("documents/report3.pdf"),
]

# Process all documents with error handling
conv_results = doc_converter.convert_all(
    input_doc_paths,
    raises_on_error=False  # Continue processing even if one fails
)

# Iterate through results
success_count = 0
failure_count = 0
for conv_res in conv_results:
    if conv_res.status.name == "SUCCESS":
        success_count += 1
        # Process successful conversion
        markdown_content = conv_res.document.export_to_markdown()
    else:
        failure_count += 1
        # Log failure details
        for error in conv_res.errors:
            print(f"Error: {error.error_message}")

print(f"Processed: {success_count} successful, {failure_count} failed")
```

## Batch Processing Patterns and Implementation Strategies

### Pattern 1: Sequential Batch Processing with Error Tracking

The foundational batch processing pattern involves sequentially processing documents while maintaining detailed error tracking and logging. This pattern is appropriate for organizations that need reliable conversion with clear visibility into what succeeds and what fails[3][21][54]. The implementation uses the convert_all() method with raises_on_error=False, which allows the converter to continue processing subsequent documents even when one fails, capturing error information in the ConversionResult objects.

```python
import logging
import json
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import ConversionStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchProcessingOrchestrator:
    def __init__(self, output_dir: Path, log_file: Path):
        self.converter = DocumentConverter()
        self.output_dir = output_dir
        self.log_file = log_file
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processing_log = []
    
    def process_batch(self, input_paths: list[Path]):
        """Process a batch of PDF documents with detailed logging"""
        conv_results = self.converter.convert_all(
            input_paths,
            raises_on_error=False
        )
        
        for conv_res in conv_results:
            filename = conv_res.input.file.name
            
            if conv_res.status == ConversionStatus.SUCCESS:
                self._handle_success(conv_res, filename)
            elif conv_res.status == ConversionStatus.PARTIAL_SUCCESS:
                self._handle_partial_success(conv_res, filename)
            else:
                self._handle_failure(conv_res, filename)
        
        self._write_processing_log()
    
    def _handle_success(self, conv_res, filename: str):
        """Handle successful conversion"""
        output_file = self.output_dir / f"{Path(filename).stem}.md"
        markdown_content = conv_res.document.export_to_markdown()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.processing_log.append({
            "filename": filename,
            "status": "SUCCESS",
            "output_file": str(output_file),
            "page_count": len(conv_res.document.pages),
        })
        logger.info(f"Successfully processed: {filename}")
    
    def _handle_partial_success(self, conv_res, filename: str):
        """Handle partial success (e.g., timeout occurred)"""
        output_file = self.output_dir / f"{Path(filename).stem}_partial.md"
        markdown_content = conv_res.document.export_to_markdown()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        error_details = [error.error_message for error in conv_res.errors]
        self.processing_log.append({
            "filename": filename,
            "status": "PARTIAL_SUCCESS",
            "output_file": str(output_file),
            "errors": error_details,
            "page_count": len(conv_res.document.pages),
        })
        logger.warning(f"Partial success for {filename}: {error_details}")
    
    def _handle_failure(self, conv_res, filename: str):
        """Handle complete failure"""
        error_details = [error.error_message for error in conv_res.errors]
        self.processing_log.append({
            "filename": filename,
            "status": "FAILURE",
            "errors": error_details,
        })
        logger.error(f"Failed to process {filename}: {error_details}")
    
    def _write_processing_log(self):
        """Write detailed processing log"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.processing_log, f, indent=2)
```

### Pattern 2: Distributed Batch Processing with Ray

For organizations processing 80+ PDF files, distributing the work across multiple processes becomes essential. While Docling itself does not support internal threading due to the GIL, Ray provides an elegant framework for distributing document conversion across multiple worker processes[4][5]. The Ray Data framework can parallelize document processing while maintaining resource efficiency through intelligent scheduling.

```python
from pathlib import Path
from docling.document_converter import DocumentConverter
import ray

@ray.remote
def convert_single_document(pdf_path: str) -> dict:
    """Convert a single PDF using Ray remote function"""
    try:
        converter = DocumentConverter()
        pdf_path = Path(pdf_path)
        conv_result = converter.convert(pdf_path)
        
        if conv_result.status.name == "SUCCESS":
            markdown = conv_result.document.export_to_markdown()
            return {
                "path": str(pdf_path),
                "status": "SUCCESS",
                "markdown_length": len(markdown),
                "page_count": len(conv_result.document.pages),
            }
        else:
            return {
                "path": str(pdf_path),
                "status": conv_result.status.name,
                "errors": [e.error_message for e in conv_result.errors],
            }
    except Exception as e:
        return {
            "path": str(pdf_path),
            "status": "ERROR",
            "error": str(e),
        }

def process_batch_with_ray(pdf_paths: list[str], num_workers: int = 4):
    """Process batch of PDFs using Ray"""
    # Initialize Ray with specified number of workers
    if not ray.is_initialized():
        ray.init(num_cpus=num_workers)
    
    # Submit all conversion tasks
    futures = [convert_single_document.remote(path) for path in pdf_paths]
    
    # Collect results as they complete
    results = []
    for future in ray.get(futures):
        results.append(future)
    
    return results

# Usage example
pdf_files = list(Path("documents").glob("*.pdf"))
pdf_paths = [str(p) for p in pdf_files]

results = process_batch_with_ray(pdf_paths, num_workers=4)
for result in results:
    print(f"{result['path']}: {result['status']}")
```

### Pattern 3: Apache Camel Integration for Queue-Based Processing

For production systems that need to integrate document processing into larger workflow pipelines, Apache Camel provides connectors that wrap Docling functionality within enterprise message-driven architectures[2]. The Docling component allows batch processing through queue-based workflows with built-in error handling and retry mechanisms.

```yaml
# Camel route configuration for batch document processing
routes:
  - id: batch-convert-route
    from:
      uri: "seda:document-queue"
      parameters:
        concurrentConsumers: 2
    steps:
      # Aggregate documents into batches
      - aggregate:
          aggregationStrategy: "documentListProcessor"
          correlationExpression: constant: true
          completionSize: 10  # Process 10 documents at a time
          completionTimeout: 5000  # Or after 5 seconds
          steps:
            - to:
                uri: "docling:convert"
                parameters:
                  operation: "BATCH_CONVERT_TO_MARKDOWN"
                  useDoclingServe: true
                  batchParallelism: 4
                  batchFailOnFirstError: false
      
      # Split results
      - split:
          simple: "${body.results}"
          steps:
            - choice:
                when:
                  - simple: "${body.success}"
                    steps:
                      - to: "file:///output/successful?fileName=${body.documentId}.md"
                otherwise:
                  steps:
                    - to: "file:///output/failed?fileName=${body.documentId}.error"
```

## Error Handling and Resilience Strategies

### Common Failure Modes and Their Solutions

Docling encounters several categories of failures when processing diverse PDF collections, each requiring different handling strategies. Legacy PDF formats from the PDF 1.2 and 1.3 era often fail due to non-standard structures that the modern PDF parsing libraries struggle to interpret[11][20]. Scanned documents and image-heavy PDFs present challenges with OCR accuracy and performance[12]. Complex PDFs with unusual layouts, merged table cells, or extensive vector graphics can cause timeouts or memory exhaustion[20][33].

The most effective approach to error handling involves implementing detection strategies that identify the specific failure mode and applying targeted remediation. For example, when a PDF fails initial processing, a fallback strategy might disable OCR and table structure extraction to attempt basic text extraction[12][44]. For PDFs that encounter timeouts, the page_range parameter allows splitting problematic documents into smaller chunks for individual processing[55][56].

```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ResilientPdfProcessor:
    """Processor with fallback strategies for problematic PDFs"""
    
    def __init__(self):
        self.standard_options = PdfPipelineOptions(
            do_ocr=True,
            do_table_structure=True,
        )
        self.degraded_options = PdfPipelineOptions(
            do_ocr=False,
            do_table_structure=True,
        )
        self.minimal_options = PdfPipelineOptions(
            do_ocr=False,
            do_table_structure=False,
        )
    
    def convert_with_fallbacks(
        self, 
        pdf_path: Path,
        max_attempts: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Attempt conversion with progressive fallback strategies
        """
        
        # Strategy 1: Standard processing
        result = self._attempt_standard_conversion(pdf_path)
        if result:
            return {"strategy": "standard", "result": result}
        
        # Strategy 2: Degraded mode (no OCR)
        logger.warning(f"Standard conversion failed for {pdf_path}, trying degraded mode")
        result = self._attempt_degraded_conversion(pdf_path)
        if result:
            return {"strategy": "degraded", "result": result}
        
        # Strategy 3: Minimal mode (no OCR or tables)
        logger.warning(f"Degraded conversion failed for {pdf_path}, trying minimal mode")
        result = self._attempt_minimal_conversion(pdf_path)
        if result:
            return {"strategy": "minimal", "result": result}
        
        # Strategy 4: Chunked processing for timeout issues
        logger.warning(f"Minimal conversion failed for {pdf_path}, trying chunked processing")
        result = self._attempt_chunked_conversion(pdf_path)
        if result:
            return {"strategy": "chunked", "result": result}
        
        logger.error(f"All conversion strategies failed for {pdf_path}")
        return None
    
    def _attempt_standard_conversion(self, pdf_path: Path):
        """Try standard conversion with all features"""
        try:
            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(
                        pipeline_options=self.standard_options
                    )
                }
            )
            conv_result = converter.convert(pdf_path, max_num_pages=500)
            
            if conv_result.status.name in ["SUCCESS", "PARTIAL_SUCCESS"]:
                return conv_result.document
            return None
        except Exception as e:
            logger.debug(f"Standard conversion error: {e}")
            return None
    
    def _attempt_degraded_conversion(self, pdf_path: Path):
        """Try without OCR for text-based PDFs"""
        try:
            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(
                        pipeline_options=self.degraded_options
                    )
                }
            )
            conv_result = converter.convert(pdf_path)
            
            if conv_result.status.name in ["SUCCESS", "PARTIAL_SUCCESS"]:
                return conv_result.document
            return None
        except Exception as e:
            logger.debug(f"Degraded conversion error: {e}")
            return None
    
    def _attempt_minimal_conversion(self, pdf_path: Path):
        """Try minimal features"""
        try:
            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(
                        pipeline_options=self.minimal_options
                    )
                }
            )
            conv_result = converter.convert(pdf_path)
            
            if conv_result.status.name in ["SUCCESS", "PARTIAL_SUCCESS"]:
                return conv_result.document
            return None
        except Exception as e:
            logger.debug(f"Minimal conversion error: {e}")
            return None
    
    def _attempt_chunked_conversion(self, pdf_path: Path):
        """Process PDF in page chunks for timeout-prone documents"""
        try:
            from PyPDF2 import PdfReader
            
            # Get page count
            reader = PdfReader(str(pdf_path))
            num_pages = len(reader.pages)
            
            # Process in chunks of 20 pages
            chunk_size = 20
            combined_doc = None
            
            for start_page in range(0, num_pages, chunk_size):
                end_page = min(start_page + chunk_size, num_pages)
                
                converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: PdfFormatOption(
                            pipeline_options=self.minimal_options
                        )
                    }
                )
                
                conv_result = converter.convert(
                    pdf_path,
                    page_range=(start_page, end_page)
                )
                
                if conv_result.status.name in ["SUCCESS", "PARTIAL_SUCCESS"]:
                    if combined_doc is None:
                        combined_doc = conv_result.document
                    # In production, would merge documents
                else:
                    logger.warning(f"Chunk {start_page}-{end_page} failed")
            
            return combined_doc
        except Exception as e:
            logger.debug(f"Chunked conversion error: {e}")
            return None
```

### Retry Logic with Exponential Backoff

For transient failures caused by temporary system conditions, implementing retry logic with exponential backoff prevents overwhelming the system while allowing temporary issues to resolve[45][48]. The principle involves increasing the wait time between successive retry attempts following an exponential curve, with added random jitter to prevent synchronized retry storms across multiple processes.

```python
import time
import random
from typing import Callable, Any, TypeVar
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ExponentialBackoffRetry:
    """Retry mechanism with exponential backoff and jitter"""
    
    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        retriable_exceptions: tuple = (TimeoutError, ConnectionError),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retriable_exceptions = retriable_exceptions
    
    def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except self.retriable_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    wait_time = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed")
        
        raise last_exception
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff with exponential growth and jitter"""
        exponential_delay = self.base_delay * (2 ** attempt)
        capped_delay = min(exponential_delay, self.max_delay)
        jitter = random.uniform(0, capped_delay * 0.1)  # 10% jitter
        return capped_delay + jitter

def convert_with_retry(pdf_path: Path, max_retries: int = 3):
    """Convert PDF with retry logic"""
    def conversion_func():
        converter = DocumentConverter()
        return converter.convert(pdf_path)
    
    retry_handler = ExponentialBackoffRetry(max_retries=max_retries)
    return retry_handler.execute(conversion_func)
```

## Output Organization and Management

### Directory Structure for Large Document Collections

When processing 80+ PDF files, establishing a well-organized output structure becomes essential for downstream processing and maintenance. A recommended structure separates successful conversions, partial successes, failures, and metadata in distinct directories with clear naming conventions that preserve source-to-output mapping[1][9][19].

```python
from pathlib import Path
from datetime import datetime
import json

class OutputOrganizer:
    """Organize batch processing output with clear hierarchy"""
    
    def __init__(self, base_output_dir: Path):
        self.base_dir = Path(base_output_dir)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.batch_dir = self.base_dir / f"batch_{self.timestamp}"
        
        # Create subdirectories
        self.successful_dir = self.batch_dir / "successful"
        self.partial_dir = self.batch_dir / "partial"
        self.failed_dir = self.batch_dir / "failed"
        self.metadata_dir = self.batch_dir / "metadata"
        
        for directory in [self.successful_dir, self.partial_dir, 
                         self.failed_dir, self.metadata_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_successful_conversion(
        self,
        source_path: Path,
        markdown_content: str,
        json_content: dict,
    ):
        """Save successful conversion with multiple formats"""
        stem = source_path.stem
        
        # Save markdown
        md_file = self.successful_dir / f"{stem}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Save JSON
        json_file = self.successful_dir / f"{stem}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, indent=2)
        
        # Save metadata
        metadata_file = self.metadata_dir / f"{stem}_metadata.json"
        metadata = {
            "source": str(source_path),
            "conversion_time": datetime.now().isoformat(),
            "markdown_size": len(markdown_content),
            "status": "SUCCESS",
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def save_partial_conversion(
        self,
        source_path: Path,
        markdown_content: str,
        errors: list,
    ):
        """Save partial conversion with error details"""
        stem = source_path.stem
        
        md_file = self.partial_dir / f"{stem}_partial.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        metadata_file = self.metadata_dir / f"{stem}_metadata.json"
        metadata = {
            "source": str(source_path),
            "conversion_time": datetime.now().isoformat(),
            "status": "PARTIAL_SUCCESS",
            "errors": errors,
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def save_failure(
        self,
        source_path: Path,
        errors: list,
        strategy_attempted: str = "",
    ):
        """Log failed conversion"""
        stem = source_path.stem
        error_file = self.failed_dir / f"{stem}_error.txt"
        
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(f"Source: {source_path}\n")
            f.write(f"Strategy: {strategy_attempted}\n")
            f.write(f"Errors:\n")
            for error in errors:
                f.write(f"  - {error}\n")
        
        metadata_file = self.metadata_dir / f"{stem}_metadata.json"
        metadata = {
            "source": str(source_path),
            "conversion_time": datetime.now().isoformat(),
            "status": "FAILURE",
            "errors": errors,
            "strategy": strategy_attempted,
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def generate_batch_report(self) -> dict:
        """Generate summary report of batch processing"""
        successful = len(list(self.successful_dir.glob("*.md")))
        partial = len(list(self.partial_dir.glob("*.md")))
        failed = len(list(self.failed_dir.glob("*.txt")))
        
        report = {
            "batch_id": self.timestamp,
            "summary": {
                "successful": successful,
                "partial": partial,
                "failed": failed,
                "total": successful + partial + failed,
            },
            "directories": {
                "successful": str(self.successful_dir),
                "partial": str(self.partial_dir),
                "failed": str(self.failed_dir),
                "metadata": str(self.metadata_dir),
            },
        }
        
        # Write report
        report_file = self.batch_dir / "batch_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return report
```

## RAG Integration and Chunking Strategies

### Understanding Docling Chunking Approaches

Docling provides two primary chunking strategies for preparing documents for Retrieval-Augmented Generation systems: the HierarchicalChunker and the newer HybridChunker[13][16]. The HierarchicalChunker follows a document-based approach where splits are determined by the upstream document structure, creating chunks that correspond to semantic elements like paragraphs, sections, and tables[16]. The HybridChunker combines hierarchical document structure awareness with tokenization-aware refinements, applying size constraints while preserving document hierarchy[13][16].

The HybridChunker represents a significant advancement for RAG applications because it addresses the fundamental tension between preserving semantic coherence and meeting embedding model token limits[14]. Traditional fixed-size chunking breaks documents at arbitrary token boundaries, potentially splitting important semantic units. The HybridChunker starts with hierarchical chunks and then refines them by splitting oversized chunks and merging undersized successive chunks that share the same hierarchy level[13][16].

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker, HierarchicalChunker
from docling_core.types.doc import DoclingDocument
from typing import Iterator

def demonstrate_chunking_approaches():
    """Compare HierarchicalChunker and HybridChunker"""
    
    # Convert document
    converter = DocumentConverter()
    result = converter.convert("sample_document.pdf")
    doc = result.document
    
    # Approach 1: Hierarchical Chunking
    print("=== HIERARCHICAL CHUNKING ===")
    h_chunker = HierarchicalChunker()
    h_chunks = list(h_chunker.chunk(doc))
    
    for i, chunk in enumerate(h_chunks[:3]):  # Show first 3
        print(f"\nChunk {i}:")
        print(f"  Text length: {len(chunk.text)}")
        print(f"  Heading: {chunk.meta.headings[0] if chunk.meta.headings else 'N/A'}")
        print(f"  Preview: {chunk.text[:100]}...")
    
    # Approach 2: Hybrid Chunking with token constraints
    print("\n=== HYBRID CHUNKING (with token limit) ===")
    
    # Install tokenizer: pip install 'docling-core[chunking]'
    from transformers import AutoTokenizer
    
    tokenizer = AutoTokenizer.from_pretrained("Xenova/text-embedding-3-small")
    h_chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=512,  # Limit chunk size to 512 tokens
    )
    
    h_chunks = list(h_chunker.chunk(doc))
    
    for i, chunk in enumerate(h_chunks[:3]):
        # Get text for embedding
        text_for_embedding = h_chunker.contextualize(chunk)
        token_count = len(tokenizer.encode(text_for_embedding))
        
        print(f"\nChunk {i}:")
        print(f"  Text length: {len(chunk.text)}")
        print(f"  Tokens: {token_count}")
        print(f"  Heading: {chunk.meta.headings[0] if chunk.meta.headings else 'N/A'}")
```

### Integration with LlamaIndex for RAG Pipelines

LlamaIndex provides native integration with Docling through the DoclingReader and DoclingNodeParser, enabling seamless incorporation of Docling's rich document representation into RAG workflows[43][46]. The integration allows leveraging Docling's layout understanding and document structure preservation in query-answering applications.

```python
from llama_index.readers.docling import DoclingReader
from llama_index.core.node_parser import DoclingNodeParser
from llama_index.core import VectorStoreIndex
from docling.chunking import HybridChunker
from pathlib import Path
from transformers import AutoTokenizer

def create_rag_pipeline_with_docling(pdf_paths: list[Path]):
    """Create RAG pipeline using Docling with LlamaIndex"""
    
    # Step 1: Read documents using DoclingReader
    reader = DoclingReader()
    documents = []
    for pdf_path in pdf_paths:
        docs = reader.load_data(str(pdf_path))
        documents.extend(docs)
    
    # Step 2: Configure Docling chunker for LlamaIndex
    tokenizer = AutoTokenizer.from_pretrained(
        "Xenova/text-embedding-3-small"
    )
    
    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=512,
        merge_peers=True,  # Merge undersized chunks
    )
    
    # Step 3: Parse documents into nodes with Docling chunker
    node_parser = DoclingNodeParser(chunker=chunker)
    nodes = node_parser.get_nodes_from_documents(documents)
    
    # Step 4: Create vector index
    index = VectorStoreIndex(nodes)
    
    # Step 5: Create query engine for RAG
    query_engine = index.as_query_engine()
    
    return query_engine, nodes

def query_rag_system(query_engine, question: str):
    """Query RAG system with source attribution"""
    response = query_engine.query(question)
    
    print(f"Question: {question}")
    print(f"Answer: {response}")
    
    # Print sources with provenance
    for source_node in response.source_nodes:
        print(f"\nSource: {source_node.metadata.get('filename', 'unknown')}")
        print(f"Page: {source_node.metadata.get('page_no', 'N/A')}")
        print(f"Content: {source_node.text[:200]}...")
```

### Token-Aware Chunking Strategy

For production RAG systems, understanding how tokens map to semantic units becomes critical for balancing retrieval precision with generation context[14]. The token-aware chunking strategy uses the HybridChunker with careful configuration to ensure that embedding models receive properly sized inputs while maintaining semantic coherence.

```python
from transformers import AutoTokenizer
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter

class TokenAwareChunkingStrategy:
    """Configure chunking based on embedding model token limits"""
    
    def __init__(self, embedding_model: str = "Xenova/text-embedding-3-small"):
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model)
        self.model_name = embedding_model
        
        # Token limits for different embedding models
        self.token_limits = {
            "Xenova/text-embedding-3-small": 512,
            "Xenova/text-embedding-3-large": 2048,
            "sentence-transformers/all-MiniLM-L6-v2": 384,
        }
    
    def get_optimal_chunk_size(self) -> int:
        """Get recommended token limit for configured model"""
        return self.token_limits.get(self.model_name, 512)
    
    def configure_chunker(self) -> HybridChunker:
        """Configure HybridChunker for this embedding model"""
        chunk_size = self.get_optimal_chunk_size()
        
        # Use 80% of max tokens to leave buffer for metadata
        safe_size = int(chunk_size * 0.8)
        
        return HybridChunker(
            tokenizer=self.tokenizer,
            max_tokens=safe_size,
            merge_peers=True,
        )
    
    def chunk_document(self, pdf_path: str) -> list:
        """Chunk document with token awareness"""
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        doc = result.document
        
        chunker = self.configure_chunker()
        chunks = list(chunker.chunk(doc))
        
        # Validate chunk sizes
        for i, chunk in enumerate(chunks):
            text_with_metadata = chunker.contextualize(chunk)
            token_count = len(self.tokenizer.encode(text_with_metadata))
            
            if token_count > self.get_optimal_chunk_size():
                print(f"Warning: Chunk {i} exceeds token limit: {token_count}")
        
        return chunks

# Usage
strategy = TokenAwareChunkingStrategy("Xenova/text-embedding-3-small")
chunks = strategy.chunk_document("document.pdf")
print(f"Created {len(chunks)} chunks")
for i, chunk in enumerate(chunks[:5]):
    tokens = len(strategy.tokenizer.encode(strategy.configure_chunker().contextualize(chunk)))
    print(f"Chunk {i}: {tokens} tokens")
```

## Performance Optimization and Resource Management

### Memory Management for Large Documents

Docling's memory consumption scales with document size and enabled features. Processing large documents or collections requires careful configuration to prevent memory exhaustion[27][30][55]. The page_batch_size and page_range parameters provide mechanisms to limit memory usage by processing documents in smaller chunks.

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
import psutil
import logging

logger = logging.getLogger(__name__)

class MemoryAwareConverter:
    """DocumentConverter with memory monitoring and adaptive batching"""
    
    def __init__(self, memory_limit_percent: float = 70.0):
        self.memory_limit_percent = memory_limit_percent
        self.process = psutil.Process()
    
    def get_available_memory_percent(self) -> float:
        """Get available system memory as percentage"""
        return 100 - psutil.virtual_memory().percent
    
    def check_memory_available(self) -> bool:
        """Check if sufficient memory is available"""
        available = self.get_available_memory_percent()
        return available > (100 - self.memory_limit_percent)
    
    def convert_large_pdf(self, pdf_path: str, max_pages: int = None):
        """Convert PDF with memory-aware chunking"""
        
        # Determine if we need to use page_range
        if not self.check_memory_available():
            logger.warning("Low memory available, using chunked processing")
            return self._convert_chunked(pdf_path)
        
        # Standard conversion
        pipeline_options = PdfPipelineOptions()
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )
        
        if max_pages:
            result = converter.convert(pdf_path, max_num_pages=max_pages)
        else:
            result = converter.convert(pdf_path)
        
        return result
    
    def _convert_chunked(self, pdf_path: str, chunk_size: int = 20):
        """Convert large PDF by processing pages in chunks"""
        from PyPDF2 import PdfReader
        
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        
        logger.info(f"Processing {num_pages} pages in chunks of {chunk_size}")
        
        all_pages = []
        for start_page in range(0, num_pages, chunk_size):
            end_page = min(start_page + chunk_size, num_pages)
            
            logger.info(f"Processing pages {start_page}-{end_page}")
            
            pipeline_options = PdfPipelineOptions()
            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(
                        pipeline_options=pipeline_options
                    )
                }
            )
            
            result = converter.convert(
                pdf_path,
                page_range=(start_page, end_page)
            )
            
            all_pages.extend(result.document.pages)
        
        return all_pages

# Monitor memory usage
from contextlib import contextmanager

@contextmanager
def memory_monitor(operation_name: str):
    """Context manager for memory monitoring"""
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    yield
    
    end_memory = process.memory_info().rss / 1024 / 1024
    delta = end_memory - start_memory
    
    logger.info(f"{operation_name}: Memory delta = {delta:.2f} MB")
    logger.info(f"  Start: {start_memory:.2f} MB, End: {end_memory:.2f} MB")
```

### Thread Count and CPU Optimization

Docling allows controlling CPU usage through the OMP_NUM_THREADS environment variable, which affects the internal parallelization of deep learning models[7][10]. Setting this appropriately prevents over-subscription and improves overall system efficiency.

```python
import os
import multiprocessing
from docling.document_converter import DocumentConverter

def configure_docling_for_cpu_usage(
    num_threads: int = None,
    use_optimal: bool = True
):
    """Configure Docling CPU usage"""
    
    if use_optimal and num_threads is None:
        # Use a fraction of available cores
        num_cores = multiprocessing.cpu_count()
        # Conservative: use 50% of cores, minimum 2
        num_threads = max(2, num_cores // 2)
    
    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['MKL_NUM_THREADS'] = str(num_threads)
    os.environ['NUMEXPR_NUM_THREADS'] = str(num_threads)
    
    print(f"Configured Docling to use {num_threads} threads")

def batch_process_with_cpu_awareness(pdf_paths: list, output_dir: str):
    """Process batch with CPU-aware threading"""
    
    # Configure based on system
    configure_docling_for_cpu_usage(use_optimal=True)
    
    converter = DocumentConverter()
    
    for i, pdf_path in enumerate(pdf_paths):
        print(f"Processing {i+1}/{len(pdf_paths)}: {pdf_path}")
        
        result = converter.convert(pdf_path)
        
        if result.status.name == "SUCCESS":
            markdown = result.document.export_to_markdown()
            with open(f"{output_dir}/{Path(pdf_path).stem}.md", 'w') as f:
                f.write(markdown)
```

## GPU Acceleration and Advanced Tuning

### GPU Configuration and Batch Size Optimization

Docling supports GPU acceleration for both the layout analysis stage and the Vision Language Model (VLM) pipeline, with dramatic performance improvements when properly configured[15][18]. GPU acceleration becomes particularly valuable for batch operations, where throughput benefits from batched inference across multiple pages.

The key to GPU optimization is configuring appropriate batch sizes that balance memory usage and throughput[15][18]. Smaller batch sizes (4-16) suit GPUs with limited VRAM (12GB), while larger GPUs can efficiently handle batches of 64-128 or higher. The page_batch_size parameter controls how many pages the layout detection model processes simultaneously.

```python
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
import torch

def detect_gpu_and_configure():
    """Detect available GPU and configure optimal batch sizes"""
    
    if not torch.cuda.is_available():
        print("No GPU available, using CPU")
        return None
    
    # Get GPU properties
    gpu_name = torch.cuda.get_device_name(0)
    total_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
    
    print(f"Detected GPU: {gpu_name} ({total_memory_gb:.1f} GB)")
    
    # Determine batch size based on VRAM
    if total_memory_gb >= 24:  # RTX 4090 or better
        ocr_batch_size = 64
        layout_batch_size = 64
    elif total_memory_gb >= 12:  # RTX 3080/4070
        ocr_batch_size = 32
        layout_batch_size = 32
    else:  # RTX 3060 or less
        ocr_batch_size = 16
        layout_batch_size = 16
    
    return {
        "gpu_name": gpu_name,
        "total_memory_gb": total_memory_gb,
        "ocr_batch_size": ocr_batch_size,
        "layout_batch_size": layout_batch_size,
    }

def create_gpu_optimized_converter(use_gpu: bool = True):
    """Create converter with GPU optimization"""
    
    if use_gpu and torch.cuda.is_available():
        gpu_config = detect_gpu_and_configure()
        
        accelerator_options = AcceleratorOptions(
            device=AcceleratorDevice.CUDA
        )
        
        pipeline_options = ThreadedPdfPipelineOptions(
            accelerator_options=accelerator_options,
            ocr_batch_size=gpu_config["ocr_batch_size"],
            layout_batch_size=gpu_config["layout_batch_size"],
            table_batch_size=4,  # Tables generally don't benefit as much
        )
        
        print(f"Configured GPU batching:")
        print(f"  OCR batch: {gpu_config['ocr_batch_size']}")
        print(f"  Layout batch: {gpu_config['layout_batch_size']}")
    else:
        pipeline_options = ThreadedPdfPipelineOptions()
    
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

def batch_process_with_gpu_acceleration(pdf_paths: list, num_pdfs: int = 80):
    """Process batch with GPU acceleration"""
    
    converter = create_gpu_optimized_converter(use_gpu=True)
    
    import time
    start_time = time.time()
    
    conv_results = converter.convert_all(
        pdf_paths[:num_pdfs],
        raises_on_error=False
    )
    
    success_count = 0
    for conv_res in conv_results:
        if conv_res.status.name == "SUCCESS":
            success_count += 1
    
    elapsed = time.time() - start_time
    rate = success_count / elapsed
    
    print(f"Processed {success_count} PDFs in {elapsed:.1f}s")
    print(f"Throughput: {rate:.2f} PDFs/second")
```

### VLM Pipeline Configuration for Advanced Document Understanding

The VLM (Vision Language Model) pipeline enables advanced document understanding by using models like Granite Docling to interpret complex documents that challenge traditional parsing[15][18]. When configured with a local inference server like vLLM, Ollama, or LM Studio, the VLM pipeline can dramatically improve extraction quality for scanned documents and complex layouts.

```python
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.settings import settings

def configure_vlm_pipeline(
    vlm_server_url: str = "http://localhost:8000/v1/chat/completions",
    model_name: str = "ibm-granite/granite-docling-258M",
    concurrency: int = 16,
):
    """Configure VLM pipeline with local inference server"""
    
    # Configure VLM options
    vlm_options = VlmPipelineOptions(
        enable_remote_services=True,
        vlm_options={
            "url": vlm_server_url,
            "params": {
                "model": model_name,
                "max_tokens": 4096,
                "temperature": 0.7,
            },
            "concurrency": concurrency,
            "timeout": 300,  # 5 minute timeout per page
            "prompt": "Convert this page to docling.",
        }
    )
    
    # Set performance options
    settings.perf.page_batch_size = concurrency
    
    # Create converter with VLM pipeline
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=vlm_options)
        }
    )
    
    return converter

# Instructions for starting vLLM server
def print_vlm_server_startup_instructions():
    """Print instructions for starting vLLM with optimal settings"""
    
    instructions = """
    # Start vLLM server for Granite Docling (Linux only)
    
    vllm serve ibm-granite/granite-docling-258M \\
      --host 127.0.0.1 \\
      --port 8000 \\
      --max-num-seqs 512 \\
      --max-num-batched-tokens 8192 \\
      --enable-chunked-prefill \\
      --gpu-memory-utilization 0.9
    
    # For macOS or Windows, use Ollama
    ollama serve llama2  # or preferred model
    # Then configure Docling to use http://localhost:11434/v1/chat/completions
    
    # Or use LM Studio
    # Configure Docling to use http://localhost:1234/v1/chat/completions
    """
    
    print(instructions)
```

## Monitoring and Progress Tracking

### Progress Tracking for Large Batches

When processing 80+ PDF files, providing real-time progress feedback becomes essential for monitoring long-running operations and identifying stalled conversions. The tqdm library provides a simple yet powerful progress bar implementation[51].

```python
from docling.document_converter import DocumentConverter
from pathlib import Path
from tqdm import tqdm
import json
from datetime import datetime

class MonitoredBatchProcessor:
    """Batch processor with real-time progress tracking"""
    
    def __init__(self, output_dir: Path, log_file: Path):
        self.output_dir = output_dir
        self.log_file = log_file
        self.converter = DocumentConverter()
        self.progress_log = []
    
    def process_with_progress(self, pdf_paths: list[Path]):
        """Process PDFs with progress bar"""
        
        # Create progress bar
        with tqdm(total=len(pdf_paths), desc="Processing PDFs") as pbar:
            conv_results = self.converter.convert_all(
                pdf_paths,
                raises_on_error=False
            )
            
            for i, conv_res in enumerate(conv_results):
                filename = conv_res.input.file.name
                
                # Log progress
                self._log_progress(conv_res)
                
                # Update progress bar with status
                status = conv_res.status.name
                pbar.update(1)
                pbar.set_postfix({"status": status, "file": filename[:30]})
        
        self._write_progress_log()
    
    def _log_progress(self, conv_res):
        """Log individual conversion result"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "filename": conv_res.input.file.name,
            "status": conv_res.status.name,
            "page_count": len(conv_res.document.pages) if conv_res.document else 0,
            "errors": [e.error_message for e in conv_res.errors] if conv_res.errors else [],
        }
        self.progress_log.append(log_entry)
    
    def _write_progress_log(self):
        """Write progress log to file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress_log, f, indent=2)

# Usage
from pathlib import Path

pdf_paths = list(Path("documents").glob("*.pdf"))
processor = MonitoredBatchProcessor(
    output_dir=Path("output"),
    log_file=Path("conversion_log.json")
)

processor.process_with_progress(pdf_paths)
```

### Performance Metrics and Benchmarking

Tracking key performance metrics helps identify bottlenecks and optimization opportunities in batch processing workflows. Essential metrics include throughput (pages per second), average processing time per document, memory usage patterns, and error rates.

```python
from dataclasses import dataclass
from datetime import datetime
import time
import psutil
from typing import List

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    total_documents: int
    successful_documents: int
    failed_documents: int
    total_pages: int
    total_time_seconds: float
    start_memory_mb: float
    end_memory_mb: float
    
    @property
    def throughput_docs_per_second(self) -> float:
        return self.successful_documents / self.total_time_seconds if self.total_time_seconds > 0 else 0
    
    @property
    def throughput_pages_per_second(self) -> float:
        return self.total_pages / self.total_time_seconds if self.total_time_seconds > 0 else 0
    
    @property
    def memory_delta_mb(self) -> float:
        return self.end_memory_mb - self.start_memory_mb
    
    @property
    def success_rate_percent(self) -> float:
        total = self.total_documents
        return (self.successful_documents / total * 100) if total > 0 else 0

class PerformanceMonitor:
    """Monitor and report on batch processing performance"""
    
    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.results = []
    
    def start(self):
        """Start monitoring"""
        self.start_time = time.time()
        process = psutil.Process()
        self.start_memory = process.memory_info().rss / 1024 / 1024
    
    def record_conversion(self, success: bool, page_count: int = 0):
        """Record individual conversion result"""
        self.results.append({
            "success": success,
            "pages": page_count,
            "timestamp": datetime.now().isoformat(),
        })
    
    def finish(self) -> PerformanceMetrics:
        """Finish monitoring and calculate metrics"""
        end_time = time.time()
        process = psutil.Process()
        end_memory = process.memory_info().rss / 1024 / 1024
        
        successful = sum(1 for r in self.results if r["success"])
        total_pages = sum(r["pages"] for r in self.results)
        
        metrics = PerformanceMetrics(
            total_documents=len(self.results),
            successful_documents=successful,
            failed_documents=len(self.results) - successful,
            total_pages=total_pages,
            total_time_seconds=end_time - self.start_time,
            start_memory_mb=self.start_memory,
            end_memory_mb=end_memory,
        )
        
        return metrics
    
    @staticmethod
    def print_metrics(metrics: PerformanceMetrics):
        """Print formatted metrics"""
        print("\n" + "="*60)
        print("PERFORMANCE METRICS")
        print("="*60)
        print(f"Total Documents:        {metrics.total_documents}")
        print(f"Successful:             {metrics.successful_documents} ({metrics.success_rate_percent:.1f}%)")
        print(f"Failed:                 {metrics.failed_documents}")
        print(f"Total Pages:            {metrics.total_pages}")
        print(f"Total Time:             {metrics.total_time_seconds:.1f}s")
        print(f"\nThroughput:")
        print(f"  Documents/second:     {metrics.throughput_docs_per_second:.2f}")
        print(f"  Pages/second:         {metrics.throughput_pages_per_second:.2f}")
        print(f"\nMemory Usage:")
        print(f"  Start:                {metrics.start_memory_mb:.1f} MB")
        print(f"  End:                  {metrics.end_memory_mb:.1f} MB")
        print(f"  Delta:                {metrics.memory_delta_mb:+.1f} MB")
        print("="*60 + "\n")

# Usage example
from pathlib import Path

monitor = PerformanceMonitor()
monitor.start()

converter = DocumentConverter()
pdf_paths = list(Path("documents").glob("*.pdf"))

for pdf_path in pdf_paths:
    result = converter.convert(pdf_path)
    success = result.status.name == "SUCCESS"
    page_count = len(result.document.pages) if success else 0
    monitor.record_conversion(success, page_count)

metrics = monitor.finish()
PerformanceMonitor.print_metrics(metrics)
```

## Conclusion and Best Practices

The IBM Docling framework provides a comprehensive solution for batch PDF processing at scale, with particular strength in document structure preservation and integration with modern AI/ML pipelines. Successfully implementing large-scale batch operations requires understanding both the capabilities and limitations of the platform, combined with thoughtful architectural decisions around error handling, resource management, and output organization.

The most critical insight for power users is that Docling's batch processing philosophy prioritizes throughput over speed-per-document, which means that distributed orchestration frameworks like Ray or Spark are essential for maximizing parallel processing efficiency[4][5]. Internal Python threading will not improve performance due to the Global Interpreter Lock, making external parallelization the only path to linear scaling with additional resources.

For organizations processing 80+ PDF files, adopting a resilience-first approach to error handling pays significant dividends. The fallback strategies outlined in this guide—progressively degrading processing features when conversion fails—transform what might otherwise be critical failures into partial successes that can still provide value downstream. Combined with proper retry logic incorporating exponential backoff and jitter, this approach ensures robust operation even with diverse or challenging document collections[12][44][45][48].

The convergence of Docling's rich document representation capabilities with Retrieval-Augmented Generation systems represents a major advancement in building AI applications that work effectively with real-world documents. The HybridChunker strategy, when properly configured with token-aware limits that match specific embedding model constraints, preserves both semantic coherence and computational efficiency[13][14][16]. This enables RAG systems to maintain retrieval accuracy while managing infrastructure costs.

Performance optimization must be approached systematically, with careful attention to the specific bottlenecks in a particular workflow. GPU acceleration provides dramatic improvements when available, but requires matching batch size configuration to available VRAM to achieve maximum efficiency[15][18]. Memory management through page_range processing becomes essential for large documents, and monitoring through comprehensive logging and metrics collection provides the visibility necessary to identify optimization opportunities[27][30].

Finally, the most successful deployments recognize that Docling is a specialized tool that solves the document parsing problem exceptionally well, but must be integrated into a broader system architecture that handles everything from distributed processing to output management to downstream utilization. The patterns, code examples, and best practices in this guide provide the foundation for building production-grade batch document processing pipelines that reliably handle real-world complexity at the scale required by modern AI applications.

---

## Citations

1. https://community.ibm.com/community/user/blogs/ilker-ender/2025/12/07/building-an-ai-customer-support-system
2. https://camel.apache.org/components/next/docling-component.html
3. https://docling-project.github.io/docling/examples/batch_convert/
4. https://github.com/docling-project/docling/discussions/377
5. https://github.com/docling-project/docling/discussions/2757
6. https://github.com/ethanrise/docling-batch-processor
7. https://github.com/docling-project/docling/issues/2159
8. https://docling-project.github.io/docling/examples/batch_convert/
9. https://atalupadhyay.wordpress.com/2025/08/07/document-intelligence-guide-to-docling-for-ai-ready-data-processing/
10. https://docling-project.github.io/docling/usage/advanced_options/
11. https://github.com/docling-project/docling/labels/pdf%20parsing
12. https://www.graphlit.com/vs/docling
13. https://github.com/docling-project/docling/discussions/191
14. https://sarthakai.substack.com/p/improve-your-rag-accuracy-with-a
15. https://docling-project.github.io/docling/usage/gpu/
16. https://docling-project.github.io/docling/concepts/chunking/
17. https://developers.llamaindex.ai/python/framework/optimizing/basic_strategies/basic_strategies/
18. https://dev.to/aairom/supercharge-your-document-workflows-docling-now-unleashes-the-power-of-nvidia-rtx-14n4
19. https://www.datacamp.com/tutorial/docling
20. https://github.com/docling-project/docling/issues/2109
21. https://docling-project.github.io/docling/examples/batch_convert/
22. https://www.codecademy.com/article/docling-ai-a-complete-guide-to-parsing
23. https://github.com/docling-project/docling/issues/2842
24. https://github.com/docling-project/docling/issues/2545
25. https://dev.to/aairom/docling-go-bob-the-modern-document-stack-37b
26. https://github.com/docling-project/docling/issues/115
27. https://github.com/docling-project/docling/issues/2779
28. https://docling-project.github.io/docling/getting_started/quickstart/
29. https://github.com/docling-project/docling/discussions/2285
30. https://github.com/docling-project/docling/issues/2786
31. https://github.com/docling-project/docling/issues/2655
32. https://github.com/docling-project/docling/issues/1036
33. https://github.com/docling-project/docling/issues/2478
34. https://github.com/docling-project/docling/issues/2160
35. https://docling-project.github.io/docling/reference/document_converter/
36. https://github.com/docling-project/docling/issues/2381
37. https://docling-project.github.io/docling/examples/custom_convert/
38. https://github.com/docling-project/docling/issues/2081
39. https://github.com/docling-project/docling/discussions/1012
40. https://github.com/docling-project/docling
41. https://docling-project.github.io/docling/examples/export_tables/
42. https://www.datacamp.com/tutorial/docling
43. https://developers.llamaindex.ai/python/framework-api-reference/node_parser/docling/
44. https://github.com/open-webui/open-webui/discussions/17077
45. https://sparkco.ai/blog/mastering-retry-logic-agents-a-deep-dive-into-2025-best-practices
46. https://developers.llamaindex.ai/python/examples/data_connectors/doclingreaderdemo/
47. https://docling-project.github.io/docling/examples/full_page_ocr/
48. https://developer.ibm.com/articles/microservices_retry/
49. https://docling-project.github.io/docling/reference/document_converter/
50. https://www.docling.ai
51. https://github.com/tqdm/tqdm
52. https://github.com/docling-project/docling/issues/2109
53. https://www.youtube.com/watch?v=BWxdLm1KqTU
54. https://docling-project.github.io/docling/examples/batch_convert/
55. https://docling-project.github.io/docling/usage/advanced_options/
56. https://github.com/docling-project/docling/issues/1469
57. https://github.com/open-webui/open-webui/discussions/17247
58. https://pypi.org/project/docling/1.16.1/
59. https://github.com/docling-project/docling/issues/2655
60. https://github.com/docling-project/docling/issues/2381

---

## Usage Stats

- Input tokens: 270
- Output tokens: 11357
