# Docling-Granite Migration Specification

**Status:** IMPLEMENTED
**Tool ID:** T054
**Date:** 2026-01-31
**Implemented:** 2026-01-31

---

## Executive Summary

Replace manual PDF text extraction workflow with IBM Docling-Granite-258M for academic paper processing in the reference library.

---

## Current State

### Existing Tools
| ID | Tool | Function | Status |
|----|------|----------|--------|
| T050 | Academic Ontology Importer | Imports metadata → Neo4j | working |
| - | reference_analyzer.py | Scans/indexes references | working |
| - | Manual extraction | PDF → txt/ | problematic |

### Current Workflow
```
PDF → [manual/unknown] → txt/ → LLM analysis → metadata/*.json → Neo4j
          ↑
      PAIN POINT
      - Image extraction fails
      - Table structure lost
      - Equations broken
      - Inconsistent chunking
```

### Reference Library Stats
- **Location:** `context-management/archive/references/pdf/`
- **Papers:** 82 academic PDFs
- **Size:** ~575MB
- **Status:** Partially processed, many pending analysis

---

## Proposed State

### New Tool: T054 Docling-Granite
```
PDF → Docling-Granite → {markdown, json} → LLM analysis → metadata/*.json → Neo4j
          ↑
      IMPROVEMENT
      - Images with coordinates
      - Table topology preserved
      - LaTeX equations
      - DocTags for RAG
```

### Capabilities Comparison

| Aspect | Old System | Docling-Granite |
|--------|-----------|-----------------|
| **Model** | Unknown/manual | VLM 258M params |
| **Images** | Lost/problematic | Extracted with bbox |
| **Tables** | Structure lost | Topology preserved |
| **Equations** | Broken | LaTeX output |
| **Chunking** | Manual | DocTags structure |
| **Output** | Plain txt | MD/JSON/HTML |
| **RAG Ready** | No | Yes (designed for it) |

---

## Migration Plan

### Phase 1: Validation (Immediate)
1. Test Docling on 3 representative papers:
   - `REF-025_Shannon_1948` (classic, simple)
   - `FRISTON_2019_FreeEnergy` (equations heavy)
   - `KOESTLER_1964_ActOfCreation` (large, images)
2. Compare output quality to existing txt/
3. Document findings

### Phase 2: Batch Processing
1. Process all 82 papers through Docling
2. Output to new directory: `references/docling_output/`
3. Preserve old txt/ for comparison

### Phase 3: Integration
1. Update reference_analyzer.py to use Docling output
2. Update import_academic_foundations.py inputs
3. Rebuild Neo4j graph with richer metadata

### Phase 4: Deprecation
1. Archive old txt/ extraction workflow
2. Mark manual extraction as DEPRECATED
3. Update TOOLS_REGISTRY.yaml

---

## Technical Details

### Installation
```bash
pip install docling
```

### Invocation (T054)
```bash
# Single file
python -m context_management.tools.docling_processor process --file {input_pdf}

# Batch (all PDFs)
python -m context_management.tools.docling_processor process

# With PYTHONPATH if needed
PYTHONPATH=context-management/tools python -m docling_processor process
```

### Output Structure
```
docling_output/
├── REF-001/
│   ├── REF-001.md           # Structured markdown
│   ├── REF-001.json         # DocTags JSON
│   └── images/              # Extracted images with coords
├── REF-002/
│   └── ...
```

### Integration Points
- **reference_analyzer.py:** Read from docling_output/ instead of txt/
- **import_academic_foundations.py:** Parse richer metadata from JSON
- **Refinery pipeline:** Use DocTags for better chunking

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Docling fails on scanned PDFs | Use OCR fallback (built-in) |
| Different output format breaks pipeline | Phase 2 parallel processing |
| Loss of existing annotations | Keep txt/ archived |

---

## Success Criteria

1. ✓ All 82 papers processed without errors
2. ✓ Image extraction rate > 90%
3. ✓ Equation preservation verified on 5 papers
4. ✓ Table structure matches source in 3 test cases
5. ✓ Neo4j import works with new format

---

## References

- [IBM Granite-Docling Docs](https://www.ibm.com/granite/docs/models/docling)
- [Docling GitHub](https://github.com/DS4SD/docling)
- [Build Multimodal RAG Tutorial](https://www.ibm.com/think/tutorials/build-multimodal-rag-langchain-with-docling-granite)
