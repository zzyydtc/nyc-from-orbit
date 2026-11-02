# nyc-from-orbit

Do satellite-derived features (heat, vegetation, night lights, learned image embeddings) add anything to next year's felony complaints and shooting counts for a New York City census tract, beyond last year's counts and census demographics? A tract-level, 2018-2025 test built on public data.

**Status: v0.1.** Live dashboard: https://zzyydtc.github.io/nyc-from-orbit/dashboard/. The data pipeline, incremental-value test and robustness checks run end to end. A radar probe shows Sentinel-1 backscatter tracks new-building filings, but radar features add about one percent or less to the prediction models. An interactive dashboard (map, trends, results) is built as a static site; no Power BI report is planned.

## Headline result

- **Felony complaints:** once the baseline is specified properly (log-transformed lags, both outcomes' lags, log population and income), satellite features add no detectable predictive value. An earlier apparent gain of about 5% came from a weak baseline.
- **Shootings:** vegetation and temperature features may add a few percent in a forward test on 2024-2025, but not in spatial cross-validation, and the test covers only two years. This is a lead, not a finding.
- A placebo check (shuffling imagery across tracts) gives no gain, so the null result is not a pipeline bug.

Details, tables and limitations: [docs/RESULTS.md](docs/RESULTS.md).

![Incremental gain](docs/figures/incremental_gain.png)

## Interactive dashboard

**Live: https://zzyydtc.github.io/nyc-from-orbit/dashboard/**

A static site (Observable Framework, MapLibre GL JS, Observable Plot) in [`dashboard/`](dashboard/), built into `docs/dashboard/`: a tract map with a year slider and a click-for-history panel, borough trends, and the results of the incremental-value test. It needs no server beyond static hosting and publishes only tract-year aggregates.

```bash
python scripts/17_export_dashboard_data.py   # refresh the aggregated data files
cd dashboard && npm ci && npm run build      # writes ../docs/dashboard
cd ../docs && python -m http.server          # then open http://localhost:8000/dashboard/
```

`npm run dev` in `dashboard/` starts a live-reloading preview. An earlier single-file map is still produced by `python scripts/16_build_web_map.py` into `docs/map/index.html`.

## Data

NYC Open Data (complaints, shootings, tracts, Department of Buildings filings), American Community Survey, Sentinel-1, Sentinel-2, Landsat, VIIRS Black Marble, and AlphaEarth annual embeddings. All public; see [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md). Two free credentials are needed: a Census API key (`CENSUS_API_KEY`) and a NASA Earthdata token (`EARTHDATA_TOKEN`).

## Run it

```bash
pip install -e ".[dev]"
```

`requirements-lock.txt` records the package versions the results were produced with (Python 3.12, Windows). The ordered script list is in [docs/RESULTS.md](docs/RESULTS.md#reproduce). Raw and derived data are not committed; scripts download them.

## Documents

- [docs/BRIEF.md](docs/BRIEF.md): two-page summary
- [docs/PLAN.md](docs/PLAN.md): original project plan
- [docs/PROBE.md](docs/PROBE.md): data availability probe
- [docs/RESULTS.md](docs/RESULTS.md): results and limitations
- [docs/MODEL_CARD.md](docs/MODEL_CARD.md): intended use and failure modes
- [docs/POWERBI.md](docs/POWERBI.md): Power BI data model and export

## Known limitations and open-source gaps

Stated plainly so you know what to expect:

- **Reproducibility:** scripts run in order (`01` to `17`, see [docs/RESULTS.md](docs/RESULTS.md#reproduce)); there is no single `make` target. Dependencies are pinned in `requirements-lock.txt`. The radar pipeline was re-run from scratch and reproduced its results exactly; the rest of the pipeline has not had a full from-scratch rerun.
- **Provenance:** the fetch scripts do not record checksums or retrieval dates for downloaded data, so a re-download after upstream revisions may differ.
- **Tests:** unit tests cover the metric code only. There is no fixture-based smoke test of the full pipeline.
- **Release hygiene:** no pre-commit hooks, no DOI, and no tagged release yet.
- **Modelling:** census covariates are static (2023 ACS), the shooting forward test spans two years, and there is no spatial error analysis. See the model card in [docs/MODEL_CARD.md](docs/MODEL_CARD.md).
- **Dashboard:** the map loads OpenStreetMap tiles directly, which is fine for a demo but not for heavy traffic.
- **Data terms:** this repository publishes only aggregated tract-year values, never incident records. Source terms are reviewed in [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).

## Contributing and support

Issues and pull requests are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [SECURITY.md](SECURITY.md). To cite this work, use [CITATION.cff](CITATION.cff).

This is an independent project and is not affiliated with, endorsed by, or sponsored by the NYPD or any other city agency.

## Attribution

This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau. Contains modified Copernicus Sentinel data 2018-2025. The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind. Landsat data courtesy of the U.S. Geological Survey; VIIRS Black Marble courtesy of NASA LAADS DAAC. NYC data courtesy of the NYPD, Department of City Planning and Department of Buildings through NYC Open Data, aggregated and modified here; the City does not endorse this project. Terms review: [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).

## Responsible use

This is an independent open-source project, not affiliated with or endorsed by the NYPD or any other agency. Reported crime reflects reporting and enforcement as well as offending. Results are descriptive and associational at annual, tract level; the project must not be used to target individuals or demographic groups.

## License

Code: MIT (see [LICENSE](LICENSE)). Documentation and figures: CC BY 4.0 (see [LICENSE-docs.md](LICENSE-docs.md)). AlphaEarth embeddings are CC BY 4.0, produced by Google and Google DeepMind.
