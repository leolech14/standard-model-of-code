# 1,440 RPBL Cells (Purpose Map) + Hadron-Specific Rows

Canonical data file: `1440_csv.csv`

## Facts
- RPBL grid size: 1,440 (12 responsibility × 4 purity × 6 boundary × 5 lifecycle)
- Rows in `1440_csv.csv`: 3,888 (hadron-specific allowed RPBL combinations; not 96×1440)
- Schema: `responsibility,purity,boundary,lifecycle,base_hadron,quark_parent,touchpoints,is_impossible,impossible_reason,visual_3d,emergence_rarity_2025,continente_cor,particula_fundamental,hadron_subtipo,forma_3d_base_variacao,exemplo_real_linguagem_neutro,regra_detecao`
- Continents present: Data Foundations, Logic & Flow, Organization, Execution, Foundations (5 total; canonical model expects 12).
- Hadron subtypes present: 96 (full set).
- Impossible rows: 81 (56 hadron subtypes) flagged `is_impossible=True` (4 unique reasons).

## How to use
- Treat `1440_csv.csv` as a “truth table”: which RPBL coordinates are enumerated for each hadron subtype, plus which ones are marked impossible.
- The `1,440` refers to the **purpose map cells**, not a catalog of repo entities.
- It is not reduced to any single “archetype catalog” size (the old 384/42 framing is now treated as versioned, not fixed).

## Next step
- Write a small extractor to emit:
  - `subhadrons_possible.csv/json` (all rows where `is_impossible=False`)
  - `subhadrons_impossible.csv/json` (all rows where `is_impossible=True`)
  - `subhadrons_384.csv/json` (once the reduction rule is defined)
  - `impossible_42.csv/json` (subset of the above)
  - Summary stats (counts by continent/hadron, rarity buckets)
