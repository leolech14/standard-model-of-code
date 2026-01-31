#!/usr/bin/env python3
"""
DoclingConfig - Configuration management for Docling batch processor.

Handles YAML config loading and provides sensible defaults.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any

import yaml


# Default paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DEFAULT_INPUT_DIR = PROJECT_ROOT / "context-management/library/references/pdf"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "context-management/library/references/docling_output"
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "context-management/config/docling_config.yaml"


@dataclass
class DoclingConfig:
    """Configuration for Docling batch processing."""

    # Paths
    input_dir: Path = field(default_factory=lambda: DEFAULT_INPUT_DIR)
    output_dir: Path = field(default_factory=lambda: DEFAULT_OUTPUT_DIR)

    # OCR and Table Settings
    enable_ocr: bool = True
    enable_table_structure: bool = True

    # Fallback behavior
    enable_fallbacks: bool = True
    max_fallback_retries: int = 3

    # Chunking for RAG
    enable_chunking: bool = True
    chunk_max_tokens: int = 512
    chunk_overlap_tokens: int = 50

    # Performance
    omp_num_threads: int = 4
    batch_size: int = 10  # Process N files before checkpoint

    # Error handling
    continue_on_error: bool = True
    max_page_limit: int = 500  # Skip files with more pages

    # Output options
    export_markdown: bool = True
    export_json: bool = True
    export_chunks: bool = True

    @classmethod
    def from_yaml(cls, config_path: Path) -> "DoclingConfig":
        """Load configuration from YAML file."""
        if not config_path.exists():
            return cls()

        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}

        # Convert path strings to Path objects
        if 'input_dir' in data:
            data['input_dir'] = Path(data['input_dir'])
        if 'output_dir' in data:
            data['output_dir'] = Path(data['output_dir'])

        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})

    @classmethod
    def from_env(cls) -> "DoclingConfig":
        """Load configuration from environment variables."""
        config = cls()

        if os.environ.get('DOCLING_INPUT_DIR'):
            config.input_dir = Path(os.environ['DOCLING_INPUT_DIR'])
        if os.environ.get('DOCLING_OUTPUT_DIR'):
            config.output_dir = Path(os.environ['DOCLING_OUTPUT_DIR'])
        if os.environ.get('DOCLING_ENABLE_OCR'):
            config.enable_ocr = os.environ['DOCLING_ENABLE_OCR'].lower() == 'true'
        if os.environ.get('OMP_NUM_THREADS'):
            config.omp_num_threads = int(os.environ['OMP_NUM_THREADS'])

        return config

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "DoclingConfig":
        """Load config from YAML if exists, then overlay env vars."""
        path = config_path or DEFAULT_CONFIG_PATH

        # Start with YAML config or defaults
        if path.exists():
            config = cls.from_yaml(path)
        else:
            config = cls()

        # Overlay environment variables
        if os.environ.get('DOCLING_INPUT_DIR'):
            config.input_dir = Path(os.environ['DOCLING_INPUT_DIR'])
        if os.environ.get('DOCLING_OUTPUT_DIR'):
            config.output_dir = Path(os.environ['DOCLING_OUTPUT_DIR'])
        if os.environ.get('OMP_NUM_THREADS'):
            config.omp_num_threads = int(os.environ['OMP_NUM_THREADS'])

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            'input_dir': str(self.input_dir),
            'output_dir': str(self.output_dir),
            'enable_ocr': self.enable_ocr,
            'enable_table_structure': self.enable_table_structure,
            'enable_fallbacks': self.enable_fallbacks,
            'max_fallback_retries': self.max_fallback_retries,
            'enable_chunking': self.enable_chunking,
            'chunk_max_tokens': self.chunk_max_tokens,
            'chunk_overlap_tokens': self.chunk_overlap_tokens,
            'omp_num_threads': self.omp_num_threads,
            'batch_size': self.batch_size,
            'continue_on_error': self.continue_on_error,
            'max_page_limit': self.max_page_limit,
            'export_markdown': self.export_markdown,
            'export_json': self.export_json,
            'export_chunks': self.export_chunks,
        }

    def validate(self) -> bool:
        """Validate configuration."""
        errors = []

        if not self.input_dir.exists():
            errors.append(f"Input directory does not exist: {self.input_dir}")

        if self.chunk_max_tokens < 100:
            errors.append(f"chunk_max_tokens too small: {self.chunk_max_tokens}")

        if self.omp_num_threads < 1:
            errors.append(f"omp_num_threads must be >= 1: {self.omp_num_threads}")

        if errors:
            for err in errors:
                print(f"Config error: {err}")
            return False

        return True
