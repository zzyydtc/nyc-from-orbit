"""Sentinel-1 RTC summer backscatter per tract and year.

Usage: python scripts/13_features_s1.py 2024 [2023 ...]
Writes data/interim/s1_<year>.csv with columns geoid, year, vv_db, vh_db, n_scenes. Ascending relative orbit 33 only,
so geometry is the same in every year. Median over June-August scenes, in dB.
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import planetary_computer as pc
from odc.stac import load as odc_load
from pystac_client import Client
from rasterio import features

BBOX = [-74.26, 40.49, -73.70, 40.92]
RES = 20
INTERIM = Path("data/interim")


def search_items(year):
    cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
    s = cat.search(collections=["sentinel-1-rtc"], bbox=BBOX, datetime=f"{year}-06-01/{year}-08-31",
                   query={"sat:orbit_state": {"eq": "ascending"}, "sat:relative_orbit": {"eq": 33}})
    return list(s.items())


def composite(items):
    ds = odc_load(items, bands=["vv", "vh"], bbox=BBOX, resolution=RES, groupby="solar_day",
                  chunks={"x": 2048, "y": 2048}, dtype="float32", nodata=-32768)
    # Power-domain median across dates, then dB.
    med = ds.where(ds > 0).median("time").compute()
    return 10 * np.log10(med), ds.sizes["time"]


def zonal(arrs, tracts):
    ref = arrs["vv"]
    transform = ref.odc.geobox.transform
    shapes = ((geom, i + 1) for i, geom in enumerate(tracts.to_crs(ref.odc.crs).geometry))
    labels = features.rasterize(shapes, out_shape=ref.shape, transform=transform, fill=0, dtype="int32")
    rows = []
    for i, geoid in enumerate(tracts["geoid"], start=1):
        m = labels == i
        row = {"geoid": geoid}
        for name, a in arrs.items():
            v = a.values[m]
            v = v[np.isfinite(v)]
            row[f"{name}_db"] = float(v.mean()) if v.size else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "geometry"]]
    for year in map(int, sys.argv[1:]):
        items = search_items(year)
        print(year, "items:", len(items), flush=True)
        db, n = composite(items)
        out = zonal({"vv": db.vv, "vh": db.vh}, tracts)
        out["year"], out["n_scenes"] = year, n
        out.to_csv(INTERIM / f"s1_{year}.csv", index=False)
        print(year, "done; tracts with data:", int(out.vv_db.notna().sum()), flush=True)


if __name__ == "__main__":
    main()
