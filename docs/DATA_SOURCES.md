# Data sources

Raw data is not stored in this repository. Each script downloads what it needs.

| Dataset | Provider | Access | Terms |
|---|---|---|---|
| NYPD complaints (historic) | NYC Open Data, dataset `qgea-i56i` | Public API | NYC Open Data terms of use |
| NYPD shooting incidents | NYC Open Data, datasets `833y-fsy8` (through 2024) and `5ucz-vwe8` (2025) | Public API | NYC Open Data terms of use |
| 2020 census tracts | NYC Open Data, dataset `63ge-mke6` | Public API | NYC Open Data terms of use |
| American Community Survey 5-year, 2023 | US Census Bureau | Free API key (`CENSUS_API_KEY`) | Census Bureau terms |
| Sentinel-2 L2A | ESA Copernicus, via Microsoft Planetary Computer | Public STAC | Copernicus Sentinel data legal notice (free, full and open) |
| Landsat Collection 2 Level 2 | USGS, via Microsoft Planetary Computer | Public STAC | USGS data policy (public domain, credit requested) |
| Sentinel-1 RTC (radar backscatter) | Microsoft Planetary Computer, derived from ESA Copernicus Sentinel-1 | Public STAC | CC BY 4.0 (as declared in the STAC collection) |
| DOB job application filings, legacy (`ic3t-wcy2`) and DOB NOW: Build (`w9ak-ipjd`) | NYC Open Data | Public API | NYC Open Data terms of use |
| VIIRS Black Marble VNP46A4 (annual) | NASA LAADS DAAC | Free Earthdata token (`EARTHDATA_TOKEN`) | NASA open data policy |
| AlphaEarth Foundations satellite embeddings, annual | Google and Google DeepMind, copy on Source Cooperative | Public | CC BY 4.0. Attribution: "The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind." |

Terms review (2026-10-30)

| Source | What the terms say | What this project does |
|---|---|---|
| NYC Open Data (NYPD, DCP, DOB datasets) | Dataset metadata carries no separate license and names the publishing agency as attribution. The portal FAQ states there are no restrictions on use, and the Technical Standards Manual describes published data as available "without restriction or licensing requirements". The full portal Terms of Use page could not be retrieved on this date (the legacy nyc.gov page returns 404), and an older version reportedly asked for a disclaimer on modified data and allowed the City to withdraw datasets. | Credits the agencies, states that the data were aggregated and modified, and disclaims City endorsement. Only aggregated counts per tract-year and simplified tract outlines are redistributed, never incident records. The general nyc.gov Terms of Use (read 2026-11-01) govern the City website, not the datasets: they prohibit claiming a relationship with the City, disclaim all warranties ("as is"), and reserve rights in website design and content, none of which this project uses. **Still to confirm before going public:** the Open Data portal's own data terms, if the portal footer links a separate page. |
| Census Bureau API (ACS 2023) | Requires the notice below on any service using the API; forbids using the data to identify people or entities; endorsement must not be implied. | Notice included in the README and on the map. Only tract-level estimates are used. |
| Copernicus Sentinel-2 | Free, full and open under the Copernicus Sentinel data legal notice; modified data must carry the credit line below. | Credit line included in the README and on the map. |
| Sentinel-1 RTC | CC BY 4.0 per the Planetary Computer collection; derived from Copernicus Sentinel-1. | Credit line included. Only per-tract summaries are redistributed. |
| Landsat Collection 2 | USGS data policy: no restriction, credit requested. | Credit included. |
| VIIRS Black Marble (NASA) | NASA-sponsored data are open (CC0 unless marked otherwise); citation is strongly requested; NASA endorsement must not be implied. | Citation included; raw files are not redistributed. |
| AlphaEarth embeddings | CC BY 4.0 with the Google and Google DeepMind attribution given in the table. | Attribution included; only per-tract averages and principal components are used. |
| OpenStreetMap tiles (web map) | Normal interactive viewing is allowed with visible attribution, no bulk download or prefetching, and an accurate Referer must be sent. | The map loads only the visible tiles, keeps the attribution visible and adds no offline features. If the map gets heavy traffic, switch to a tile provider with an agreement. |
| Leaflet 1.9.4 | BSD-2-Clause, loaded from cdnjs. | No copy is redistributed. |

Required notices (also in the README):

- "This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."
- "Contains modified Copernicus Sentinel data 2018-2025."
- "The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind."
- Landsat courtesy of the U.S. Geological Survey; VIIRS Black Marble VNP46A4 courtesy of NASA LAADS DAAC.
- Retrieval: all datasets were pulled in October 2026 (2025 shootings come from a separate dataset, listed above). Rerunning later will return newer records and slightly different numbers.
- This table summarises the public terms; it is not a legal review.
- This is an independent project with no affiliation with, or endorsement by, the New York City Police Department, the City of New York, NASA, ESA, Google or any other data provider.
