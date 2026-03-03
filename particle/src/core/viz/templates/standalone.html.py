#!/usr/bin/env python3
"""
Generate standalone.html template from the existing template.html.

This script transforms template.html to use Vite-compatible placeholders
and the new payload injection strategy.

Usage:
    python standalone.html.py  # Outputs templates/standalone.html
"""

from pathlib import Path

def generate_standalone_template():
    """Transform template.html into a Vite-compatible standalone template."""
    assets_dir = Path(__file__).parent.parent / "assets"
    template_path = assets_dir / "template.html"

    if not template_path.exists():
        raise FileNotFoundError(f"Source template not found: {template_path}")

    content = template_path.read_text(encoding="utf-8")

    # 1. Replace {{STYLES}} with __STYLES_PLACEHOLDER__
    content = content.replace("{{STYLES}}", "__STYLES_PLACEHOLDER__")

    # 2. Replace {{VERSION}} with __VERSION_PLACEHOLDER__
    content = content.replace("{{VERSION}}", "__VERSION_PLACEHOLDER__")

    # 3. Remove the 3 inlined <script> blocks (HardwareInfo, ControlRegistry, SettingsPanel)
    #    They are between "<!-- INLINED MODULES FOR GENERATED REPORTS -->" and the APP_JS script
    inlined_start = content.find("<!-- INLINED MODULES FOR GENERATED REPORTS -->")
    app_js_script = content.find("<script>\n        {{APP_JS}}")
    if app_js_script < 0:
        app_js_script = content.find("<script>\n    {{APP_JS}}")
    if app_js_script < 0:
        # Try looser match
        app_js_script = content.find("{{APP_JS}}")
        if app_js_script > 0:
            # Back up to the <script> tag
            app_js_script = content.rfind("<script>", 0, app_js_script)

    if inlined_start > 0 and app_js_script > inlined_start:
        # Remove inlined scripts, keep the APP_JS script
        content = content[:inlined_start] + "\n    " + content[app_js_script:]

    # 4. Add payload script tag before the bundle script
    payload_tag = '    <script id="collider-payload" type="application/json">__PAYLOAD_PLACEHOLDER__</script>\n\n'

    # Find the APP_JS injection point and replace
    content = content.replace(
        "<script>\n        {{APP_JS}}\n    </script>",
        payload_tag + '    <script>\n        __BUNDLE_JS_PLACEHOLDER__\n    </script>'
    )

    # Fallback if indentation differs
    if "__BUNDLE_JS_PLACEHOLDER__" not in content:
        content = content.replace("{{APP_JS}}", "__BUNDLE_JS_PLACEHOLDER__")
        # Insert payload tag before the script containing the bundle
        bundle_pos = content.find("__BUNDLE_JS_PLACEHOLDER__")
        if bundle_pos > 0:
            script_pos = content.rfind("<script>", 0, bundle_pos)
            if script_pos > 0:
                content = content[:script_pos] + payload_tag + content[script_pos:]

    # 5. Also ensure __PAYLOAD_PLACEHOLDER__ is in the content
    if "__PAYLOAD_PLACEHOLDER__" not in content:
        # Emergency fallback: insert before </body>
        content = content.replace(
            "</body>",
            f'{payload_tag}</body>'
        )

    return content


if __name__ == "__main__":
    output_dir = Path(__file__).parent
    output_path = output_dir / "standalone.html"
    content = generate_standalone_template()
    output_path.write_text(content, encoding="utf-8")
    print(f"Generated {output_path} ({len(content)} bytes)")
