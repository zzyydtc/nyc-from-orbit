"""NASA Black Marble annual night lights (VNP46A4, tile h10v04) sampled per tract.

Usage: python scripts/06_features_viirs.py 2024 [2023 ...]
Needs EARTHDATA_TOKEN in the environment. Writes data/interim/viirs_<year>.csv (geoid, year, ntl).
The grid is 15 arc-seconds (about 460 x 350 m), coarser than most NYC tracts, so each tract takes a
bilinear sample at its representative point rather than a pixel average.
"""
import os
import sys
from pathlib import Path

import geopandas as gpd
import h5py
import numpy as np
import pandas as pd
import requests
from scipy.ndimage import map_coordinates

RAW = Path("data/raw")
INTERIM = Path("data/interim")
DATASET = "HDFEOS/GRIDS/VIIRS_Grid_DNB_2d/Data Fields/AllAngle_Composite_Snow_Free"
LON0, LAT0, STEP = -80.0, 50.0, 1 / 240  # tile h10v04 upper-left corner and pixel size in degrees


def granule_url(year):
    r = requests.get(
        "https://cmr.earthdata.nasa.gov/search/granules.json",
        params={
            "short_name": "VNP46A4",
            "temporal": f"{year}-01-01T00:00:00Z,{year}-12-31T23:59:59Z",
            "bounding_box": "-74.1,40.6,-73.7,40.9",
            "page_size": 10,
        },
        timeout=60,
    )
    r.raise_for_status()
    for e in r.json()["feed"]["entry"]:
        for link in e["links"]:
            if link.get("rel", "").endswith("/data#") and "h10v04" in link["href"] and link["href"].endswith(".h5"):
                return link["href"]
    raise RuntimeError(f"no h10v04 granule for {year}")


def download(year):
    path = RAW / f"viirs_{year}.h5"
    if path.exists():
        return path
    token = os.environ.get("EARTHDATA_TOKEN")
    if not token:
        sys.exit("EARTHDATA_TOKEN is not set")
    with requests.get(granule_url(year), headers={"Authorization": f"Bearer {token}"}, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    return path


def main():
    tracts = gpd.read_file(RAW / "tracts2020.geojson")[["geoid", "geometry"]]
    pts = tracts.to_crs(32618).geometry.representative_point().to_crs(4326)
    cols = (pts.x.values - LON0) / STEP - 0.5
    rows = (LAT0 - pts.y.values) / STEP - 0.5
    for year in map(int, sys.argv[1:]):
        with h5py.File(download(year), "r") as f:
            ds = f[DATASET]
            arr = ds[...].astype("float32")
            fill = ds.attrs.get("_FillValue", [65535])[0]
            scale = float(np.atleast_1d(ds.attrs.get("scale_factor", [0.1]))[0])
        arr[arr == fill] = np.nan
        arr *= scale
        filled = np.nan_to_num(arr, nan=0.0)  # unlit and masked pixels contribute zero radiance
        ntl = map_coordinates(filled, [rows, cols], order=1, mode="nearest")
        out = pd.DataFrame({"geoid": tracts["geoid"].values, "year": year, "ntl": ntl})
        out.to_csv(INTERIM / f"viirs_{year}.csv", index=False)
        print(year, "done; median radiance:", float(np.median(ntl)), flush=True)


if __name__ == "__main__":
    main()
