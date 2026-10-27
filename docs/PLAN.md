# NYC From Orbit: Neighborhood Change vs Violent Crime, 2018–2025

Project plan. Status: **plan only, no code yet.** Last updated 2026-10-25.

This is an independent open-source project. It is not affiliated with, endorsed by, or built for the New York City Police Department (NYPD). It uses public data, GIS tooling and satellite imagery, and it is written for an analytics audience such as a police-department analytics office.

**Reliability tags used throughout**

- **[search]**: came from a web search result.
- **[verified]**: the source page was opened and read.
- **[memory]**: recalled, not verified.
- **[inference]**: reasoning, not a fact about a source.
- **[untested]**: needs a probe before anyone relies on it.
- **[not found]**: searched for, not found. This does **not** mean it has not been done.

---

## 1. The idea

**Question:** do satellite-derived features add anything to next year's shooting counts for a New York City census tract, beyond last year's shootings and the census demographics?

**One-sentence version:** a seven-year, tract-level test of whether heat, tree canopy, construction and night lights carry information about where and when shootings move, with an honest scorecard of what satellites can and cannot see.

**Audience framing:** the brief and map are written as decision support for a police-department analytics office: plain language, three findings, one caveat box. The analysis stays descriptive and associational, at tract level, annual resolution.

**Why this design**

- The test that is rarely run in the work I found is incremental value: does a satellite feature help once last year's outcome and the census variables are already in the model?
- A null or small result is still a deliverable if it is reported honestly. The project is about method and judgment, not a headline accuracy figure.
- Everything needed is free and public: NYC Open Data, the Census API, and open satellite archives.

**Novelty statement (rewritten after prior-art review).** This project is not a first.

- Already done: satellite imagery to neighborhood crime (Najjar et al. 2018, Chicago); geospatial foundation-model embeddings (AlphaEarth, Prithvi, Clay) to crime, including New York (Gong et al. 2026); heat and shootings in NYC using air temperature; tree canopy and crime in NYC; night lights and crime, including an unpublished New York map; Sentinel-1 new-building and demolition detection.
- Not found: a New York tract-level 2018–2025 panel with one-year-lagged Landsat land-surface temperature, Sentinel-1, Sentinel-2 canopy and VIIRS features against shootings; a spatial-block and forward-chained test of their incremental value over lagged outcomes and census variables; and validation of radar building-change detection against NYC Department of Buildings permits.
- Amateur and open-source landscape (GitHub, Kaggle): no complete replication found. The closest pieces are single-sensor, single-year, cross-sectional.
- Recommended description: **a rigorous replication and extension, with an honest scorecard.**

**Willingness to pay:** unclear. Possible interest from civic-data and city research teams is unverified.

---

## 2. Prior work

### 2.1 Research literature

| Work | What it did | Tag |
|---|---|---|
| [Najjar et al. 2018, "Crime Mapping from Satellite Imagery via Deep Learning"](https://ar5iv.arxiv.org/html/1812.06764) | CNN on satellite images plus over a million Chicago crime reports; reported 79% accuracy in Chicago and 70–72% when transferred to Denver and San Francisco | [search] |
| [Built environment and neighborhood crime from satellite imagery, 2017](https://arxiv.org/abs/1710.05483) | Transfer learning on high-resolution imagery; image features explain up to 82% of variation in tract crime rates. "Predict" means cross-sectional association, not forecasting | [verified: abstract page] |
| [Gong et al. 2026, "Earth Embeddings Reveal Diverse Urban Signals from Space"](https://www.alphaxiv.org/abs/2604.03456) | AlphaEarth (64-d), Prithvi-EO-2.0 and Clay-v1.5 embeddings predict 14 neighborhood indicators including violent and petty crime across six US metro areas including New York, 2020–2023, mainly LightGBM. Crime prediction skill correlates negatively with population density (ρ = −0.71) | [verified: abstract page] |
| [Guo et al. 2026, "MobFusion"](https://arxiv.org/abs/2606.01745) | Income, population density and crime prediction across three US metros; cities and spatial unit not stated on the abstract page | [verified: abstract page; details unverified] |
| [Kondo et al. 2017, tree cover and gun assault, Philadelphia](https://research.fs.usda.gov/treesearch/54568) | Being under tree cover at the time of assault: odds ratio 0.70 (case-control) and 0.55 (case-crossover) | [verified] |
| Street trees and crime in NYC, 2021 (Urban Forestry & Urban Greening 65:127366) | Tree canopy, streetscape greenery and species diversity associated with lower crime | [search; paper not opened] |
| Extreme heat and firearm violence in NYC public housing, 2025 (Journal of Urban Health) | Monthly maximum temperature associated with shootings; air conditioning examined as a mitigator | [search; paper not opened] |
| Cincinnati VIIRS nightlight gradient and street robbery and burglary; Newark LED street-lighting quasi-experiment | Night lights and lighting versus crime | [search] |
| Landsat analysis-ready data with NYC construction records for parcel-level reconstruction (2025) | Tract-level "reconstruction intensity" from Landsat time series, accuracy 87% | [search; paper not opened] |
| [Racek et al. 2025, PNAS Nexus](https://www.alphagalileo.org/en-gb/Item-Display/ItemId/267670) | Unsupervised Sentinel-1 coherence-based building destruction detection, 12-day cycle; validated on Beirut, Mariupol and Gaza | [search; press release] |
| Sentinel-1 new-building detection (DLR Bavaria; single-track success 36%, more tracks improves) | Radar change detection of construction, accuracy up to 90% against ground truth | [search] |
| Lum and Isaac; Ensign et al. on predictive policing feedback loops | Reported-crime data reflects policing records, not crime itself | [search] |

### 2.2 Open-source and amateur landscape (GitHub and Kaggle, searched 2026-10-25)

| Project | Content | Difference from this plan |
|---|---|---|
| [earth-embeddings-workshop-in-crime](https://github.com/edgar-daniel-codes/earth-embeddings-workshop-in-crime) | Mexico City, AlphaEarth embeddings to street-level crime risk, group cross-validation by year and municipality, Streamlit apps | Not New York; emphasizes risk tiering, no lagged-increment test |
| [Vital-City-NYC/streetlight-cities](https://github.com/Vital-City-NYC/streetlight-cities) | NYC and four other cities; VIIRS Black Marble (NYC 2023) against nighttime violent crime on a hexagon grid; marked draft, unpublished | Cross-sectional, one lights year, no panel or lag |
| [sf-crime-gee-analysis](https://github.com/Airahb/sf-crime-gee-analysis) | San Francisco; NDVI and terrain vs crime density; robust OLS | Single city, cross-sectional, small |
| NYC "heat hypothesis" student projects | Manhattan 2013–2023, weather-station temperature vs crime | Air temperature, not land-surface temperature |
| NYC urban-heat-island projects (Landsat LST, tree cover) | Heat and canopy modeling | No crime variable |
| About 190 NYC shooting-data analyses | Descriptive analysis of shooting incidents | No satellite features |

Kaggle: no satellite-and-crime notebook found; the nearest are urban-heat-island challenge notebooks that predict NYC temperature from Sentinel features, with no crime variable.

**Limits of this review.** GitHub repository search matches names, descriptions and topics, not code or most README text; Kaggle multi-word search is noisy; private repositories and other platforms were not covered. Papers behind login walls were not opened. "Not found" is weak evidence.

---

## 3. Data inventory

Nothing below has been downloaded. Dataset IDs appear only where a search returned one.

### 3.1 Outcomes

| Layer | Source | Notes | Tag |
|---|---|---|---|
| Complaints, historic | NYC Open Data "NYPD Complaint Data Historic", identifier `qgea-i56i` | A catalog entry describes 2006 through 2019, while portal mirrors show later modification dates (2024-04-23 and 2025-04-15). Confirm the live coverage end date. Some records lack geolocation and carry coordinates 0,0: filter before spatial work. | [search] |
| Complaints, current year | NYPD "Year-to-Date" complaint data on NYC Open Data | Separate dataset from the historic file; exact name and ID not confirmed. | [search, partial] |
| Shootings | NYPD Shooting Incident Data (historic plus year-to-date) on NYC Open Data | Preferred outcome: less enforcement-driven than complaint categories. | [memory] |

### 3.2 Context

| Layer | Source | Notes | Tag |
|---|---|---|---|
| Demographics | ACS 5-year tract estimates via the Census API; TIGER tract boundaries | Population, age, income, poverty, rent burden, education, race and ethnicity (bias check only). 2020 tract boundaries differ from 2010: plan a crosswalk, or use Neighborhood Tabulation Areas for the robustness run. | [memory] |
| Land use | MapPLUTO, building footprints | Vacant lots, building age, land-use mix. | [memory] |
| Construction and demolition | NYC Department of Buildings permit and job-filing datasets | Ground truth for the radar building-change test. | [memory] |
| Service requests | NYC 311 | Optional text-analysis layer and neglect proxy. | [memory] |
| Tree canopy | NYC tree canopy and land-cover products; street tree census | Check available years. | [memory, untested] |
| Street network | OpenStreetMap via OSMnx | For adjacency and accessibility features. | [memory] |

### 3.3 Satellite

| Sensor | Use | Practical notes | Tag |
|---|---|---|---|
| Sentinel-2 L2A, 10 m | Vegetation (NDVI), built-up and construction change, bare soil and vacant-lot signal | Cloud-mask, build summer composites per year. Likely via Planetary Computer (`sentinel-2-l2a`). | [memory] |
| Landsat 8/9 Collection 2 Level 2 | Land-surface temperature (summer mean, hot-day anomalies) | Thermal band about 100 m, resampled to 30 m: tract-level signal only. Collection `landsat-c2-l2`. Landsat 9 from 2021. | [memory] |
| Sentinel-1 | Backscatter change for construction and demolition; coherence change for the radar building-change test | RTC product (`sentinel-1-rtc`) for backscatter; coherence needs SLC and extra processing. Dense high-rise areas cause layover and shadow. | [memory, untested] |
| VIIRS night lights | Economic activity and lighting proxy | Monthly or annual composites (for example NASA Black Marble, product VNP46A4 as used by the Vital City project). 500 m: coarse for tracts. | [verified for product name; availability untested] |
| AlphaEarth annual embeddings | Pre-computed 64-dimensional, 10 m embeddings used as a baseline feature set | Year coverage for NYC and access route need confirming (Earth Engine). | [memory, untested] |
| NAIP or NYC orthoimagery | High-resolution context | Update cadence and years need checking. | [memory, untested] |

### 3.4 Known data pitfalls

- Complaint records with 0,0 coordinates; report type and location precision limits.
- NYPD data are public and location-offset by design; this project makes no claims below tract level.
- Commuter-heavy tracts (Midtown, Financial District): residential population is a bad denominator. Flag them and run with and without.
- 2020 tract boundary change.
- Reporting and enforcement bias: see Section 9.

---

## 4. Method

### 4.1 Analysis unit and panel

- Unit: census tract (about 2,300 in NYC [memory]); NTA as the robustness aggregation.
- Time: annual, 2018–2025. 2026 is a partial year and is excluded or shown separately.
- Panel columns: tract id, year, outcome counts by category, year-matched lagged ACS covariates, satellite features, lagged outcome.

### 4.2 Satellite feature specification

| Feature | Derivation | Lag used |
|---|---|---|
| Canopy and greenness | Summer (Jun–Aug) median NDVI per tract; canopy fraction if land-cover years allow | t−1 |
| Impervious surface or construction change | Year-over-year change in a built-up index; Sentinel-1 backscatter change | t−1 |
| Land-surface temperature | Summer mean LST; count of hot days above a tract-relative threshold; anomaly versus the tract's eight-year mean | t−1 and same summer (seasonal test) |
| Night lights | Annual mean radiance and its change | t−1 |
| Vacant or bare-surface fraction | Tract-level Sentinel-2 bare-soil index | t−1 |

Compositing: cloud and shadow masking, seasonal windows, median compositing, and a per-tract valid-pixel fraction kept as a quality column.

### 4.3 Analyses

1. **Descriptive maps.** Small multiples by year; correlation matrix; Moran's I (PySAL `esda`).
2. **Panel count model.** Negative binomial or Poisson (statsmodels), tract and year fixed effects, log population offset, one-year-lagged satellite features, standard errors clustered by tract. Robustness: NTA aggregation; exclude commuter-heavy tracts; leads as a placebo test; separate crime categories.
3. **Incremental-value prediction test (core).** Predict next-year tract outcome under four feature sets: (a) last year's outcome only; (b) plus ACS; (c) plus hand-built satellite features; (d) plus AlphaEarth embeddings as a strong baseline. Models: gradient boosting and a regularized count model (scikit-learn). Validation: spatial block cross-validation (leave-one-borough-out, then leave-one-precinct-cluster-out) plus forward-chained time splits (train through 2022, test 2023; and so on). Report Poisson deviance, MAE and rank agreement on the top decile of tracts. The primary claim is the increment from (b) to (c) and from (b) to (d), with uncertainty.
4. **Embedding comparison.** Embeddings to crime already exist in the literature, so this is a comparison, not a claim: do hand-built indices and embeddings each add anything beyond lagged outcomes and census variables? Optional: a small PyTorch CNN or Clay embeddings.
5. **Seasonal heat test.** Monthly shootings against monthly land-surface-temperature anomaly and canopy, separating a summer effect from a place effect.
6. **Radar building-change test.** Sentinel-1 backscatter and coherence change events for construction and demolition, validated against Department of Buildings demolition and new-building permits. Success criterion: recover a stated share of known permit events at known sites, with a stated false-positive rate. A Phase 0 probe on two or three known sites decides how much effort this gets; a documented failure is an acceptable outcome.
7. **Bias check (appendix).** Prediction error across groups of tracts by demographic composition and borough.

### 4.4 Tooling

| Need | Tools |
|---|---|
| Data handling | Python, SQL (DuckDB or SQLite), pandas, NumPy |
| Geospatial | GeoPandas, rasterio, xarray, PySAL; GeoPy for distances; STAC clients for Planetary Computer |
| Statistics and ML | statsmodels, scikit-learn, optionally PyTorch |
| Network features | networkx and OSMnx, only if they earn their place |
| Text | NLTK on 311 descriptions, only if it earns its place |
| Visualization | Matplotlib; MapLibre GL JS or deck.gl for the web map; Power BI for the leadership report |

Do not add optional modules just to list a tool. A tool used for no reason reads as keyword stuffing.

---

## 5. Deliverables

1. **Interactive web map.** Tract choropleth with a 2018–2025 time slider, toggles for satellite and outcome layers, tract cards on click. Static hosting, no backend. MapLibre GL JS or deck.gl to be chosen.
2. **Two-page leadership brief (PDF).** Three findings, one chart each, one caveat box, plain language.
3. **Power BI report** on the exported tract panel, mirroring the brief. Power BI Desktop is Windows-only; the repository ships the exported tract table, a PDF export and a short description of the data model, since a `.pbix` file is a binary and a published workspace needs a licence (not checked).
4. **Reproducible repository.** README, pinned environment, a single run order, cached data excluded from git, a data-provenance table with retrieval dates.
5. **Model card and scorecard.** What was tested, what the satellite features added, what failed.
6. **Optional short write-up or video.**

### Repository layout

```
nyc-from-orbit/
  README.md  LICENSE  CITATION.cff  CHANGELOG.md
  CONTRIBUTING.md  CODE_OF_CONDUCT.md  SECURITY.md
  environment.yml  Makefile  pyproject.toml
  .github/            # issue and pull-request templates, CI workflows
  data/               # gitignored: raw and interim; fetch scripts only
  src/
    ingest_nypd.py  ingest_acs.py  ingest_dob.py
    stac_composites.py  features.py  panel.py
    models_panel.py  models_predict.py  bias_check.py  radar_change.py
  tests/              # unit tests and small fixtures
  notebooks/          # exploration only
  site/               # static map
  powerbi/            # exported table, PDF, data-model notes
  brief/              # two-page PDF source
  docs/               # PLAN.md, model card, provenance table, data licences
```

---

## 6. Open-source standards

The repository is private now and will be made public. Everything is built to open-source standards from the first commit.

**Repository files**

- `LICENSE`: MIT for code (confirmed 2026-10-25); documentation and figures under CC BY 4.0.
- `README.md` with purpose, scope, quick start, data sources, results summary, limitations, and the non-affiliation statement.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), `SECURITY.md`, issue and pull-request templates.
- `CITATION.cff`, `CHANGELOG.md`, semantic-version tags, and a release archive with a DOI (for example via Zenodo).

**Reproducibility**

- Pinned environment file and a single `make` run order from raw download to final figures.
- Raw data are not committed. Fetch scripts record URLs, retrieval dates and checksums, and a provenance table lists every dataset with its licence and terms.
- Small, synthetic or public-sample fixtures for tests so CI runs without large downloads.

**Quality**

- Continuous integration: lint (ruff), tests (pytest), and a smoke run of the pipeline on the fixtures.
- Pre-commit hooks, typed function signatures where practical, and a notebook output-stripping hook.
- Code review through pull requests even for a single maintainer, using the same templates a contributor would see.

**Responsible release**

- An ethics and limitations statement in the README: reported-crime data reflect reporting and policing intensity, results are associational, tract-level and annual, and the project must not be used to target individuals or demographic groups.
- A model card and datasheet describing data, intended use, non-use and known failure modes.
- Data-terms check for every source before public release, with attribution as each licence requires.

**Pre-public checklist** (all must pass before the visibility change)

1. Scan full git history for credentials, tokens, personal data and local paths.
2. Confirm no third-party data are redistributed beyond what each licence permits.
3. Confirm no references to private plans, employers, applications or unpublished contacts remain in files or history.
4. Set repository description, topics and social preview; enable branch protection and security alerts.
5. Check that the README and docs describe the project as it is, not as planned.

---

## 7. Schedule (starts 2026-10-25)

Effort figures are estimates, not commitments. Target for a first public release is 2026-11-02.

| Phase | Work | Effort | Target date | Exit criterion |
|---|---|---|---|---|
| 0. Probe | Pull one real sample of each layer for a handful of tracts; check whether 10 m imagery shows real tract-to-tract differences in NYC; test Sentinel-1 on two or three known demolition sites; confirm outcome-data date coverage; check AlphaEarth availability for NYC | 0.5 day | 2026-10-25 | Written go or no-go with screenshots of real samples |
| 1. Panel and scaffolding | Repository scaffolding to Section 6 standards (license, templates, CI, environment); ingest outcomes and ACS; build composites and features; assemble the tract-year panel | 2 days | 2026-10-27 | Panel with quality columns, provenance table, CI green |
| 2. Analysis | Maps, panel model, incremental-value test with all four feature sets, robustness, bias check | 2 days | 2026-10-29 | Scorecard with honest increments and uncertainty |
| 3. Radar building-change test | Backscatter and coherence change against permits | 2 days | 2026-10-31 | Recovery rate against permits, or a documented failure |
| 4. Deliverables | Web map, two-page brief, Power BI report and exports, README, model card | 2 days | 2026-11-02 | Release candidate; pre-public checklist reviewed |

---

## 8. Success criteria

- A reviewer can reproduce the headline numbers from the repository.
- The brief states in plain language what the satellite features added to prediction and where they failed.
- Every claim traces to a named dataset and a retrieval date.
- A null or small effect is reported at its true size, not rescued by choosing the metric.
- The repository passes its own open-source checklist.

---

## 9. Risks and limits

| Risk | Why it matters | Mitigation |
|---|---|---|
| 10 m satellite data too coarse for NYC tracts | Signal may be near zero | Phase 0 probe; fall back to NAIP or NYC orthoimagery |
| Increment is zero or small | Lagged outcomes usually explain most variation [inference]; embedding work shows weakest signal in dense areas (ρ = −0.71) | Design the brief around increment size and uncertainty; report nulls |
| Read as a first or as crime prediction | Substantial prior work exists; "predicting crime" carries policy baggage | Describe as replication and extension; use "association and lag test" |
| Reporting and enforcement bias | Complaint data measure reporting and policing intensity, not crime itself | Prefer shootings and serious violent or property categories; say so at the top of the brief |
| Ecological fallacy | Tract-level association is not individual-level cause | Descriptive framing only; no causal claims without a design |
| Commuter-heavy tracts | Population denominators mislead | Exclude or flag; run both ways |
| 2020 tract boundary change | Breaks panel continuity | Crosswalk, or NTA robustness run |
| Radar layover and shadow in dense areas | Radar test may fail | Phase 0 probe; report failure plainly |
| Cloud cover and Landsat revisit | Thin summer composites | Keep valid-pixel fraction; use multi-month windows |
| Power BI portability | Desktop-only, binary files | Ship exports and PDF; document the data model |
| Time | Seven days for the full scope | Phases 0–2 are the minimum viable release; Phases 3–4 can slip to a later release |
| Public-release hygiene | Mistakes in history are permanent | Pre-public checklist in Section 6 |

**Scope guard.** The project does not produce individual-level or block-level predictions, real-time tactical output, or anything that targets demographic groups. Tract-level, annual, descriptive and associational only.

---

## 10. Decisions (2026-10-25)

1. **Framing:** written for a police-department analytics audience, with a clear non-affiliation statement.
2. **Hook:** revised to the incremental-value question (Section 1); avoid "first" and "predicting crime" in public material.
3. **Embeddings:** included as a comparison feature set (AlphaEarth, optionally Clay), not as a selling point.
4. **Radar building-change test:** included in scope (Phase 3), with a Phase 0 feasibility probe.
5. **Power BI report:** included as a deliverable.
6. **Schedule:** starts 2026-10-25.
7. **Repository:** private for now, public later; development follows the standards in Section 6.

License: MIT for code (confirmed 2026-10-25).

---

## 11. Sources checked

- [Najjar et al. 2018](https://ar5iv.arxiv.org/html/1812.06764)
- [Built environment and neighborhood crime from satellite imagery (2017)](https://arxiv.org/abs/1710.05483)
- [Gong et al. 2026, Earth Embeddings Reveal Diverse Urban Signals from Space](https://www.alphaxiv.org/abs/2604.03456)
- [Guo et al. 2026, MobFusion](https://arxiv.org/abs/2606.01745)
- [Kondo et al. 2017, tree cover and gun assault](https://research.fs.usda.gov/treesearch/54568)
- [Racek et al. 2025, press release](https://www.alphagalileo.org/en-gb/Item-Display/ItemId/267670)
- [NYPD Complaint Data Historic, catalog entry](https://catalog.data.gov/dataset/nypd-complaint-data-historic)
- [Runaway Feedback Loops in Predictive Policing](https://arxiv.org/pdf/1706.09847)
- [Vital-City-NYC/streetlight-cities](https://github.com/Vital-City-NYC/streetlight-cities)
- [earth-embeddings-workshop-in-crime](https://github.com/edgar-daniel-codes/earth-embeddings-workshop-in-crime)
- [sf-crime-gee-analysis](https://github.com/Airahb/sf-crime-gee-analysis)

Not checked: shooting-incident dataset details, ACS tract availability, tree-canopy product years, AlphaEarth availability for NYC, NAIP years, and every item tagged [memory] or [search; paper not opened].
