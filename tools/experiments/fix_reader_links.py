
import os
import yaml
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path("/Users/lech/PROJECTS_all/PROJECT_elements")
GOV_DIR = ROOT_DIR / "governance"
STAGING_DIR = GOV_DIR / "staging"

# Structure mapping symlinks to logical sections
STRUCTURE = {
    "Governance": [
        "VISUAL_GUIDE.qmd",
        "ROADMAP.qmd",
        "DECISIONS.qmd",
        "QUALITY_GATES.md",
        "REPO_STRUCTURE.md",
        "TOPOLOGY_MAP.md",
        "ARCHITECTURE_AUDIT_2026.md",
        "PIPELINES.md"
    ],
    "Particle (Standard Model)": {
        "Theory": "staging/particle_theory",
        "Specs": "staging/particle_specs"
    },
    "Wave (Intelligence)": {
        "Docs": "staging/wave_docs"
    }
}

def generate_config():
    sidebar_contents = []

    # 1. Governance (Local Files)
    gov_section = {"section": "Governance", "contents": []}
    for filename in STRUCTURE["Governance"]:
        if (GOV_DIR / filename).exists():
            text = get_title(GOV_DIR / filename)
            gov_section["contents"].append({"text": text, "href": filename})
    sidebar_contents.append(gov_section)

    # 2. Particle (Symlinked Staging)
    particle_section = {"section": "Particle (Standard Model)", "contents": []}
    for sub, path_rel in STRUCTURE["Particle (Standard Model)"].items():
        sym_path = GOV_DIR / path_rel
        if sym_path.exists():
            # Scan the directory
            items = scan_directory(sym_path, path_rel)
            if items:
                particle_section["contents"].append({"section": sub, "contents": items})
    sidebar_contents.append(particle_section)

    # 3. Wave (Symlinked Staging)
    wave_section = {"section": "Wave (Intelligence)", "contents": []}
    for sub, path_rel in STRUCTURE["Wave (Intelligence)"].items():
        sym_path = GOV_DIR / path_rel
        if sym_path.exists():
             # Scan the directory
            items = scan_directory(sym_path, path_rel)
            if items:
                wave_section["contents"].append({"section": sub, "contents": items})
    sidebar_contents.append(wave_section)

    # Collect all render targets from sidebar
    render_targets = ["*.md", "*.qmd"]
    for section in sidebar_contents:
        if "contents" in section:
            for item in section["contents"]:
                if isinstance(item, dict):
                    if "href" in item:
                        render_targets.append(item["href"])
                    elif "contents" in item:
                        for sub_item in item["contents"]:
                            if "href" in sub_item:
                                render_targets.append(sub_item["href"])

    config = {
        "project": {
            "type": "website",
            "output-dir": "../docs/reader",
            "render": render_targets
        },
        "website": {
            "title": "PROJECT_elements Reader",
            "site-url": "https://github.com/leolech14/particle",
            "description": "Official Documentation Reader.",
            "sidebar": {
                "style": "floating",
                "background": "#202022",
                "border": True,
                "collapse-level": 2,
                "contents": sidebar_contents
            },
            "page-footer": {
                "left": "PROJECT_elements v1.0",
                "right": [{"icon": "github", "href": "https://github.com/leolech14/particle"}]
            }
        },
        "format": {
            "html": {
                "theme": "cosmo",
                "css": "style.css",
                "include-after-body": "theme_selector.html",
                "toc": True,
                "toc-depth": 3,
                "anchor-sections": True,
                "smooth-scroll": True,
                "embed-resources": False, # Crucial for relative linking
                "mermaid": {
                    "theme": "dark",
                    "themeVariables": {
                        "cScale0": "#2d2d30", "cScale1": "#202022", "mainBkg": "#202022", "primaryColor": "#2d2d30", "primaryTextColor": "#dcdcdc", "lineColor": "#5c7c8a"
                    }
                }
            }
        }
    }

    with open(GOV_DIR / "_quarto.yml", "w") as f:
        yaml.dump(config, f, sort_keys=False)

    print(f"Generated unified _quarto.yml with {len(sidebar_contents)} sections.")

def scan_directory(path, parent_rel_path):
    contents = []
    # Walk just the top level or recursion? Let's do 1 level for now to avoid mess
    # or recursive if small.
    for root, dirs, files in os.walk(path):
        rel_root = os.path.relpath(root, path)
        if rel_root == ".": rel_root = ""

        # Skip hidden/archive
        if "archive" in root or ".git" in root or ".agent" in root:
            continue

        for f in sorted(files):
            if f.endswith(".md") or f.endswith(".qmd"):
                # Exclude aggregation files from the Reader
                if "_COMPLETE" in f or "ALL.md" in f or "INDEX.md" in f:
                    continue

                # Construct href relative to GOV_DIR
                # path_rel is "staging/particle_theory"
                # f path is "staging/particle_theory/THEORY_AXIOMS.md"
                file_rel = os.path.join(parent_rel_path, rel_root, f)
                text = get_title(Path(f))
                contents.append({"text": text, "href": file_rel})
    return contents

def get_title(path):
    name = path.stem.replace("_", " ").replace("-", " ").title()
    if "VISUAL_GUIDE" in path.name: return "🏗️ Visual Guide"
    if "ROADMAP" in path.name: return "📍 Roadmap"
    return name

if __name__ == "__main__":
    generate_config()
