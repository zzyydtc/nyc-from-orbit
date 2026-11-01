---
title: About
style: style.css
---

# About this project

<p class="lede">An independent, open-source test of whether satellite-derived features carry information about tract-level reported crime that last year's counts and census demographics do not. The honest answer so far is: mostly no.</p>

## Design

- **Unit:** 2020 census tracts with at least 100 residents (about 2,190), target years 2019 to 2025.
- **Outcomes:** felony complaints and shooting incidents from NYC Open Data, counted per tract-year.
- **Baseline:** log lagged counts of both outcomes, log population and income, and 2023 ACS age, poverty, renter and degree shares (held constant across years).
- **Satellite features, previous year:** Sentinel-2 vegetation, Landsat surface temperature, VIIRS night lights, AlphaEarth embeddings (8 components), Sentinel-1 radar backscatter and its change.
- **Model:** Poisson regression with a population offset and year and county effects.
- **Validation:** spatial-block cross-validation (whole clusters of neighbouring tracts held out) and a forward test on 2024 and 2025.

## Limits

- Reported crime reflects reporting and enforcement behaviour as well as offending.
- Everything is annual and tract-level; crime concentrates at finer places and times.
- Census covariates are static (2023); demographic change over the period is not modelled.
- The forward test has two years, and shootings fell sharply in 2025.
- Results are associations, not causes.

## Responsible use

Not for targeting individuals or demographic groups, or for resource allocation without independent review of reporting bias. See the model card in the repository.

## Data and required notices

This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau. Contains modified Copernicus Sentinel data 2018-2025. The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind. Landsat data courtesy of the U.S. Geological Survey; VIIRS Black Marble courtesy of NASA LAADS DAAC. NYC data courtesy of the NYPD, Department of City Planning and Department of Buildings through NYC Open Data, aggregated and modified here; the City does not endorse this project. Map tiles &copy; OpenStreetMap contributors.

2025 shootings come from a separate NYC Open Data dataset than 2018 to 2024. Full source table and terms review: DATA_SOURCES.md in the repository.

## Code and reproduction

All scripts, the model card and the full results write-up are in the [GitHub repository](https://github.com/zzyydtc/nyc-from-orbit). This dashboard is built with Observable Framework, MapLibre GL JS and Observable Plot from aggregated tract-year files; no incident records are published.
