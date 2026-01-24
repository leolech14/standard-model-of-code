#!/usr/bin/env python3
"""
REFINERY - Context Atomization Engine

Breaks large context (code, docs, config) into atomic chunks with metadata.
Integrates with CacheRegistry for persistence and TierRouter for relevance scoring.

Architecture:
    Input: Large files (Python, Markdown, YAML)
    Process: Semantic chunking with type-specific strategies
    Output: RefineryNode objects with source, type, relevance score

Usage:
    from aci.refinery import Refinery

    refinery = Refinery()
    nodes = refinery.process_file("src/core/pipeline.py")
    refinery.export_to_json(nodes, "chunks.json")

Best Practices Applied:
- RAG-style semantic splitting (not fixed-size tokens)
- Compaction: retain essential details, discard noise
- Relevance scoring via embeddings/heuristics
- Cache for repeated processing
"""

import hashlib
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chunk registry location
CHUNK_REGISTRY_DIR = Path(__file__).parent.parent.parent.parent / "intelligence" / "chunks"


@dataclass
class RefineryNode:
    """Atomic chunk with full metadata."""
    content: str                    # The chunk text
    source_file: str                # Origin file path
    chunk_id: str                   # Unique ID (SHA256-based)
    chunk_type: str                 # Type: function, class, section, config_block, etc.
    relevance_score: float = 0.0   # 0.0-1.0 relevance score
    start_line: int = 0            # Line number in source (if applicable)
    end_line: int = 0              # End line number
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
    created_at: float = field(default_factory=time.time)
    embedding: List[float] = field(default_factory=list)  # Vector embedding (384-dim for MiniLM)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return asdict(self)

    @property
    def token_estimate(self) -> int:
        """Rough token count estimate (chars / 4)."""
        return len(self.content) // 4

    def __repr__(self) -> str:
        return f"RefineryNode({self.chunk_type}:{self.chunk_id[:8]}... {self.token_estimate}tok)"


class EmbeddingEngine:
    """
    Vector embedding engine using sentence-transformers.

    Uses all-MiniLM-L6-v2: 22M params, 384 dims, ~15ms/1K tokens.
    Loads model lazily on first use.
    """

    _instance = None
    _model = None

    def __new__(cls):
        """Singleton pattern - only load model once."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading embedding model: all-MiniLM-L6-v2...")
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Embedding model loaded.")
            except ImportError:
                logger.warning("sentence-transformers not installed. Embeddings disabled.")
                logger.warning("Install with: pip install sentence-transformers")
                self._model = None
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self._model = None

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (384-dim each), or empty lists if unavailable
        """
        self._load_model()

        if self._model is None:
            return [[] for _ in texts]

        try:
            embeddings = self._model.encode(texts, show_progress_bar=False)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return [[] for _ in texts]

    def embed_single(self, text: str) -> List[float]:
        """Embed a single text string."""
        result = self.embed([text])
        return result[0] if result else []

    @property
    def is_available(self) -> bool:
        """Check if embedding model is available."""
        self._load_model()
        return self._model is not None

    @property
    def dimension(self) -> int:
        """Embedding dimension (384 for MiniLM)."""
        return 384


class FileChunker(ABC):
    """Base class for file-specific chunking strategies."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = ""
        self._load()

    def _load(self):
        """Load file content."""
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='replace') as f:
                self.content = f.read()
        except Exception as e:
            logger.error(f"Failed to load {self.file_path}: {e}")
            self.content = ""

    @abstractmethod
    def chunk(self) -> List[Tuple[str, str, int, int]]:
        """
        Split file into semantic chunks.

        Returns:
            List of (content, chunk_type, start_line, end_line) tuples
        """
        pass


class PythonChunker(FileChunker):
    """Chunks Python files by semantic units (functions, classes, imports)."""

    # Patterns for Python constructs
    PATTERNS = {
        'class': re.compile(r'^class\s+(\w+)', re.MULTILINE),
        'function': re.compile(r'^(?:async\s+)?def\s+(\w+)', re.MULTILINE),
        'import_block': re.compile(r'^(?:import|from)\s+.+$', re.MULTILINE),
    }

    def chunk(self) -> List[Tuple[str, str, int, int]]:
        """Split Python file into functions, classes, and import blocks."""
        chunks = []
        lines = self.content.split('\n')

        if not lines:
            return chunks

        # Extract imports at top
        import_lines = []
        import_end = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                import_lines.append(line)
                import_end = i + 1
            elif stripped and not stripped.startswith('#') and import_lines:
                break

        if import_lines:
            chunks.append(('\n'.join(import_lines), 'imports', 1, import_end))

        # Find class and function definitions
        current_def = None
        current_start = 0
        current_type = None
        buffer: List[str] = []

        for i, line in enumerate(lines):
            # Detect new definition at column 0
            if line and not line[0].isspace():
                # Save previous definition if exists
                if current_def and buffer:
                    content = '\n'.join(buffer)
                    chunks.append((content, current_type, current_start + 1, i))
                    buffer = []

                # Check for class
                class_match = self.PATTERNS['class'].match(line)
                if class_match:
                    current_def = class_match.group(1)
                    current_type = 'class'
                    current_start = i
                    buffer = [line]
                    continue

                # Check for function
                func_match = self.PATTERNS['function'].match(line)
                if func_match:
                    current_def = func_match.group(1)
                    current_type = 'function'
                    current_start = i
                    buffer = [line]
                    continue

                # Neither - reset
                if current_def:
                    content = '\n'.join(buffer)
                    chunks.append((content, current_type, current_start + 1, i))
                current_def = None
                buffer = []
            elif current_def:
                buffer.append(line)

        # Don't forget last definition
        if current_def and buffer:
            content = '\n'.join(buffer)
            chunks.append((content, current_type, current_start + 1, len(lines)))

        return chunks


class MarkdownChunker(FileChunker):
    """Chunks Markdown files by sections (headers)."""

    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def chunk(self) -> List[Tuple[str, str, int, int]]:
        """Split Markdown into sections based on headers."""
        chunks = []
        lines = self.content.split('\n')

        if not lines:
            return chunks

        current_section = []
        current_level = 0
        section_start = 0

        for i, line in enumerate(lines):
            header_match = self.HEADER_PATTERN.match(line)
            if header_match:
                # Save previous section
                if current_section:
                    content = '\n'.join(current_section)
                    chunk_type = f"h{current_level}" if current_level else "preamble"
                    chunks.append((content, chunk_type, section_start + 1, i))

                # Start new section
                current_level = len(header_match.group(1))
                current_section = [line]
                section_start = i
            else:
                current_section.append(line)

        # Last section
        if current_section:
            content = '\n'.join(current_section)
            chunk_type = f"h{current_level}" if current_level else "preamble"
            chunks.append((content, chunk_type, section_start + 1, len(lines)))

        return chunks


class YamlChunker(FileChunker):
    """Chunks YAML files by top-level keys."""

    TOP_KEY_PATTERN = re.compile(r'^(\w[\w\-]*):')

    def chunk(self) -> List[Tuple[str, str, int, int]]:
        """Split YAML into top-level key blocks."""
        chunks = []
        lines = self.content.split('\n')

        if not lines:
            return chunks

        current_key = None
        current_block = []
        block_start = 0

        for i, line in enumerate(lines):
            # Skip comments and empty at start
            if not line.strip() or line.strip().startswith('#'):
                if current_key:
                    current_block.append(line)
                continue

            # Check for top-level key (no indent)
            if line and not line[0].isspace():
                key_match = self.TOP_KEY_PATTERN.match(line)
                if key_match:
                    # Save previous block
                    if current_key and current_block:
                        content = '\n'.join(current_block)
                        chunks.append((content, f"yaml_key:{current_key}", block_start + 1, i))

                    current_key = key_match.group(1)
                    current_block = [line]
                    block_start = i
                    continue

            if current_key:
                current_block.append(line)

        # Last block
        if current_key and current_block:
            content = '\n'.join(current_block)
            chunks.append((content, f"yaml_key:{current_key}", block_start + 1, len(lines)))

        return chunks


class GenericChunker(FileChunker):
    """Generic chunker for unknown file types - splits by blank lines."""

    def chunk(self) -> List[Tuple[str, str, int, int]]:
        """Split by paragraph (double newlines)."""
        chunks = []

        paragraphs = re.split(r'\n\s*\n', self.content)
        line_num = 1

        for para in paragraphs:
            if para.strip():
                para_lines = para.count('\n') + 1
                chunks.append((para, 'paragraph', line_num, line_num + para_lines - 1))
                line_num += para_lines + 1  # +1 for blank line
            else:
                line_num += 1

        return chunks


class Refinery:
    """
    Main context atomization engine.

    Orchestrates:
    1. File type detection and chunking
    2. Relevance scoring
    3. Optional vector embeddings
    4. Caching of processed chunks
    5. Export to JSON
    """

    def __init__(self, cache_dir: Path = CHUNK_REGISTRY_DIR, enable_embeddings: bool = False):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._chunk_cache: Dict[str, List[RefineryNode]] = {}
        self.enable_embeddings = enable_embeddings
        self._embedding_engine = EmbeddingEngine() if enable_embeddings else None

    def _get_chunker(self, file_path: str) -> FileChunker:
        """Get appropriate chunker for file type."""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == '.py':
            return PythonChunker(file_path)
        elif suffix in ('.md', '.markdown'):
            return MarkdownChunker(file_path)
        elif suffix in ('.yaml', '.yml'):
            return YamlChunker(file_path)
        else:
            return GenericChunker(file_path)

    def _generate_chunk_id(self, file_path: str, content: str) -> str:
        """Generate unique ID for chunk based on content and source."""
        hasher = hashlib.sha256()
        hasher.update(file_path.encode('utf-8'))
        hasher.update(content.encode('utf-8'))
        return hasher.hexdigest()[:16]

    def _score_relevance(self, content: str, chunk_type: str) -> float:
        """
        Score chunk relevance (0.0 - 1.0).

        Heuristics:
        - Longer content = more relevant (up to a point)
        - Certain types score higher (class > function > imports)
        - Docstrings boost score
        - Comments in code slightly reduce score (noise)
        """
        score = 0.5  # Base score

        # Type bonuses
        type_weights = {
            'class': 0.2,
            'function': 0.15,
            'h1': 0.2,
            'h2': 0.15,
            'h3': 0.1,
            'imports': 0.05,
            'yaml_key': 0.1,
            'paragraph': 0.0,
            'preamble': 0.05,
        }

        # Check for partial type matches (like yaml_key:xxx)
        base_type = chunk_type.split(':')[0] if ':' in chunk_type else chunk_type
        score += type_weights.get(base_type, 0.0)

        # Length score (logarithmic, caps at ~1000 chars)
        content_len = len(content.strip())
        if content_len > 50:
            import math
            length_score = min(0.2, 0.05 * math.log10(content_len))
            score += length_score

        # Docstring bonus for Python
        if '"""' in content or "'''" in content:
            score += 0.1

        # Type hint bonus
        if '->' in content or ': ' in content:
            score += 0.05

        # Clamp to 0.0 - 1.0
        return max(0.0, min(1.0, score))

    def process_file(self, file_path: str, use_cache: bool = True) -> List[RefineryNode]:
        """
        Atomize a file into RefineryNodes.

        Args:
            file_path: Path to file to process
            use_cache: Whether to use/update cache

        Returns:
            List of RefineryNode objects
        """
        file_path = str(Path(file_path).resolve())

        # Check cache
        if use_cache and file_path in self._chunk_cache:
            logger.info(f"Cache hit for {file_path}")
            return self._chunk_cache[file_path]

        # Get appropriate chunker
        chunker = self._get_chunker(file_path)

        if not chunker.content:
            logger.warning(f"Empty or unreadable file: {file_path}")
            return []

        # Chunk the file
        raw_chunks = chunker.chunk()

        # Build RefineryNodes
        nodes = []
        for content, chunk_type, start_line, end_line in raw_chunks:
            if not content.strip():
                continue

            chunk_id = self._generate_chunk_id(file_path, content)
            relevance = self._score_relevance(content, chunk_type)

            node = RefineryNode(
                content=content,
                source_file=file_path,
                chunk_id=chunk_id,
                chunk_type=chunk_type,
                relevance_score=relevance,
                start_line=start_line,
                end_line=end_line,
                metadata={
                    'file_type': Path(file_path).suffix,
                    'file_name': Path(file_path).name,
                }
            )
            nodes.append(node)

        # Generate embeddings if enabled
        if self.enable_embeddings and self._embedding_engine and nodes:
            texts = [n.content for n in nodes]
            embeddings = self._embedding_engine.embed(texts)
            for node, emb in zip(nodes, embeddings):
                node.embedding = emb
            logger.info(f"Generated {len(embeddings)} embeddings")

        logger.info(f"Processed {file_path}: {len(nodes)} chunks")

        # Update cache
        if use_cache:
            self._chunk_cache[file_path] = nodes

        return nodes

    def process_directory(
        self,
        dir_path: str,
        extensions: List[str] = None,
        max_files: int = 100
    ) -> List[RefineryNode]:
        """
        Process all matching files in a directory.

        Args:
            dir_path: Directory to scan
            extensions: File extensions to include (default: .py, .md, .yaml, .yml)
            max_files: Maximum files to process (safety limit)

        Returns:
            Combined list of RefineryNodes from all files
        """
        if extensions is None:
            extensions = ['.py', '.md', '.yaml', '.yml']

        dir_path_obj = Path(dir_path)
        all_nodes: List[RefineryNode] = []
        file_count = 0

        for ext in extensions:
            for file_path in dir_path_obj.rglob(f'*{ext}'):
                if file_count >= max_files:
                    logger.warning(f"Reached max_files limit ({max_files})")
                    break

                # Skip hidden files and common excludes
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if 'node_modules' in str(file_path) or '__pycache__' in str(file_path):
                    continue

                nodes = self.process_file(str(file_path))
                all_nodes.extend(nodes)
                file_count += 1

        logger.info(f"Processed {file_count} files, {len(all_nodes)} total chunks")
        return all_nodes

    def export_to_json(self, nodes: List[RefineryNode], output_path: str):
        """Export nodes to JSON file."""
        data = {
            'exported_at': time.time(),
            'node_count': len(nodes),
            'total_tokens': sum(n.token_estimate for n in nodes),
            'nodes': [n.to_dict() for n in nodes]
        }

        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path_obj, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported {len(nodes)} nodes to {output_path}")

    def filter_by_relevance(
        self,
        nodes: List[RefineryNode],
        min_score: float = 0.5
    ) -> List[RefineryNode]:
        """Filter nodes by minimum relevance score."""
        return [n for n in nodes if n.relevance_score >= min_score]

    def select_top_k(
        self,
        nodes: List[RefineryNode],
        k: int = 10
    ) -> List[RefineryNode]:
        """Select top K nodes by relevance."""
        return sorted(nodes, key=lambda n: n.relevance_score, reverse=True)[:k]

    def compact_for_context(
        self,
        nodes: List[RefineryNode],
        max_tokens: int = 50000
    ) -> List[RefineryNode]:
        """
        Select nodes to fit within token budget.

        Strategy: Greedy selection by relevance until budget exhausted.
        """
        sorted_nodes = sorted(nodes, key=lambda n: n.relevance_score, reverse=True)
        selected = []
        total_tokens = 0

        for node in sorted_nodes:
            if total_tokens + node.token_estimate <= max_tokens:
                selected.append(node)
                total_tokens += node.token_estimate
            elif total_tokens >= max_tokens:
                break

        logger.info(f"Compacted to {len(selected)} nodes, ~{total_tokens} tokens")
        return selected

    def semantic_search(
        self,
        query: str,
        nodes: List[RefineryNode],
        top_k: int = 5
    ) -> List[Tuple[RefineryNode, float]]:
        """
        Search nodes by semantic similarity to query.

        Args:
            query: Search query text
            nodes: List of nodes to search
            top_k: Number of top results to return

        Returns:
            List of (node, similarity_score) tuples, sorted by similarity
        """
        if not self._embedding_engine:
            logger.warning("Embeddings not enabled. Use enable_embeddings=True")
            return []

        # Filter nodes with embeddings
        embedded_nodes = [n for n in nodes if n.embedding]
        if not embedded_nodes:
            logger.warning("No embedded nodes found. Run with embeddings enabled.")
            return []

        # Embed query
        query_emb = self._embedding_engine.embed_single(query)
        if not query_emb:
            return []

        # Compute cosine similarity
        import numpy as np
        query_vec = np.array(query_emb)

        results = []
        for node in embedded_nodes:
            node_vec = np.array(node.embedding)
            similarity = np.dot(query_vec, node_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(node_vec))
            results.append((node, float(similarity)))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def stats(self) -> Dict[str, Any]:
        """Get refinery statistics."""
        all_nodes = []
        for nodes in self._chunk_cache.values():
            all_nodes.extend(nodes)

        if not all_nodes:
            return {'cached_files': 0, 'cached_chunks': 0}

        return {
            'cached_files': len(self._chunk_cache),
            'cached_chunks': len(all_nodes),
            'total_tokens': sum(n.token_estimate for n in all_nodes),
            'avg_relevance': sum(n.relevance_score for n in all_nodes) / len(all_nodes),
            'chunk_types': list(set(n.chunk_type for n in all_nodes)),
        }


# CLI interface
if __name__ == "__main__":
    import sys

    # Parse arguments
    enable_embed = '--embed' in sys.argv
    if enable_embed:
        sys.argv.remove('--embed')

    search_query = None
    if '--search' in sys.argv:
        idx = sys.argv.index('--search')
        if idx + 1 < len(sys.argv):
            search_query = sys.argv[idx + 1]
            sys.argv.pop(idx + 1)
            sys.argv.pop(idx)

    refinery = Refinery(enable_embeddings=enable_embed or bool(search_query))

    if len(sys.argv) < 2:
        print("Usage: python refinery.py <file_or_dir> [options]")
        print("\nOptions:")
        print("  --export <output.json>  Export chunks to JSON")
        print("  --embed                 Generate vector embeddings")
        print("  --search <query>        Semantic search (implies --embed)")
        print("\nExample:")
        print("  python refinery.py src/core/full_analysis.py")
        print("  python refinery.py src/ --export chunks.json")
        print("  python refinery.py src/ --embed --search 'pipeline stages'")
        sys.exit(1)

    target = sys.argv[1]
    output_path = None

    if '--export' in sys.argv:
        idx = sys.argv.index('--export')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    target_path = Path(target)

    if target_path.is_file():
        nodes = refinery.process_file(str(target_path))
    elif target_path.is_dir():
        nodes = refinery.process_directory(str(target_path))
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

    # Print summary
    print(f"\n=== REFINERY Results ===")
    print(f"Total chunks: {len(nodes)}")
    print(f"Total tokens: ~{sum(n.token_estimate for n in nodes)}")
    if enable_embed:
        embedded_count = sum(1 for n in nodes if n.embedding)
        print(f"Embedded: {embedded_count}/{len(nodes)}")

    if nodes:
        avg_rel = sum(n.relevance_score for n in nodes) / len(nodes)
        print(f"Avg relevance: {avg_rel:.2f}")

        # Semantic search if requested
        if search_query:
            print(f"\n=== Semantic Search: '{search_query}' ===")
            results = refinery.semantic_search(search_query, nodes, top_k=5)
            for node, score in results:
                print(f"  {score:.3f} | {node.chunk_type:15} | {node.source_file.split('/')[-1]}:{node.start_line}")
        else:
            # Top 5 by relevance
            print(f"\nTop 5 chunks by relevance:")
            for node in refinery.select_top_k(nodes, 5):
                print(f"  {node.relevance_score:.2f} | {node.chunk_type:15} | {node.source_file.split('/')[-1]}:{node.start_line}")

    if output_path:
        refinery.export_to_json(nodes, output_path)
        print(f"\nExported to: {output_path}")
