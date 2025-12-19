# 🩺 Spectrometer Refactoring Toolkit

> **"Turn your Monolith into Atoms."**

This toolkit uses the Spectrometer's understanding of code structure to **automatically decompose** large files (God Classes) into modular architectures.

## The Tools

| Script | Purpose |
|--------|---------|
| `auto_refactor_routes.py` | **The Router Extractor**. Takes a `server.js` (Express), extracts all routes into separate files (`api_*.js`), creates a `router.js` dispatch table, and rewires the main server. |
| `auto_extract.py` | **The Scalpel**. Extracts specific functions or blocks from a file into new modules based on AST patterns. |
| `extract_dependencies.py` | **The Tracer**. Analyzes extracted code to find missing dependencies and pulls them from the source file into shared libraries (`lib/`). |
| `validate_routes.py` | **The Checkup**. Scans extracted route files for missing imports or broken references. |

## Usage: The "God Class" Operation

To refactor a massive `server.js`:

```bash
# 1. Run the Refactor
python3 tools/refactor/auto_refactor_routes.py /path/to/your/repo/server.js

# 2. Validate the Output
python3 tools/refactor/validate_routes.py --dir /path/to/your/repo/refactored/routes
```

## How It Works

1.  **Parse**: Reads the source code using Tree-Sitter (AST).
2.  **Identify**: Finds specific patterns (e.g., `app.get('/api/...' ...)`)
3.  **Extract**: Moves the logic block + imports + helpers to a new file.
4.  **Wiring**: Generates a central router to dispatch requests to the new atoms.
5.  **Fallback**: Keeps the old code as a backup (Strangler Fig pattern).

## Safety

*   **Non-Destructive**: Does not delete original code.
*   **Logic-Preserving**: Moves code blocks verbatim; does not "rewrite" logic with LLMs.
*   **Reversible**: If it fails, just delete the `refactored/` folder.
