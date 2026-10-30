"""New-building and demolition job filings per tract and year, from NYC DOB open data.

Legacy DOB Job Application Filings (ic3t-wcy2) and DOB NOW: Build (w9ak-ipjd) are both read for 2018 onward; a job lives in only one system, so the union has no double count.
Writes data/interim/dob_tract_year.csv with columns geoid, year, new_buildings, demolitions.
"""
import io

import geopandas as gpd
import pandas as pd
import requests

BASE = "https://data.cityofnewyork.us/resource"


def soda(dataset, params):
    rows, offset = [], 0
    while True:
        r = requests.get(f"{BASE}/{dataset}.csv", params={**params, "$limit": 50000, "$offset": offset}, timeout=180)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text), dtype=str)
        rows.append(df)
        if len(df) < 50000:
            return pd.concat(rows, ignore_index=True)
        offset += 50000


def legacy():
    df = soda("ic3t-wcy2", {
        "$select": "job_type,pre__filing_date,gis_latitude,gis_longitude",
        "$where": "job_type in ('NB','DM') AND gis_latitude IS NOT NULL",
        "$order": ":id",
    })
    df["date"] = pd.to_datetime(df.pre__filing_date, format="%m/%d/%Y", errors="coerce")
    df = df[df.date >= "2018-01-01"]
    return df.assign(kind=df.job_type.map({"NB": "new_buildings", "DM": "demolitions"}),
                     lat=df.gis_latitude.astype(float), lon=df.gis_longitude.astype(float))[["date", "kind", "lat", "lon"]]


def now():
    df = soda("w9ak-ipjd", {
        "$select": "job_type,filing_date,latitude,longitude",
        "$where": "job_type in ('New Building','Full Demolition') AND filing_date >= '2020-01-01T00:00:00' "
                  "AND latitude IS NOT NULL",
        "$order": ":id",
    })
    df["date"] = pd.to_datetime(df.filing_date, errors="coerce")
    return df.assign(kind=df.job_type.map({"New Building": "new_buildings", "Full Demolition": "demolitions"}),
                     lat=df.latitude.astype(float), lon=df.longitude.astype(float))[["date", "kind", "lat", "lon"]]


def main():
    jobs = pd.concat([legacy(), now()], ignore_index=True).dropna()
    jobs = jobs[(jobs.lat.between(40.4, 41.0)) & (jobs.lon.between(-74.4, -73.6))]
    pts = gpd.GeoDataFrame(jobs, geometry=gpd.points_from_xy(jobs.lon, jobs.lat), crs=4326)
    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "geometry"]].to_crs(4326)
    j = gpd.sjoin(pts, tracts, how="inner", predicate="within")
    j["year"] = j.date.dt.year
    out = j.groupby(["geoid", "year", "kind"]).size().unstack("kind", fill_value=0).reset_index()
    for c in ("new_buildings", "demolitions"):
        if c not in out:
            out[c] = 0
    out.to_csv("data/interim/dob_tract_year.csv", index=False)
    print(out.groupby("year")[["new_buildings", "demolitions"]].sum())


if __name__ == "__main__":
    main()
