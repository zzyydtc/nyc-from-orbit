# Model card

## What this is

A set of Poisson regression comparisons that ask whether satellite-derived tract features add predictive information about next-year felony complaints and shootings in New York City, beyond last year's outcome and census covariates. It is a research analysis, not a deployed model.

## Intended use

- Studying whether remote-sensing features carry information that conventional covariates miss.
- Teaching and replication of a spatial-validation workflow.

## Out-of-scope and prohibited use

- Predicting where individuals will offend, or targeting individuals or demographic groups.
- Operational deployment such as patrol allocation. The analysis is annual and tract-level, and its outcomes measure reporting and enforcement as well as crime.
- Causal claims about vegetation, light or temperature affecting crime.

## Data

See `DATA_SOURCES.md`. Outcomes are NYC Open Data point records aggregated to 2020 census tracts for 2018-2025. Imagery features are annual summaries per tract.

## Evaluation

Spatial-block cross-validation and a forward test on 2024-2025, with a placebo check and robustness variants. Results and limitations are in `RESULTS.md`.

## Known failure modes and biases

- Complaint data reflect who reports and where police are present. Models may reproduce those patterns.
- Static 2023 demographic covariates misstate earlier years.
- Heavily commercial or transit-heavy tracts have low resident populations, which inflates per-capita rates and makes count models unstable there.
- The forward test is short and spans a period of unusual decline in shootings.

## Maintenance

Maintained by an individual. Issues and pull requests are welcome; see `CONTRIBUTING.md`.
