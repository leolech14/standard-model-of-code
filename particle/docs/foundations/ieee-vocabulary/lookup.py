#!/usr/bin/env python3
"""
IEEE SEVOCAB Lookup Tool
========================
Query the IEEE Software Engineering Vocabulary (5,401 terms).

Usage:
    python3 lookup.py "repository"
    python3 lookup.py --search "test"
    python3 lookup.py --exists "LOCUS"
    python3 lookup.py --stats
"""

import sqlite3
import json
import argparse
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "SEVOCAB.db"
JSON_PATH = Path(__file__).parent / "SEVOCAB_canonical.json"


def get_db():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"SEVOCAB.db not found at {DB_PATH}")
    return sqlite3.connect(DB_PATH)


def ieee_lookup(term: str) -> dict | None:
    """Look up term definition. Returns dict or None."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT t.term, d.definition, d.source
        FROM terms t
        JOIN definitions d ON t.id = d.term_id
        WHERE t.term_lower = ?
        ORDER BY d.def_num
        LIMIT 1
    """, (term.lower(),))
    row = c.fetchone()
    conn.close()

    if row:
        return {"term": row[0], "definition": row[1], "source": row[2]}
    return None


def ieee_exists(term: str) -> bool:
    """Check if term exists in IEEE vocabulary."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT 1 FROM terms WHERE term_lower = ?", (term.lower(),))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def ieee_search(pattern: str) -> list[str]:
    """Search for terms containing pattern."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT term FROM terms
        WHERE term_lower LIKE ?
        ORDER BY term
    """, (f"%{pattern.lower()}%",))
    results = [row[0] for row in c.fetchall()]
    conn.close()
    return results


def ieee_stats() -> dict:
    """Get database statistics."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM terms")
    terms = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM definitions")
    defs = c.fetchone()[0]
    conn.close()
    return {"terms": terms, "definitions": defs}


def main():
    parser = argparse.ArgumentParser(description="IEEE SEVOCAB Lookup")
    parser.add_argument("term", nargs="?", help="Term to look up")
    parser.add_argument("--search", "-s", help="Search for terms containing pattern")
    parser.add_argument("--exists", "-e", help="Check if term exists (returns 0/1)")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    if args.stats:
        stats = ieee_stats()
        print(f"IEEE SEVOCAB: {stats['terms']:,} terms, {stats['definitions']:,} definitions")
        return 0

    if args.exists:
        exists = ieee_exists(args.exists)
        if exists:
            print(f"YES: '{args.exists}' is an IEEE standard term")
            return 0
        else:
            print(f"NO: '{args.exists}' is NOT in IEEE vocabulary (SMC extension?)")
            return 1

    if args.search:
        results = ieee_search(args.search)
        print(f"Found {len(results)} terms containing '{args.search}':\n")
        for t in results[:30]:
            print(f"  {t}")
        if len(results) > 30:
            print(f"  ... and {len(results) - 30} more")
        return 0

    if args.term:
        result = ieee_lookup(args.term)
        if result:
            print(f"\n{result['term']}")
            print("=" * 60)
            print(f"{result['definition']}")
            if result['source']:
                print(f"\nSource: {result['source']}")
            return 0
        else:
            print(f"'{args.term}' not found in IEEE SEVOCAB")
            print("This may be an SMC-specific term.")
            return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
