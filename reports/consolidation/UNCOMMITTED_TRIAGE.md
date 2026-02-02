# UNCOMMITTED_TRIAGE

**Generated:** 2026-02-02T20:33:12.264323+00:00
**Total files:** 316

## Executive Summary

- Status counts: {'M': 247, 'A': 66, 'D': 1, 'm': 2}
- Decision counts: {'needs-review': 316}

### Analyze.py Status

- **ERROR:** GEMINI_API_KEY required; analyze.py forensic runs failed.

### Cerebras Status

- **ERROR:** CEREBRAS_API_KEY not available; cerebras enrichment skipped.

## By Realm Summary

- **.agent**: 52 files; decisions: {'needs-review': 52}
- **docs**: 40 files; decisions: {'needs-review': 40}
- **governance**: 7 files; decisions: {'needs-review': 7}
- **observer**: 14 files; decisions: {'needs-review': 14}
- **other**: 8 files; decisions: {'needs-review': 8}
- **particle**: 82 files; decisions: {'needs-review': 82}
- **reports**: 6 files; decisions: {'needs-review': 6}
- **research**: 87 files; decisions: {'needs-review': 87}
- **wave**: 20 files; decisions: {'needs-review': 20}

## High-Risk Candidates (Heuristic)

- `observer/merged/backend/main.py` (M, observer)
- `observer/merged/backend/models/pipeline.py` (M, observer)
- `observer/merged/backend/routes/pipeline.py` (A, observer)
- `observer/merged/frontend/src/Dashboard.tsx` (M, observer)
- `observer/merged/frontend/src/components/FileSystem.tsx` (M, observer)
- `observer/merged/frontend/src/main.tsx` (M, observer)
- `observer/merged/frontend/src/services/api.ts` (A, observer)
- `observer/merged/frontend/src/types.ts` (A, observer)
- `observer/merged/frontend/vite.config.ts` (M, observer)
- `particle/src/core/constraint_engine.py` (M, particle)
- `wave/experiments/refinery-platform/next-env.d.ts` (A, wave)
- `wave/tools/ai/analyze.py` (M, wave)
- `wave/tools/ai/cerebras_doc_validator.py` (A, wave)
- `wave/tools/ai/hf_spaces.py` (A, wave)

## Unknowns / Next Actions

- Provide `GEMINI_API_KEY` (or configure Vertex) to run forensic triage via analyze.py.
- Provide `CEREBRAS_API_KEY` to run 70B quick enrichment for code deltas.
- Re-run triage after keys are available to classify keep/revert/needs-review with evidence.

## Notes

- This report does not modify any dirty files; it only records observations.
- Detailed analyze outputs are in `reports/consolidation/_analyze/`.
- Cerebras outputs (if run) are in `reports/consolidation/_cerebras/`.
