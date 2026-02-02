Project Root: /Users/lech/PROJECTS_all/PROJECT_elements
Analyzing:    /Users/lech/PROJECTS_all/PROJECT_elements
Model:        gemini-3-pro-preview
Mode:         FORENSIC

Selected 30 files:
  - docs/reader/ARCHITECTURE_AUDIT_2026.html
  - docs/reader/CHANGELOG.html
  - docs/reader/CONTRIBUTING.html
  - docs/reader/DECISIONS.html
  - docs/reader/DEFINITION_OF_DONE.html
  ... and 25 more

Building context from local files...
Context size: ~1,647,912 tokens (6,591,649 chars)
Line numbers: enabled

============================================================
CRITICAL: Context (1,647,912 tokens) EXCEEDS
          the 1,000,000 token limit!
          The API call will likely fail or truncate.
          Use --set with a smaller set or --max-files
============================================================


  Auto-interactive: enabled (context > 50,000 tokens)
                    Use --force-oneshot to override
Review: Non-interactive environment detected. Disabling interactive mode.
DEBUG: doppler command failed: Token not found in system keyring
Doppler Error: secret not found in keyring


============================================================
GEMINI API KEY REQUIRED
============================================================

Backend: AI Studio (Developer API)
Model: gemini-3-pro-preview

Setup:
  1. Get API key from: https://aistudio.google.com/apikey
  2. export GEMINI_API_KEY='your-api-key'

Or use Vertex AI backend:
  export GEMINI_BACKEND=vertex
============================================================
