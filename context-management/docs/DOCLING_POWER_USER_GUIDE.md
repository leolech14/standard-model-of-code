# Docling Power User Guide

> Persistent knowledge from research. Every pattern here is implementation-ready.

## Quick Reference

```bash
# Validate installation
python -m docling_processor validate

# Process single file
python -m docling_processor process --file path/to/doc.pdf

# Batch process (82 PDFs)
python -m docling_processor process

# Resume interrupted batch
python -m docling_processor resume --batch batch_20260131_045514

# Export chunks for RAG
python -m docling_processor export-chunks --batch latest
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DOCLING PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│  INPUT          PROCESSING              OUTPUT                  │
│  ─────          ──────────              ──────                  │
│  PDF ──┐                                                        │
│  DOCX ─┼──► Parser ──► Layout ──► Tables ──► Chunks ──► JSON   │
│  PPTX ─┤    Backend   Analysis   Former     (RAG)      MD      │
│  HTML ─┤                                               Chunks   │
│  IMG ──┘    ▼                    ▼                              │
│             OCR                  VLM                            │
│             (optional)           (optional)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Fallback Strategy (4-Tier)

| Tier | Strategy | Use Case |
|------|----------|----------|
| 1 | `standard` | Default - full OCR + tables |
| 2 | `no_ocr` | Born-digital PDFs, text-native |
| 3 | `minimal` | Problematic layouts |
| 4 | `chunked` | Very large files, memory issues |

## GPU Acceleration

### NVIDIA CUDA

```python
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions

# RTX 4090 (24GB) - optimal config
accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CUDA)
pipeline_options = ThreadedPdfPipelineOptions(
    ocr_batch_size=64,
    layout_batch_size=64,
    table_batch_size=4
)
```

### Batch Size by GPU

| GPU | VRAM | Batch Size |
|-----|------|------------|
| RTX 5090 | 32GB | 64-128 |
| RTX 4090 | 24GB | 32-64 |
| RTX 5070 | 12GB | 16-32 |
| Apple M1/M2/M3 | Unified | 16-32 (MPS) |

### vLLM Server (6x speedup)

```bash
vllm serve ibm-granite/granite-docling-258M \
  --host 127.0.0.1 --port 8000 \
  --max-num-seqs 512 \
  --max-num-batched-tokens 8192 \
  --enable-chunked-prefill \
  --gpu-memory-utilization 0.9
```

## Framework Integrations

### LangChain

```python
from langchain_community.document_loaders import DoclingLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

# Load with Docling
loader = DoclingLoader("document.pdf")
documents = loader.load()

# Build RAG
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
qa_chain = RetrievalQA.from_chain_type(
    llm=your_llm,
    retriever=vectorstore.as_retriever()
)

response = qa_chain.run("What is this document about?")
```

### LlamaIndex

```python
from llama_index.readers.docling import DoclingReader
from llama_index import VectorStoreIndex

reader = DoclingReader()
documents = reader.load_data("document.pdf")

index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

response = query_engine.query("Summarize this document")
```

### Haystack

```python
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import DoclingConverter
from haystack.pipelines import Pipeline

converter = DoclingConverter()
documents = converter.convert("document.pdf")

document_store = InMemoryDocumentStore()
document_store.write_documents(documents)
```

## Vector Database Integration

### Pinecone (Managed)

```python
from pinecone import Pinecone
from langchain.vectorstores import Pinecone as PineconeStore

# Best for: Rapid prototyping, serverless
index = PineconeStore.from_documents(
    docs,
    embeddings,
    index_name="docling-index"
)
```

### Milvus (Self-Hosted, Billion-Scale)

```python
from pymilvus import connections, Collection

# Best for: On-premises, cost efficiency at scale
connections.connect("default", host="localhost", port="19530")
```

### Weaviate (Hybrid Search)

```python
from weaviate import Client

# Best for: Hybrid vector + keyword search
client = Client("http://localhost:8080")
```

### Qdrant (Filtered Retrieval)

```python
from qdrant_client import QdrantClient

# Best for: Rich metadata filtering
client = QdrantClient("localhost", port=6333)
```

## Enterprise Deployment

### Docling Serve (API Server)

```bash
# Docker deployment
podman run -p 5001:5001 -e DOCLING_SERVE_ENABLE_UI=1 \
  quay.io/docling-project/docling-serve

# API call
curl -X 'POST' 'http://localhost:5001/v1/convert/source' \
  -H 'Content-Type: application/json' \
  -d '{"sources": [{"kind": "http", "url": "https://example.com/doc.pdf"}]}'
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-serve
spec:
  replicas: 3
  selector:
    matchLabels:
      app: docling-serve
  template:
    spec:
      containers:
      - name: docling-serve
        image: quay.io/docling-project/docling-serve
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
        ports:
        - containerPort: 5001
```

## Error Handling Patterns

### Circuit Breaker

```python
from dataclasses import dataclass
from typing import Set

@dataclass
class CircuitBreaker:
    failed_docs: Set[str] = field(default_factory=set)
    max_failures: int = 3

    def should_skip(self, doc_id: str) -> bool:
        return doc_id in self.failed_docs

    def record_failure(self, doc_id: str):
        self.failed_docs.add(doc_id)
```

### Resume Pattern

```python
import json
from pathlib import Path

def load_progress(log_path: Path) -> dict:
    if log_path.exists():
        return json.loads(log_path.read_text())
    return {"processed": [], "failed": [], "timestamp": None}

def save_progress(log_path: Path, progress: dict):
    log_path.write_text(json.dumps(progress, indent=2))

# Usage
progress = load_progress(Path("progress.json"))
for doc in all_docs:
    if doc in progress["processed"]:
        continue
    # Process...
    progress["processed"].append(doc)
    save_progress(Path("progress.json"), progress)
```

## Performance Benchmarks

| Config | Pages/Second | Use Case |
|--------|--------------|----------|
| CPU-only | 1.5-3.0 | Development |
| GPU (CUDA) | 6-12 | Production |
| VLM + vLLM | 2-4.5 | Multimodal |
| Distributed (Ray) | 50+ | Enterprise |

## Chunking for RAG

### HybridChunker (Recommended)

```python
from docling_core.transforms.chunker import HybridChunker

chunker = HybridChunker(
    max_tokens=512,
    overlap_tokens=50
)

chunks = chunker.chunk(docling_document)
```

### Chunk Strategy by Use Case

| Use Case | max_tokens | overlap |
|----------|------------|---------|
| Dense retrieval | 256-512 | 50 |
| Summarization | 1024-2048 | 100 |
| Q&A | 512 | 50 |
| Code docs | 1024 | 100 |

## Comparison: Docling vs Alternatives

| Feature | Docling | LlamaParse | Unstructured |
|---------|---------|------------|--------------|
| Table accuracy | 94%+ | 90%+ | 85%+ |
| Open source | Yes | No | Partial |
| On-premises | Yes | No | Yes |
| GPU acceleration | Yes | Cloud | Yes |
| Forms/checkboxes | Limited | Good | Good |
| Handwriting | No | Limited | Limited |

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| OOM on large PDF | Reduce batch size, enable chunked fallback |
| Timeout | Increase `document_timeout`, split PDF |
| Poor table extraction | Enable `do_table_structure=True` |
| Missing text | Enable OCR with `do_ocr=True` |
| Slow processing | Use GPU, reduce enrichments |

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("docling").setLevel(logging.DEBUG)
```

## References

- [IBM Docling GitHub](https://github.com/docling-project/docling)
- [Docling Serve](https://github.com/docling-project/docling-serve)
- [Research Paper](https://arxiv.org/abs/2408.09869)
- [Integration Docs](https://docling.site/integrations/)
