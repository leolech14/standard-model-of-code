# Continents (Legacy “12”) – Current Evidence: 5 Macro Regions

Earlier docs conflated “continents” and “quarks”. In the checked-in RPBL dataset (`1440_csv.csv`), we currently have:

- **Macro regions** (`continente_cor`): 5 values (listed below)
- **Fundamental families** (`particula_fundamental`): 12 values (Bits/Bytes/… — see `spectrometer_v12_minimal/1440_summary.json`)

## Macro regions present in `1440_csv.csv` (`continente_cor`)
- Data Foundations
- Logic & Flow
- Organization
- Execution
- Foundations

## About the “12” claim
If the model truly needs “12 continents”, those names are not currently present as `continente_cor` values in the checked-in assets. Likely sources: upstream GROK threads and/or the THEORY canvases.

## Action
- Until new evidence is imported, downstream tooling should treat the above **five** as the only concrete `continente_cor` values available in-repo.
- If you want “12”, define them explicitly in a machine-readable canon file and regenerate any derived datasets.
