#!/usr/bin/env python3
"""
Cerebras Documentation Validator
================================
Validates documentation for overclaiming language.

Usage:
    python cerebras_doc_validator.py validate particle/docs/theory/
    python cerebras_doc_validator.py validate particle/docs/theory/L0_AXIOMS.md
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CEREBRAS_API_URL = "https://api.cerebras.ai/v1/chat/completions"
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "llama-3.3-70b")

VALIDATION_PROMPT = """You are a documentation reviewer for the Standard Model of Code project.

CONTEXT: We are reframing documentation from "scientific discovery" language to "practical tool / reference model" language. SMC is NOT claiming to discover universal laws - it's proposing a reference model for AI context compression.

OVERCLAIMING PATTERNS TO FLAG:
1. "we discovered" / "we found" / "we proved" (OUR claims, not external citations)
2. "VALIDATED" as a status label (should be "GROUNDED" or "AI-REVIEWED")
3. "PROOF" when referring to OUR arguments (should be "ARGUMENT")
4. "universal law" / "fundamental truth" / "Laws of Code" / "Natural Laws" (except external Lehman's Laws)
5. "must be true" / "is necessary" when applied to our framework (not math theorems)
6. Any claim of scientific discovery rather than practical utility

OK TO KEEP:
- References to external theorems (Lawvere, Gödel, Bejan's Constructal)
- "validated" when describing empirical testing (e.g., "tested on 91 repos")
- "proof" in context of Lean 4 formal verification
- Lehman's Laws of Software Evolution (external academic work)

For the following document, identify ALL instances of overclaiming language.

OUTPUT FORMAT (JSON):
{{
  "file": "filename.md",
  "issues": [
    {{
      "line": 42,
      "text": "exact text found",
      "category": "MUST_FIX|OK_EXTERNAL|OK_EMPIRICAL|REVIEW",
      "reason": "why this is flagged",
      "suggestion": "replacement text if MUST_FIX"
    }}
  ],
  "summary": {{
    "must_fix": 3,
    "ok_external": 5,
    "review": 1
  }}
}}

DOCUMENT TO ANALYZE:
---
{content}
---

Respond with ONLY the JSON output, no other text."""


def get_api_key():
    """Get Cerebras API key from environment."""
    key = os.getenv("CEREBRAS_API_KEY")
    if not key:
        # Try doppler
        import subprocess
        try:
            result = subprocess.run(
                ["doppler", "secrets", "get", "CEREBRAS_API_KEY", "--plain"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                key = result.stdout.strip()
        except:
            pass
    if not key:
        print("ERROR: CEREBRAS_API_KEY not found in environment or Doppler")
        sys.exit(1)
    return key


def call_cerebras(prompt: str, api_key: str) -> str:
    """Call Cerebras API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": CEREBRAS_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4000
    }

    response = requests.post(CEREBRAS_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]["content"]


def validate_file(file_path: Path, api_key: str) -> dict:
    """Validate a single file."""
    print(f"  Validating: {file_path.name}...", end=" ", flush=True)

    content = file_path.read_text()

    # Truncate if too long (Cerebras context limit)
    if len(content) > 30000:
        content = content[:30000] + "\n\n[... TRUNCATED ...]"

    prompt = VALIDATION_PROMPT.format(content=content)

    try:
        response = call_cerebras(prompt, api_key)

        # Parse JSON from response
        # Handle case where response might have markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]

        result = json.loads(response.strip())
        result["file"] = str(file_path)

        must_fix = result.get("summary", {}).get("must_fix", 0)
        print(f"Found {must_fix} issues to fix")

        return result

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return {"file": str(file_path), "error": f"JSON parse error: {e}", "raw": response[:500]}
    except Exception as e:
        print(f"Error: {e}")
        return {"file": str(file_path), "error": str(e)}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate documentation for overclaiming")
    parser.add_argument("command", choices=["validate"])
    parser.add_argument("path", help="File or directory to validate")
    parser.add_argument("--output", "-o", help="Output file for report")
    args = parser.parse_args()

    api_key = get_api_key()
    path = Path(args.path)

    if path.is_file():
        files = [path]
    else:
        files = sorted(path.glob("**/*.md"))

    print(f"\n=== Cerebras Documentation Validator ===")
    print(f"Model: {CEREBRAS_MODEL}")
    print(f"Files to validate: {len(files)}\n")

    results = []
    total_must_fix = 0

    for f in files:
        result = validate_file(f, api_key)
        results.append(result)
        total_must_fix += result.get("summary", {}).get("must_fix", 0)
        time.sleep(0.2)  # Rate limiting

    # Output report
    report = {
        "timestamp": datetime.now().isoformat(),
        "model": CEREBRAS_MODEL,
        "total_files": len(files),
        "total_must_fix": total_must_fix,
        "results": results
    }

    output_path = args.output or str(PROJECT_ROOT / ".agent/intelligence/OVERCLAIMING_AUDIT_REPORT.json")
    Path(output_path).write_text(json.dumps(report, indent=2))

    print(f"\n=== SUMMARY ===")
    print(f"Files validated: {len(files)}")
    print(f"Total MUST_FIX issues: {total_must_fix}")
    print(f"Report saved to: {output_path}")

    # Print issues summary
    print(f"\n=== MUST_FIX ISSUES ===")
    for r in results:
        if "issues" in r:
            must_fix_issues = [i for i in r["issues"] if i.get("category") == "MUST_FIX"]
            if must_fix_issues:
                print(f"\n{r['file']}:")
                for issue in must_fix_issues:
                    print(f"  Line {issue.get('line', '?')}: {issue.get('text', '')[:60]}...")
                    print(f"    -> {issue.get('suggestion', 'No suggestion')}")


if __name__ == "__main__":
    main()
