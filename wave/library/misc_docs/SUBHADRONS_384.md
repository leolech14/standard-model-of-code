# Archetype Catalog (Legacy “384 Subhadrons”) – Status

Legacy target: “384 = 342 possible + 42 impossible”. A full 384-node archetype set exists in `THEORY_COMPLETE.canvas`, but it is not yet canonicalized to a stable forbidden/smell split.

## What exists
- `1440_csv.csv` defines the RPBL coordinate space (1,440) and enumerates 3,888 hadron-specific rows across the full 96 hadron subtypes, including 81 rows flagged `is_impossible=True`.
- `THEORY_COMPLETE.canvas` contains **384** `sub_*` nodes (subhadrons).
- A reproducible extraction snapshot from the canvas:
  - `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv`
  - `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.md`
  - Consistency report: `spectrometer_v12_minimal/validation/384_42_consistency_report.md`

## What’s missing
- A canonical, machine-readable 384-item catalog derived from a single ruleset (rather than “what the canvas marks today”), aligned with the theory target of **42** impossibles.
- A clear reduction rule that relates `1440_csv.csv` (RPBL truth table) ⇄ 384 named subhadrons.

## Next step
- Decide the semantics split:
  - **Impossible (hard law violation)**: the canonical 42
  - **Smell / anti-pattern (soft violation)**: everything else currently marked antimatter in the canvas
- Then generate canonical files from rules:
  - `subhadrons_384.csv/json` (canonical)
  - `impossible_42.csv/json` (canonical subset)
  - Summary stats (counts by continent/hadron/law)
