# AI Operating Manual: The Alien Architecture

> "We are building the Standard Model of Code. This requires tools that can see the hypercomplex topology."

## The Core Problem: Context Amnesia
Standard AI tools (IDE Chat) have a limited view. They see only what is open. They cannot reason about the "Global Topology" of 10,000 files, nor can they rigorously verify "line-level evidence" across the entire repo.

## The Solution: Three Specialized Roles

We have deployed a "Triad" of AI capabilities to solve this.

### 1. The Librarian (Exploration & Discovery)
**Tool**: Vertex AI Agent Builder (Web Interface)
**Best For**: "Where is X?", Onboarding, finding the "needle in the haystack".
**Mechanism**: Search Index (RAG).
**Usage**:
- Go to [Agent Builder Console](https://console.cloud.google.com/gen-app-builder/data-stores?project=elements-archive-2026).
- Ask: *"Where is the retry logic for GCS uploads?"*
- Result: Returns specific file chunks and summaries.

### 2. The Surgeon (Forensic Traceability)
**Tool**: `context-management/tools/ai/analyze.py --mode forensic`
**Best For**: Verification, Auditing, "Prove it".
**Mechanism**: Gemini 2.0 Flash with strict citation instructions.
**Usage**:
```bash
python context-management/tools/ai/analyze.py "List all hardcoded timeout values in the archive tool" --dir context-management/tools/archive --mode forensic
```
**Why it works**: The system prompt forces the AI to output:
> `[context-management/tools/archive/archive.py:L45-L48]` "timeout=30"

### 3. The Architect (Global Reasoning)
**Tool**: `context-management/tools/ai/analyze.py --mode architect`
**Best For**: High-level design, Theory-vs-Implementation checks.
**Mechanism**: Injects `metadata/COLLIDER_ARCHITECTURE.md` into the context window automatically.
**Usage**:
```bash
python context-management/tools/ai/analyze.py "Does the archive tool violate the 'Atom' isolation principle?" --mode architect
```
**Why it works**: The model "reads" your theory definitions before looking at the code, ensuring it speaks your language (Rings, Atoms, Tiers).

## The Workflow

1.  **Mirror the Brain**:
    ```bash
    python context-management/tools/archive/archive.py mirror
    ```
    *Builds the global context in the cloud.*

2.  **Consult the Architect**:
    ```bash
    .tools_venv/bin/python context-management/tools/ai/analyze.py "Review tools/archive for compliance with the Standard Model" --mode architect
    ```

3.  **Verify with the Surgeon**:
    ```bash
    .tools_venv/bin/python context-management/tools/ai/analyze.py "Show me the exact lines where we handle GCS errors" --mode forensic
    ```
