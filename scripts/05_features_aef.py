"""AlphaEarth annual embeddings averaged per tract.

Usage: python scripts/05_features_aef.py 2024 [2023 ...]
Reads the 20 m overview of each COG covering NYC (so the transfer stays small), de-quantizes,
and writes data/interim/aef_<year>.csv with columns geoid, year, a00..a63.
Attribution: "The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind."
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio import features
from rasterio.transform import from_origin
from rasterio.windows import Window

EXTENT = (562000, 4482000, 610000, 4531000)  # west, south, east, north in EPSG:32618
RES = 20
OV = 0  # first overview level = 4096 x 4096 per file = 20 m
INTERIM = Path("data/interim")
W = (EXTENT[2] - EXTENT[0]) // RES
H = (EXTENT[3] - EXTENT[1]) // RES


def https(path):
    return path.replace("s3://us-west-2.opendata.source.coop/", "https://data.source.coop/")


def mosaic(tiles):
    """Return an int8 array (64, H, W), top-down, -128 where there is no data."""
    out = np.full((64, H, W), -128, dtype=np.int8)
    for t in tiles.itertuples():
        w, s, e, n = max(t.utm_west, EXTENT[0]), max(t.utm_south, EXTENT[1]), min(t.utm_east, EXTENT[2]), min(t.utm_north, EXTENT[3])
        if w >= e or s >= n:
            continue
        col0, col1 = (w - t.utm_west) // RES, (e - t.utm_west) // RES
        row0, row1 = (s - t.utm_south) // RES, (n - t.utm_south) // RES  # rows count northward
        with rasterio.open("/vsicurl/" + https(t.path), overview_level=OV) as src:
            block = src.read(window=Window(col0, row0, col1 - col0, row1 - row0))
        block = block[:, ::-1, :]  # flip to top-down
        x0, y1 = (w - EXTENT[0]) // RES, (EXTENT[3] - n) // RES
        out[:, y1:y1 + block.shape[1], x0:x0 + block.shape[2]] = block
    return out


def main():
    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "geometry"]].to_crs(32618)
    transform = from_origin(EXTENT[0], EXTENT[3], RES, RES)
    labels = features.rasterize(
        ((g, i + 1) for i, g in enumerate(tracts.geometry)), out_shape=(H, W), transform=transform, fill=0, dtype="int32"
    )
    index = pd.read_csv("data/raw/aef_tiles.csv")
    for year in map(int, sys.argv[1:]):
        arr = mosaic(index[index.year == year])
        valid = (arr[0] != -128) & (labels > 0)
        lab = labels[valid]
        counts = np.bincount(lab, minlength=len(tracts) + 1).astype("float64")
        res = {"geoid": tracts["geoid"].values}
        for b in range(64):
            v = arr[b][valid].astype("float32")
            dq = (v / 127.5) ** 2 * np.sign(v)
            sums = np.bincount(lab, weights=dq, minlength=len(tracts) + 1)
            with np.errstate(invalid="ignore", divide="ignore"):
                res[f"a{b:02d}"] = (sums / counts)[1:]
        out = pd.DataFrame(res)
        out["year"] = year
        out["n_pixels"] = counts[1:].astype(int)
        out.to_csv(INTERIM / f"aef_{year}.csv", index=False)
        print(year, "done; tracts with data:", int((counts[1:] > 0).sum()), flush=True)


if __name__ == "__main__":
    main()
