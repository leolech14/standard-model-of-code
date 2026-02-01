"""
LlamaIndex Integration for Docling Processor

Provides DoclingIndexReader for LlamaIndex RAG pipelines.
"""

import logging
from pathlib import Path
from typing import List, Optional, Any

logger = logging.getLogger(__name__)


class DoclingIndexReader:
    """
    LlamaIndex-compatible reader using Docling.

    Converts PDFs to LlamaIndex Document objects optimized for indexing.

    Usage:
        from docling_processor.integrations import DoclingIndexReader
        from llama_index import VectorStoreIndex

        reader = DoclingIndexReader()
        documents = reader.load_data("document.pdf")

        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        use_hybrid_chunker: bool = True,
    ):
        """
        Initialize the Docling Index Reader.

        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Overlap tokens between chunks
            use_hybrid_chunker: Use semantic-aware chunking
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_hybrid_chunker = use_hybrid_chunker

    def load_data(self, file_path: str) -> List[Any]:
        """
        Load documents from file path.

        Args:
            file_path: Path to PDF file or directory

        Returns:
            List of LlamaIndex Document objects
        """
        try:
            from llama_index.core import Document
        except ImportError:
            try:
                from llama_index import Document
            except ImportError:
                raise ImportError(
                    "llama-index is required for this integration. "
                    "Install with: pip install llama-index"
                )

        from ..processor import DoclingProcessor
        from ..config import DoclingConfig
        from ..chunker import DoclingChunker

        config = DoclingConfig.load()
        config.chunk_max_tokens = self.chunk_size
        config.chunk_overlap_tokens = self.chunk_overlap

        processor = DoclingProcessor(config)
        chunker = DoclingChunker(config)

        documents = []
        path = Path(file_path)

        if path.is_file():
            files = [path]
        else:
            files = list(path.glob("*.pdf"))

        for pdf_file in files:
            result = processor.process_single(pdf_file)

            if result.status == "failed":
                logger.warning(f"Failed to process {pdf_file}: {result.error_message}")
                continue

            chunks = chunker.chunk_result(result)

            for chunk in chunks:
                doc = Document(
                    text=chunk.get("text", ""),
                    metadata={
                        "file_path": str(pdf_file),
                        "file_name": pdf_file.name,
                        "ref_id": result.ref_id,
                        "chunk_id": chunk.get("chunk_id"),
                        "page_numbers": chunk.get("page_numbers", []),
                        "section": chunk.get("section"),
                        "token_count": chunk.get("token_count"),
                    },
                    excluded_embed_metadata_keys=["file_path", "chunk_id"],
                    excluded_llm_metadata_keys=["file_path", "chunk_id", "token_count"],
                )
                documents.append(doc)

        logger.info(f"Loaded {len(documents)} documents from {len(files)} files")
        return documents


class DoclingQueryEngine:
    """
    Pre-configured query engine using Docling + LlamaIndex.

    Usage:
        engine = DoclingQueryEngine("./pdfs/")
        response = engine.query("What is the main finding?")
    """

    def __init__(
        self,
        documents_path: str,
        llm: Optional[Any] = None,
        embed_model: Optional[Any] = None,
        similarity_top_k: int = 5,
    ):
        self.documents_path = documents_path
        self.llm = llm
        self.embed_model = embed_model
        self.similarity_top_k = similarity_top_k
        self._index = None
        self._query_engine = None

    def _build_index(self):
        """Build the index lazily."""
        if self._index is not None:
            return

        try:
            from llama_index.core import VectorStoreIndex, Settings
        except ImportError:
            from llama_index import VectorStoreIndex, Settings

        # Configure LLM and embeddings if provided
        if self.llm:
            Settings.llm = self.llm
        if self.embed_model:
            Settings.embed_model = self.embed_model

        # Load documents
        reader = DoclingIndexReader()
        documents = reader.load_data(self.documents_path)

        # Build index
        self._index = VectorStoreIndex.from_documents(documents)
        self._query_engine = self._index.as_query_engine(
            similarity_top_k=self.similarity_top_k
        )

    def query(self, question: str) -> Any:
        """Query the documents."""
        self._build_index()
        return self._query_engine.query(question)

    def retrieve(self, query: str) -> List[Any]:
        """Retrieve relevant nodes without generation."""
        self._build_index()
        retriever = self._index.as_retriever(similarity_top_k=self.similarity_top_k)
        return retriever.retrieve(query)
