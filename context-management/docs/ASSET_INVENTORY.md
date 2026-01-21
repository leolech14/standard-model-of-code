# Asset Inventory: The Automations

> "If it automates the project, it is listed here."

## 1. The Active Command Center (context-management)
*These are the tools you should use daily to operate the Alien Architecture.*

### The Intelligence (AI)
| Tool | Command | Description |
| :--- | :--- | :--- |
| **The Surgeon** | `python context-management/tools/ai/analyze.py --mode forensic` | **Forensic Analysis**. Provides verifiable facts with line-number citations. |
| **The Architect** | `python context-management/tools/ai/analyze.py --mode architect` | **Global Reasoning**. Analyzes code against the `COLLIDER_ARCHITECTURE` theory. |
| **The Librarian** | *(Browser Interface)* | **vertex-ai-agent-builder**. Instant search and Q&A over the entire repo. |
| **RAG Setup** | `python context-management/tools/ai/setup_rag.py` | **Infrastructure**. Automates RAG setup and NotebookLM bundling. |

### The Machinery (Mirror & Maintenance)
| Tool | Command | Description |
| :--- | :--- | :--- |
| **The Mirror** | `python context-management/tools/archive/archive.py mirror` | **Cloud Sync**. Mirrors the repo to `gs://elements-archive-2026` for AI access. |
| **Timestamp Tracker** | `python context-management/tools/maintenance/timestamps.py` | **Auditing**. Updates `project_elements_file_timestamps.csv` for drift detection. |
| **Stale Archiver** | `python context-management/tools/maintenance/archive_stale.py` | **Cleanup**. Auto-moves old files to `archive/zombie_code`. |
| **Bootstrapper** | `bash context-management/tools/maintenance/boot.sh` | **Setup**. Initializes the environment (legacy). |

### Audit & Analysis Tools
| Tool | Command | Description |
| :--- | :--- | :--- |
| **Metadata Generator** | `python context-management/tools/maintenance/generate_metadata_csv.py` | Creates comprehensive file audit CSV. |
| **Set Analyzer** | `python context-management/tools/maintenance/analyze_sets.py` | Reports coverage metrics per Analysis Set. |
| **Relocation Finder** | `python context-management/tools/maintenance/find_relocation_candidates.py` | Identifies misplaced file clusters. |

### Reports & Audits
| Report | Path |
| :--- | :--- |
| **Repository Audit (2026-01-19)** | `context-management/docs/REPOSITORY_AUDIT_2026-01-19.md` |
| **File Metadata CSV** | `context-management/output/file_metadata_audit.csv` |
| **Analysis Sets Report** | `context-management/output/analysis_sets_report.md` |

---

## 2. Reference Datasets (The Gold Nuggets)
*Canonical data structures extracted from theory.*

| Dataset | Path | Status |
| :--- | :--- | :--- |
| **96 Hadrons (Full)** | `context-management/reference_datasets/HADRONS_96.md` | **Canonical**. Extracted from Grok threads. |
| **12 Continents** | *(Missing)* | **Partial**. Needs extraction. |
| **1440 Grid** | `context-management/reference_datasets/RPBL_1440.csv` | **Raw Data**. The validation matrix. |

---

## 3. The Legacy Archive (Code Graveyard)
*These scripts are in `archive/`. They are NOT active, but contain valuable logic you might want to resurrect.*

### Implementation Scripts (`archive/scripts/`)
*   `analyze_structure.py`: Old structural analysis logic.
*   `analyze_theory.py`: Logic for parsing the old theory files.
*   `batch_analysis_runner.py`: Old bulk processing script.
*   `code_smell_validator.py`: Early linter experiments.
*   `constraints_calculator.py`: Logic for "Physical Constraints" theory.
*   `1440_csv_generator.py`: Old timestamp generator.

### Orphaned Tools (`archive/orphaned_tools_2025/`)
*   `archive_assets.py`
*   `scan_repo_truth_sources.py`
*   `validate_subhadron_dataset.py`

*(Note: There are ~50 more scripts in these folders. Use "The Librarian" (Agent Builder) to search inside them if you need to find "that old logic that checked for circular dependencies".)*
