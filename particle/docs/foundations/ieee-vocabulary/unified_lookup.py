#!/usr/bin/env python3
"""
Unified Standards Vocabulary Lookup
====================================
Query IEEE SEVOCAB (5,401 terms), INCOSE (21 terms), and SEBoK (435 terms).

Usage:
    python3 unified_lookup.py "system"
    python3 unified_lookup.py --all "architecture"
    python3 unified_lookup.py --compare "validation"
    python3 unified_lookup.py --smc-check "LOCUS"
    python3 unified_lookup.py --stats
"""

import sqlite3
import json
import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "SEVOCAB.db"
INCOSE_PATH = BASE_DIR / "INCOSE.json"
SEBOK_PATH = BASE_DIR / "SEBOK_terms.txt"


def load_incose():
    """Load INCOSE definitions."""
    if not INCOSE_PATH.exists():
        return {}
    with open(INCOSE_PATH) as f:
        data = json.load(f)
    return data.get("terms", {})


def load_sebok_terms():
    """Load SEBoK term list."""
    if not SEBOK_PATH.exists():
        return set()
    with open(SEBOK_PATH) as f:
        return {line.strip().lower() for line in f if line.strip()}


def ieee_lookup(term: str) -> dict | None:
    """Look up term in IEEE SEVOCAB."""
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(DB_PATH)
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


def incose_lookup(term: str) -> dict | None:
    """Look up term in INCOSE definitions."""
    incose = load_incose()
    key = term.lower()
    if key in incose:
        return {
            "term": key,
            "definition": incose[key]["definition"],
            "notes": incose[key].get("notes", ""),
            "source": "INCOSE-TP-2020-002-06"
        }
    return None


def sebok_exists(term: str) -> bool:
    """Check if term exists in SEBoK."""
    sebok = load_sebok_terms()
    return term.lower() in sebok


def unified_lookup(term: str) -> dict:
    """Look up term in all sources."""
    return {
        "term": term,
        "ieee": ieee_lookup(term),
        "incose": incose_lookup(term),
        "sebok": sebok_exists(term)
    }


def compare_definitions(term: str):
    """Compare definitions across standards."""
    result = unified_lookup(term)

    print(f"\n{'='*60}")
    print(f"TERM: {term}")
    print('='*60)

    sources_found = []

    if result["ieee"]:
        sources_found.append("IEEE")
        print(f"\n[IEEE SEVOCAB]")
        print(f"  {result['ieee']['definition'][:200]}...")
        if result['ieee']['source']:
            print(f"  Source: {result['ieee']['source']}")

    if result["incose"]:
        sources_found.append("INCOSE")
        print(f"\n[INCOSE]")
        print(f"  {result['incose']['definition']}")
        if result['incose']['notes']:
            print(f"  Notes: {result['incose']['notes'][:150]}...")

    if result["sebok"]:
        sources_found.append("SEBoK")
        print(f"\n[SEBoK]")
        print(f"  Term exists in SEBoK glossary (definition requires web lookup)")

    if not sources_found:
        print(f"\n  NOT FOUND in any standard vocabulary.")
        print(f"  This may be an SMC-specific term.")
    else:
        print(f"\n  Found in: {', '.join(sources_found)}")

    return result


def smc_check(term: str):
    """Check if SMC term overlaps with standards."""
    result = unified_lookup(term)

    ieee = result["ieee"] is not None
    incose = result["incose"] is not None
    sebok = result["sebok"]

    if ieee or incose or sebok:
        print(f"'{term}': EXISTS in standards")
        if ieee:
            print(f"  - IEEE: {result['ieee']['definition'][:100]}...")
        if incose:
            print(f"  - INCOSE: {result['incose']['definition'][:100]}...")
        if sebok:
            print(f"  - SEBoK: (term listed)")
        return "OVERLAP"
    else:
        print(f"'{term}': NOVEL - not in IEEE/INCOSE/SEBoK")
        return "NOVEL"


def get_stats():
    """Get statistics for all vocabularies."""
    # IEEE
    ieee_count = 0
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM terms")
        ieee_count = c.fetchone()[0]
        conn.close()

    # INCOSE
    incose = load_incose()
    incose_count = len(incose)

    # SEBoK
    sebok = load_sebok_terms()
    sebok_count = len(sebok)

    return {
        "ieee": ieee_count,
        "incose": incose_count,
        "sebok": sebok_count,
        "total_unique": "~5,500+"  # approximate, with overlaps
    }


def main():
    parser = argparse.ArgumentParser(description="Unified Standards Vocabulary Lookup")
    parser.add_argument("term", nargs="?", help="Term to look up")
    parser.add_argument("--all", "-a", metavar="TERM", help="Look up in all sources")
    parser.add_argument("--compare", "-c", metavar="TERM", help="Compare definitions across standards")
    parser.add_argument("--smc-check", "-s", metavar="TERM", help="Check if SMC term overlaps with standards")
    parser.add_argument("--stats", action="store_true", help="Show vocabulary statistics")

    args = parser.parse_args()

    if args.stats:
        stats = get_stats()
        print("\nUnified Standards Vocabulary")
        print("=" * 40)
        print(f"IEEE SEVOCAB:  {stats['ieee']:,} terms")
        print(f"INCOSE:        {stats['incose']} core definitions")
        print(f"SEBoK:         {stats['sebok']} terms (names only)")
        print(f"{'─'*40}")
        print(f"Coverage:      {stats['total_unique']} unique concepts")
        return 0

    if args.compare:
        compare_definitions(args.compare)
        return 0

    if args.smc_check:
        smc_check(args.smc_check)
        return 0

    if args.all:
        compare_definitions(args.all)
        return 0

    if args.term:
        # Default: IEEE lookup
        result = ieee_lookup(args.term)
        if result:
            print(f"\n{result['term']}")
            print("=" * 60)
            print(result['definition'])
            if result['source']:
                print(f"\nSource: {result['source']}")
        else:
            # Try INCOSE
            result = incose_lookup(args.term)
            if result:
                print(f"\n{result['term']} (INCOSE)")
                print("=" * 60)
                print(result['definition'])
            else:
                print(f"'{args.term}' not found in IEEE or INCOSE.")
                if sebok_exists(args.term):
                    print(f"Note: Term exists in SEBoK (definition requires web lookup)")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
