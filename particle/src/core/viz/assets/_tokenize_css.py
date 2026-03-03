#!/usr/bin/env python3
"""
Phase 1R: Systematic px-to-token replacement for styles.css.

Applies context-aware replacements following the Category A-J mapping
from the Phase 1R plan. Run once, then delete this script.
"""

import re
from pathlib import Path

CSS_FILE = Path(__file__).parent / "styles.css"


def tokenize_css(css: str) -> str:
    """Apply all token replacements to CSS content."""

    # ── Category D: Letter-spacing (global safe) ──────────────────────
    css = css.replace("letter-spacing: 0.3px", "letter-spacing: var(--letter-spacing-tight)")
    css = css.replace("letter-spacing: 0.4px", "letter-spacing: var(--letter-spacing-tight)")
    css = css.replace("letter-spacing: 0.5px", "letter-spacing: var(--letter-spacing-snug)")
    css = css.replace("letter-spacing: 0.6px", "letter-spacing: var(--letter-spacing-snug)")
    css = css.replace("letter-spacing: 1.2px", "letter-spacing: var(--letter-spacing-wide)")
    css = css.replace("letter-spacing: 1.5px", "letter-spacing: var(--letter-spacing-wide)")
    css = css.replace("letter-spacing: 2px", "letter-spacing: var(--letter-spacing-wider)")
    # 1px must come after 1.2px and 1.5px to avoid partial matches
    css = css.replace("letter-spacing: 1px", "letter-spacing: var(--letter-spacing-normal)")

    # ── Category I: Blur values ───────────────────────────────────────
    css = css.replace("blur(8px)", "blur(var(--blur-sm))")
    css = css.replace("blur(12px)", "blur(var(--blur-md))")
    css = css.replace("blur(20px)", "blur(var(--blur-lg))")
    css = css.replace("blur(24px)", "blur(var(--blur-xl))")

    # ── Category H: Toggle switch dimensions ──────────────────────────
    # Toggle container
    css = re.sub(
        r'(\.toggle-switch\s*\{[^}]*?)width:\s*44px',
        r'\1width: var(--size-component-toggle-width)',
        css
    )
    css = re.sub(
        r'(\.toggle-switch\s*\{[^}]*?)height:\s*24px',
        r'\1height: var(--size-component-toggle-height)',
        css
    )
    # Toggle thumb (::after)
    css = re.sub(
        r'(\.toggle-switch::after\s*\{[^}]*?)top:\s*2px',
        r'\1top: var(--size-component-toggle-inset)',
        css
    )
    css = re.sub(
        r'(\.toggle-switch::after\s*\{[^}]*?)left:\s*2px',
        r'\1left: var(--size-component-toggle-inset)',
        css
    )
    css = re.sub(
        r'(\.toggle-switch::after\s*\{[^}]*?)width:\s*20px',
        r'\1width: var(--size-component-toggle-thumb)',
        css
    )
    css = re.sub(
        r'(\.toggle-switch::after\s*\{[^}]*?)height:\s*20px',
        r'\1height: var(--size-component-toggle-thumb)',
        css
    )
    # Toggle active translateX
    css = css.replace(
        "transform: translateX(20px)",
        "transform: translateX(var(--size-component-toggle-thumb))"
    )

    # ── Category H: Slider dimensions ─────────────────────────────────
    # Base slider track height
    css = re.sub(
        r'(input\[type="range"\]\s*\{[^}]*?)height:\s*4px',
        r'\1height: var(--size-component-slider-track)',
        css
    )
    # Base slider thumb
    css = re.sub(
        r'(input\[type="range"\]::-webkit-slider-thumb\s*\{[^}]*?)width:\s*14px',
        r'\1width: var(--size-component-slider-thumb)',
        css
    )
    css = re.sub(
        r'(input\[type="range"\]::-webkit-slider-thumb\s*\{[^}]*?)height:\s*14px',
        r'\1height: var(--size-component-slider-thumb)',
        css
    )
    css = re.sub(
        r'(input\[type="range"\]::-moz-range-thumb\s*\{[^}]*?)width:\s*14px',
        r'\1width: var(--size-component-slider-thumb)',
        css
    )
    css = re.sub(
        r'(input\[type="range"\]::-moz-range-thumb\s*\{[^}]*?)height:\s*14px',
        r'\1height: var(--size-component-slider-thumb)',
        css
    )
    # .slider-input (larger slider)
    css = re.sub(
        r'(\.slider-input\s*\{[^}]*?)height:\s*6px',
        r'\1height: var(--size-component-slider-track-lg)',
        css
    )
    css = re.sub(
        r'(\.slider-input::-webkit-slider-thumb\s*\{[^}]*?)width:\s*16px',
        r'\1width: calc(var(--size-component-slider-thumb) + var(--spacing-0-5))',
        css
    )
    css = re.sub(
        r'(\.slider-input::-webkit-slider-thumb\s*\{[^}]*?)height:\s*16px',
        r'\1height: calc(var(--size-component-slider-thumb) + var(--spacing-0-5))',
        css
    )
    # Amplifier meta-slider thumb (18px)
    css = re.sub(
        r'(\.slider-row\.meta-amplifier\s+\.slider-input::-webkit-slider-thumb\s*\{[^}]*?)width:\s*18px',
        r'\1width: var(--size-component-slider-thumb-lg)',
        css
    )
    css = re.sub(
        r'(\.slider-row\.meta-amplifier\s+\.slider-input::-webkit-slider-thumb\s*\{[^}]*?)height:\s*18px',
        r'\1height: var(--size-component-slider-thumb-lg)',
        css
    )

    # ── Category H: Cmd button dimensions ─────────────────────────────
    css = re.sub(
        r'(\.cmd-btn\s*\{[^}]*?)width:\s*40px',
        r'\1width: var(--size-component-cmd-button)',
        css
    )
    css = re.sub(
        r'(\.cmd-btn\s*\{[^}]*?)height:\s*40px',
        r'\1height: var(--size-component-cmd-button)',
        css
    )

    # ── Category H: Swatch dimensions ─────────────────────────────────
    css = re.sub(
        r'(\.oklch-swatch\s*\{[^}]*?)width:\s*60px',
        r'\1width: var(--size-component-swatch)',
        css
    )
    css = re.sub(
        r'(\.oklch-swatch\s*\{[^}]*?)height:\s*60px',
        r'\1height: var(--size-component-swatch)',
        css
    )

    # ── Category H: Confidence bar ────────────────────────────────────
    css = re.sub(
        r'(\.insights-confidence-bar\s*\{[^}]*?)width:\s*50px',
        r'\1width: var(--size-component-confidence-bar-width)',
        css
    )
    css = re.sub(
        r'(\.insights-confidence-bar\s*\{[^}]*?)height:\s*4px',
        r'\1height: var(--size-component-confidence-bar-height)',
        css
    )

    # ── Category H: Divider height ────────────────────────────────────
    css = re.sub(
        r'(\.cmd-divider\s*\{[^}]*?)height:\s*28px',
        r'\1height: var(--size-component-divider-height)',
        css
    )

    # ── Category H: Chip border-radius ────────────────────────────────
    css = re.sub(
        r'(\.chip\s*\{[^}]*?)border-radius:\s*14px',
        r'\1border-radius: var(--size-component-chip-radius)',
        css
    )

    # ── Category H: Tooltip arrow ─────────────────────────────────────
    css = css.replace(
        "border: 6px solid transparent",
        "border: var(--size-component-tooltip-arrow) solid transparent"
    )

    # ── Category E: Panel widths → clamp() ────────────────────────────
    # Sidebar width: 260px
    css = re.sub(
        r'(\.sidebar\s*\{[^}]*?)width:\s*260px',
        r'\1width: clamp(200px, 25vw, 280px)',
        css
    )
    # Insights panel width: 420px
    css = re.sub(
        r'(\.insights-panel\s*\{[^}]*?)width:\s*420px',
        r'\1width: clamp(300px, 38vw, 480px)',
        css
    )
    # Selection panel: 320px
    css = re.sub(
        r'(\.selection-panel\s*\{[^}]*?)width:\s*320px',
        r'\1width: clamp(240px, 30vw, 360px)',
        css
    )
    # File panel: 400px
    css = re.sub(
        r'(\.file-panel\s*\{[^}]*?)width:\s*400px',
        r'\1width: clamp(280px, 35vw, 420px)',
        css
    )
    # OKLCH picker: 320px
    css = re.sub(
        r'(\.oklch-picker\s*\{[^}]*?)width:\s*320px',
        r'\1width: clamp(240px, 30vw, 360px)',
        css
    )
    # Insights panel right offset: 300px
    # right: 300px → right: clamp(220px, 30vw, 340px) (if present)
    css = re.sub(
        r'(\.insights-panel[^{]*\{[^}]*?)right:\s*300px',
        r'\1right: clamp(220px, 30vw, 340px)',
        css
    )
    # Control bar min-width: 800px
    css = re.sub(
        r'(\.control-bar\.floating\s*\{[^}]*?)min-width:\s*800px',
        r'\1min-width: clamp(600px, 80vw, 900px)',
        css
    )
    # Floating panel min/max width
    css = re.sub(
        r'(\.floating-panel\s*\{[^}]*?)min-width:\s*340px',
        r'\1min-width: clamp(280px, 35vw, 400px)',
        css
    )
    css = re.sub(
        r'(\.floating-panel\s*\{[^}]*?)max-width:\s*420px',
        r'\1max-width: clamp(360px, 38vw, 480px)',
        css
    )

    # ── Category F: max-height → viewport-relative ────────────────────
    css = css.replace("max-height: 100px", "max-height: min(100px, 20vh)")
    css = css.replace("max-height: 120px", "max-height: min(120px, 25vh)")
    css = css.replace("max-height: 150px", "max-height: min(150px, 30vh)")
    css = css.replace("max-height: 300px", "max-height: min(300px, 40vh)")
    css = css.replace("max-height: 350px", "max-height: min(350px, 45vh)")
    css = css.replace("max-height: 600px", "max-height: min(600px, 70vh)")
    css = css.replace("max-height: 800px", "max-height: min(800px, 80vh)")

    # ── Category G: Position offsets ──────────────────────────────────
    # top: 140px → var(--offset-content-top)
    css = re.sub(
        r'(\s)top:\s*140px',
        r'\1top: var(--offset-content-top)',
        css
    )
    # top: 100px in hover-panel
    css = re.sub(
        r'(\.hover-panel\s*\{[^}]*?)top:\s*100px',
        r'\1top: var(--offset-sidebar-top)',
        css
    )
    # bottom: 80px → var(--offset-bottom-dock)
    css = re.sub(
        r'(\s)bottom:\s*80px',
        r'\1bottom: var(--offset-bottom-dock)',
        css
    )
    # bottom: 70px → var(--offset-bottom-dock-above)
    css = re.sub(
        r'(\s)bottom:\s*70px',
        r'\1bottom: var(--offset-bottom-dock-above)',
        css
    )
    # bottom: 60px
    css = re.sub(
        r'(\s)bottom:\s*60px',
        r'\1bottom: calc(var(--offset-bottom-dock) - var(--spacing-8))',
        css
    )
    # bottom: 100px
    css = re.sub(
        r'(\s)bottom:\s*100px',
        r'\1bottom: calc(var(--offset-bottom-dock) + var(--spacing-8))',
        css
    )
    # top: 92px (sidebar)
    css = re.sub(
        r'(\s)top:\s*92px',
        r'\1top: var(--offset-sidebar-top)',
        css
    )
    # left: 20px (file-panel)
    css = re.sub(
        r'(\.file-panel\s*\{[^}]*?)left:\s*20px',
        r'\1left: var(--offset-sidebar-left)',
        css
    )
    # bottom: 24px (control-bar)
    css = re.sub(
        r'(\.control-bar\.floating\s*\{[^}]*?)bottom:\s*24px',
        r'\1bottom: var(--spacing-10)',
        css
    )

    # ── Category C: Font sizes ────────────────────────────────────────
    # font-size: 6px → 3xs
    css = css.replace("font-size: 6px", "font-size: var(--typography-size-3xs)")
    # font-size: 8px → 2xs (close to 7px token)
    css = css.replace("font-size: 8px", "font-size: var(--typography-size-2xs)")
    # font-size: 9px → 2xs
    css = css.replace("font-size: 9px", "font-size: var(--typography-size-2xs)")
    # font-size: 10px → xs
    css = css.replace("font-size: 10px", "font-size: var(--typography-size-xs)")
    # font-size: 11px → sm
    css = css.replace("font-size: 11px", "font-size: var(--typography-size-sm)")
    # font-size: 14px → md (only standalone, not inside other values)
    css = re.sub(r'font-size:\s*14px', 'font-size: var(--typography-size-md)', css)
    # font-size: 18px → 2xl
    css = css.replace("font-size: 18px", "font-size: var(--typography-size-2xl)")

    # ── Category B: Border radius (context-safe patterns) ─────────────
    # border-radius: 3px → var(--radius-sm)  (but not inside shorthand)
    css = re.sub(r'border-radius:\s*3px;', 'border-radius: var(--radius-sm);', css)
    # border-radius: 8px → var(--radius-lg)
    css = re.sub(r'border-radius:\s*8px;', 'border-radius: var(--radius-lg);', css)
    # border-radius: 10px → var(--radius-xl)
    css = re.sub(r'border-radius:\s*10px;', 'border-radius: var(--radius-xl);', css)
    # border-radius: 12px → var(--radius-2xl)
    css = re.sub(r'border-radius:\s*12px;', 'border-radius: var(--radius-2xl);', css)

    # ── Category A: Spacing - tooltip padding/margin ──────────────────
    # Tooltip: padding: 6px 12px → var(--spacing-2-5) var(--spacing-5)
    css = re.sub(
        r'(\.tooltip\s*\{[^}]*?)padding:\s*6px 12px',
        r'\1padding: var(--spacing-2-5) var(--spacing-5)',
        css
    )
    # .cmd-divider margin: 6px 4px
    css = re.sub(
        r'(\.cmd-divider\s*\{[^}]*?)margin:\s*6px 4px',
        r'\1margin: var(--spacing-2-5) var(--spacing-1-5)',
        css
    )

    # ── Category A: Amplifier meta-slider spacing ─────────────────────
    css = re.sub(
        r'(\.slider-row\.meta-amplifier\s*\{[^}]*?)padding:\s*10px 12px',
        r'\1padding: var(--spacing-4) var(--spacing-5)',
        css
    )
    css = re.sub(
        r'(\.slider-row\.meta-amplifier\s*\{[^}]*?)margin:\s*12px 0',
        r'\1margin: var(--spacing-5) 0',
        css
    )
    # right: 10px in meta-amplifier::before
    css = re.sub(
        r'(\.slider-row\.meta-amplifier::before\s*\{[^}]*?)right:\s*10px',
        r'\1right: var(--spacing-4)',
        css
    )
    # padding: 0 4px in meta-amplifier::before
    css = re.sub(
        r'(\.slider-row\.meta-amplifier::before\s*\{[^}]*?)padding:\s*0 4px',
        r'\1padding: 0 var(--spacing-1-5)',
        css
    )
    # margin-top: 4px in meta-amplifier .slider-desc
    css = re.sub(
        r'(\.slider-row\.meta-amplifier\s+\.slider-desc\s*\{[^}]*?)margin-top:\s*4px',
        r'\1margin-top: var(--spacing-1-5)',
        css
    )

    # ── Category A: Segmented control spacing ─────────────────────────
    css = re.sub(
        r'(\.segmented-control\s*\{[^}]*?)padding:\s*3px',
        r'\1padding: var(--spacing-1)',
        css
    )
    css = re.sub(
        r'(\.segment\s*\{[^}]*?)padding:\s*8px 12px',
        r'\1padding: var(--spacing-3) var(--spacing-5)',
        css
    )

    # ── Category A: Panel close button padding ────────────────────────
    css = re.sub(
        r'(\.panel-close\s*\{[^}]*?)padding:\s*4px',
        r'\1padding: var(--spacing-1-5)',
        css
    )

    # ── Category A: Control bar padding ───────────────────────────────
    css = re.sub(
        r'(\.control-bar\.floating\s*\{[^}]*?)padding:\s*4px',
        r'\1padding: var(--spacing-1-5)',
        css
    )

    # ── Category A: Chip count spacing ────────────────────────────────
    css = re.sub(
        r'(\.chip-count\s*\{[^}]*?)margin-left:\s*4px',
        r'\1margin-left: var(--spacing-1-5)',
        css
    )

    # ── Floating panel inner spacing ──────────────────────────────────
    css = re.sub(
        r'(\.floating-panel::before\s*\{[^}]*?)left:\s*6px',
        r'\1left: var(--spacing-2-5)',
        css
    )
    css = re.sub(
        r'(\.floating-panel::before\s*\{[^}]*?)top:\s*30px',
        r'\1top: var(--spacing-12)',
        css
    )
    css = re.sub(
        r'(\.floating-panel::before\s*\{[^}]*?)bottom:\s*30px',
        r'\1bottom: var(--spacing-12)',
        css
    )
    css = re.sub(
        r'(\.floating-panel::before\s*\{[^}]*?)width:\s*2px',
        r'\1width: var(--spacing-0-5)',
        css
    )
    # border-radius: 2px in floating-panel::before
    css = re.sub(
        r'(\.floating-panel::before\s*\{[^}]*?)border-radius:\s*2px',
        r'\1border-radius: var(--spacing-0-5)',
        css
    )

    # ── Floating panel organic shape 60px → component token ───────────
    # Keep 60px in border-radius for the organic concave shape -- it's intentional design
    # But reference as a distinct value type

    # ── Transition patterns using raw time values ─────────────────────
    # transition: left 150ms ease-out, top 150ms ease-out → var(--transition-position)
    css = css.replace(
        "transition: left 150ms ease-out, top 150ms ease-out",
        "transition: var(--transition-position)"
    )
    # transition: all 0.15s → var(--transition-default)
    css = re.sub(
        r'(\.segment\s*\{[^}]*?)transition:\s*all 0\.15s',
        r'\1transition: var(--transition-default)',
        css
    )

    # ── Focus outlines (accessibility) ────────────────────────────────
    css = re.sub(
        r'outline:\s*2px solid var\(--color-border-focus\)',
        'outline: var(--spacing-0-5) solid var(--color-border-focus)',
        css
    )
    css = re.sub(
        r'outline-offset:\s*2px',
        'outline-offset: var(--spacing-0-5)',
        css
    )

    # ── File-panel max-height and other remaining ─────────────────────
    # oklch-canvas-2d height: 120px
    css = re.sub(
        r'(\.oklch-canvas-2d\s*\{[^}]*?)height:\s*120px',
        r'\1height: min(120px, 25vh)',
        css
    )

    # ── border-left: 3px solid → spacing-1 ────────────────────────────
    css = re.sub(
        r'border-left:\s*3px solid',
        'border-left: var(--spacing-1) solid',
        css
    )

    # ── border: 2px solid (non-1px borders, excluding toggle inset) ───
    css = re.sub(
        r'(\.oklch-swatch\s*\{[^}]*?)border:\s*2px solid',
        r'\1border: var(--spacing-0-5) solid',
        css
    )
    css = re.sub(
        r'(\.oval-debug\s*\{[^}]*?)border:\s*2px dashed',
        r'\1border: var(--spacing-0-5) dashed',
        css
    )

    # ── max-width patterns ────────────────────────────────────────────
    css = re.sub(
        r'(\.sidebar-search input\s*\{[^}]*?)max-width:\s*240px',
        r'\1max-width: clamp(180px, 20vw, 260px)',
        css
    )
    css = re.sub(
        r'max-width:\s*180px',
        'max-width: clamp(140px, 18vw, 200px)',
        css
    )

    # ── Category A: Remaining isolated spacing fixes ──────────────────
    # hover-panel-row .label min-width: 70px
    # oklch-slider-group label width: 70px
    # Keep these as design decisions (label alignment widths)

    # ── top: 0px → just 0 ────────────────────────────────────────────
    css = css.replace("top: 0px", "top: 0")

    # ── arc-left floating-panel right: 6px ────────────────────────────
    css = re.sub(
        r'(arc-left.*?\.floating-panel::before\s*\{[^}]*?)right:\s*6px',
        r'\1right: var(--spacing-2-5)',
        css,
        flags=re.DOTALL
    )

    # ── Transform translateX with raw px ──────────────────────────────
    css = css.replace(
        "transform: translateX(30px)",
        "transform: translateX(var(--spacing-12))"
    )

    # ── Transition patterns ───────────────────────────────────────────
    # transition: opacity 0.15s ease, transform 0.15s ease → proper token
    css = css.replace(
        "transition: opacity 0.15s ease, transform 0.15s ease",
        "transition: opacity var(--duration-normal) var(--easing-ease), transform var(--duration-normal) var(--easing-ease)"
    )
    # transition: all 0.4s cubic-bezier → keep as is (custom easing)

    # ── box-shadow with hardcoded px ──────────────────────────────────
    # box-shadow: 0 4px 12px → rendering primitives in shadows, keep
    # box-shadow: 0 10px 40px → keep (shadow values are rendering primitives)

    # ── translateY(-8px) / translateY(-4px) in tooltips ───────────────
    # These are animation offsets -- keep as rendering primitives

    # ── transform: translateX(8px/12px/-8px/-12px) in tooltip variants ─
    # These are small animation offsets -- keep as rendering primitives

    # ── left: -6px, right: -12px in tooltip arrows ────────────────────
    # These are negative offsets for arrow positioning -- keep

    # ── --px/--py panel layout variables ──────────────────────────────
    # These are CSS custom property definitions, not hardcoded values -- keep

    # ── 1px borders (Category J) ──────────────────────────────────────
    # All 1px borders are rendering primitives -- KEEP

    # ── border: 1.5px ─────────────────────────────────────────────────
    # Keep as rendering edge case

    return css


def main():
    print(f"Reading {CSS_FILE}")
    original = CSS_FILE.read_text()

    # Count raw px before
    before_count = len(re.findall(r'\d+px', original))
    print(f"  Raw px occurrences before: {before_count}")

    result = tokenize_css(original)

    # Count raw px after
    after_count = len(re.findall(r'\d+px', result))
    print(f"  Raw px occurrences after: {after_count}")
    print(f"  Tokens applied: {before_count - after_count}")

    CSS_FILE.write_text(result)
    print(f"  Written to {CSS_FILE}")


if __name__ == "__main__":
    main()
