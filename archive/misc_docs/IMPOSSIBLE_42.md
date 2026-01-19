# Forbidden Archetypes (Legacy “42 Impossible”) – Canonicalization Pending

Legacy theory target: 42 “hard impossible” archetypes (architectural antimatter). Not yet enumerated as a final, fully justified list in this repo.

## What exists
- `1440_csv.csv` contains 81 rows flagged `is_impossible=True`, spanning 56 hadron subtypes (mostly “Immutable cannot have mutating operations” plus specific domain violations). This is a truth table, not the canonical 42 list.
- A canonical skeleton exists (16 confirmed + placeholders): `spectrometer_v12_minimal/IMPOSSIBLE_42_CANONICAL.csv` and `spectrometer_v12_minimal/IMPOSSIBLE_42_CANONICAL.md`
- `THEORY_COMPLETE.canvas` contains 384 `sub_*` nodes; the current canvas snapshot marks **239** of them as antimatter (not 42). Snapshot + reconciliation report:
  - `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv`
  - `spectrometer_v12_minimal/validation/384_42_consistency_report.md`

## What’s missing
- The definitive 42-item set with names, parent hadron, and rationale, produced from a single ruleset that aligns:
  - 11 laws (`spectrometer_v12_minimal/LAW_11_CANONICAL.json`)
  - the 384 subhadrons
  - the “impossible” semantics (hard law violations only)

## Next step
- Decide which antimatter items are truly “hard impossible” (42) vs “strong smells”.
- Once canonicalized, generate and store:
  - `impossible_42.csv/json` (final list)
  - A law→impossible mapping table (each of the 42 traceable to a law)
