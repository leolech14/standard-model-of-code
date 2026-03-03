import re
from pathlib import Path

path = Path("/Users/lech/PROJECTS_all/PROJECT_elements/particle/src/core/viz/assets/template.html")
content = path.read_text(encoding="utf-8")

# Remove script tags pointing to assets/modules
# Pattern: <script src="assets/modules/.*"></script>
# We'll be aggressive but careful not to remove 3rd party libs if they match not
# The grep said: <script src="assets/modules/circuit-breaker.js"></script>

# Regex to remove lines containing src="assets/modules/
# We use multiline to handle potential formatting
content = re.sub(r'<script\s+src=["\']assets/modules/[^"\']+["\']\s*></script>\s*', '', content)

path.write_text(content, encoding="utf-8")
print(f"Cleaned {path}")
