#!/usr/bin/env python3
import os
import sys
import requests
import argparse
import time

# Configuration
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_VERSION = "2022-06-28"
ROOT_PAGE_TITLE = "PROJECT_elements Navigation"
IGNORE_DIRS = {".git", ".gemini", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}
IGNORE_FILES = {".DS_Store"}

if not NOTION_API_KEY:
    print("Error: NOTION_API_KEY environment variable not set.")
    print("Please run with: doppler run -p notion-integration -c dev -- python3 tools/sync_to_notion.py")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION,
}

def search_page(title):
    """Search for a page by title."""
    url = "https://api.notion.com/v1/search"
    payload = {
        "query": title,
        "filter": {"value": "page", "property": "object"},
        "page_size": 1
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    results = response.json().get("results", [])
    # Filter for exact match just in case
    for page in results:
        # Check if title matches exactly. Notion search is fuzzy.
        # Title property key might vary, usually "title"
        props = page.get("properties", {})
        for prop_name, prop_val in props.items():
            if prop_val["type"] == "title":
                text_content = ""
                for t in prop_val["title"]:
                    text_content += t["plain_text"]
                if text_content == title:
                    return page
    return None

def list_accessbile_pages():
    """List all pages the integration can see."""
    url = "https://api.notion.com/v1/search"
    payload = {
        "filter": {"value": "page", "property": "object"},
        "page_size": 100
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    results = response.json().get("results", [])

    print(f"Found {len(results)} pages accessible to integration:")
    for page in results:
        title = "Untitled"
        props = page.get("properties", {})
        for prop_name, prop_val in props.items():
            if prop_val["type"] == "title":
                text_content = ""
                for t in prop_val["title"]:
                    text_content += t.get("plain_text", "")
                title = text_content
        print(f"- {title} (ID: {page['id']})")


def create_page(title, parent_page_id=None, content_blocks=[]):
    """Create a new page."""
    url = "https://api.notion.com/v1/pages"

    # If no parent provided, it creates a top-level page (workspace root effectively for the integration)
    # BUT integrations can only create children of pages they have access to.
    # So we MUST SEARCH for a root page first or prompt user?
    # Actually, integrations usually need a parent page shared with them.
    # Except if we create a "root" page, we assume the integration has access to some parent?
    # Wait, the search might return pages shared with the integration.
    # If we can't find a root page, we might fail unless we know a specific parent ID.
    # Let's assume for "root" we need to inform the user to share a page?
    # OR we try to create without parent? Notion API requires a parent (database or page).
    # We will search for the specific title first.

    payload = {
        "properties": {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        },
        "children": content_blocks
    }

    if parent_page_id:
        payload["parent"] = {"page_id": parent_page_id}
    else:
        # We can't create strictly "root" pages via API usually without a parent.
        # We need to find *some* page that is shared with the integration to use as parent.
        # For now, let's assume we find the existing "PROJECT_elements Navigation" or fail.
        print("Error: meaningful parent_page_id required for creating pages.")
        return None

    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to create page '{title}': {response.text}")
        return None
    return response.json()

def update_page_content(page_id, blocks):
    """Append blocks to a page."""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    payload = {"children": blocks}
    response = requests.patch(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_children(page_id):
    """Get existing children of a page to avoid duplicates."""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("results", [])

def text_block(text, bold=False):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {"content": text},
                "annotations": {"bold": bold}
            }]
        }
    }

def heading_block(text, level=2):
    t = f"heading_{level}"
    return {
        "object": "block",
        "type": t,
        f"{t}": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def code_block(text, language="plain text"):
    return {
        "object": "block",
        "type": "code",
        "code": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "language": language
        }
    }

def sync_directory(current_path, parent_page_id, dry_run=False, depth=0):
    if depth > 3: # Safety limit for first run
        return

    try:
        entries = sorted(os.listdir(current_path))
    except PermissionError:
        return

    # Separate dirs and files
    dirs = []
    files = []
    for entry in entries:
        full_path = os.path.join(current_path, entry)
        if os.path.isdir(full_path):
            if entry not in IGNORE_DIRS:
                dirs.append(entry)
        else:
            if entry not in IGNORE_FILES:
                files.append(entry)

    print(f"Syncing {current_path} to page {parent_page_id}...")

    # For files, we just list them as text/code blocks in the current page
    if files and not dry_run:
        # Group files into a single code block maybe? Or list?
        # Let's do a list of text blocks
        blocks = []
        blocks.append(heading_block("Files", 3))
        # Create a text representation
        file_list_str = "\n".join(files)
        blocks.append(code_block(file_list_str))

        # Check if we already have these blocks?
        # For simplicity in this v1 script, we append. Ideally we'd sync.
        # To avoid infinite append, maybe we clear first? No, delete is risky.
        # We will just append for now.
        update_page_content(parent_page_id, blocks)

    # For directories, we find or create child pages
    if dirs:
        existing_children_blocks = []
        if not dry_run:
            existing_children_blocks = get_children(parent_page_id)

        # Map child page titles to IDs
        existing_pages = {}
        for block in existing_children_blocks:
            if block["type"] == "child_page":
                existing_pages[block["child_page"]["title"]] = block["id"]

        for d in dirs:
            print(f"  -> Dir: {d}")
            if dry_run:
                sync_directory(os.path.join(current_path, d), "fake_id", dry_run, depth+1)
                continue

            child_id = existing_pages.get(d)
            if not child_id:
                # Create sub-page
                print(f"Creating page for directory: {d}")
                new_page = create_page(d, parent_page_id)
                if new_page:
                    child_id = new_page["id"]
                else:
                    continue

            # Recurse
            sync_directory(os.path.join(current_path, d), child_id, dry_run, depth+1)

def main():
    parser = argparse.ArgumentParser(description="Sync local file structure to Notion.")
    parser.add_argument("--dry-run", action="store_true", help="Audit run, don't change Notion.")
    parser.add_argument("--list", action="store_true", help="List all accessible pages and exit.")
    parser.add_argument("--root", default=".", help="Root directory to sync")
    args = parser.parse_args()

    if args.list:
        list_accessbile_pages()
        return

    print(f"Searching for root page: '{ROOT_PAGE_TITLE}'...")
    root_page = search_page(ROOT_PAGE_TITLE)

    if not root_page:
        print(f"Root page '{ROOT_PAGE_TITLE}' not found.")
        print("Please share an existing page with the integration or create one with this exact title.")
        print("The integration cannot create top-level pages without a known parent.")
        return

    root_id = root_page["id"]
    print(f"Found root page. ID: {root_id}")

    abs_root = os.path.abspath(args.root)
    sync_directory(abs_root, root_id, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
