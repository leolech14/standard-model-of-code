import re
from pathlib import Path

modules_dir = Path("/Users/lech/PROJECTS_all/PROJECT_elements/particle/src/core/viz/assets/modules")
files = list(modules_dir.glob("*.js"))

pattern = re.compile(r"^const\s+(\w+)\s*=\s*\(function", re.MULTILINE)

for f in files:
    content = f.read_text(encoding="utf-8")

    # Check if we need to patch
    if pattern.search(content):
        new_content = pattern.sub(r"window.\1 = (function", content)
        f.write_text(new_content, encoding="utf-8")
        print(f"Patched {f.name}")
    else:
        # Check if it was already patched or doesn't match
        if "window." in content and "= (function" in content:
            print(f"Skipped {f.name} (already appears patched or different structure)")
        else:
            print(f"Skipped {f.name} (pattern not found)")
