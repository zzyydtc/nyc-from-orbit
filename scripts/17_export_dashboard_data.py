"""Export the aggregated data files used by the static dashboard in dashboard/.

Writes dashboard/src/data/: tracts.geojson (simplified outlines with an index), values.json (per-tract yearly values
and colour breaks), boroughs.csv, gains.csv and radar.csv. Only tract-level aggregates are written, never incident
records. Needs data/processed/panel.csv and the output/ tables from scripts 09, 14 and 15.
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import mapping

OUT = Path("dashboard/src/data")
YEARS = list(range(2018, 2026))
VARS = {
    "felony_rate": ("Felony complaints", "per 1,000 residents"),
    "shoot_rate": ("Shooting incidents", "per 1,000 residents"),
    "ndvi_mean": ("Vegetation (NDVI)", "Sentinel-2, summer"),
    "lst_mean": ("Surface temperature", "deg C, Landsat summer"),
    "ntl": ("Night lights", "nW/cm2/sr, VIIRS"),
    "vv_db": ("Radar backscatter VV", "dB, Sentinel-1 summer"),
}


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(x, 5) for x in c]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv("data/processed/panel.csv", dtype={"geoid": str})
    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "boroname", "geometry"]]
    pop = panel.drop_duplicates("geoid").set_index("geoid")["pop"]
    tracts = tracts[tracts.geoid.map(pop).fillna(0) >= 100].reset_index(drop=True)
    tracts["geometry"] = tracts.geometry.simplify(0.0002)
    p = panel[panel.year.isin(YEARS)].copy()
    p["pop"] = p.geoid.map(pop)
    p["felony_rate"] = 1000 * p.felony_complaints / p["pop"]
    p["shoot_rate"] = 1000 * p.shootings / p["pop"]

    feats = []
    for i, (g, b, geom) in enumerate(zip(tracts.geoid, tracts.boroname, tracts.geometry, strict=True)):
        m = mapping(geom)
        feats.append({"type": "Feature", "id": i, "properties": {"i": i, "geoid": g, "borough": b},
                      "geometry": {"type": m["type"], "coordinates": rnd(json.loads(json.dumps(m["coordinates"])))}})
    (OUT / "tracts.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats},
                                                   separators=(",", ":")), encoding="utf-8")

    values = {"years": YEARS, "vars": {}}
    for v, (label, unit) in VARS.items():
        w = p.pivot(index="geoid", columns="year", values=v).reindex(tracts.geoid)[YEARS]
        arr = w.values
        finite = arr[np.isfinite(arr)]
        if (finite == 0).mean() > 0.3:
            br = [0.0] + [float(q) for q in np.quantile(finite[finite > 0], [0.25, 0.5, 0.75, 0.92])]
        else:
            br = [float(q) for q in np.quantile(finite, [0.17, 0.33, 0.5, 0.67, 0.83])]
        values["vars"][v] = {
            "label": label, "unit": unit, "breaks": [round(x, 3) for x in br],
            "values": [[None if not np.isfinite(x) else round(float(x), 3) for x in row] for row in arr],
        }
    (OUT / "values.json").write_text(json.dumps(values, separators=(",", ":")), encoding="utf-8")

    geo = tracts[["geoid", "boroname"]].rename(columns={"boroname": "borough"})
    b = p.merge(geo, on="geoid")
    b = b[b.geoid.isin(tracts.geoid)]
    g = b.groupby(["borough", "year"]).agg(felony=("felony_complaints", "sum"), shootings=("shootings", "sum"),
                                           pop=("pop", "sum")).reset_index()
    g["felony_per_1000"] = (1000 * g.felony / g["pop"]).round(3)
    g["shootings_per_1000"] = (1000 * g.shootings / g["pop"]).round(4)
    g.to_csv(OUT / "boroughs.csv", index=False)

    rows = []
    for outcome in ("felony_complaints", "shootings"):
        r = pd.read_csv(f"output/robustness_{outcome}.csv")
        r = r[r.variant.str.startswith(("STRONGER", "PLACEBO"))].assign(family="optical, light, embeddings")
        rr = pd.read_csv(f"output/radar_models_{outcome}.csv").assign(family="radar")
        rr = rr[rr.variant.isin(["strong baseline, radar level", "PLACEBO: radar shuffled across tracts"])]
        rows.append(pd.concat([r, rr]).assign(outcome=outcome))
    gains = pd.concat(rows)[["outcome", "family", "variant", "features", "cv_gain_pct", "fwd_gain_pct"]]
    gains.round(2).to_csv(OUT / "gains.csv", index=False)
    pd.read_csv("output/radar_probe.csv").round(4).to_csv(OUT / "radar.csv", index=False)
    print({f.name: f.stat().st_size for f in OUT.iterdir()})


if __name__ == "__main__":
    main()
