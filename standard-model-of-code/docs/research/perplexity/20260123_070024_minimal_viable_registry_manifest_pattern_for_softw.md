# Perplexity Research: Minimal viable registry/manifest pattern for software projects. What is the ABSOLUTE MINIMUM a machi...

> **Date:** 2026-01-23 07:00:24
> **Model:** sonar-pro
> **Query Length:** 493 chars

---

## Query

Minimal viable registry/manifest pattern for software projects. What is the ABSOLUTE MINIMUM a machine-readable registry needs? Looking for: (1) Essential fields only - no bloat, (2) Single-file vs multi-file tradeoffs, (3) YAML vs JSON vs TOML for config registries, (4) Examples of elegant minimal registries from popular open source projects (package.json, Cargo.toml, pyproject.toml). Focus on the 'worse is better' philosophy - simple implementations that work vs complex ones that don't.

---

## Response

### Absolute Minimum Fields for a Machine-Readable Registry
A minimal viable registry/manifest for software projects requires **only these 5 essential fields** to enable discovery, installation, and basic verification: **name**, **version**, **source URL** (or download URL), **license**, and **dependencies** (as a list of name+version pairs). These suffice for a "worse is better" approach—simple enough to parse quickly, yet functional for core tasks like fetching and building software without bloat like descriptions or authors[1][3].

### Single-File vs Multi-File Tradeoffs
- **Single-file (recommended for minimalism)**: One file (e.g., `project.toml`) holds all metadata at the project root. Pros: Atomic, easy to version-control, parse, and distribute; no assembly needed. Cons: Can grow unwieldy if schemas expand. Fits "worse is better" by prioritizing simplicity over modularity.
- **Multi-file**: Splits into schema + data (e.g., `schema.json` + `manifest.json`). Pros: Reusable schemas, easier scaling. Cons: More complex tooling, risk of desync, higher adoption barrier. Avoid for absolute minimum unless registries span multiple projects[1][3][4].

### YAML vs JSON vs TOML for Config Registries
| Format | Pros for Minimal Registries | Cons | Best For "Worse is Better" |
|--------|-----------------------------|------|----------------------------|
| **TOML** | Human-readable, no quotes for strings, strict typing, tiny parsers; excels at config-like manifests. | Less ubiquitous tooling than JSON. | **Top choice**: Simple, robust for single-file project manifests (e.g., Cargo.toml)[3]. |
| **JSON** | Universal parsing, strict, compact; battle-tested in npm. | Verbose escaping, no comments. | Good for web/interop; minimal but less readable. |
| **YAML** | Highly readable, comments, multi-line strings. | Parsing ambiguity, security risks (evals), bloat from indentation. | Avoid for machine-first; too fragile for absolute minimum[6]. |

TOML wins for minimal viable: parseable everywhere modern tools exist, readable without IDEs, aligns with Rust/Cargo's success[3].

### Examples from Popular Open Source Projects
These embody "worse is better"—tiny files that just work, powering massive ecosystems:

- **package.json (npm/Node.js)**: Ultra-minimal core: `{"name": "foo", "version": "1.0.0", "main": "index.js"}`. Adds `dependencies` and `scripts` sparingly. Single-file, JSON. Powers millions of packages via exact dependency resolution[1].
- **Cargo.toml (Rust)**: `[[package]] name = "foo" version = "0.1.0" dependencies = ["bar = '1.0'"]`. TOML's brevity shines; single-file per crate. Resolves transitive deps perfectly with lockfile companion[3].
- **pyproject.toml (Python/PEEP)**: `[project] name = "foo" version = "1.0.0" dependencies = ["bar>=1.0"]`. Emerging standard, TOML-based, single-file. Replaces setup.py bloat; focuses on build/install essentials[3].

These avoid fluff (e.g., no README in manifest); tools fetch extras from repo. Start with Cargo.toml as template for new projects—proven at scale[1][3].

---

## Citations

1. https://pmc.ncbi.nlm.nih.gov/articles/PMC9455149/
2. https://visuresolutions.com/alm-guide/software-requirements-specification-document/
3. https://www.software.ac.uk/blog/best-practices-software-registries-and-repositories
4. https://registries.govstack.global/development-2/6-functional-requirements
5. https://alastairreid.github.io/mrs-at-scale/
6. https://rdmkit.elixir-europe.org/machine_actionability
7. https://doc.slices-ri.eu/BasicServices/MRS/MRS.html
8. https://asana.com/resources/software-requirement-document-template
9. https://www.federalregister.gov/documents/2025/08/22/2025-16147/request-for-comment-on-2025-minimum-elements-for-a-software-bill-of-materials

---

## Usage Stats

- Input tokens: 111
- Output tokens: 745
