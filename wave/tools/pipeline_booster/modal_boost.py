"""
Modal-specific Pipeline Booster

The EASIEST way to get GPU acceleration. Just 3 steps:
1. pip install modal
2. modal setup
3. Use @modal_boost decorator

Example:
    from pipeline_booster.modal_boost import modal_boost, docling_boost

    # Generic GPU boost
    @modal_boost(gpu="a100")
    def my_function(data):
        return process(data)

    # Pre-configured for Docling
    results = docling_boost(["doc1.pdf", "doc2.pdf"])
"""

import os
import logging
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)

# Check if Modal is available
try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    modal = None


def check_modal_setup() -> Dict[str, Any]:
    """Check if Modal is installed and configured."""
    result = {
        "installed": MODAL_AVAILABLE,
        "authenticated": False,
        "ready": False,
        "message": "",
    }

    if not MODAL_AVAILABLE:
        result["message"] = "Modal not installed. Run: pip install modal"
        return result

    if os.environ.get("MODAL_TOKEN_ID"):
        result["authenticated"] = True
        result["ready"] = True
        result["message"] = "Modal ready to use!"
    else:
        result["message"] = "Modal installed but not authenticated. Run: modal setup"

    return result


def modal_boost(
    gpu: str = "any",
    memory_gb: int = 16,
    timeout: int = 3600,
    image_packages: Optional[List[str]] = None,
) -> Callable:
    """
    Decorator to run a function on Modal with GPU.

    Args:
        gpu: GPU type ("any", "t4", "a100", "a10g", "h100")
        memory_gb: Memory in GB
        timeout: Timeout in seconds
        image_packages: Additional pip packages to install

    Example:
        @modal_boost(gpu="a100")
        def train_model(data):
            return model.train(data)
    """

    if not MODAL_AVAILABLE:
        def fallback_decorator(func):
            logger.warning("Modal not available, running locally")
            return func
        return fallback_decorator

    def decorator(func: Callable) -> Callable:
        # Create Modal app
        app = modal.App(f"boost-{func.__name__}")

        # Configure GPU
        gpu_config = {
            "any": modal.gpu.Any(),
            "t4": modal.gpu.T4(),
            "a10g": modal.gpu.A10G(),
            "a100": modal.gpu.A100(),
            "h100": modal.gpu.H100(),
        }.get(gpu.lower(), modal.gpu.Any())

        # Build image
        packages = ["torch", "numpy"]
        if image_packages:
            packages.extend(image_packages)

        image = modal.Image.debian_slim(python_version="3.11").pip_install(*packages)

        @app.function(
            gpu=gpu_config,
            image=image,
            timeout=timeout,
            memory=memory_gb * 1024,  # Convert to MB
        )
        def remote_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        def wrapper(*args, **kwargs):
            with app.run():
                return remote_wrapper.remote(*args, **kwargs)

        wrapper._modal_app = app
        wrapper._original_func = func

        return wrapper

    return decorator


# Pre-configured Docling booster
def create_docling_app():
    """Create a Modal app pre-configured for Docling."""

    if not MODAL_AVAILABLE:
        return None

    app = modal.App("docling-booster")

    # Docling-optimized image
    image = (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install("libgl1-mesa-glx", "libglib2.0-0")  # For OpenCV
        .pip_install(
            "docling>=2.71.0",
            "docling-core",
            "torch",
            "pypdf",
        )
    )

    return app, image


def docling_boost(
    pdf_paths: List[str],
    gpu: str = "a100",
    enable_ocr: bool = True,
    enable_tables: bool = True,
) -> List[Dict[str, Any]]:
    """
    Process PDFs with Docling on Modal GPU.

    Args:
        pdf_paths: List of PDF file paths
        gpu: GPU type to use
        enable_ocr: Enable OCR for scanned documents
        enable_tables: Enable table extraction

    Returns:
        List of processing results

    Example:
        results = docling_boost(["paper1.pdf", "paper2.pdf"])
        for r in results:
            print(r["markdown"][:500])
    """

    if not MODAL_AVAILABLE:
        logger.error("Modal not available. Install with: pip install modal && modal setup")
        raise ImportError("Modal required for docling_boost")

    app = modal.App("docling-boost")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install("libgl1-mesa-glx", "libglib2.0-0")
        .pip_install("docling>=2.71.0", "docling-core", "torch", "pypdf")
    )

    gpu_config = {
        "t4": modal.gpu.T4(),
        "a10g": modal.gpu.A10G(),
        "a100": modal.gpu.A100(),
    }.get(gpu.lower(), modal.gpu.A100())

    @app.function(gpu=gpu_config, image=image, timeout=3600)
    def process_pdf(pdf_content: bytes, filename: str, options: dict) -> dict:
        """Process a single PDF on Modal."""
        import tempfile
        from pathlib import Path

        # Write PDF to temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(pdf_content)
            temp_path = f.name

        try:
            from docling.document_converter import DocumentConverter
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.datamodel.base_models import InputFormat
            from docling.document_converter import PdfFormatOption

            # Configure pipeline
            pipeline_options = PdfPipelineOptions(
                do_ocr=options.get("enable_ocr", True),
                do_table_structure=options.get("enable_tables", True),
            )

            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )

            result = converter.convert(temp_path)
            doc = result.document

            return {
                "filename": filename,
                "status": "success",
                "markdown": doc.export_to_markdown(),
                "page_count": len(doc.pages) if hasattr(doc, 'pages') else 0,
            }

        except Exception as e:
            return {
                "filename": filename,
                "status": "error",
                "error": str(e),
            }

        finally:
            Path(temp_path).unlink(missing_ok=True)

    # Read PDFs and process
    results = []
    options = {"enable_ocr": enable_ocr, "enable_tables": enable_tables}

    with app.run():
        for pdf_path in pdf_paths:
            path = Path(pdf_path)
            if not path.exists():
                results.append({"filename": str(path), "status": "error", "error": "File not found"})
                continue

            pdf_content = path.read_bytes()
            result = process_pdf.remote(pdf_content, path.name, options)
            results.append(result)

    return results


# Quick setup helper
def quick_setup():
    """Print quick setup instructions."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           PIPELINE BOOSTER - QUICK SETUP                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Step 1: Install Modal                                       ║
║  $ pip install modal                                         ║
║                                                              ║
║  Step 2: Authenticate (opens browser)                        ║
║  $ modal setup                                               ║
║                                                              ║
║  Step 3: Use it!                                             ║
║  from pipeline_booster.modal_boost import docling_boost      ║
║  results = docling_boost(["doc.pdf"])                        ║
║                                                              ║
║  That's it! Your code now runs on A100 GPUs.                 ║
║                                                              ║
║  Cost: ~$0.001/second (first $30/month free)                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    status = check_modal_setup()
    print(f"Modal Status: {status}")
    if not status["ready"]:
        quick_setup()
