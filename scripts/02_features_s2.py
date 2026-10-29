"""Sentinel-2 summer NDVI per tract and year.

Usage: python scripts/02_features_s2.py 2024 [2023 ...]
Writes data/interim/s2_<year>.csv with columns geoid, year, ndvi_mean, ndvi_p90, green_share, n_scenes.
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
RES = 20  # metres; 10 m is possible but 4x the compute
CLEAR_SCL = [4, 5, 6, 7]  # vegetation, bare soil, water, unclassified
INTERIM = Path("data/interim")


def search_items(year):
    cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
    items = []
    # Per-tile queries avoid the timeouts seen on one borough-sized search.
    for tile in ("18TWL", "18TWK", "18TXL", "18TXK"):
        s = cat.search(
            collections=["sentinel-2-l2a"],
            bbox=BBOX,
            datetime=f"{year}-06-01/{year}-08-31",
            query={"s2:mgrs_tile": {"eq": tile}, "eo:cloud_cover": {"lt": 25}},
            max_items=60,
        )
        items.extend(s.items())
    return items


def ndvi_composite(items):
    ds = odc_load(
        items, bands=["B04", "B08", "SCL"], bbox=BBOX, resolution=RES, groupby="solar_day",
        chunks={"x": 2048, "y": 2048}, dtype="float32", nodata=0,
    )
    clear = ds.SCL.isin(CLEAR_SCL)
    red, nir = ds.B04.where(clear), ds.B08.where(clear)
    ndvi = ((nir - red) / (nir + red)).where(lambda x: np.isfinite(x))
    return ndvi.median("time").compute(), ds.sizes["time"]


def zonal(ndvi, tracts):
    transform = ndvi.odc.geobox.transform
    shapes = ((geom, i + 1) for i, geom in enumerate(tracts.to_crs(ndvi.odc.crs).geometry))
    labels = features.rasterize(shapes, out_shape=ndvi.shape, transform=transform, fill=0, dtype="int32")
    vals = ndvi.values
    rows = []
    for i, geoid in enumerate(tracts["geoid"], start=1):
        v = vals[labels == i]
        v = v[np.isfinite(v)]
        rows.append({
            "geoid": geoid,
            "ndvi_mean": float(v.mean()) if v.size else np.nan,
            "ndvi_p90": float(np.percentile(v, 90)) if v.size else np.nan,
            "green_share": float((v > 0.5).mean()) if v.size else np.nan,
            "n_pixels": int(v.size),
        })
    return pd.DataFrame(rows)


def main():
    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "geometry"]]
    for year in map(int, sys.argv[1:]):
        items = search_items(year)
        print(year, "items:", len(items), flush=True)
        ndvi, n = ndvi_composite(items)
        out = zonal(ndvi, tracts)
        out["year"], out["n_scenes"] = year, n
        out.to_csv(INTERIM / f"s2_{year}.csv", index=False)
        print(year, "done; tracts with data:", int(out.ndvi_mean.notna().sum()), flush=True)


if __name__ == "__main__":
    main()
