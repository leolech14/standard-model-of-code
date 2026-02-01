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
import uuid  # Added for parcel IDs
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from pathlib import Path
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from ai.aci.schema import RefineryNode  # Shared Schema

try:
    from ai.aci.refinery.publishers.neo4j_publisher import Neo4jPublisher
except ImportError:
    Neo4jPublisher = None


# Import ACI Semantic Logic
try:
    from ai.aci.semantic_finder import compute_semantic_distance, SemanticMatch, SemanticTarget
except ImportError:
    # Fallback for circular imports or path issues during standalone runs
    compute_semantic_distance = None
    SemanticMatch = Any
    SemanticTarget = Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chunk registry location
CHUNK_REGISTRY_DIR = Path(__file__).parent.parent.parent.parent / "intelligence" / "chunks"




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
        'constant': re.compile(r'^([A-Z_][A-Z0-9_]*)\s*=', re.MULTILINE),
        'variable': re.compile(r'^([a-z_][a-z0-9_]*)\s*=', re.MULTILINE),
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

                # Check for constant/variable
                const_match = self.PATTERNS['constant'].match(line)
                var_match = self.PATTERNS['variable'].match(line)
                if const_match or var_match:
                    current_def = (const_match or var_match).group(1)
                    current_type = 'constant' if const_match else 'variable'
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

    def __init__(self, cache_dir: Path = CHUNK_REGISTRY_DIR, enable_embeddings: bool = False, context_depth: str = "medium", config: dict = None):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._chunk_cache: Dict[str, List[RefineryNode]] = {}
        self.enable_embeddings = enable_embeddings
        self._embedding_engine = EmbeddingEngine() if enable_embeddings else None

        # Layer 2 Parametric Config
        self.config = config or {}
        refinery_cfg = self.config.get('refinery', {})

        # Context Depth: shallow | medium | deep
        self.context_depth = refinery_cfg.get('context_depth', context_depth)
        logger.info(f"⚙️ Refinery initialized with context_depth='{self.context_depth}'")

        # Threshold Overrides (Paramilitary Controls)
        threshold_high = refinery_cfg.get('threshold_high', 0.6)
        threshold_low = refinery_cfg.get('threshold_low', 0.3)
        attention_mode = refinery_cfg.get('attention_mode', 'laminar')
        logger.info(f"🛡️ Attention Gear: mode='{attention_mode}', thresholds=({threshold_low}, {threshold_high})")

        # Initialize Graph Publisher (The Unification)
        self.publisher = None
        if Neo4jPublisher:
            try:
                self.publisher = Neo4jPublisher()
            except Exception as e:
                logger.warning(f"Failed to init Neo4jPublisher: {e}")


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

    def _apply_attention_gate(
        self,
        node: RefineryNode,
        semantic_match: Optional[SemanticMatch]
    ) -> float:
        """
        Apply semantic attention gate to a node.

        Uses compute_semantic_distance to boost relevance based on query intent.
        Adjusts thresholds based on flow type (Laminar vs Turbulent).
        """
        if not semantic_match or not semantic_match.targets or not compute_semantic_distance:
            return node.relevance_score

        # 1. Compute distance to matched targets
        # We need to map RefineryNode to a "particle" dict for compute_semantic_distance
        particle = {
            "dimensions": {
                "D1_WHAT": node.chunk_type,
                "D2_LAYER": node.metadata.get("layer", "Unknown"),
                "D3_ROLE": node.metadata.get("role", "Unknown"),
            }
        }

        min_dist = 1.0
        for target in semantic_match.targets:
            target_particle = {
                "dimensions": {
                    "D2_LAYER": target.layer or "Unknown",
                    "D3_ROLE": target.roles[0] if target.roles else "Unknown",
                }
            }
            dist = compute_semantic_distance(particle, target_particle)
            min_dist = min(min_dist, dist)

        # 2. Boost relevance (Similarity = 1 - Distance)
        similarity = 1.0 - min_dist
        boosted_score = node.relevance_score + (similarity * 0.3)

        # 3. Flow-based Thresholding
        # Turbulent flow (mixed) allows broader retention (lower threshold)
        # Laminar flow (coherent) is strict (higher threshold)
        refinery_cfg = self.config.get('refinery', {})
        threshold_high = refinery_cfg.get('threshold_high', 0.6)
        threshold_low = refinery_cfg.get('threshold_low', 0.3)

        base_threshold = 0.5
        if semantic_match.context_flow == "turbulent":
            base_threshold = threshold_low
        elif semantic_match.context_flow == "laminar":
            base_threshold = threshold_high

        return max(0.0, min(1.0, boosted_score)) if boosted_score >= base_threshold else 0.0

    def process_file(
        self,
        file_path: str,
        use_cache: bool = True,
        parent_parcel_id: str = None,
        batch_id: str = None,
        semantic_match: Optional[SemanticMatch] = None
    ) -> List[RefineryNode]:
        """
        Atomize a file into RefineryNodes.

        Args:
            file_path: Path to file to process
            use_cache: Whether to use/update cache
            parent_parcel_id: ID of the input Parcel (from Scanner)
            batch_id: ID of the processing batch (for copresence tracking)

        Returns:
            List of RefineryNode objects
        """
        file_path = str(Path(file_path).resolve())

        # Check cache (Skip logic for now if we want to enforce new waybills?
        # Ideally cache key should include parent_parcel_id, but keeping simple for now)
        if use_cache and file_path in self._chunk_cache:
            logger.info(f"Cache hit for {file_path}")
            # TODO: Should probably update the waybill of cached items?
            # For now, just return cached.
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

            # Context Depth Filtering (Layer 2)
            if self.context_depth == "shallow":
                if chunk_type not in ('class', 'h1', 'h2'):
                    continue
            elif self.context_depth == "medium":
                # Filter out low-level noise in medium mode
                if chunk_type in ('constant', 'variable', 'h4', 'h5', 'h6', 'paragraph'):
                     continue
            # 'deep' mode allows all chunks

            chunk_id = self._generate_chunk_id(file_path, content)
            relevance = self._score_relevance(content, chunk_type)

            # Mint new Parcel ID for this chunk (Sub-parcel)
            parcel_id = f"pcl_{uuid.uuid4().hex[:12]}"

            # Create Structured Waybill
            # Event: "chunking"
            # Context: "who was in the room?" -> The Batch
            waybill = {
                "parcel_id": parcel_id,
                "parent_id": parent_parcel_id or "orphaned_ingest",
                "route": [
                    {
                        "event": "chunked",
                        "timestamp": int(time.time()),
                        "agent": "refinery.py",
                        "context": {
                            "source_file": Path(file_path).name,
                            "batch_id": batch_id or "single_run"
                            # In a real system, we'd list other_parcels here too
                        }
                    }
                ]
            }

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
                },
                waybill=waybill
            )

            # Apply Attention Gate
            node.relevance_score = self._apply_attention_gate(node, semantic_match)

            if node.relevance_score > 0:
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

        # Phase 9: The Gap Bridge (Publication)
        if self.publisher and nodes:
             # We need to extract parcel_id and batch_id from the first node's waybill,
             # or passed args.
             # Nodes generated have waybill populated.
             if nodes[0].waybill:
                 pid = nodes[0].waybill.get("parcel_id")
                 # Batch ID is nested in waybill->route->context->batch_id but
                 # we can also use the passed batch_id arg.
                 # Let's use the passed batch_id for robust logs, defaulting to waybill context if needed.
                 bid = batch_id or "unknown_batch"

                 self.publisher.publish_atoms(nodes, pid, bid)

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

                # Skip by exact path part matching (not substring)
                # This prevents false positives like skipping "docs/__pycache__explain.md"
                skip_dirs = {'.git', '.venv', '.tools_venv', '__pycache__', 'node_modules',
                            '.pytest_cache', '.mypy_cache', '.tox', 'dist', 'build', '.eggs'}

                # Check if any path part exactly matches a skip directory
                if any(part in skip_dirs for part in file_path.parts):
                    continue

                nodes = self.process_file(str(file_path))
                all_nodes.extend(nodes)
                file_count += 1

        logger.info(f"Processed {file_count} files, {len(all_nodes)} total chunks")
        return all_nodes

    def _validate_chunks(self, nodes: List[RefineryNode]) -> None:
        """
        Validate chunks before writing to prevent corruption.

        Raises:
            ValueError: If validation fails
        """
        if not nodes:
            raise ValueError("No chunks to export")

        for i, chunk in enumerate(nodes):
            # Required fields
            if not chunk.content:
                raise ValueError(f"Chunk {i}: Empty content")
            if not chunk.source_file:
                raise ValueError(f"Chunk {i}: Missing source_file")
            if not chunk.chunk_id:
                raise ValueError(f"Chunk {i}: Missing chunk_id")
            if not chunk.chunk_type:
                raise ValueError(f"Chunk {i}: Missing chunk_type")

            # Reasonable bounds
            if chunk.token_estimate > 200000:
                raise ValueError(f"Chunk {i}: Too large ({chunk.token_estimate} tokens)")
            if chunk.token_estimate < 0:
                raise ValueError(f"Chunk {i}: Negative token count")

            # Relevance in range
            if not (0 <= chunk.relevance_score <= 1.0):
                raise ValueError(f"Chunk {i}: Invalid relevance {chunk.relevance_score}")

            # Line numbers valid
            if chunk.start_line < 0 or chunk.end_line < 0:
                raise ValueError(f"Chunk {i}: Invalid line numbers")
            if chunk.end_line < chunk.start_line:
                raise ValueError(f"Chunk {i}: end_line < start_line")

        # Sanity check total
        total_tokens = sum(c.token_estimate for c in nodes)
        if total_tokens > 10_000_000:
            raise ValueError(f"Total tokens unreasonable: {total_tokens:,}")

        logger.info(f"Validation passed: {len(nodes)} chunks, {total_tokens:,} tokens")

    def export_to_json(self, nodes: List[RefineryNode], output_path: str):
        """Export nodes to JSON file with validation."""

        # Validate before writing
        self._validate_chunks(nodes)

        data = {
            'exported_at': time.time(),
            'node_count': len(nodes),
            'total_tokens': sum(n.token_estimate for n in nodes),
            'nodes': [n.to_dict() for n in nodes]
        }

        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write (temp → verify → rename)
        temp_path = output_path_obj.with_suffix('.tmp')

        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            # Verify JSON is valid
            with open(temp_path, 'r', encoding='utf-8') as f:
                json.load(f)

            # Commit (atomic on POSIX)
            temp_path.rename(output_path_obj)

            logger.info(f"Exported {len(nodes)} nodes to {output_path}")

        except Exception as e:
            # Cleanup on failure
            if temp_path.exists():
                temp_path.unlink()
            raise RuntimeError(f"Export failed: {e}") from e

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
