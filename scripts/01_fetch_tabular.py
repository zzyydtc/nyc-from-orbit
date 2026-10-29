"""Fetch tabular inputs and build the tract-year outcome table.

Writes to data/raw and data/interim (both git-ignored):
  tracts2020.geojson, acs2023.csv, outcomes_tract_year.csv
"""
import os
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

RAW = Path("data/raw")
INTERIM = Path("data/interim")
YEARS = range(2018, 2026)
SODA = "https://data.cityofnewyork.us/resource/{}.json"
S = requests.Session()
S.headers["User-Agent"] = "nyc-from-orbit/0.1"

ACS_VARS = {
    "B01003_001E": "pop",
    "B19013_001E": "median_income",
    "B01002_001E": "median_age",
    "B17001_001E": "pov_universe",
    "B17001_002E": "pov_below",
    "B25003_001E": "tenure_total",
    "B25003_003E": "renter_occupied",
    "B15003_001E": "edu_total",
    "B15003_022E": "edu_bachelors",
    "B15003_023E": "edu_masters",
    "B15003_024E": "edu_prof",
    "B15003_025E": "edu_doctorate",
}
COUNTIES = {"005": "Bronx", "047": "Brooklyn", "061": "Manhattan", "081": "Queens", "085": "Staten Island"}


def fetch_tracts():
    path = RAW / "tracts2020.geojson"
    if not path.exists():
        r = S.get(SODA.format("63ge-mke6").replace(".json", ".geojson") + "?$limit=5000", timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)
    gdf = gpd.read_file(path)
    return gdf[["geoid", "boroname", "geometry"]].to_crs(4326)


def fetch_acs(year=2023):
    key = os.environ.get("CENSUS_API_KEY")
    if not key:
        sys.exit("CENSUS_API_KEY is not set")
    frames = []
    for county in COUNTIES:
        r = S.get(
            f"https://api.census.gov/data/{year}/acs/acs5",
            params={"get": ",".join(ACS_VARS), "for": "tract:*", "in": f"state:36 county:{county}", "key": key},
            timeout=60,
        )
        r.raise_for_status()
        rows = r.json()
        df = pd.DataFrame(rows[1:], columns=rows[0])
        df["geoid"] = df["state"] + df["county"] + df["tract"]
        frames.append(df)
    acs = pd.concat(frames).rename(columns=ACS_VARS)
    for c in ACS_VARS.values():
        acs[c] = pd.to_numeric(acs[c], errors="coerce").where(lambda s: s > -1)  # negatives are Census sentinels
    acs["poverty_rate"] = acs["pov_below"] / acs["pov_universe"]
    acs["renter_share"] = acs["renter_occupied"] / acs["tenure_total"]
    acs["bachelors_plus"] = acs[["edu_bachelors", "edu_masters", "edu_prof", "edu_doctorate"]].sum(axis=1) / acs["edu_total"]
    return acs[["geoid", "pop", "median_income", "median_age", "poverty_rate", "renter_share", "bachelors_plus"]]


def soda_points(dataset, date_col, where_extra, start, end, cols):
    """Page through a SODA dataset and return rows with coordinates."""
    out = []
    # Month-sized windows keep each query small; deep offset paging on the full table times out.
    for lo in pd.date_range(start, end, freq="MS"):
        hi = lo + pd.offsets.MonthBegin(1)
        where = f"{date_col} >= '{lo:%Y-%m-%d}T00:00:00' and {date_col} < '{hi:%Y-%m-%d}T00:00:00' and latitude is not null"
        if where_extra:
            where += f" and {where_extra}"
        for attempt in range(4):
            try:
                r = S.get(
                    SODA.format(dataset),
                    params={"$select": ",".join(cols), "$where": where, "$limit": 50000},
                    timeout=120,
                )
                r.raise_for_status()
                break
            except requests.RequestException:
                if attempt == 3:
                    raise
        rows = r.json()
        if len(rows) == 50000:
            raise RuntimeError(f"window {lo:%Y-%m} hit the page limit; split it further")
        out.extend(rows)
    return pd.DataFrame(out)


def to_tract_year(df, tracts, date_col, name):
    df = df.copy()
    df["year"] = pd.to_datetime(df[date_col]).dt.year
    lat, lon = pd.to_numeric(df["latitude"]), pd.to_numeric(df["longitude"])
    # The recent shooting extract has latitude and longitude swapped; NYC latitude is always positive.
    swapped = lat < 0
    lat, lon = lat.where(~swapped, lon), lon.where(~swapped, pd.to_numeric(df["latitude"]))
    pts = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(lon, lat), crs=4326)
    joined = gpd.sjoin(pts, tracts[["geoid", "geometry"]], how="inner", predicate="within")
    counts = joined.groupby(["geoid", "year"]).size().rename(name).reset_index()
    print(name, "points:", len(df), "matched to a tract:", len(joined))
    return counts


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    tracts = fetch_tracts()
    print("tracts:", len(tracts))
    acs = fetch_acs()
    acs.to_csv(INTERIM / "acs2023.csv", index=False)
    print("acs rows:", len(acs))

    felony = soda_points(
        "qgea-i56i", "cmplnt_fr_dt", "law_cat_cd='FELONY'", "2018-01-01", "2025-12-31",
        ["cmplnt_fr_dt", "latitude", "longitude"],
    )
    felony_c = to_tract_year(felony, tracts, "cmplnt_fr_dt", "felony_complaints")

    shoot_hist = soda_points("833y-fsy8", "occur_date", None, "2018-01-01", "2024-12-31",
                             ["occur_date", "latitude", "longitude"])
    shoot_ytd = soda_points("5ucz-vwe8", "occur_date", None, "2025-01-01", "2025-12-31",
                            ["occur_date", "latitude", "longitude"])
    shoot = pd.concat([shoot_hist, shoot_ytd])
    shoot_c = to_tract_year(shoot, tracts, "occur_date", "shootings")

    grid = pd.MultiIndex.from_product([tracts["geoid"], list(YEARS)], names=["geoid", "year"]).to_frame(index=False)
    panel = grid.merge(felony_c, how="left").merge(shoot_c, how="left").fillna({"felony_complaints": 0, "shootings": 0})
    panel.to_csv(INTERIM / "outcomes_tract_year.csv", index=False)
    print(panel.groupby("year")[["felony_complaints", "shootings"]].sum())


if __name__ == "__main__":
    main()
