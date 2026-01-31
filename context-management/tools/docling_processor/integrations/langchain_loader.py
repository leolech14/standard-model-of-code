"""
LangChain Integration for Docling Processor

Provides DoclingRAGLoader for seamless LangChain RAG pipeline integration.
"""

import logging
from pathlib import Path
from typing import List, Optional, Iterator, Dict, Any

logger = logging.getLogger(__name__)


class DoclingRAGLoader:
    """
    LangChain-compatible document loader using Docling.

    Converts PDFs to LangChain Document objects with metadata preservation.
    Supports batch processing, chunking, and fallback strategies.

    Usage:
        from docling_processor.integrations import DoclingRAGLoader

        loader = DoclingRAGLoader("document.pdf")
        documents = loader.load()

        # With FAISS
        from langchain.vectorstores import FAISS
        vectorstore = FAISS.from_documents(documents, embeddings)
    """

    def __init__(
        self,
        file_path: str,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        use_fallback: bool = True,
        include_tables: bool = True,
        include_images: bool = False,
    ):
        """
        Initialize the Docling RAG Loader.

        Args:
            file_path: Path to PDF file or directory
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Overlap tokens between chunks
            use_fallback: Enable 4-tier fallback for problematic PDFs
            include_tables: Include table content in output
            include_images: Include image descriptions (requires VLM)
        """
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_fallback = use_fallback
        self.include_tables = include_tables
        self.include_images = include_images

    def load(self) -> List[Any]:
        """
        Load and convert documents to LangChain Document format.

        Returns:
            List of LangChain Document objects
        """
        try:
            from langchain.schema import Document
        except ImportError:
            raise ImportError(
                "langchain is required for this integration. "
                "Install with: pip install langchain"
            )

        from ..processor import DoclingProcessor
        from ..config import DoclingConfig
        from ..chunker import DoclingChunker

        config = DoclingConfig.load()
        config.chunk_max_tokens = self.chunk_size
        config.chunk_overlap_tokens = self.chunk_overlap
        config.enable_fallbacks = self.use_fallback

        processor = DoclingProcessor(config)
        chunker = DoclingChunker(config)

        documents = []

        if self.file_path.is_file():
            files = [self.file_path]
        else:
            files = list(self.file_path.glob("*.pdf"))

        for pdf_file in files:
            result = processor.process_single(pdf_file)

            if result.status == "failed":
                logger.warning(f"Failed to process {pdf_file}: {result.error_message}")
                continue

            # Get chunks
            chunks = chunker.chunk_result(result)

            for chunk in chunks:
                doc = Document(
                    page_content=chunk.get("text", ""),
                    metadata={
                        "source": str(pdf_file),
                        "ref_id": result.ref_id,
                        "parcel_id": result.parcel_id,
                        "chunk_id": chunk.get("chunk_id"),
                        "page_numbers": chunk.get("page_numbers", []),
                        "section": chunk.get("section"),
                        "token_count": chunk.get("token_count"),
                        "strategy_used": result.strategy_used,
                    }
                )
                documents.append(doc)

        logger.info(f"Loaded {len(documents)} chunks from {len(files)} files")
        return documents

    def lazy_load(self) -> Iterator[Any]:
        """
        Lazily load documents one at a time.

        Yields:
            LangChain Document objects
        """
        for doc in self.load():
            yield doc


class DoclingQAChain:
    """
    Pre-configured QA chain using Docling + LangChain.

    Usage:
        qa = DoclingQAChain(
            documents_path="./pdfs/",
            llm=your_llm,
            embeddings=your_embeddings
        )
        answer = qa.ask("What is the main topic?")
    """

    def __init__(
        self,
        documents_path: str,
        llm: Any,
        embeddings: Any,
        vector_store_type: str = "faiss",
    ):
        self.documents_path = documents_path
        self.llm = llm
        self.embeddings = embeddings
        self.vector_store_type = vector_store_type
        self._chain = None
        self._vectorstore = None

    def _build_chain(self):
        """Build the QA chain lazily."""
        if self._chain is not None:
            return

        try:
            from langchain.chains import RetrievalQA
            from langchain.vectorstores import FAISS
        except ImportError:
            raise ImportError("langchain required: pip install langchain")

        # Load documents
        loader = DoclingRAGLoader(self.documents_path)
        documents = loader.load()

        # Build vector store
        if self.vector_store_type == "faiss":
            self._vectorstore = FAISS.from_documents(documents, self.embeddings)
        else:
            raise ValueError(f"Unsupported vector store: {self.vector_store_type}")

        # Build chain
        self._chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self._vectorstore.as_retriever(search_kwargs={"k": 5})
        )

    def ask(self, question: str) -> str:
        """Ask a question about the documents."""
        self._build_chain()
        return self._chain.run(question)

    def similarity_search(self, query: str, k: int = 5) -> List[Any]:
        """Find similar chunks without LLM."""
        self._build_chain()
        return self._vectorstore.similarity_search(query, k=k)
