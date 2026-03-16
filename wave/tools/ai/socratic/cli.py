#!/usr/bin/env python3
"""Socratic Semantic Validator CLI.

Usage:
    doppler run -- python wave/tools/ai/socratic/cli.py --domain atoms
    doppler run -- python wave/tools/ai/socratic/cli.py --domain atoms --candidate particle/src/core/atom.py
    doppler run -- python wave/tools/ai/socratic/cli.py --list-domains
"""

import sys
from pathlib import Path

# Ensure wave/tools/ai/ is on sys.path for _shared imports
_AI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AI_DIR))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Socratic Semantic Validator — hypothesis-driven code verification",
    )
    parser.add_argument("--domain", help="Domain name from semantic_models.yaml")
    parser.add_argument("--candidate", help="Explicit file path to verify (skips discovery)")
    parser.add_argument("--store-name", help="File Search store name")
    parser.add_argument("--output", "-o", help="Output file path for markdown report")
    parser.add_argument("--index", action="store_true", help="Index files to store before verifying")
    parser.add_argument("--list-domains", action="store_true", help="List available domains")
    parser.add_argument("--sync-gcs", action="store_true", help="Sync output to GCS (requires billing)")

    args = parser.parse_args()

    if args.list_domains:
        from socratic.domain_runner import load_semantic_models
        models = load_semantic_models()
        print("Available domains:")
        for name, config in models.items():
            desc = config.get("description", config.get("scope", ""))
            n_defs = len(config.get("definitions", {}))
            print(f"  {name:20s} ({n_defs} concepts) {desc}")
        sys.exit(0)

    if not args.domain:
        parser.error("--domain is required (or use --list-domains)")

    from socratic.domain_runner import verify_domain
    verify_domain(
        domain=args.domain,
        store_name=args.store_name,
        output=args.output,
        index=args.index,
        candidate=args.candidate,
        sync_gcs=args.sync_gcs,
    )


if __name__ == "__main__":
    main()
