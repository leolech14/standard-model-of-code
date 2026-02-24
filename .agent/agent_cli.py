#!/usr/bin/env python3
"""
agent_cli.py - Unified entry point for .agent governance tools.

Thin routing layer. All business logic lives in the delegated tools.

Usage:
    python .agent/agent_cli.py status
    python .agent/agent_cli.py run [--safe] [--dry-run]
    python .agent/agent_cli.py health
    python .agent/agent_cli.py deck deal [--json] [--minimal]
    python .agent/agent_cli.py deck list
    python .agent/agent_cli.py macro list
    python .agent/agent_cli.py macro run MACRO-ID [--dry-run]
    python .agent/agent_cli.py trigger status
    python .agent/agent_cli.py trigger check
"""

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

# Ensure imports resolve from any cwd
AGENT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = AGENT_DIR / "tools"
sys.path.insert(0, str(TOOLS_DIR))

# ---------------------------------------------------------------------------
# Lazy imports with graceful degradation
# ---------------------------------------------------------------------------

def _import(module_name: str):
    """Import a module from TOOLS_DIR; return None on failure."""
    try:
        import importlib
        return importlib.import_module(module_name)
    except Exception as exc:
        print(f"[warn] Could not import {module_name}: {exc}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_status(_args):
    mod = _import("autopilot")
    if mod is None:
        sys.exit(1)
    mod.cmd_status()


def cmd_run(args):
    mod = _import("autopilot")
    if mod is None:
        sys.exit(1)
    success = mod.cmd_run(
        safe_mode=getattr(args, "safe", False),
        dry_run=getattr(args, "dry_run", False),
    )
    sys.exit(0 if success else 1)


def cmd_health(_args):
    mod = _import("autopilot")
    if mod is None:
        sys.exit(1)
    mod.cmd_health()


def cmd_deck_deal(args):
    mod = _import("deal_cards")
    if mod is None:
        sys.exit(1)
    # deal_cards.main() parses sys.argv; call internals directly instead
    deck = mod.load_deck()
    meters = mod.load_meters()
    phase = mod.get_current_phase()
    playable = mod.filter_cards(deck, phase, {"meters": meters, "phase": phase})[:5]

    if getattr(args, "json", False):
        import json
        print(json.dumps({
            "phase": phase,
            "meters": meters,
            "cards": [{"id": c["id"], "title": c["title"]} for c in playable],
            "wildcard": True,
        }, indent=2))
    elif getattr(args, "minimal", False):
        mod.display_minimal(playable, phase)
    else:
        mod.display_full(playable, phase, meters)


def cmd_deck_list(_args):
    mod = _import("deal_cards")
    if mod is None:
        sys.exit(1)
    deck = mod.load_deck()
    if not deck:
        print("No cards found in .agent/deck/")
        return
    print(f"{'ID':<14} {'Title':<45} {'Status'}")
    print("-" * 72)
    for card in deck:
        cid = card.get("id", "?")
        title = card.get("title", "?")[:44]
        status = card.get("status", "?")
        print(f"{cid:<14} {title:<45} {status}")


def cmd_macro_list(_args):
    mod = _import("macro_executor")
    if mod is None:
        sys.exit(1)
    # Reuse the existing cmd_list implementation via a minimal args namespace
    mod.cmd_list(SimpleNamespace())


def cmd_macro_run(args):
    mod = _import("macro_executor")
    if mod is None:
        sys.exit(1)
    ns = SimpleNamespace(
        macro_id=args.macro_id,
        dry_run=getattr(args, "dry_run", False),
        force=getattr(args, "force", False),
    )
    mod.cmd_run(ns)


def cmd_trigger_status(_args):
    mod = _import("trigger_engine")
    if mod is None:
        sys.exit(1)
    mod.cmd_status(SimpleNamespace())


def cmd_trigger_check(_args):
    mod = _import("trigger_engine")
    if mod is None:
        sys.exit(1)
    mod.cmd_check_all(SimpleNamespace())


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agent_cli",
        description="Unified .agent governance CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="command", metavar="COMMAND")

    # status
    sub.add_parser("status", help="Overall system status")

    # run
    run_p = sub.add_parser("run", help="Run full autopilot cycle")
    run_p.add_argument("--safe", action="store_true", help="Safe mode (extra checks)")
    run_p.add_argument("--dry-run", "-n", dest="dry_run", action="store_true", help="Preview without executing")

    # health
    sub.add_parser("health", help="Deep health check all systems")

    # deck
    deck_p = sub.add_parser("deck", help="Decision Deck commands")
    deck_sub = deck_p.add_subparsers(dest="deck_cmd", metavar="SUBCOMMAND")
    deal_p = deck_sub.add_parser("deal", help="Deal available cards")
    deal_p.add_argument("--json", action="store_true", help="JSON output")
    deal_p.add_argument("--minimal", action="store_true", help="Minimal one-line output")
    deck_sub.add_parser("list", help="List all cards in the deck")

    # macro
    macro_p = sub.add_parser("macro", help="Macro executor commands")
    macro_sub = macro_p.add_subparsers(dest="macro_cmd", metavar="SUBCOMMAND")
    macro_sub.add_parser("list", help="List all macros")
    run_macro_p = macro_sub.add_parser("run", help="Execute a macro")
    run_macro_p.add_argument("macro_id", help="Macro ID (e.g. MACRO-001)")
    run_macro_p.add_argument("--dry-run", "-n", dest="dry_run", action="store_true")
    run_macro_p.add_argument("--force", action="store_true", help="Run even if DRAFT")

    # trigger
    trig_p = sub.add_parser("trigger", help="Trigger engine commands")
    trig_sub = trig_p.add_subparsers(dest="trigger_cmd", metavar="SUBCOMMAND")
    trig_sub.add_parser("status", help="Trigger engine status")
    trig_sub.add_parser("check", help="Show all trigger configurations")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "status":
            cmd_status(args)
        elif args.command == "run":
            cmd_run(args)
        elif args.command == "health":
            cmd_health(args)
        elif args.command == "deck":
            if args.deck_cmd == "deal":
                cmd_deck_deal(args)
            elif args.deck_cmd == "list":
                cmd_deck_list(args)
            else:
                parser.parse_args(["deck", "--help"])
        elif args.command == "macro":
            if args.macro_cmd == "list":
                cmd_macro_list(args)
            elif args.macro_cmd == "run":
                cmd_macro_run(args)
            else:
                parser.parse_args(["macro", "--help"])
        elif args.command == "trigger":
            if args.trigger_cmd == "status":
                cmd_trigger_status(args)
            elif args.trigger_cmd == "check":
                cmd_trigger_check(args)
            else:
                parser.parse_args(["trigger", "--help"])
        else:
            parser.print_help()
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
