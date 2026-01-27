# Research: Who coined the term 'holon' according to Koestler's work in the reference library?

> **Date:** 2026-01-27 14:38:36
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:36a09e3f7904f5ff59e1d8139f1bcb6e627622be80409fa4512dc315a91e226b`
> **Raw JSON:** `raw/20260127_143836_who_coined_the_term__holon__according_to_koestler.json`

---

## Query

Who coined the term 'holon' according to Koestler's work in the reference library?

---

## Response

```tool_code
import json
from pathlib import Path

REFS_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path(".")
CATALOG_PATH = REFS_DIR / "index/catalog.json"
CONCEPT_INDEX_PATH = REFS_DIR / "index/concept_index.json"
METADATA_DIR = REFS_DIR / "metadata"

def find_works_by_author(author_name: str) -> list[dict]:
    """Finds works by a given author within the reference library.

    Args:
        author_name: The name of the author to search for.

    Returns:
        A list of dictionaries, where each dictionary represents a work
        by the specified author.  Returns an empty list if no works
        are found.
    """

    try:
        with open(CATALOG_PATH, 'r') as f:
            catalog_data = json.load(f)
            references = catalog_data.get('references', [])

            author_works = [
                ref for ref in references
                if author_name.lower() in [a.lower() for a in ref.get('authors', [])]
            ]
            return author_works

    except FileNotFoundError:
        print(f"Error: catalog.json not found at {CATALOG_PATH}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {CATALOG_PATH}")
        return []


def find_ref_by_concept(concept: str) -> list[str]:
    """Finds reference IDs associated with a concept in the concept index.

    Args:
        concept: The concept to search for.

    Returns:
        A list of reference IDs associated with the concept.
    """
    try:
        with open(CONCEPT_INDEX_PATH, 'r') as f:
            concept_data = json.load(f)
            ref_ids = concept_data.get(concept.lower().replace(' ', '_'), [])  # Normalize key
            return ref_ids
    except FileNotFoundError:
        print(f"Error: concept_index.json not found at {CONCEPT_INDEX_PATH}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {CONCEPT_INDEX_PATH}")
        return []


def get_metadata(ref_id: str) -> dict | None:
    """Retrieves metadata for a given reference ID.

    Args:
        ref_id: The reference ID to look up.

    Returns:
        A dictionary containing the metadata for the reference, or None
        if the reference ID is not found.
    """
    metadata_file = METADATA_DIR / f"{ref_id}.json"
    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            return metadata
    except FileNotFoundError:
        print(f"Error: Metadata file not found for {ref_id} at {metadata_file}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {metadata_file}")
        return None


def search_references_by_title(search_term: str) -> list[dict]:
    """Searches references by a term in the title.

    Args:
        search_term: The term to search for in the reference titles.

    Returns:
        A list of dictionaries, where each dictionary represents a reference
        that contains the search term in its title.
    """

    try:
        with open(CATALOG_PATH, 'r') as f:
            catalog_data = json.load(f)
            references = catalog_data.get('references', [])

            matching_refs = [
                ref for ref in references
                if search_term.lower() in ref.get('title', '').lower()
            ]
            return matching_refs

    except FileNotFoundError:
        print(f"Error: catalog.json not found at {CATALOG_PATH}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {CATALOG_PATH}")
        return []


def who_coined(concept: str):
  """
  Determines who coined the specified concept based on the reference library.

  Args:
      concept (str): The concept to find the originator of.

  Returns:
      str: A string indicating who coined the concept, or a message
           that the originator is not found in the reference library.
  """
  ref_ids = find_ref_by_concept(concept)
  if not ref_ids:
      return f"Concept '{concept}' not found in the concept index."

  originator_ref_id = ref_ids[0] # Assuming the first ref_id is the originator

  metadata = get_metadata(originator_ref_id)

  if metadata:
      authors = metadata.get('authors', [])
      title = metadata.get('title','')
      year = metadata.get('year','')
      if authors:
          author_str = ', '.join(authors)
          return f"The term '{concept}' is associated with {author_str} in the reference '{title}' ({year})."
      else:
          return f"The reference '{originator_ref_id}' associated with '{concept}' has no author information."
  else:
      return f"No metadata found for the reference associated with '{concept}'."

# Example usage
concept_name = "holons"
originator = who_coined(concept_name)
print(originator)

```

---

## Citations

_No citations provided_
