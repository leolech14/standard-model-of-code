# Docling Batch Processor

**Tool ID:** T054
**Status:** Working
**Subsystem:** WAVE (Context/Intelligence)

Production-ready batch processor for 82 academic PDFs using IBM Docling.

## Features

- **4-tier fallback** for problematic PDFs (OCR → no_ocr → minimal → chunked)
- **Parcel/Waybill tracking** following Refinery logistics patterns
- **HybridChunker integration** for RAG-ready output
- **Batch processing** with checkpoint/resume capability
- **Atomic writes** to prevent corruption

## Quick Start

```bash
# Validate installation
python -m context_management.tools.docling_processor validate

# Process all PDFs
python -m context_management.tools.docling_processor process

# Process single file
python -m context_management.tools.docling_processor process \
    --file context-management/library/references/pdf/FRISTON_2019_FreeEnergyPrincipleParticularPhysics.pdf

# Check status
python -m context_management.tools.docling_processor status

# Resume failed batch
python -m context_management.tools.docling_processor resume --batch latest
```

## Configuration

Edit `context-management/config/docling_config.yaml`:

```yaml
input_dir: "context-management/library/references/pdf"
output_dir: "context-management/library/references/docling_output"
enable_ocr: true
enable_table_structure: true
enable_fallbacks: true
chunk_max_tokens: 512
omp_num_threads: 4
```

Override with environment variables:
- `DOCLING_INPUT_DIR`
- `DOCLING_OUTPUT_DIR`
- `OMP_NUM_THREADS`

## Output Structure

```
docling_output/
├── batch_YYYYMMDD_HHMMSS/
│   ├── manifest.json         # Batch metadata + results
│   ├── successful/           # Full conversions
│   │   ├── REF-001.md
│   │   ├── REF-001.json
│   │   └── REF-001_chunks.json
│   ├── partial/              # Fallback conversions
│   ├── failed/               # Error logs only
│   └── metadata/             # Waybills per file
└── latest -> batch_...       # Symlink to most recent
```

## Fallback Strategies

| Strategy | OCR | Tables | Use Case |
|----------|-----|--------|----------|
| `standard` | Yes | Yes | Default, handles scans |
| `no_ocr` | No | Yes | Text-native PDFs |
| `minimal` | No | No | Memory-constrained |
| `chunked` | No | No | Very large documents (20-page chunks) |

## Programmatic Usage

```python
from context_management.tools.docling_processor import DoclingProcessor, DoclingConfig

config = DoclingConfig.load()
processor = DoclingProcessor(config)

# Single file
result = processor.process_single(Path("paper.pdf"))
print(f"Status: {result.status}, Chunks: {result.chunk_count}")

# Batch processing
manifest = processor.process_batch()
print(f"Processed: {manifest.total_files}, Failed: {manifest.failed}")
```

## Integration Points

| Tool | Integration |
|------|-------------|
| `reference_analyzer.py` | Reads docling_output for enhanced analysis |
| `import_academic_foundations.py` | Uses DocTags JSON for Neo4j |
| `Refinery pipeline` | Chunks exported as RefineryNodes |
| `TOOLS_REGISTRY.yaml` | Registered as T054 |

## Dependencies

```
docling>=2.71.0
docling-ibm-models
docling-core
tqdm
pyyaml
```

## Troubleshooting

### Memory Issues
- Reduce `omp_num_threads` to 2
- Enable `enable_fallbacks: true`
- System will auto-fallback to minimal settings

### OCR Failures
- Fallback to `no_ocr` strategy automatically
- Check if PDF is text-native (try `pdftotext`)

### Large Documents
- Auto-fallback to chunked processing (20 pages at a time)
- Increase `max_page_limit` if needed

## Verification

```bash
# 1. Validate dependencies
python -m context_management.tools.docling_processor validate

# 2. Test single file
python -m context_management.tools.docling_processor process \
    --file context-management/library/references/pdf/FRISTON_2019_FreeEnergyPrincipleParticularPhysics.pdf

# 3. Check output
cat context-management/library/references/docling_output/latest/manifest.json | jq '.summary'

# 4. Full batch (all 82 papers)
python -m context_management.tools.docling_processor process
```
