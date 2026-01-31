#!/usr/bin/env python3
"""
SEVOCAB - IEEE Software Engineering Vocabulary Lookup
======================================================
Query the IEEE SEVOCAB database (5,401 terms).

Usage:
    python sevocab.py lookup "repository"
    python sevocab.py search "architect"
    python sevocab.py validate-smc
    python sevocab.py stats
"""

import sqlite3
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Database path
DB_PATH = Path(__file__).parent.parent / "archive/references/swebok/SEVOCAB.db"
JSON_PATH = Path(__file__).parent.parent / "archive/references/swebok/SEVOCAB.json"


def get_connection():
    """Get database connection."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"SEVOCAB database not found at {DB_PATH}")
    return sqlite3.connect(DB_PATH)


def lookup(term: str) -> List[Dict]:
    """Look up exact term definition."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT t.term, d.def_num, d.definition, d.source
        FROM terms t
        JOIN definitions d ON t.id = d.term_id
        WHERE t.term_lower = ?
        ORDER BY d.def_num
    """, (term.lower(),))

    results = []
    for row in c.fetchall():
        results.append({
            "term": row[0],
            "def_num": row[1],
            "definition": row[2],
            "source": row[3]
        })

    conn.close()
    return results


def search(pattern: str) -> List[str]:
    """Search for terms containing pattern."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT term FROM terms
        WHERE term_lower LIKE ?
        ORDER BY term
    """, (f"%{pattern.lower()}%",))

    results = [row[0] for row in c.fetchall()]
    conn.close()
    return results


def term_exists(term: str) -> bool:
    """Check if term exists in SEVOCAB."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT 1 FROM terms WHERE term_lower = ?", (term.lower(),))
    exists = c.fetchone() is not None

    conn.close()
    return exists


def get_stats() -> Dict:
    """Get database statistics."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM terms")
    term_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM definitions")
    def_count = c.fetchone()[0]

    c.execute("SELECT COUNT(DISTINCT source) FROM definitions WHERE source != ''")
    source_count = c.fetchone()[0]

    conn.close()

    return {
        "terms": term_count,
        "definitions": def_count,
        "sources": source_count
    }


def validate_smc_terms() -> Dict:
    """Validate SMC terms against SEVOCAB."""

    # SMC core vocabulary
    smc_terms = [
        # Universes
        "PROJECTOME", "CODOME", "CONTEXTOME",
        # Realms
        "PARTICLE", "WAVE", "OBSERVER",
        # Phase States
        "MODULE", "AUTOMATION", "INFRASTRUCTURE", "CONFIG",
        # Classification
        "Atom", "Tier", "Role",
        # Key Roles
        "Query", "Command", "Validator", "Factory", "Repository",
        "Service", "Controller", "Handler", "Transformer", "Utility",
        # States
        "SYMMETRIC", "ORPHAN", "PHANTOM", "DRIFT", "AMNESIAC",
        # Subsystems
        "Collider", "HSL", "ACI", "BARE",
        # LOCUS
        "LOCUS", "Ring", "RPBL",
        # Other
        "Task", "Run", "Technical Debt", "Ground Truth"
    ]

    found = []
    missing = []

    for term in smc_terms:
        if term_exists(term):
            found.append(term)
        else:
            missing.append(term)

    return {
        "total": len(smc_terms),
        "found_in_ieee": len(found),
        "smc_only": len(missing),
        "found": found,
        "missing": missing
    }


# CLI
def main():
    parser = argparse.ArgumentParser(description="IEEE SEVOCAB Lookup")
    subparsers = parser.add_subparsers(dest="command")

    # lookup
    lookup_p = subparsers.add_parser("lookup", help="Look up exact term")
    lookup_p.add_argument("term", help="Term to look up")

    # search
    search_p = subparsers.add_parser("search", help="Search for terms")
    search_p.add_argument("pattern", help="Search pattern")

    # validate-smc
    subparsers.add_parser("validate-smc", help="Validate SMC terms")

    # stats
    subparsers.add_parser("stats", help="Show database stats")

    args = parser.parse_args()

    if args.command == "lookup":
        results = lookup(args.term)
        if results:
            print(f"\n{results[0]['term']}")
            print("=" * 60)
            for r in results:
                print(f"\n({r['def_num']}) {r['definition']}")
                if r['source']:
                    print(f"    Source: {r['source']}")
        else:
            print(f"Term '{args.term}' not found in SEVOCAB")

    elif args.command == "search":
        results = search(args.pattern)
        print(f"\nFound {len(results)} terms containing '{args.pattern}':\n")
        for t in results[:50]:
            print(f"  {t}")
        if len(results) > 50:
            print(f"  ... and {len(results) - 50} more")

    elif args.command == "validate-smc":
        results = validate_smc_terms()
        print(f"\nSMC × SEVOCAB Validation")
        print("=" * 40)
        print(f"Total SMC terms:    {results['total']}")
        print(f"Found in IEEE:      {results['found_in_ieee']} ({100*results['found_in_ieee']//results['total']}%)")
        print(f"SMC-only:           {results['smc_only']} ({100*results['smc_only']//results['total']}%)")
        print(f"\nIEEE-aligned: {', '.join(results['found'][:10])}...")
        print(f"\nSMC innovations: {', '.join(results['missing'][:10])}...")

    elif args.command == "stats":
        stats = get_stats()
        print(f"\nSEVOCAB Database Statistics")
        print("=" * 40)
        print(f"Terms:       {stats['terms']:,}")
        print(f"Definitions: {stats['definitions']:,}")
        print(f"Sources:     {stats['sources']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
