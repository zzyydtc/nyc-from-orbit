# Data sources

Raw data is not stored in this repository. Each script downloads what it needs.

| Dataset | Provider | Access | Terms |
|---|---|---|---|
| NYPD complaints (historic) | NYC Open Data, dataset `qgea-i56i` | Public API | NYC Open Data terms of use |
| NYPD shooting incidents | NYC Open Data, datasets `833y-fsy8` (through 2024) and `5ucz-vwe8` (2025) | Public API | NYC Open Data terms of use |
| 2020 census tracts | NYC Open Data, dataset `63ge-mke6` | Public API | NYC Open Data terms of use |
| American Community Survey 5-year, 2023 | US Census Bureau | Free API key (`CENSUS_API_KEY`) | Census Bureau terms |
| Sentinel-2 L2A | ESA Copernicus, via Microsoft Planetary Computer | Public STAC | Copernicus open data terms |
| Landsat Collection 2 Level 2 | USGS, via Microsoft Planetary Computer | Public STAC | USGS public domain |
| Sentinel-1 RTC (radar backscatter) | ESA Copernicus, via Microsoft Planetary Computer | Public STAC | Copernicus open data terms |
| DOB job application filings, legacy (`ic3t-wcy2`) and DOB NOW: Build (`w9ak-ipjd`) | NYC Open Data | Public API | NYC Open Data terms of use |
| VIIRS Black Marble VNP46A4 (annual) | NASA LAADS DAAC | Free Earthdata token (`EARTHDATA_TOKEN`) | NASA open data policy |
| AlphaEarth Foundations satellite embeddings, annual | Google and Google DeepMind, copy on Source Cooperative | Public | CC BY 4.0. Attribution: "The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind." |

Notes

- Retrieval: all datasets were pulled in October 2026 (2025 shootings come from a separate dataset, listed above). Rerunning later will return newer records and slightly different numbers.
- NYC Open Data and Census terms should be re-checked before public release; this table lists the providers, not a legal review.
- This is an independent project with no affiliation with, or endorsement by, the New York City Police Department or any other agency.
