"""
Vector Store Integration for Docling Processor

Factory pattern for connecting to various vector databases.
Supports: Pinecone, Milvus, Weaviate, Qdrant, FAISS, Chroma
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Any, Dict

logger = logging.getLogger(__name__)


class VectorStoreType(Enum):
    """Supported vector store types."""
    FAISS = "faiss"
    CHROMA = "chroma"
    PINECONE = "pinecone"
    MILVUS = "milvus"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"


@dataclass
class VectorStoreConfig:
    """Configuration for vector store connection."""
    store_type: VectorStoreType
    collection_name: str = "docling_documents"

    # Connection settings (varies by store type)
    host: Optional[str] = None
    port: Optional[int] = None
    api_key: Optional[str] = None
    environment: Optional[str] = None

    # Index settings
    dimension: int = 384  # Default for MiniLM
    metric: str = "cosine"

    # FAISS/Chroma specific
    persist_directory: Optional[str] = None


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""

    def __init__(self, config: VectorStoreConfig, embeddings: Any):
        self.config = config
        self.embeddings = embeddings
        self._store = None

    @abstractmethod
    def add_documents(self, documents: List[Any]) -> List[str]:
        """Add documents to the store."""
        pass

    @abstractmethod
    def similarity_search(self, query: str, k: int = 5) -> List[Any]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """Delete documents by ID."""
        pass


class FAISSStore(BaseVectorStore):
    """FAISS vector store implementation."""

    def _get_store(self):
        if self._store is None:
            try:
                from langchain.vectorstores import FAISS
            except ImportError:
                raise ImportError("Install langchain: pip install langchain faiss-cpu")

            if self.config.persist_directory:
                persist_path = Path(self.config.persist_directory)
                if persist_path.exists():
                    self._store = FAISS.load_local(
                        str(persist_path),
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    return self._store

            # Create empty store - will be populated on first add
            self._store = None
        return self._store

    def add_documents(self, documents: List[Any]) -> List[str]:
        from langchain.vectorstores import FAISS

        if self._store is None:
            self._store = FAISS.from_documents(documents, self.embeddings)
        else:
            self._store.add_documents(documents)

        if self.config.persist_directory:
            self._store.save_local(self.config.persist_directory)

        return [doc.metadata.get("chunk_id", str(i)) for i, doc in enumerate(documents)]

    def similarity_search(self, query: str, k: int = 5) -> List[Any]:
        store = self._get_store()
        if store is None:
            return []
        return store.similarity_search(query, k=k)

    def delete(self, ids: List[str]) -> None:
        logger.warning("FAISS does not support deletion. Rebuild index instead.")


class ChromaStore(BaseVectorStore):
    """Chroma vector store implementation."""

    def _get_store(self):
        if self._store is None:
            try:
                from langchain.vectorstores import Chroma
            except ImportError:
                raise ImportError("Install chromadb: pip install chromadb")

            self._store = Chroma(
                collection_name=self.config.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.config.persist_directory,
            )
        return self._store

    def add_documents(self, documents: List[Any]) -> List[str]:
        store = self._get_store()
        return store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 5) -> List[Any]:
        store = self._get_store()
        return store.similarity_search(query, k=k)

    def delete(self, ids: List[str]) -> None:
        store = self._get_store()
        store.delete(ids)


class PineconeStore(BaseVectorStore):
    """Pinecone vector store implementation (managed, serverless)."""

    def _get_store(self):
        if self._store is None:
            try:
                from langchain.vectorstores import Pinecone
                from pinecone import Pinecone as PineconeClient
            except ImportError:
                raise ImportError("Install pinecone: pip install pinecone-client langchain-pinecone")

            pc = PineconeClient(api_key=self.config.api_key)

            # Check if index exists
            if self.config.collection_name not in pc.list_indexes().names():
                pc.create_index(
                    name=self.config.collection_name,
                    dimension=self.config.dimension,
                    metric=self.config.metric,
                    spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
                )

            self._store = Pinecone.from_existing_index(
                index_name=self.config.collection_name,
                embedding=self.embeddings
            )
        return self._store

    def add_documents(self, documents: List[Any]) -> List[str]:
        store = self._get_store()
        return store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 5) -> List[Any]:
        store = self._get_store()
        return store.similarity_search(query, k=k)

    def delete(self, ids: List[str]) -> None:
        store = self._get_store()
        store.delete(ids)


class MilvusStore(BaseVectorStore):
    """Milvus vector store implementation (self-hosted, billion-scale)."""

    def _get_store(self):
        if self._store is None:
            try:
                from langchain.vectorstores import Milvus
            except ImportError:
                raise ImportError("Install pymilvus: pip install pymilvus langchain")

            connection_args = {
                "host": self.config.host or "localhost",
                "port": self.config.port or 19530,
            }

            self._store = Milvus(
                embedding_function=self.embeddings,
                collection_name=self.config.collection_name,
                connection_args=connection_args,
            )
        return self._store

    def add_documents(self, documents: List[Any]) -> List[str]:
        store = self._get_store()
        return store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 5) -> List[Any]:
        store = self._get_store()
        return store.similarity_search(query, k=k)

    def delete(self, ids: List[str]) -> None:
        store = self._get_store()
        store.delete(ids)


class WeaviateStore(BaseVectorStore):
    """Weaviate vector store implementation (hybrid search)."""

    def _get_store(self):
        if self._store is None:
            try:
                from langchain.vectorstores import Weaviate
                import weaviate
            except ImportError:
                raise ImportError("Install weaviate: pip install weaviate-client langchain")

            client = weaviate.Client(
                url=f"http://{self.config.host or 'localhost'}:{self.config.port or 8080}"
            )

            self._store = Weaviate(
                client=client,
                index_name=self.config.collection_name,
                text_key="text",
                embedding=self.embeddings,
            )
        return self._store

    def add_documents(self, documents: List[Any]) -> List[str]:
        store = self._get_store()
        return store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 5) -> List[Any]:
        store = self._get_store()
        return store.similarity_search(query, k=k)

    def delete(self, ids: List[str]) -> None:
        store = self._get_store()
        store.delete(ids)


class QdrantStore(BaseVectorStore):
    """Qdrant vector store implementation (filtered retrieval)."""

    def _get_store(self):
        if self._store is None:
            try:
                from langchain.vectorstores import Qdrant
                from qdrant_client import QdrantClient
            except ImportError:
                raise ImportError("Install qdrant: pip install qdrant-client langchain")

            client = QdrantClient(
                host=self.config.host or "localhost",
                port=self.config.port or 6333,
            )

            self._store = Qdrant(
                client=client,
                collection_name=self.config.collection_name,
                embeddings=self.embeddings,
            )
        return self._store

    def add_documents(self, documents: List[Any]) -> List[str]:
        store = self._get_store()
        return store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 5) -> List[Any]:
        store = self._get_store()
        return store.similarity_search(query, k=k)

    def delete(self, ids: List[str]) -> None:
        store = self._get_store()
        store.delete(ids)


class VectorStoreFactory:
    """
    Factory for creating vector store instances.

    Usage:
        from docling_processor.integrations import VectorStoreFactory

        # Create FAISS store (local, fast)
        store = VectorStoreFactory.create(
            store_type="faiss",
            embeddings=your_embeddings,
            persist_directory="./vector_db"
        )

        # Create Pinecone store (managed, serverless)
        store = VectorStoreFactory.create(
            store_type="pinecone",
            embeddings=your_embeddings,
            api_key="your-api-key",
            collection_name="docling-docs"
        )

        # Add documents
        from docling_processor.integrations import DoclingRAGLoader
        loader = DoclingRAGLoader("./pdfs/")
        documents = loader.load()
        store.add_documents(documents)

        # Search
        results = store.similarity_search("What is the main topic?", k=5)
    """

    _STORE_CLASSES = {
        VectorStoreType.FAISS: FAISSStore,
        VectorStoreType.CHROMA: ChromaStore,
        VectorStoreType.PINECONE: PineconeStore,
        VectorStoreType.MILVUS: MilvusStore,
        VectorStoreType.WEAVIATE: WeaviateStore,
        VectorStoreType.QDRANT: QdrantStore,
    }

    @classmethod
    def create(
        cls,
        store_type: str,
        embeddings: Any,
        collection_name: str = "docling_documents",
        host: Optional[str] = None,
        port: Optional[int] = None,
        api_key: Optional[str] = None,
        persist_directory: Optional[str] = None,
        dimension: int = 384,
        **kwargs
    ) -> BaseVectorStore:
        """
        Create a vector store instance.

        Args:
            store_type: Type of store (faiss, chroma, pinecone, milvus, weaviate, qdrant)
            embeddings: Embedding model instance
            collection_name: Name of the collection/index
            host: Host for self-hosted stores
            port: Port for self-hosted stores
            api_key: API key for managed stores
            persist_directory: Directory for local persistence
            dimension: Vector dimension (default 384 for MiniLM)

        Returns:
            Configured vector store instance
        """
        try:
            store_enum = VectorStoreType(store_type.lower())
        except ValueError:
            raise ValueError(
                f"Unknown store type: {store_type}. "
                f"Supported: {[t.value for t in VectorStoreType]}"
            )

        config = VectorStoreConfig(
            store_type=store_enum,
            collection_name=collection_name,
            host=host,
            port=port,
            api_key=api_key,
            persist_directory=persist_directory,
            dimension=dimension,
        )

        store_class = cls._STORE_CLASSES[store_enum]
        return store_class(config, embeddings)

    @classmethod
    def list_supported(cls) -> List[str]:
        """List supported vector store types."""
        return [t.value for t in VectorStoreType]
