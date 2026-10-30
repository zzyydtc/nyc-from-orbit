"""Export flat tables for the Power BI report to data/processed/powerbi/.

Tables: tract_year.csv (fact), tract_geo.csv (tract attributes with centroid), results.csv (model gains),
and tracts.geojson for a map visual.
"""
from pathlib import Path

import geopandas as gpd
import pandas as pd

OUT = Path("data/processed/powerbi")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv("data/processed/panel.csv", dtype={"geoid": str})
    cols = ["geoid", "year", "felony_complaints", "shootings", "ndvi_mean", "green_share", "lst_mean", "ntl",
            "aef_pc1", "aef_pc2"]
    panel[cols].to_csv(OUT / "tract_year.csv", index=False)

    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "boroname", "geometry"]]
    acs = panel.drop_duplicates("geoid")[["geoid", "pop", "median_income", "median_age", "poverty_rate",
                                         "renter_share", "bachelors_plus"]]
    cent = tracts.to_crs(32618).geometry.centroid.to_crs(4326)
    geo = tracts[["geoid", "boroname"]].assign(lon=cent.x.values, lat=cent.y.values).merge(acs, on="geoid", how="left")
    geo.to_csv(OUT / "tract_geo.csv", index=False)
    tracts.assign(geometry=tracts.geometry.simplify(0.0001)).to_file(OUT / "tracts.geojson", driver="GeoJSON")

    res = []
    for outcome in ("felony_complaints", "shootings"):
        r = pd.read_csv(f"output/robustness_{outcome}.csv")
        r.insert(0, "outcome", outcome)
        res.append(r)
    pd.concat(res).to_csv(OUT / "results.csv", index=False)
    print({p.name: p.stat().st_size for p in OUT.iterdir()})


if __name__ == "__main__":
    main()
