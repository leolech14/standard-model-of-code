# Research: According to the reference library, who coined the term 'holon'?

> **Date:** 2026-01-27 14:35:59
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:d01f28824f5ea12e57234dc673b48665d6c1e11b102b8a0a5367b5fee7a7aadb`
> **Raw JSON:** `raw/20260127_143559_according_to_the_reference_library__who_coined_the.json`

---

## Query

According to the reference library, who coined the term 'holon'?

---

## Response

```tool_code
import json
from pathlib import Path

REFS_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path(".")
CONCEPT_INDEX_PATH = REFS_DIR / "context-management/archive/references/index/concept_index.json"

def find_source_for_concept(concept: str) -> list[str]:
    """
    Finds the references associated with a given concept in the concept index.

    Args:
        concept: The concept to search for.

    Returns:
        A list of reference IDs associated with the concept, or an empty list if the concept is not found.
    """
    try:
        with open(CONCEPT_INDEX_PATH, "r") as f:
            concept_index = json.load(f)
            return concept_index.get(concept, [])
    except FileNotFoundError:
        print(f"Error: Concept index file not found at {CONCEPT_INDEX_PATH}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {CONCEPT_INDEX_PATH}")
        return []

def get_author_from_ref_id(ref_id: str) -> str:
    """
    Retrieves the author's last name from a reference ID by looking at the catalog.json file.

    Args:
        ref_id: The reference ID to search for (e.g., "KOESTLER-1967").

    Returns:
        The author's last name as a string, or "Unknown" if the reference ID is not found or the author is not available.
    """
    catalog_path = REFS_DIR / "context-management/archive/references/index/catalog.json"
    try:
        with open(catalog_path, "r") as f:
            catalog = json.load(f)
            for ref in catalog["references"]:
                if ref["ref_id"] == ref_id:
                    return ref["authors"][0]
        return "Unknown"
    except FileNotFoundError:
        print(f"Error: Catalog file not found at {catalog_path}")
        return "Unknown"
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {catalog_path}")
        return "Unknown"
    except KeyError:
        print(f"Error: Could not find keys in {catalog_path}")
        return "Unknown"

# Find references related to 'holons'
references = find_source_for_concept("holons")

if references:
    # Print the author of the first work listed for 'holons'
    author = get_author_from_ref_id(references[0])
    print(f"According to the reference library, the term 'holon' was coined by {author}.")
else:
    print("The reference library does not contain information about who coined the term 'holon'.")
```

---

## Citations

_No citations provided_
