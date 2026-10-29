# Phase 0 probe: data availability

Run date: 2026-10-27. Script: `scripts/probe_phase0.py`. The goal was to check, with real requests, that each layer is reachable and usable for NYC census tracts before building anything.

## Results

| Layer | Source | Status | Notes |
|---|---|---|---|
| Complaints, 2006-2025 | NYC Open Data `qgea-i56i` | Available | About 460k-570k rows per year; 2018-2025 fully covered. A few rows have bad dates (years before 2006) and must be filtered. |
| Shooting incidents | NYC Open Data `833y-fsy8` | Available through 2024 | 2025 lives in the year-to-date dataset and still needs to be confirmed. |
| Census tracts, 2020 | NYC Open Data `63ge-mke6` | Available | 2,325 features, `geoid` key present. |
| ACS 5-year covariates | Census API | Available with a free key | Without a key the API returns "Missing Key". With one, a 2023 query returned 805 Brooklyn tracts. Key is read from `CENSUS_API_KEY`. |
| Sentinel-2 L2A | Planetary Computer STAC | Available | A 1 km box returned about 36 scenes per summer; a real NDVI chip read at 10 m resolution (112 x 83 pixels). |
| Landsat Collection 2 L2 | Planetary Computer STAC | Available | 24-31 scenes per summer for 2019 and 2024; carries the thermal band for surface temperature. |
| Sentinel-1 RTC | Planetary Computer STAC | Available | 8 scenes per summer at 10 m; a VV chip read succeeded. Whether the signal detects building change is a Phase 3 question. |
| AlphaEarth embeddings | Public COGs on Source Cooperative (CC BY 4.0) | Available, 2017-2025 | UTM zone 18N covers NYC; 64 channels; files are large (up to several GB) but cloud-optimized. The files are stored bottom-up, so the supplied VRTs must be used. No account needed. |
| Night lights (VIIRS Black Marble) | NASA LAADS DAAC, product VNP46A4 (annual), found through CMR | Available with a free Earthdata token | Tile h10v04 covers NYC. A ranged download with the token returned HTTP 206 and a valid HDF5 header. Token is read from `EARTHDATA_TOKEN`. Listing the LAADS archive directory timed out, so granules are located through CMR instead. |

## Observations

- Querying a whole-borough bounding box against the STAC API timed out; small boxes and short date ranges work. Fetch scripts must query per tract or per small tile.
- Sentinel-2 over a 1 km Manhattan box gave NDVI from -0.13 to 0.65, so 10 m pixels do resolve green and built surfaces.

## Decision

**Go.** Every planned layer is reachable: outcomes, tracts, ACS, Sentinel-2, Landsat, AlphaEarth and night lights. Keys and tokens are read from environment variables and never stored in the repository.

Open items:

1. Confirm the 2025 shooting data source.
2. Radar building-change test: data is present, the signal is untested.
3. The Earthdata token expires after about 60 days; regenerate it if downloads start returning 401.
