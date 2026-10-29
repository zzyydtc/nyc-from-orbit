"""Find the AlphaEarth COG files that cover NYC, for every year.

Reads the public file index and writes data/raw/aef_tiles.csv (year, url, utm bounds).
"""
from pathlib import Path

import pandas as pd
import requests

BASE = "https://data.source.coop/tge-labs/"
INDEX = BASE + "aef/v1/annual/aef_index.csv"
# NYC extent in UTM zone 18N (EPSG:32618), metres
NYC_UTM = (562000, 4482000, 610000, 4531000)


def main():
    head = requests.head(INDEX, timeout=30, allow_redirects=True)
    print("index size MB:", int(head.headers.get("content-length", 0)) / 1e6)
    rows = []
    with requests.get(INDEX, stream=True, timeout=300) as r:
        r.raise_for_status()
        r.raw.decode_content = True
        for chunk in pd.read_csv(r.raw, chunksize=100_000):
            hit = chunk[chunk["utm_zone"] == "18N"]
            hit = hit[
                (hit.utm_east > NYC_UTM[0]) & (hit.utm_west < NYC_UTM[2])
                & (hit.utm_north > NYC_UTM[1]) & (hit.utm_south < NYC_UTM[3])
            ]
            rows.append(hit)
    out = pd.concat(rows)
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    out.to_csv("data/raw/aef_tiles.csv", index=False)
    print(out.columns.tolist())
    print(out.groupby("year").size())


if __name__ == "__main__":
    main()
