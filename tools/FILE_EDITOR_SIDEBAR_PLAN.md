# File Editor Sidebar - Strategic Implementation Plan

## Executive Summary

A comprehensive editing sidebar integrated into the file preview lightbox, providing format-specific toolkits for manipulating files directly in the browser. The sidebar appears to the left of the file content, with tools dynamically loaded based on file type category.

---

## Architecture Overview

```
+------------------+----------------------------------------+
|                  |                                        |
|   EDIT SIDEBAR   |         FILE PREVIEW CONTENT           |
|   (Dynamic)      |         (Lightbox Inner)               |
|                  |                                        |
|   - Tools        |   [Image/Video/Code/Document/etc.]     |
|   - Properties   |                                        |
|   - Metadata     |                                        |
|   - Actions      |                                        |
|                  |                                        |
+------------------+----------------------------------------+
     280px                      Flexible
```

---

## Canonical File Format Taxonomy

### Category 1: IMAGES (Raster)
| Format | MIME Type | Magic Bytes | Metadata Standards | Edit Library |
|--------|-----------|-------------|-------------------|--------------|
| JPEG | image/jpeg | `FF D8 FF` | EXIF, IPTC, XMP | Fabric.js, Cropper.js |
| PNG | image/png | `89 50 4E 47` | XMP, tEXt chunks | Fabric.js |
| GIF | image/gif | `47 49 46 38` | XMP | gif.js |
| WebP | image/webp | `52 49 46 46` | EXIF, XMP | Fabric.js |
| AVIF | image/avif | HEIF container | EXIF, XMP | (limited) |
| TIFF | image/tiff | `49 49 2A 00` | EXIF, IPTC, XMP | (server-side) |
| BMP | image/bmp | `42 4D` | None | Fabric.js |
| HEIC | image/heic | HEIF container | EXIF, XMP | heic2any.js |

### Category 2: IMAGES (Vector)
| Format | MIME Type | Magic Bytes | Metadata Standards | Edit Library |
|--------|-----------|-------------|-------------------|--------------|
| SVG | image/svg+xml | `<svg` or `<?xml` | XMP embedded | SVG.js, Fabric.js |
| AI | application/illustrator | `%PDF` | XMP | (view only) |
| EPS | application/postscript | `%!PS` | XMP | (view only) |

### Category 3: VIDEO
| Format | MIME Type | Magic Bytes | Metadata Standards | Edit Library |
|--------|-----------|-------------|-------------------|--------------|
| MP4 | video/mp4 | `66 74 79 70` | XMP, iTunes atoms | Video.js, ffmpeg.wasm |
| WebM | video/webm | `1A 45 DF A3` | Matroska metadata | Video.js |
| MOV | video/quicktime | `66 74 79 70` | QuickTime metadata | Video.js |
| AVI | video/x-msvideo | `52 49 46 46` | RIFF INFO | Video.js |
| MKV | video/x-matroska | `1A 45 DF A3` | Matroska metadata | Video.js |

### Category 4: AUDIO
| Format | MIME Type | Magic Bytes | Metadata Standards | Edit Library |
|--------|-----------|-------------|-------------------|--------------|
| MP3 | audio/mpeg | `FF FB` or `49 44 33` | ID3v1, ID3v2 | Tone.js, Wavesurfer.js |
| WAV | audio/wav | `52 49 46 46` | RIFF INFO, BWF | Wavesurfer.js |
| FLAC | audio/flac | `66 4C 61 43` | Vorbis comments | Wavesurfer.js |
| OGG | audio/ogg | `4F 67 67 53` | Vorbis comments | Wavesurfer.js |
| AAC | audio/aac | `FF F1` | ID3, iTunes | Wavesurfer.js |
| M4A | audio/mp4 | `66 74 79 70` | iTunes atoms | Wavesurfer.js |
| AIFF | audio/aiff | `46 4F 52 4D` | AIFF chunks | Wavesurfer.js |

### Category 5: DOCUMENTS
| Format | MIME Type | Magic Bytes | Metadata Standards | Edit Library |
|--------|-----------|-------------|-------------------|--------------|
| PDF | application/pdf | `25 50 44 46` | XMP, Dublin Core | pdf-lib, PDF.js |
| DOCX | application/vnd...wordprocessingml | `50 4B 03 04` | Office Open XML | mammoth.js |
| XLSX | application/vnd...spreadsheetml | `50 4B 03 04` | Office Open XML | SheetJS |
| PPTX | application/vnd...presentationml | `50 4B 03 04` | Office Open XML | (view only) |
| ODT | application/vnd.oasis.opendocument | `50 4B 03 04` | ODF metadata | (parse only) |
| RTF | application/rtf | `7B 5C 72 74 66` | Limited | (parse only) |
| TXT | text/plain | None | None | Monaco Editor |
| MD | text/markdown | None | YAML frontmatter | EasyMDE |

### Category 6: CODE
| Format | MIME Type | Extensions | Syntax | Edit Library |
|--------|-----------|------------|--------|--------------|
| JavaScript | text/javascript | .js, .mjs | ES2024 | Monaco Editor |
| TypeScript | text/typescript | .ts, .tsx | TypeScript 5.x | Monaco Editor |
| Python | text/x-python | .py, .pyw | Python 3.x | Monaco Editor |
| HTML | text/html | .html, .htm | HTML5 | Monaco Editor |
| CSS | text/css | .css, .scss, .less | CSS3+ | Monaco Editor |
| JSON | application/json | .json | JSON/JSON5 | Monaco Editor, JSON Hero |
| YAML | application/yaml | .yaml, .yml | YAML 1.2 | Monaco Editor |
| XML | application/xml | .xml | XML 1.1 | Monaco Editor |
| SQL | application/sql | .sql | Various dialects | Monaco Editor |
| Shell | application/x-sh | .sh, .bash, .zsh | Bash/Zsh | Monaco Editor |
| Rust | text/x-rust | .rs | Rust 2024 | Monaco Editor |
| Go | text/x-go | .go | Go 1.22+ | Monaco Editor |
| C/C++ | text/x-c | .c, .cpp, .h | C23/C++23 | Monaco Editor |
| Java | text/x-java | .java | Java 21+ | Monaco Editor |
| Swift | text/x-swift | .swift | Swift 5.x | Monaco Editor |
| Kotlin | text/x-kotlin | .kt, .kts | Kotlin 2.x | Monaco Editor |

### Category 7: DATA
| Format | MIME Type | Magic Bytes | Schema | Edit Library |
|--------|-----------|-------------|--------|--------------|
| JSON | application/json | None | JSON Schema | JSON Hero, Monaco |
| CSV | text/csv | None | None | PapaParse + grid |
| TSV | text/tab-separated-values | None | None | PapaParse + grid |
| XML | application/xml | `3C 3F 78 6D 6C` | XSD, DTD | Monaco Editor |
| YAML | application/yaml | None | JSON Schema | Monaco Editor |
| TOML | application/toml | None | TOML spec | Monaco Editor |
| INI | text/plain | None | Informal | Monaco Editor |
| Protobuf | application/protobuf | None | .proto schema | Monaco Editor |
| Parquet | application/parquet | `50 41 52 31` | Arrow schema | (read only) |
| SQLite | application/x-sqlite3 | `53 51 4C 69` | SQL schema | sql.js |

### Category 8: 3D MODELS
| Format | MIME Type | Magic Bytes | Metadata | View/Edit Library |
|--------|-----------|-------------|----------|-------------------|
| GLTF | model/gltf+json | `{"` (JSON) | Embedded | Three.js, Babylon.js |
| GLB | model/gltf-binary | `67 6C 54 46` | Embedded | Three.js, Babylon.js |
| OBJ | model/obj | None (text) | MTL file | Three.js |
| STL | model/stl | `73 6F 6C 69 64` | Header only | Three.js |
| FBX | application/octet-stream | Various | Embedded | Three.js (limited) |
| USDZ | model/vnd.usdz+zip | `50 4B 03 04` | USD metadata | Model-Viewer |
| DAE | model/vnd.collada+xml | `<?xml` | XML metadata | Three.js |

### Category 9: ARCHIVES
| Format | MIME Type | Magic Bytes | Metadata | Library |
|--------|-----------|-------------|----------|---------|
| ZIP | application/zip | `50 4B 03 04` | Central directory | libarchive.js |
| TAR | application/x-tar | `75 73 74 61 72` | Header | libarchive.js |
| GZIP | application/gzip | `1F 8B` | Header | pako.js |
| 7Z | application/x-7z-compressed | `37 7A BC AF` | Header | libarchive.js |
| RAR | application/vnd.rar | `52 61 72 21` | Header | libarchive.js |
| BZIP2 | application/x-bzip2 | `42 5A 68` | None | (decompress only) |

### Category 10: FONTS
| Format | MIME Type | Magic Bytes | Metadata | Library |
|--------|-----------|-------------|----------|---------|
| TTF | font/ttf | `00 01 00 00` | OpenType tables | opentype.js |
| OTF | font/otf | `4F 54 54 4F` | OpenType tables | opentype.js |
| WOFF | font/woff | `77 4F 46 46` | Compressed OT | opentype.js |
| WOFF2 | font/woff2 | `77 4F 46 32` | Compressed OT | opentype.js |

---

## Metadata Schema (Extensible)

```typescript
interface FileMetadataSchema {
  // Core (all files)
  core: {
    path: string;
    name: string;
    extension: string;
    mimeType: string;
    size: number;
    created: Date;
    modified: Date;
    accessed: Date;
  };

  // Technical (format-specific)
  technical: {
    format: string;           // e.g., "JPEG", "PNG"
    version?: string;         // e.g., "1.0", "2.0"
    encoding?: string;        // e.g., "UTF-8", "base64"
    compression?: string;     // e.g., "DEFLATE", "LZW"
    colorSpace?: string;      // e.g., "sRGB", "Adobe RGB"
    bitDepth?: number;
    dimensions?: { width: number; height: number };
    duration?: number;        // seconds for media
    sampleRate?: number;      // Hz for audio
    bitRate?: number;         // bps for media
    frameRate?: number;       // fps for video
    channels?: number;        // audio channels
    codec?: string;
  };

  // Descriptive (content)
  descriptive: {
    title?: string;
    description?: string;
    keywords?: string[];
    subject?: string;
    language?: string;
    category?: string;
  };

  // Creator/Rights
  rights: {
    creator?: string;
    author?: string;
    copyright?: string;
    license?: string;
    licenseUrl?: string;
    attribution?: string;
  };

  // Location (GPS)
  location?: {
    latitude?: number;
    longitude?: number;
    altitude?: number;
    accuracy?: number;
    placeName?: string;
  };

  // Image-specific (EXIF)
  exif?: {
    make?: string;
    model?: string;
    lens?: string;
    focalLength?: number;
    aperture?: number;
    shutterSpeed?: string;
    iso?: number;
    flash?: boolean;
    whiteBalance?: string;
    exposureMode?: string;
    meteringMode?: string;
    orientation?: number;
    dateTimeOriginal?: Date;
  };

  // Audio-specific (ID3)
  audio?: {
    artist?: string;
    album?: string;
    albumArtist?: string;
    track?: number;
    totalTracks?: number;
    disc?: number;
    totalDiscs?: number;
    year?: number;
    genre?: string;
    composer?: string;
    bpm?: number;
    lyrics?: string;
    artwork?: string;  // base64 or URL
  };

  // Document-specific
  document?: {
    pageCount?: number;
    wordCount?: number;
    characterCount?: number;
    revision?: number;
    template?: string;
    application?: string;
  };

  // 3D Model-specific
  model3d?: {
    vertices?: number;
    faces?: number;
    materials?: number;
    textures?: number;
    animations?: number;
    bones?: number;
    boundingBox?: { min: [number, number, number]; max: [number, number, number] };
  };

  // Custom/Extension (open)
  custom?: Record<string, unknown>;

  // XMP (raw for preservation)
  xmp?: string;

  // Native format tags (raw)
  native?: Record<string, unknown>;
}
```

---

## Edit Toolkit by Category

### IMAGE TOOLKIT
```
+---------------------------+
| IMAGE TOOLS               |
+---------------------------+
| [Crop] [Rotate] [Flip]    |
| [Resize] [Scale]          |
+---------------------------+
| ADJUSTMENTS               |
| Brightness    [----o----] |
| Contrast      [----o----] |
| Saturation    [----o----] |
| Exposure      [----o----] |
| Highlights    [----o----] |
| Shadows       [----o----] |
+---------------------------+
| FILTERS                   |
| [Grayscale] [Sepia]       |
| [Invert] [Blur]           |
| [Sharpen] [Vignette]      |
+---------------------------+
| ANNOTATIONS               |
| [Text] [Arrow] [Shape]    |
| [Highlight] [Redact]      |
+---------------------------+
| METADATA                  |
| Title: [____________]     |
| Author: [___________]     |
| Copyright: [________]     |
| Keywords: [_________]     |
+---------------------------+
| [Reset] [Export] [Save]   |
+---------------------------+
```

**Libraries:**
- Fabric.js - Canvas manipulation, annotations
- Cropper.js - Cropping
- CamanJS - Filters and adjustments
- piexifjs - EXIF read/write
- FileSaver.js - Export

### VIDEO TOOLKIT
```
+---------------------------+
| VIDEO TOOLS               |
+---------------------------+
| Timeline                  |
| [=====|====|========]     |
| 00:00  01:23  03:45       |
+---------------------------+
| TRIM                      |
| Start: [00:00:15]         |
| End:   [00:03:30]         |
| [Set In] [Set Out]        |
+---------------------------+
| EXTRACT                   |
| [Frame as PNG]            |
| [Audio as MP3]            |
| [GIF from range]          |
+---------------------------+
| PLAYBACK                  |
| Speed: [0.5x][1x][2x]     |
| [Loop] [Mute]             |
+---------------------------+
| METADATA                  |
| Title: [____________]     |
| Artist: [___________]     |
+---------------------------+
| [Export Clip]             |
+---------------------------+
```

**Libraries:**
- Video.js - Playback
- ffmpeg.wasm - Processing (heavy)
- gif.js - GIF creation
- Wavesurfer.js - Audio waveform

### AUDIO TOOLKIT
```
+---------------------------+
| AUDIO TOOLS               |
+---------------------------+
| Waveform                  |
| [~~~~~|~~~~~|~~~~~]       |
| 00:00  02:15  04:30       |
+---------------------------+
| TRIM                      |
| Start: [00:00:10]         |
| End:   [00:04:20]         |
| [Set In] [Set Out]        |
+---------------------------+
| EFFECTS                   |
| [Fade In] [Fade Out]      |
| [Normalize] [Amplify]     |
+---------------------------+
| ID3 TAGS                  |
| Title:  [____________]    |
| Artist: [____________]    |
| Album:  [____________]    |
| Track:  [__] of [__]      |
| Year:   [____]            |
| Genre:  [▼ Select]        |
+---------------------------+
| ARTWORK                   |
| [+] Add Cover Art         |
| [Current artwork thumb]   |
+---------------------------+
| [Export] [Save Tags]      |
+---------------------------+
```

**Libraries:**
- Wavesurfer.js - Waveform display
- Tone.js - Audio processing
- music-metadata - Tag reading
- browser-id3-writer - Tag writing
- jsmediatags - Multi-format tags

### CODE TOOLKIT
```
+---------------------------+
| CODE TOOLS                |
+---------------------------+
| Language: [TypeScript ▼]  |
| Theme:    [Dark ▼]        |
+---------------------------+
| FORMAT                    |
| [Prettier] [ESLint Fix]   |
| Indent: [2][4][Tab]       |
+---------------------------+
| TRANSFORM                 |
| [Minify] [Beautify]       |
| [Sort imports]            |
| [Remove comments]         |
+---------------------------+
| ANALYZE                   |
| Lines: 245                |
| Characters: 8,432         |
| Functions: 12             |
| Classes: 3                |
+---------------------------+
| FIND & REPLACE            |
| Find:    [__________]     |
| Replace: [__________]     |
| [x] Regex  [ ] Case       |
+---------------------------+
| [Copy] [Download]         |
+---------------------------+
```

**Libraries:**
- Monaco Editor - Code editing
- Prettier - Formatting
- ESLint - Linting (via worker)
- Terser - Minification

### DOCUMENT (PDF) TOOLKIT
```
+---------------------------+
| PDF TOOLS                 |
+---------------------------+
| Pages: 1 of 24  [< >]     |
| Zoom: [Fit][100%][200%]   |
+---------------------------+
| ANNOTATIONS               |
| [Highlight] [Underline]   |
| [Strikethrough]           |
| [Comment] [Note]          |
| [Draw] [Stamp]            |
+---------------------------+
| EDIT                      |
| [Add Text] [Add Image]    |
| [Delete Page]             |
| [Rotate Page]             |
| [Extract Pages]           |
+---------------------------+
| FILL & SIGN               |
| [Fill Form]               |
| [Add Signature]           |
| [Add Date]                |
+---------------------------+
| METADATA                  |
| Title:   [___________]    |
| Author:  [___________]    |
| Subject: [___________]    |
| Keywords:[___________]    |
+---------------------------+
| [Export] [Print]          |
+---------------------------+
```

**Libraries:**
- PDF.js - Rendering
- pdf-lib - Editing/Creation
- pdf-annotate.js - Annotations
- jsPDF - Generation

### DATA (JSON/CSV) TOOLKIT
```
+---------------------------+
| DATA TOOLS                |
+---------------------------+
| View: [Tree][Table][Raw]  |
+---------------------------+
| TRANSFORM                 |
| [Format/Pretty]           |
| [Minify/Compact]          |
| [Sort Keys]               |
+---------------------------+
| QUERY (JMESPath)          |
| [___________________]     |
| [Run Query]               |
+---------------------------+
| VALIDATE                  |
| Schema: [Select...]       |
| Status: Valid             |
+---------------------------+
| CONVERT                   |
| [JSON <-> YAML]           |
| [JSON <-> CSV]            |
| [JSON <-> XML]            |
+---------------------------+
| STATS                     |
| Keys: 45                  |
| Arrays: 3                 |
| Depth: 4                  |
| Size: 12.4 KB             |
+---------------------------+
| [Copy] [Download]         |
+---------------------------+
```

**Libraries:**
- JSON Hero (inspiration)
- Monaco Editor
- js-yaml - YAML conversion
- PapaParse - CSV parsing
- ajv - JSON Schema validation
- jmespath - Query

### 3D MODEL TOOLKIT
```
+---------------------------+
| 3D TOOLS                  |
+---------------------------+
| View                      |
| [Orbit] [Pan] [Zoom]      |
| [Reset View]              |
+---------------------------+
| DISPLAY                   |
| [Wireframe] [Solid]       |
| [Textured] [Normals]      |
| [Bounding Box]            |
+---------------------------+
| LIGHTING                  |
| [Ambient] [Directional]   |
| [Point] [Spot]            |
| Intensity: [----o----]    |
+---------------------------+
| BACKGROUND                |
| [Dark] [Light] [HDRI]     |
+---------------------------+
| STATS                     |
| Vertices: 12,456          |
| Faces: 24,912             |
| Materials: 3              |
| Textures: 5               |
+---------------------------+
| EXPORT                    |
| [GLB] [OBJ] [STL]         |
| [Screenshot]              |
+---------------------------+
```

**Libraries:**
- Three.js - Rendering
- Babylon.js - Alternative
- model-viewer - Simple embed
- gltf-transform - Editing

### MARKDOWN TOOLKIT
```
+---------------------------+
| MARKDOWN TOOLS            |
+---------------------------+
| View: [Edit][Preview][Both]|
+---------------------------+
| FORMAT                    |
| [B] [I] [S] [Code]        |
| [H1][H2][H3]              |
| [Link] [Image]            |
| [Quote] [List] [Table]    |
+---------------------------+
| INSERT                    |
| [Checkbox]                |
| [Code Block]              |
| [Math (LaTeX)]            |
| [Diagram (Mermaid)]       |
+---------------------------+
| FRONTMATTER               |
| title: [___________]      |
| date:  [___________]      |
| tags:  [___________]      |
+---------------------------+
| EXPORT                    |
| [HTML] [PDF] [DOCX]       |
+---------------------------+
```

**Libraries:**
- EasyMDE - Editor
- marked - Parsing
- highlight.js - Code blocks
- mermaid - Diagrams
- KaTeX - Math
- markdown-it - Advanced parsing

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
1. Sidebar component architecture
2. Dynamic tool loader based on file type
3. Metadata schema implementation
4. Basic file type detection (magic bytes)

### Phase 2: Image Editing (Week 2)
1. Fabric.js integration
2. Crop, rotate, resize
3. Basic filters
4. EXIF read/write
5. Export functionality

### Phase 3: Code Editing (Week 3)
1. Monaco Editor integration
2. Language detection
3. Formatting (Prettier)
4. Find & replace
5. Syntax analysis

### Phase 4: Document Editing (Week 4)
1. PDF.js viewer
2. pdf-lib editing
3. Annotations
4. Metadata editing
5. Export options

### Phase 5: Media Tools (Week 5)
1. Video.js player enhancements
2. Wavesurfer.js audio
3. Trimming UI
4. ID3 tag editing
5. Frame/audio extraction

### Phase 6: Data & 3D (Week 6)
1. JSON/YAML/CSV tools
2. Three.js 3D viewer enhancements
3. Model stats and export
4. Data conversion tools

### Phase 7: Polish & Integration (Week 7)
1. Undo/redo for all tools
2. Keyboard shortcuts
3. Settings persistence
4. Performance optimization
5. Testing and bug fixes

---

## Open Source Libraries Summary

| Category | Primary Library | npm Package | GitHub Stars |
|----------|----------------|-------------|--------------|
| Image Canvas | Fabric.js | fabric | 28k+ |
| Image Crop | Cropper.js | cropperjs | 13k+ |
| Image EXIF | piexifjs | piexifjs | 500+ |
| Code Editor | Monaco Editor | monaco-editor | 40k+ |
| Code Format | Prettier | prettier | 49k+ |
| PDF View | PDF.js | pdfjs-dist | 48k+ |
| PDF Edit | pdf-lib | pdf-lib | 7k+ |
| Video Player | Video.js | video.js | 38k+ |
| Audio Waveform | Wavesurfer.js | wavesurfer.js | 8k+ |
| Audio Tags | music-metadata | music-metadata | 900+ |
| Audio Process | Tone.js | tone | 13k+ |
| 3D Render | Three.js | three | 102k+ |
| 3D Simple | model-viewer | @google/model-viewer | 6k+ |
| Markdown | EasyMDE | easymde | 2k+ |
| JSON View | JSON Hero | (internal) | - |
| YAML Parse | js-yaml | js-yaml | 6k+ |
| CSV Parse | PapaParse | papaparse | 12k+ |
| Archive | libarchive.js | libarchivejs | 200+ |
| Font Parse | opentype.js | opentype.js | 4k+ |

---

## File Size Considerations

| Library | Minified Size | Gzipped | Load Strategy |
|---------|---------------|---------|---------------|
| Fabric.js | 300KB | 80KB | Lazy load |
| Monaco Editor | 5MB | 1.5MB | Lazy load + worker |
| PDF.js | 500KB | 150KB | Lazy load |
| Three.js | 600KB | 150KB | Already loaded |
| Tone.js | 400KB | 100KB | Lazy load |
| Wavesurfer.js | 100KB | 30KB | Lazy load |
| Cropper.js | 40KB | 12KB | Bundle |
| piexifjs | 30KB | 10KB | Bundle |

**Strategy:** Only load libraries when their category is opened. Use code splitting and dynamic imports.

---

## Security Considerations

1. **All processing client-side** - No file upload to servers
2. **Sandbox WebWorkers** - Heavy processing in workers
3. **Memory limits** - Cap file sizes per format
4. **Sanitize inputs** - Validate all user inputs
5. **Content Security Policy** - Restrict eval for Monaco

---

## Next Steps

1. [ ] Review and approve this plan
2. [ ] Prioritize which categories to implement first
3. [ ] Set up library bundling strategy
4. [ ] Create sidebar component skeleton
5. [ ] Implement file type detection
6. [ ] Begin Phase 1 implementation

---

## References

- Perplexity Research: File Format Taxonomy (2026-01-31)
- Perplexity Research: Open Source Editors (2026-01-31)
- Perplexity Research: Metadata Standards (2026-01-31)
