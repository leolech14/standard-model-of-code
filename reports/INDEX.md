# Reports Directory

**Unified location for all project reports and audits.**

## Structure

```
reports/
├── refinery/        Refinery docs_audit reports (JSON + Markdown)
├── audits/          Architecture audits, socratic audits, validation reports
├── archives/        Historical reports from various subsystems
└── INDEX.md         This file
```

## Refinery Reports

Time-stamped documentation audits from the Refinery system:
- `docs_audit_YYYYMMDD_HHMMSS.{json,md}` - Timestamped reports
- `docs_audit_latest.{json,md}` - Symlinks to most recent

## Audit Reports

Strategic analyses and architectural reviews:
- Architecture audits
- Socratic audits
- Consolidation reports
- Validation reports
- Pipeline validation

## Archives

Historical reports from:
- `context-management/docs/reports/` (16 files, 24MB)
- `standard-model-of-code/docs/reports/` (20 files)
- `context-management/library/reports/` (3 files)
- `governance/staging/reports/` (8 files)

## Note for Developers

**Python code paths not yet updated.** Tools still reference old locations:
- `context-management/tools/refinery/` - Update to `../../reports/refinery/`
- Other tooling may need path adjustments

See TASK-105 for migration details.

---

**Created:** 2026-01-31  
**Task:** TASK-105 - Unify Reports Directories (6 to 1)
