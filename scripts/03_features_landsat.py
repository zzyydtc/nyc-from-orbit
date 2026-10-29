"""Landsat 8/9 summer land surface temperature per tract and year.

Usage: python scripts/03_features_landsat.py 2024 [2023 ...]
Writes data/interim/lst_<year>.csv with columns geoid, year, lst_mean, lst_p90, n_scenes.
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
RES = 30
INTERIM = Path("data/interim")
CLOUD_BITS = 0b11110  # dilated cloud, cirrus, cloud, cloud shadow


def search_items(year):
    cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
    items = []
    # Landsat scenes are fixed path/row; query each of the two that cover NYC separately to avoid timeouts.
    for path, row in ((13, 32), (13, 31), (14, 32), (14, 31)):
        s = cat.search(
            collections=["landsat-c2-l2"],
            bbox=BBOX,
            datetime=f"{year}-06-01/{year}-08-31",
            query={
                "landsat:wrs_path": {"eq": str(path).zfill(3)},
                "landsat:wrs_row": {"eq": str(row).zfill(3)},
                "eo:cloud_cover": {"lt": 30},
                "platform": {"in": ["landsat-8", "landsat-9"]},
            },
            max_items=40,
        )
        items.extend(s.items())
    return items


def lst_composite(items):
    ds = odc_load(
        items, bands=["lwir11", "qa_pixel"], bbox=BBOX, resolution=RES, groupby="solar_day",
        chunks={"x": 2048, "y": 2048}, dtype="float32", nodata=0,
    )
    qa = ds.qa_pixel.astype("uint16")
    clear = (qa & CLOUD_BITS) == 0
    kelvin = ds.lwir11 * 0.00341802 + 149.0
    celsius = (kelvin - 273.15).where(clear & (ds.lwir11 > 0))
    return celsius.median("time").compute(), ds.sizes["time"]


def zonal(lst, tracts):
    shapes = ((g, i + 1) for i, g in enumerate(tracts.to_crs(lst.odc.crs).geometry))
    labels = features.rasterize(shapes, out_shape=lst.shape, transform=lst.odc.geobox.transform, fill=0, dtype="int32")
    vals = lst.values
    rows = []
    for i, geoid in enumerate(tracts["geoid"], start=1):
        v = vals[labels == i]
        v = v[np.isfinite(v)]
        rows.append({
            "geoid": geoid,
            "lst_mean": float(v.mean()) if v.size else np.nan,
            "lst_p90": float(np.percentile(v, 90)) if v.size else np.nan,
        })
    return pd.DataFrame(rows)


def main():
    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "geometry"]]
    for year in map(int, sys.argv[1:]):
        items = search_items(year)
        print(year, "items:", len(items), flush=True)
        lst, n = lst_composite(items)
        out = zonal(lst, tracts)
        out["year"], out["n_scenes"] = year, n
        out.to_csv(INTERIM / f"lst_{year}.csv", index=False)
        print(year, "done; tracts with data:", int(out.lst_mean.notna().sum()), flush=True)


if __name__ == "__main__":
    main()
