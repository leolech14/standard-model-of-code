import os
from pathlib import Path

path = Path("/Users/lech/PROJECTS_all/PROJECT_elements/particle/src/core/viz/assets/template.html")
lines = path.read_text(encoding="utf-8").splitlines()

# Filter out lines with assets/modules/
new_lines = [l for l in lines if 'src="assets/modules/' not in l and 'src=\'assets/modules/' not in l]

if len(new_lines) < len(lines):
    print(f"Removed {len(lines) - len(new_lines)} lines.")
    path.write_text("\n".join(new_lines), encoding="utf-8")
else:
    print("No lines removed (pattern not found).")
