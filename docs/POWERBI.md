# Power BI report

The report file itself (`.pbix`) is not in the repository yet. This page describes the data model and how to build the report from the exported tables.

## Export

```bash
python scripts/11_export_powerbi.py
```

This writes four files to `data/processed/powerbi/` (not committed):

| File | Grain | Contents |
|---|---|---|
| `tract_year.csv` | tract x year (18,600 rows) | `felony_complaints`, `shootings`, `ndvi_mean`, `green_share`, `lst_mean`, `ntl`, `aef_pc1`, `aef_pc2` |
| `tract_geo.csv` | tract (2,325 rows) | borough, centroid `lon`/`lat`, 2023 ACS covariates |
| `results.csv` | variant x feature set | percent deviance reduction under spatial-block CV and the forward test |
| `tracts.geojson` | tract | simplified geometry for a shape map |

## Model

Relate `tract_year[geoid]` to `tract_geo[geoid]` (many-to-one, single direction). Add a `Year` slicer from `tract_year[year]`.

Suggested measures:

```
Felony per 1000 = DIVIDE(SUM(tract_year[felony_complaints]) * 1000, SUM(tract_geo[pop]))
Shootings = SUM(tract_year[shootings])
```

Take care with the population measure when summing across several years: `pop` is a single 2023 value per tract, so divide by it once per year.

## Suggested pages

1. **Map:** shape map or bubble map of the chosen outcome by tract with a year slicer, and a second map of one imagery feature.
2. **Trends:** borough-level lines for both outcomes, 2018-2025.
3. **Does imagery add anything?:** bar chart from `results.csv` for the strong-baseline rows, with a note that the forward test covers two years.

Keep the caveats from `RESULTS.md` on the page: reporting bias, annual tract-level scale, associations only, no affiliation with any agency.
