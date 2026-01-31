
import os
import yaml
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path("/Users/lech/PROJECTS_all/PROJECT_elements")
GOV_DIR = ROOT_DIR / "governance"

# The sections we want in our sidebar
STRUCTURE = {
    "Governance": [
        "governance/THE_MISSING_MANUAL.md",
        "governance/VISUAL_GUIDE.qmd",
        "governance/ROADMAP.qmd",
        "governance/DECISIONS.qmd",
        "governance/QUALITY_GATES.md",
        "governance/REPO_STRUCTURE.md",
        "governance/TOPOLOGY_MAP.md",
        "governance/ARCHITECTURE_AUDIT_2026.md",
        "governance/PIPELINES.md"
    ],
    "Subsystems (Particle)": [
        "standard-model-of-code/docs/theory/THEORY_AXIOMS.md",
        "standard-model-of-code/docs/theory/THEORY_COMPLETE_ALL.md",
         "standard-model-of-code/docs/specs/PIPELINE_STAGES.md"
    ],
    "Intelligence (Wave)": [
        "context-management/docs/CONTEXTOME.md",
        "context-management/docs/PROJECTOME.md",
        "context-management/registry/REGISTRY_REPORT.md"
    ]
}

def generate_config():
    """Generates the _quarto.yml file dynamically."""

    sidebar_contents = []

    # 1. Governance Section
    gov_section = {"section": "Governance", "contents": []}
    for path in STRUCTURE["Governance"]:
        p = Path(path)
        if (ROOT_DIR / path).exists():
            href = os.path.relpath(ROOT_DIR / path, GOV_DIR)
            text = get_title(ROOT_DIR / path)
            gov_section["contents"].append({"text": text, "href": href})
    sidebar_contents.append(gov_section)

    # 2. Standard Model
    sm_section = {"section": "Standard Model", "contents": []}
    for path in STRUCTURE["Subsystems (Particle)"]:
        if (ROOT_DIR / path).exists():
            href = os.path.relpath(ROOT_DIR / path, GOV_DIR)
            text = get_title(ROOT_DIR / path)
            sm_section["contents"].append({"text": text, "href": href})
    sidebar_contents.append(sm_section)

    # 3. Intelligence
    cm_section = {"section": "Intelligence", "contents": []}
    for path in STRUCTURE["Intelligence (Wave)"]:
        if (ROOT_DIR / path).exists():
            href = os.path.relpath(ROOT_DIR / path, GOV_DIR)
            text = get_title(ROOT_DIR / path)
            cm_section["contents"].append({"text": text, "href": href})
    sidebar_contents.append(cm_section)

    # 4. Canonical Full Tree (Auto-scan)
    # This is a bit risky for noise, so let's stick to a curated list for now
    # or implement a "Filesystem" section at the bottom.

    config = {
        "project": {
            "type": "website",
            "output-dir": "../docs/reader"
        },
        "website": {
            "title": "PROJECT_elements Reader",
            "site-url": "https://github.com/leolech14/standard-model-of-code",
            "description": "Official Documentation Reader for the PROJECT_elements Standard Model.",
            "sidebar": {
                "style": "floating",
                "background": "#202022",
                "border": True,
                "collapse-level": 2,
                "contents": sidebar_contents
            },
            "page-footer": {
                "left": "PROJECT_elements v1.0",
                "right": [
                    {"icon": "github", "href": "https://github.com/leolech14/standard-model-of-code"}
                ]
            }
        },
        "format": {
            "html": {
                "theme": "cosmo",
                "css": "style.css",
                "include-after-body": "theme_selector.html",
                "toc": True,
                "toc-depth": 3,
                "title-block-banner": False,
                "anchor-sections": True,
                "smooth-scroll": True,
                "embed-resources": False, # Changed to False for better linking
                "mermaid": {
                    "theme": "dark",
                    "themeVariables": {
                        "cScale0": "#2d2d30",
                        "cScale1": "#202022",
                        "cScale2": "#2d2d30",
                        "cScale3": "#202022",
                        "primaryColor": "#2d2d30",
                        "primaryTextColor": "#dcdcdc",
                        "primaryBorderColor": "#5c7c8a",
                        "lineColor": "#5c7c8a",
                        "secondaryColor": "#161618",
                        "tertiaryColor": "#161618",
                        "mainBkg": "#202022",
                        "textColor": "#dcdcdc"
                    }
                }
            }
        }
    }

    with open(GOV_DIR / "_quarto.yml", "w") as f:
        yaml.dump(config, f, sort_keys=False)

    print(f"Generated _quarto.yml with {len(sidebar_contents)} sections.")

def get_title(path):
    # Simple heuristic to get a nice title from filename or first line
    name = path.stem.replace("_", " ").replace("-", " ").title()
    # Manual overrides for icons
    if "VISUAL_GUIDE" in path.name: return "🏗️ Visual Guide"
    if "ROADMAP" in path.name: return "📍 Roadmap"
    if "DECISIONS" in path.name: return "⚖️ Decisions"
    if "QUALITY_GATES" in path.name: return "🛡️ Quality Gates"
    if "REPO_STRUCTURE" in path.name: return "📂 Repo Structure"
    if "TOPOLOGY_MAP" in path.name: return "🗺️ Topology Map"
    if "ARCHITECTURE_AUDIT" in path.name: return "🔍 Audit 2026"
    if "PIPELINES" in path.name: return "⚙️ Pipelines"
    if "THE_MISSING_MANUAL" in path.name: return "📘 The Missing Manual"
    return name

if __name__ == "__main__":
    generate_config()
