#!/usr/bin/env python3
"""
DoclingChunker - Hybrid chunking for RAG integration.

Converts Docling output to RefineryNode format for Neo4j/vector storage.
Uses semantic chunking with configurable token limits.
"""

import hashlib
import logging
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import RefineryNode from the ACI schema
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "ai"))
    from aci.schema import RefineryNode
except ImportError:
    # Fallback: define minimal RefineryNode if import fails
    from dataclasses import dataclass, field

    @dataclass
    class RefineryNode:
        """Fallback RefineryNode definition."""
        content: str
        source_file: str
        chunk_id: str
        chunk_type: str
        relevance_score: float = 0.0
        start_line: int = 0
        end_line: int = 0
        metadata: Dict[str, Any] = field(default_factory=dict)
        created_at: float = field(default_factory=time.time)
        embedding: List[float] = field(default_factory=list)
        waybill: Dict[str, Any] = field(default_factory=dict)

        def to_dict(self) -> Dict[str, Any]:
            return {
                "content": self.content,
                "source_file": self.source_file,
                "chunk_id": self.chunk_id,
                "chunk_type": self.chunk_type,
                "relevance_score": self.relevance_score,
                "start_line": self.start_line,
                "end_line": self.end_line,
                "metadata": self.metadata,
                "created_at": self.created_at,
                "embedding": self.embedding,
                "waybill": self.waybill
            }

        @property
        def token_estimate(self) -> int:
            return len(self.content) // 4


class DoclingChunker:
    """
    Chunks Docling output into RefineryNode format.

    Supports:
    - Semantic chunking by document structure (headers, paragraphs)
    - Token-limited chunking with overlap
    - Preservation of document hierarchy in metadata
    """

    def __init__(
        self,
        max_tokens: int = 512,
        overlap_tokens: int = 50,
        min_chunk_tokens: int = 50
    ):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.min_chunk_tokens = min_chunk_tokens

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate (chars / 4)."""
        return len(text) // 4

    def generate_chunk_id(self, content: str, source: str) -> str:
        """Generate unique chunk ID."""
        hasher = hashlib.sha256()
        hasher.update(source.encode('utf-8'))
        hasher.update(content.encode('utf-8'))
        return hasher.hexdigest()[:16]

    def chunk_markdown(
        self,
        markdown_content: str,
        source_file: str,
        ref_id: str,
        parent_parcel_id: str,
        batch_id: Optional[str] = None
    ) -> List[RefineryNode]:
        """
        Chunk markdown content into RefineryNodes.

        Splits by headers and paragraphs, respecting token limits.
        """
        nodes = []
        lines = markdown_content.split('\n')

        current_section = []
        current_header = ""
        current_level = 0
        section_start_line = 0

        def flush_section():
            nonlocal current_section, current_header, section_start_line

            if not current_section:
                return

            content = '\n'.join(current_section).strip()
            if not content or self.estimate_tokens(content) < self.min_chunk_tokens:
                return

            # If content exceeds max, split it
            if self.estimate_tokens(content) > self.max_tokens:
                sub_chunks = self._split_large_content(content, current_header)
                for i, sub_content in enumerate(sub_chunks):
                    node = self._create_node(
                        content=sub_content,
                        source_file=source_file,
                        ref_id=ref_id,
                        chunk_type=f"h{current_level}" if current_level else "section",
                        header=current_header,
                        start_line=section_start_line,
                        end_line=section_start_line + len(current_section),
                        parent_parcel_id=parent_parcel_id,
                        batch_id=batch_id,
                        sub_index=i if len(sub_chunks) > 1 else None
                    )
                    nodes.append(node)
            else:
                node = self._create_node(
                    content=content,
                    source_file=source_file,
                    ref_id=ref_id,
                    chunk_type=f"h{current_level}" if current_level else "section",
                    header=current_header,
                    start_line=section_start_line,
                    end_line=section_start_line + len(current_section),
                    parent_parcel_id=parent_parcel_id,
                    batch_id=batch_id
                )
                nodes.append(node)

            current_section = []

        for i, line in enumerate(lines):
            # Detect headers
            if line.startswith('#'):
                flush_section()
                level = len(line) - len(line.lstrip('#'))
                current_level = min(level, 6)
                current_header = line.lstrip('#').strip()
                current_section = [line]
                section_start_line = i + 1
            else:
                current_section.append(line)

        # Flush remaining
        flush_section()

        logger.info(f"Chunked {source_file}: {len(nodes)} chunks")
        return nodes

    def _split_large_content(self, content: str, header: str) -> List[str]:
        """Split large content into smaller chunks with overlap."""
        chunks = []
        paragraphs = content.split('\n\n')

        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self.estimate_tokens(para)

            if current_tokens + para_tokens > self.max_tokens and current_chunk:
                # Flush current chunk
                chunk_text = '\n\n'.join(current_chunk)
                if header and not chunks:  # Add header to first chunk
                    chunk_text = f"# {header}\n\n{chunk_text}"
                chunks.append(chunk_text)

                # Overlap: keep last paragraph
                if self.overlap_tokens > 0 and current_chunk:
                    current_chunk = [current_chunk[-1]]
                    current_tokens = self.estimate_tokens(current_chunk[0])
                else:
                    current_chunk = []
                    current_tokens = 0

            current_chunk.append(para)
            current_tokens += para_tokens

        # Flush remaining
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(chunk_text)

        return chunks if chunks else [content]

    def _create_node(
        self,
        content: str,
        source_file: str,
        ref_id: str,
        chunk_type: str,
        header: str,
        start_line: int,
        end_line: int,
        parent_parcel_id: str,
        batch_id: Optional[str] = None,
        sub_index: Optional[int] = None
    ) -> RefineryNode:
        """Create a RefineryNode with proper waybill."""
        chunk_id = self.generate_chunk_id(content, source_file)
        parcel_id = f"pcl_{uuid.uuid4().hex[:12]}"

        waybill = {
            "parcel_id": parcel_id,
            "parent_id": parent_parcel_id,
            "ref_id": ref_id,
            "route": [
                {
                    "event": "chunked_from_docling",
                    "timestamp": int(time.time()),
                    "agent": "docling.chunker.py",
                    "context": {
                        "source_file": Path(source_file).name,
                        "batch_id": batch_id or "single_run",
                        "header": header,
                        "sub_index": sub_index
                    }
                }
            ]
        }

        return RefineryNode(
            content=content,
            source_file=source_file,
            chunk_id=chunk_id,
            chunk_type=chunk_type,
            relevance_score=self._score_relevance(content, chunk_type, header),
            start_line=start_line,
            end_line=end_line,
            metadata={
                "ref_id": ref_id,
                "header": header,
                "source_type": "academic_pdf",
                "sub_index": sub_index
            },
            waybill=waybill
        )

    def _score_relevance(self, content: str, chunk_type: str, header: str) -> float:
        """Score chunk relevance (0.0 - 1.0)."""
        score = 0.5  # Base score

        # Type bonuses
        if chunk_type in ('h1', 'h2'):
            score += 0.2
        elif chunk_type == 'h3':
            score += 0.15
        elif chunk_type in ('h4', 'h5', 'h6'):
            score += 0.1

        # Header keyword bonuses (academic relevance)
        header_lower = header.lower()
        if any(kw in header_lower for kw in ['abstract', 'introduction', 'conclusion', 'method']):
            score += 0.15
        if any(kw in header_lower for kw in ['result', 'discussion', 'analysis']):
            score += 0.1
        if 'reference' in header_lower or 'bibliography' in header_lower:
            score -= 0.2  # Reduce score for reference sections

        # Content length bonus (logarithmic)
        content_len = len(content.strip())
        if content_len > 100:
            import math
            score += min(0.15, 0.03 * math.log10(content_len))

        return max(0.0, min(1.0, score))

    def chunk_docling_result(
        self,
        docling_result: Any,  # DoclingDocument
        source_file: str,
        ref_id: str,
        parent_parcel_id: str,
        batch_id: Optional[str] = None
    ) -> List[RefineryNode]:
        """
        Chunk a DoclingDocument directly using its structure.

        This method uses Docling's native document structure when available,
        falling back to markdown chunking if needed.
        """
        # Try to use Docling's chunker if available
        try:
            from docling_core.transforms.chunker.hybrid_chunker import HybridChunker

            # Use default tokenizer (MiniLM-L6-v2, 512 max tokens)
            chunker = HybridChunker()

            chunks = list(chunker.chunk(docling_result))
            nodes = []

            for i, chunk in enumerate(chunks):
                chunk_text = chunk.text if hasattr(chunk, 'text') else str(chunk)
                chunk_id = self.generate_chunk_id(chunk_text, source_file)
                parcel_id = f"pcl_{uuid.uuid4().hex[:12]}"

                # Extract metadata from chunk if available
                chunk_meta = {}
                if hasattr(chunk, 'meta'):
                    chunk_meta = chunk.meta if isinstance(chunk.meta, dict) else {}

                waybill = {
                    "parcel_id": parcel_id,
                    "parent_id": parent_parcel_id,
                    "ref_id": ref_id,
                    "route": [
                        {
                            "event": "chunked_hybrid",
                            "timestamp": int(time.time()),
                            "agent": "docling.HybridChunker",
                            "context": {
                                "source_file": Path(source_file).name,
                                "batch_id": batch_id or "single_run",
                                "chunk_index": i
                            }
                        }
                    ]
                }

                node = RefineryNode(
                    content=chunk_text,
                    source_file=source_file,
                    chunk_id=chunk_id,
                    chunk_type="hybrid_chunk",
                    relevance_score=0.6,  # Default for hybrid chunks
                    start_line=0,
                    end_line=0,
                    metadata={
                        "ref_id": ref_id,
                        "source_type": "academic_pdf",
                        "chunk_index": i,
                        **chunk_meta
                    },
                    waybill=waybill
                )
                nodes.append(node)

            logger.info(f"HybridChunker produced {len(nodes)} chunks for {ref_id}")
            return nodes

        except ImportError:
            logger.warning("docling.chunking not available, using markdown chunking")
            # Fall back to markdown-based chunking
            md_content = docling_result.export_to_markdown() if hasattr(docling_result, 'export_to_markdown') else str(docling_result)
            return self.chunk_markdown(md_content, source_file, ref_id, parent_parcel_id, batch_id)
        except Exception as e:
            logger.error(f"HybridChunker failed: {e}, falling back to markdown")
            md_content = docling_result.export_to_markdown() if hasattr(docling_result, 'export_to_markdown') else str(docling_result)
            return self.chunk_markdown(md_content, source_file, ref_id, parent_parcel_id, batch_id)


def create_chunker(config) -> DoclingChunker:
    """Create DoclingChunker from DoclingConfig."""
    return DoclingChunker(
        max_tokens=config.chunk_max_tokens,
        overlap_tokens=config.chunk_overlap_tokens
    )
