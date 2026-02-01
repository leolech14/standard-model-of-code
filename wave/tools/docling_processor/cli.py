#!/usr/bin/env python3
"""
Docling CLI - Command-line interface for batch PDF processing.

Commands:
    process       - Process PDFs (all or single file)
    resume        - Resume failed batch
    status        - Show processing status
    validate      - Validate installation
    export-chunks - Export chunks to Neo4j
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from .config import DoclingConfig, DEFAULT_CONFIG_PATH
from .processor import DoclingProcessor, validate_installation
from .output import BatchManifest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def cmd_validate(args):
    """Validate Docling installation."""
    print("Validating Docling installation...")
    print()

    ok, message = validate_installation()

    if ok:
        print("[OK] All dependencies available")
        print()

        # Test quick conversion
        print("Testing quick conversion...")
        config = DoclingConfig.load(Path(args.config) if args.config else None)
        processor = DoclingProcessor(config)

        # Find a small PDF to test
        test_pdfs = list(config.input_dir.glob("*.pdf"))
        if test_pdfs:
            smallest = min(test_pdfs, key=lambda p: p.stat().st_size)
            print(f"  Test file: {smallest.name} ({smallest.stat().st_size // 1024} KB)")

            try:
                # Just try to create the converter
                converter = processor._get_converter({})
                print("  [OK] DocumentConverter initialized")
            except Exception as e:
                print(f"  [WARN] Converter init failed: {e}")
        else:
            print("  No PDFs found in input directory")

        return 0
    else:
        print(f"[FAIL] {message}")
        return 1


def cmd_process(args):
    """Process PDFs."""
    config = DoclingConfig.load(Path(args.config) if args.config else None)

    # Override config from args
    if args.no_ocr:
        config.enable_ocr = False
    if args.no_tables:
        config.enable_table_structure = False
    if args.no_fallback:
        config.enable_fallbacks = False
    if args.threads:
        config.omp_num_threads = args.threads

    if not config.validate():
        return 1

    processor = DoclingProcessor(config)

    if args.file:
        # Single file mode
        pdf_path = Path(args.file)
        if not pdf_path.exists():
            print(f"File not found: {pdf_path}")
            return 1

        print(f"Processing single file: {pdf_path}")
        result = processor.process_single(pdf_path)

        print()
        print(f"Status: {result.status}")
        print(f"Strategy: {result.strategy_used}")
        print(f"Pages: {result.page_count}")
        print(f"Chunks: {result.chunk_count}")
        print(f"Time: {result.processing_time_seconds:.2f}s")

        if result.error_message:
            print(f"Error: {result.error_message}")

        if result.markdown_path:
            print(f"Markdown: {result.markdown_path}")
        if result.json_path:
            print(f"JSON: {result.json_path}")
        if result.chunks_path:
            print(f"Chunks: {result.chunks_path}")

        return 0 if result.status in ('success', 'partial') else 1

    else:
        # Batch mode
        print(f"Processing batch from: {config.input_dir}")
        print(f"Output to: {config.output_dir}")
        print()

        manifest = processor.process_batch()

        print()
        print("=== BATCH COMPLETE ===")
        print(f"Total: {manifest.total_files}")
        print(f"Successful: {manifest.successful}")
        print(f"Partial: {manifest.partial}")
        print(f"Failed: {manifest.failed}")
        print(f"Duration: {manifest.duration_seconds:.1f}s")
        print(f"Manifest: {config.output_dir / manifest.batch_id / 'manifest.json'}")

        return 0 if manifest.failed == 0 else 1


def cmd_resume(args):
    """Resume from failed batch."""
    config = DoclingConfig.load(Path(args.config) if args.config else None)

    batch_id = args.batch if args.batch else "latest"

    print(f"Resuming batch: {batch_id}")

    processor = DoclingProcessor(config)

    try:
        manifest = processor.process_batch(resume_from=batch_id)

        print()
        print("=== RESUME COMPLETE ===")
        print(f"Total: {manifest.total_files}")
        print(f"Successful: {manifest.successful}")
        print(f"Failed: {manifest.failed}")

        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1


def cmd_status(args):
    """Show processing status."""
    config = DoclingConfig.load(Path(args.config) if args.config else None)
    processor = DoclingProcessor(config)

    status = processor.get_status()

    print("=== DOCLING PROCESSOR STATUS ===")
    print()
    print(f"Input dir: {status['input_dir']}")
    print(f"Output dir: {status['output_dir']}")
    print(f"PDFs available: {status['pdf_count']}")
    print(f"Batches: {status['total_batches']}")
    print()

    if status['batches']:
        print("Recent batches:")
        for batch in sorted(status['batches'], key=lambda b: b.get('timestamp', ''), reverse=True)[:5]:
            if 'error' in batch:
                print(f"  {batch['batch_id']}: [ERROR] {batch['error']}")
            else:
                success_rate = batch.get('success_rate', 0) * 100
                print(f"  {batch['batch_id']}: {batch['successful']}/{batch['total_files']} ({success_rate:.0f}%)")

    return 0


def cmd_export_chunks(args):
    """Export chunks to Neo4j or file."""
    config = DoclingConfig.load(Path(args.config) if args.config else None)

    batch_id = args.batch if args.batch else "latest"

    # Load manifest
    if batch_id == "latest":
        latest_link = config.output_dir / "latest"
        if latest_link.is_symlink():
            batch_id = latest_link.resolve().name

    manifest_path = config.output_dir / batch_id / "manifest.json"
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}")
        return 1

    manifest = BatchManifest.load(manifest_path)

    print(f"Exporting chunks from batch: {batch_id}")
    print(f"Total results: {manifest.total_files}")

    # Collect all chunks
    all_chunks = []
    for result in manifest.results:
        if result.chunks_path and Path(result.chunks_path).exists():
            with open(result.chunks_path) as f:
                data = json.load(f)
                all_chunks.extend(data.get('chunks', []))

    print(f"Total chunks: {len(all_chunks)}")

    if args.publish_neo4j:
        # Try to publish to Neo4j
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "ai"))
            from aci.refinery.publishers.neo4j_publisher import Neo4jPublisher

            publisher = Neo4jPublisher()
            print("Publishing to Neo4j...")

            # Convert to RefineryNode format
            from aci.schema import RefineryNode
            nodes = []
            for chunk_data in all_chunks:
                node = RefineryNode(
                    content=chunk_data['content'],
                    source_file=chunk_data['source_file'],
                    chunk_id=chunk_data['chunk_id'],
                    chunk_type=chunk_data['chunk_type'],
                    relevance_score=chunk_data.get('relevance_score', 0.5),
                    metadata=chunk_data.get('metadata', {}),
                    waybill=chunk_data.get('waybill', {})
                )
                nodes.append(node)

            publisher.publish_atoms(nodes, batch_id, batch_id)
            print(f"Published {len(nodes)} chunks to Neo4j")

        except ImportError as e:
            print(f"Neo4j publisher not available: {e}")
            return 1
        except Exception as e:
            print(f"Failed to publish to Neo4j: {e}")
            return 1
    else:
        # Export to file
        output_file = config.output_dir / batch_id / "all_chunks.json"
        with open(output_file, 'w') as f:
            json.dump({
                "batch_id": batch_id,
                "chunk_count": len(all_chunks),
                "chunks": all_chunks
            }, f, indent=2)

        print(f"Exported to: {output_file}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Docling Batch PDF Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Validate installation
    python -m wave.tools.docling validate

    # Process single file
    python -m wave.tools.docling process --file paper.pdf

    # Process all PDFs
    python -m wave.tools.docling process

    # Resume failed batch
    python -m wave.tools.docling resume --batch latest

    # Check status
    python -m wave.tools.docling status

    # Export chunks
    python -m wave.tools.docling export-chunks --batch latest
        """
    )

    parser.add_argument('--config', type=str, help='Path to config YAML file')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # validate
    validate_parser = subparsers.add_parser('validate', help='Validate installation')

    # process
    process_parser = subparsers.add_parser('process', help='Process PDFs')
    process_parser.add_argument('--file', type=str, help='Process single file')
    process_parser.add_argument('--no-ocr', action='store_true', help='Disable OCR')
    process_parser.add_argument('--no-tables', action='store_true', help='Disable table structure')
    process_parser.add_argument('--no-fallback', action='store_true', help='Disable fallback strategies')
    process_parser.add_argument('--threads', type=int, help='Number of OMP threads')

    # resume
    resume_parser = subparsers.add_parser('resume', help='Resume failed batch')
    resume_parser.add_argument('--batch', type=str, default='latest', help='Batch ID to resume')

    # status
    status_parser = subparsers.add_parser('status', help='Show processing status')

    # export-chunks
    export_parser = subparsers.add_parser('export-chunks', help='Export chunks')
    export_parser.add_argument('--batch', type=str, default='latest', help='Batch ID')
    export_parser.add_argument('--publish-neo4j', action='store_true', help='Publish to Neo4j')

    args = parser.parse_args()

    if args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'process':
        return cmd_process(args)
    elif args.command == 'resume':
        return cmd_resume(args)
    elif args.command == 'status':
        return cmd_status(args)
    elif args.command == 'export-chunks':
        return cmd_export_chunks(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
