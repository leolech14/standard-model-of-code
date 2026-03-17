"""
Component Scanner — analyzes a React/TSX component and classifies every value.

Takes a TSX file as input. Produces:
1. Audit report (what's hardcoded, what's logic, what's behavior)
2. Token mapping (hardcoded → Algebra-UI token)
3. Recipe skeleton (slots, variants, states)
4. Scroll skeleton (purpose, sense, controls)

Usage:
    python component_scanner.py path/to/Component.tsx
    python component_scanner.py path/to/Component.tsx --output /tmp/audit
"""

import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# ── Tailwind → Token Mapping ──────────────────────────────

# Neutral grays → Algebra-UI achromatic tokens
NEUTRAL_MAP = {
    "neutral-50": "--color-text",
    "neutral-100": "--color-text",
    "neutral-200": "--color-text-secondary",
    "neutral-300": "--color-text-secondary",
    "neutral-400": "--color-text-muted",
    "neutral-500": "--color-text-muted",
    "neutral-600": "--color-text-muted",
    "neutral-700": "--color-border",
    "neutral-800": "--color-border",
    "neutral-900": "--color-surface-hover",
    "neutral-925": "--color-surface",
    "neutral-950": "--color-bg",
}

# Named colors → Algebra-UI chromatic tokens
COLOR_MAP = {
    "indigo": "--color-accent",
    "emerald": "--color-emerald",
    "blue": "--color-blue",
    "red": "--color-danger",
    "rose": "--color-rose",
    "amber": "--color-amber",
    "yellow": "--color-warning",
    "green": "--color-positive",
    "purple": "--color-purple",
    "violet": "--color-purple",
    "cyan": "--color-cyan",
    "orange": "--color-amber",
    "slate": "--color-text-muted",
    "gray": "--color-text-muted",
    "zinc": "--color-text-muted",
    "stone": "--color-text-muted",
}

# Spacing values → Algebra-UI spacing tokens
SPACING_MAP = {
    "0.5": "--space-0-5",
    "1": "--space-1",
    "1.5": "--space-1-5",
    "2": "--space-2",
    "3": "--space-3",
    "4": "--space-4",
    "5": "--space-5",
    "6": "--space-6",
    "8": "--space-8",
    "10": "--space-10",
    "12": "--space-12",
    "16": "--space-16",
    "20": "--space-20",
    "24": "--space-24",
}

# Radius values → Algebra-UI radius tokens
RADIUS_MAP = {
    "rounded-sm": "--radius-sm",
    "rounded": "--radius",
    "rounded-md": "--radius",
    "rounded-lg": "--radius-lg",
    "rounded-xl": "--radius-lg",
    "rounded-2xl": "--radius-lg",
    "rounded-full": "--radius-full",
    "rounded-[2px]": "--radius-sm",
}

# Font size → typography tokens
FONT_MAP = {
    "text-[9px]": "--text-xs",
    "text-[10px]": "--text-xs",
    "text-xs": "--text-xs",
    "text-sm": "--text-sm",
    "text-base": "--text-base",
    "text-lg": "--text-lg",
    "text-xl": "--text-xl",
    "text-2xl": "--text-2xl",
}


# ── Regex Patterns ────────────────────────────────────────

# Match Tailwind classes with colors: bg-neutral-900, text-indigo-500/40, border-emerald-400/20
RE_TW_COLOR = re.compile(
    r'(?:bg|text|border|ring|shadow|from|to|via|outline|fill|stroke|divide|placeholder)'
    r'-'
    r'(neutral|slate|gray|zinc|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|white|black)'
    r'-?'
    r'(\d+)?'
    r'(?:/(\d+))?'
)

# Match spacing classes: p-4, mx-2, gap-3, w-64, h-48
RE_TW_SPACING = re.compile(
    r'(?:p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr|gap|space-x|space-y|w|h|min-w|min-h|max-w|max-h)'
    r'-'
    r'(\d+(?:\.\d+)?|\[\d+px\])'
)

# Match radius classes
RE_TW_RADIUS = re.compile(r'rounded(?:-[a-z]+)?(?:-\[\dpx\])?')

# Match font size classes
RE_TW_FONT = re.compile(r'text-(?:\[[\dpx]+\]|xs|sm|base|lg|xl|2xl|3xl)')

# Match React state hooks
RE_STATE_HOOK = re.compile(r'useState\s*<?\s*([^>]+)?\s*>?\s*\(\s*([^)]*)\s*\)')

# Match component function/const declarations
RE_COMPONENT = re.compile(r'(?:export\s+)?(?:const|function)\s+(\w+)\s*(?::\s*React\.FC)?')

# Match props interface/type
RE_PROPS = re.compile(r'(?:interface|type)\s+(\w*Props\w*)\s*(?:=\s*)?{([^}]+)}', re.DOTALL)

# Match event handlers
RE_HANDLERS = re.compile(r'(?:onClick|onChange|onSubmit|onToggle|onSelect|onContextMenu|onDoubleClick)\s*=')

# Match conditional rendering
RE_CONDITIONAL = re.compile(r'(?:\?\s*\(|&&\s*\(|ternary|isExpanded|isSelected|viewMode|selected)')


# ── Data Models ───────────────────────────────────────────

@dataclass
class HardcodedValue:
    """A single hardcoded visual value found in the component."""
    line: int
    original: str
    category: str  # color | spacing | radius | font | layout | animation
    suggested_token: Optional[str]
    context: str  # surrounding code for context
    confidence: float  # 0-1, how confident the mapping is


@dataclass
class StateVar:
    """A React state variable."""
    name: str
    type: str
    initial_value: str
    line: int
    behavior_type: str  # navigation | toggle | filter | selection | view-mode


@dataclass
class SlotDefinition:
    """A structural slot in the component."""
    name: str
    element: str  # div, button, input, etc.
    role: str  # sidebar, toolbar, content, footer, etc.
    line: int


@dataclass
class ComponentAudit:
    """Complete audit result for a component."""
    file_path: str
    component_name: str
    total_lines: int
    # Appearance
    hardcoded_values: List[HardcodedValue] = field(default_factory=list)
    hardcoded_count: int = 0
    token_coverage: float = 0.0  # % that can be auto-mapped
    # Behavior
    state_vars: List[StateVar] = field(default_factory=list)
    event_handlers: int = 0
    conditional_renders: int = 0
    # Structure
    slots: List[SlotDefinition] = field(default_factory=list)
    sub_components: List[str] = field(default_factory=list)
    props_interface: Optional[str] = None
    # Purpose (inferred)
    inferred_purpose: str = ""
    inferred_role: str = ""  # anchor | detail | evidence | action
    inferred_cost: str = ""  # glance | scan | study | analyze
    # Summary
    conversion_difficulty: str = ""  # easy | moderate | hard
    manual_review_items: List[str] = field(default_factory=list)


# ── Scanner ───────────────────────────────────────────────

def scan_component(filepath: str) -> ComponentAudit:
    """Scan a TSX file and produce a complete audit."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    content = path.read_text(errors="ignore")
    lines = content.split("\n")
    audit = ComponentAudit(
        file_path=str(path),
        component_name=path.stem,
        total_lines=len(lines),
    )

    # 1. Find component name
    for m in RE_COMPONENT.finditer(content):
        name = m.group(1)
        if name[0].isupper():  # React components start uppercase
            audit.component_name = name
            break

    # 2. Scan for hardcoded visual values
    for i, line in enumerate(lines, 1):
        # Colors
        for m in RE_TW_COLOR.finditer(line):
            color_name = m.group(1)
            shade = m.group(2) or ""
            opacity = m.group(3)
            original = m.group(0)

            key = f"{color_name}-{shade}" if shade else color_name
            suggested = None
            confidence = 0.0

            if key in NEUTRAL_MAP:
                suggested = NEUTRAL_MAP[key]
                confidence = 0.85
            elif color_name in COLOR_MAP:
                suggested = COLOR_MAP[color_name]
                confidence = 0.7
            elif color_name in ("white", "black"):
                suggested = "--color-text" if "text" in original else "--color-bg"
                confidence = 0.6

            audit.hardcoded_values.append(HardcodedValue(
                line=i,
                original=original,
                category="color",
                suggested_token=suggested,
                context=line.strip()[:120],
                confidence=confidence,
            ))

        # Font sizes
        for m in RE_TW_FONT.finditer(line):
            original = m.group(0)
            suggested = FONT_MAP.get(original)
            audit.hardcoded_values.append(HardcodedValue(
                line=i,
                original=original,
                category="font",
                suggested_token=suggested,
                context=line.strip()[:120],
                confidence=0.9 if suggested else 0.5,
            ))

        # Radius
        for m in RE_TW_RADIUS.finditer(line):
            original = m.group(0)
            suggested = RADIUS_MAP.get(original)
            audit.hardcoded_values.append(HardcodedValue(
                line=i,
                original=original,
                category="radius",
                suggested_token=suggested,
                context=line.strip()[:120],
                confidence=0.9 if suggested else 0.5,
            ))

    audit.hardcoded_count = len(audit.hardcoded_values)
    mapped = sum(1 for v in audit.hardcoded_values if v.suggested_token)
    audit.token_coverage = (mapped / audit.hardcoded_count * 100) if audit.hardcoded_count > 0 else 100

    # 3. Scan for state/behavior
    for m in RE_STATE_HOOK.finditer(content):
        type_hint = m.group(1) or "unknown"
        initial = m.group(2).strip()
        line_num = content[:m.start()].count("\n") + 1

        # Classify behavior type
        name_lower = initial.lower() + " " + type_hint.lower()
        if any(k in name_lower for k in ["path", "folder", "navigate", "breadcrumb", "route"]):
            btype = "navigation"
        elif any(k in name_lower for k in ["expanded", "open", "collapsed", "toggle", "visible"]):
            btype = "toggle"
        elif any(k in name_lower for k in ["search", "filter", "query"]):
            btype = "filter"
        elif any(k in name_lower for k in ["selected", "selection", "checked"]):
            btype = "selection"
        elif any(k in name_lower for k in ["view", "mode", "layout", "sort"]):
            btype = "view-mode"
        else:
            btype = "general"

        audit.state_vars.append(StateVar(
            name=type_hint,
            type=type_hint,
            initial_value=initial[:50],
            line=line_num,
            behavior_type=btype,
        ))

    audit.event_handlers = len(RE_HANDLERS.findall(content))
    audit.conditional_renders = len(RE_CONDITIONAL.findall(content))

    # 4. Infer sub-components
    imports_section = content[:content.find("export") if "export" in content else 500]
    for m in re.finditer(r'import\s+{([^}]+)}\s+from\s+[\'"]\./', imports_section):
        for name in m.group(1).split(","):
            name = name.strip()
            if name and name[0].isupper():
                audit.sub_components.append(name)

    # 5. Infer props interface
    for m in RE_PROPS.finditer(content):
        audit.props_interface = m.group(1)
        break

    # 6. Infer purpose from component name and content
    name_lower = audit.component_name.lower()
    if any(k in name_lower for k in ["explorer", "browser", "navigator", "tree"]):
        audit.inferred_purpose = "Navigate and explore a hierarchical data structure"
        audit.inferred_role = "detail"
        audit.inferred_cost = "study"
    elif any(k in name_lower for k in ["metric", "stat", "gauge", "counter"]):
        audit.inferred_purpose = "Display a key metric at a glance"
        audit.inferred_role = "anchor"
        audit.inferred_cost = "glance"
    elif any(k in name_lower for k in ["timeline", "history", "feed", "list"]):
        audit.inferred_purpose = "Show chronological events or items"
        audit.inferred_role = "evidence"
        audit.inferred_cost = "scan"
    elif any(k in name_lower for k in ["inspector", "detail", "panel"]):
        audit.inferred_purpose = "Inspect detailed properties of a selected item"
        audit.inferred_role = "detail"
        audit.inferred_cost = "study"
    elif any(k in name_lower for k in ["form", "config", "settings", "editor"]):
        audit.inferred_purpose = "Configure or edit system parameters"
        audit.inferred_role = "action"
        audit.inferred_cost = "analyze"
    elif any(k in name_lower for k in ["grid", "inventory", "table"]):
        audit.inferred_purpose = "Display a collection of items in a structured layout"
        audit.inferred_role = "detail"
        audit.inferred_cost = "scan"
    else:
        audit.inferred_purpose = f"Component: {audit.component_name}"
        audit.inferred_role = "detail"
        audit.inferred_cost = "scan"

    # 7. Assess conversion difficulty
    if audit.hardcoded_count < 20 and len(audit.state_vars) < 3:
        audit.conversion_difficulty = "easy"
    elif audit.hardcoded_count < 60 and len(audit.state_vars) < 6:
        audit.conversion_difficulty = "moderate"
    else:
        audit.conversion_difficulty = "hard"

    # 8. Flag items needing manual review
    unmapped = [v for v in audit.hardcoded_values if not v.suggested_token]
    if unmapped:
        audit.manual_review_items.append(f"{len(unmapped)} values without token mapping")
    if audit.event_handlers > 5:
        audit.manual_review_items.append(f"{audit.event_handlers} event handlers — check for side effects")
    if audit.conditional_renders > 10:
        audit.manual_review_items.append(f"Complex conditional rendering — may need recipe variants")

    return audit


def generate_scroll_skeleton(audit: ComponentAudit) -> Dict[str, Any]:
    """Generate a Scroll (semantic file) skeleton from the audit."""
    return {
        "id": f"component.{audit.component_name.lower().replace('_', '-')}",
        "kind": "panel",
        "purpose": {
            "exists_to": audit.inferred_purpose,
            "becoming": f"A fully parametric {audit.component_name}",
            "relevance": 0.7,
            "attention_cost": audit.inferred_cost,
            "narrative_role": audit.inferred_role,
        },
        "structure": {
            "slots": [s.name for s in audit.slots] or ["root"],
            "variants": [sv.behavior_type for sv in audit.state_vars if sv.behavior_type == "view-mode"],
            "states": [sv.behavior_type for sv in audit.state_vars if sv.behavior_type in ("toggle", "selection")],
        },
        "sense": {
            "source": "local",
            "endpoint": "TBD",
            "interval_ms": 0,
        },
        "controls": [
            {"id": sv.name, "kind": sv.behavior_type, "safe": True}
            for sv in audit.state_vars
            if sv.behavior_type in ("filter", "view-mode", "toggle")
        ],
        "conversion": {
            "original_file": audit.file_path,
            "total_lines": audit.total_lines,
            "hardcoded_values": audit.hardcoded_count,
            "token_coverage": f"{audit.token_coverage:.0f}%",
            "difficulty": audit.conversion_difficulty,
            "manual_review": audit.manual_review_items,
        },
    }


def generate_token_map(audit: ComponentAudit) -> List[Dict[str, str]]:
    """Generate the hardcoded → token mapping table."""
    seen = set()
    mappings = []
    for v in audit.hardcoded_values:
        if v.suggested_token and v.original not in seen:
            seen.add(v.original)
            mappings.append({
                "original": v.original,
                "token": v.suggested_token,
                "category": v.category,
                "confidence": f"{v.confidence:.0%}",
            })
    # Sort by category then original
    mappings.sort(key=lambda m: (m["category"], m["original"]))
    return mappings


# ── CLI ───────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python component_scanner.py <path/to/Component.tsx> [--output dir]")
        sys.exit(1)

    filepath = sys.argv[1]
    output_dir = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    # Scan
    audit = scan_component(filepath)
    scroll = generate_scroll_skeleton(audit)
    token_map = generate_token_map(audit)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"Component Scanner: {audit.component_name}")
    print(f"{'=' * 60}")
    print(f"  File: {audit.file_path}")
    print(f"  Lines: {audit.total_lines}")
    print(f"  Difficulty: {audit.conversion_difficulty.upper()}")
    print()
    print(f"  APPEARANCE ({audit.hardcoded_count} hardcoded values)")
    by_cat = defaultdict(int)
    for v in audit.hardcoded_values:
        by_cat[v.category] += 1
    for cat, count in sorted(by_cat.items()):
        print(f"    {cat}: {count}")
    print(f"    Token coverage: {audit.token_coverage:.0f}%")
    print()
    print(f"  BEHAVIOR ({len(audit.state_vars)} state variables)")
    for sv in audit.state_vars:
        print(f"    {sv.name} ({sv.behavior_type}): {sv.initial_value}")
    print(f"    Event handlers: {audit.event_handlers}")
    print(f"    Conditional renders: {audit.conditional_renders}")
    print()
    print(f"  STRUCTURE")
    print(f"    Sub-components: {audit.sub_components or 'none'}")
    print(f"    Props: {audit.props_interface or 'none'}")
    print()
    print(f"  PURPOSE (inferred)")
    print(f"    {audit.inferred_purpose}")
    print(f"    Role: {audit.inferred_role}, Cost: {audit.inferred_cost}")
    print()
    if audit.manual_review_items:
        print(f"  MANUAL REVIEW NEEDED:")
        for item in audit.manual_review_items:
            print(f"    - {item}")
    print()
    print(f"  TOKEN MAP ({len(token_map)} unique mappings)")
    for m in token_map[:15]:
        print(f"    {m['original']:30s} → {m['token']:30s} ({m['confidence']})")
    if len(token_map) > 15:
        print(f"    ... and {len(token_map) - 15} more")

    # Output files
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        (out / "audit.json").write_text(json.dumps(asdict(audit), indent=2, default=str))
        (out / "scroll.yaml").write_text(json.dumps(scroll, indent=2, default=str))
        (out / "token_map.json").write_text(json.dumps(token_map, indent=2))

        print(f"\n  Output written to {out}/")
        print(f"    audit.json   — full audit report")
        print(f"    scroll.yaml  — semantic file skeleton")
        print(f"    token_map.json — hardcoded → token mappings")


if __name__ == "__main__":
    main()
