import re
from pathlib import Path

path = Path("/Users/lech/PROJECTS_all/PROJECT_elements/particle/src/core/viz/assets/template.html")
content = path.read_text(encoding="utf-8")

# Fix STYLES (multi-line)
# Pattern: { followed by whitespace, {, whitespace, STYLES, whitespace, }, whitespace, }
# We want to replace the whole block inside <style>...</style> if possible, or just the brace pattern.
# The pattern seen:
#         {
#                 {
#                 STYLES
#             }
#         }
content = re.sub(r'\{\s*\{\s*STYLES\s*\}\s*\}', '{{STYLES}}', content, flags=re.DOTALL)

# Fix APP_JS (single line but maybe spaces)
# { { APP_JS } }
content = re.sub(r'\{\s*\{\s*APP_JS\s*\}\s*\}', '{{APP_JS}}', content)

path.write_text(content, encoding="utf-8")
print(f"Fixed {path}")
