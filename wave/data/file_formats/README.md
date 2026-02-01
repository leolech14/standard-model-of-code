# File Format Intelligence

Canonical repository for computer file format knowledge, metadata standards, and editing capabilities.

## Contents

### Core Files

| File | Purpose |
|------|---------|
| `format_taxonomy.json` | Complete taxonomy of 80+ file formats organized by category |
| `metadata_schema.json` | JSON Schema for universal file metadata storage |
| `magic_bytes.json` | Magic byte signatures for format detection (TBD) |
| `edit_toolkits.json` | Editing tool configurations per format (TBD) |

### Schema Structure

```
FileMetadata
├── core           # Path, name, size, dates (required)
├── technical      # Format-specific: dimensions, codec, bitrate
├── descriptive    # Dublin Core: title, description, keywords
├── creator        # Author, artist, contributors
├── rights         # Copyright, license
├── location       # GPS coordinates
├── exif           # Camera/image metadata
├── audio          # ID3/Vorbis tags
├── document       # PDF/Office properties
├── model3d        # 3D geometry stats
├── archive        # Archive contents
├── code           # Source analysis
├── xmp            # Raw XMP preservation
├── native         # Unmapped format-specific tags
└── custom         # User extensions
```

### Format Categories

1. **Image Raster** - JPEG, PNG, GIF, WebP, AVIF, TIFF, BMP, HEIC
2. **Image Vector** - SVG, AI, EPS
3. **Video** - MP4, WebM, MOV, AVI, MKV
4. **Audio** - MP3, WAV, FLAC, OGG, AAC, M4A, AIFF
5. **Document** - PDF, DOCX, XLSX, PPTX, ODT, RTF, TXT, MD
6. **Code** - JavaScript, TypeScript, Python, HTML, CSS, JSON, YAML, XML
7. **3D Model** - GLTF, GLB, OBJ, STL, FBX, USDZ
8. **Archive** - ZIP, TAR, GZIP, 7Z, RAR
9. **Font** - TTF, OTF, WOFF, WOFF2
10. **Data** - CSV, TSV, Parquet, SQLite

### Metadata Standards Covered

- **EXIF** - Exchangeable Image File Format (cameras)
- **IPTC** - International Press Telecommunications Council (editorial)
- **XMP** - Extensible Metadata Platform (universal)
- **Dublin Core** - Resource description (documents)
- **ID3** - Audio tags (MP3)
- **Vorbis Comments** - Audio tags (FLAC/OGG)
- **JSON-LD** - Linked data (web)
- **OpenType** - Font metadata

### Usage

```typescript
import taxonomy from './format_taxonomy.json';
import schema from './metadata_schema.json';

// Get format info
const jpegInfo = taxonomy.categories.image_raster.formats.jpeg;
console.log(jpegInfo.mimeTypes);     // ['image/jpeg']
console.log(jpegInfo.metadataStandards); // ['EXIF', 'IPTC', 'XMP']
console.log(jpegInfo.editLibraries.primary); // 'fabric'

// Validate metadata
import Ajv from 'ajv';
const ajv = new Ajv();
const validate = ajv.compile(schema);
const valid = validate(fileMetadata);
```

### Research Sources

- Perplexity Research: File Format Taxonomy (2026-01-31)
- Perplexity Research: Open Source Editors (2026-01-31)
- Perplexity Research: Metadata Standards (2026-01-31)
- IANA MIME Types Registry
- Gary Kessler's File Signatures Table
- W3C Media Type Specifications
- EXIF.org Specifications
- ID3.org Tag Specifications

## Related

- `tools/file_explorer.py` - File explorer using this data
- `tools/FILE_EDITOR_SIDEBAR_PLAN.md` - Implementation plan
- `particle/` - Theoretical framework

---
*Part of PROJECT_elements Context Management System*
