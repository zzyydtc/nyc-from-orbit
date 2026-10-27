"""Phase 0 probe: check that each data layer is reachable and usable for NYC tracts.

Prints a compact report to stdout. No raw data is committed; samples go to data/probe/.
"""
import json
import sys
from pathlib import Path

import requests

OUT = Path("data/probe")
OUT.mkdir(parents=True, exist_ok=True)
S = requests.Session()
S.headers["User-Agent"] = "nyc-from-orbit-probe/0.1"


def section(name):
    print(f"\n=== {name} ===")


def soda_year_counts(dataset, date_col):
    url = f"https://data.cityofnewyork.us/resource/{dataset}.json"
    q = {"$select": f"date_extract_y({date_col}) as y, count(*) as n", "$group": "y", "$order": "y"}
    r = S.get(url, params=q, timeout=60)
    r.raise_for_status()
    return r.json()


def probe_outcomes():
    section("NYPD outcomes (NYC Open Data)")
    for label, ds, col in [
        ("shooting incidents (historic)", "833y-fsy8", "occur_date"),
        ("complaints (historic)", "qgea-i56i", "cmplnt_fr_dt"),
        ("complaints (current year)", "5uac-w243", "cmplnt_fr_dt"),
    ]:
        try:
            rows = soda_year_counts(ds, col)
            print(label, {r["y"]: int(r["n"]) for r in rows if "y" in r})
        except Exception as e:  # noqa: BLE001
            print(label, "FAILED", repr(e)[:200])


def probe_tracts():
    section("Census tracts (2020, NYC)")
    url = "https://data.cityofnewyork.us/resource/63ge-mke6.geojson?$limit=5000"
    try:
        r = S.get(url, timeout=120)
        r.raise_for_status()
        gj = r.json()
        feats = gj["features"]
        print("tract features:", len(feats))
        print("properties:", list(feats[0]["properties"].keys()))
        (OUT / "tracts2020.geojson").write_text(json.dumps(gj))
    except Exception as e:  # noqa: BLE001
        print("FAILED", repr(e)[:200])


def probe_acs():
    section("ACS 5-year (Census API, no key)")
    for yr in (2018, 2023):
        url = f"https://api.census.gov/data/{yr}/acs/acs5"
        q = {"get": "NAME,B01003_001E,B19013_001E", "for": "tract:*", "in": "state:36 county:047"}
        try:
            r = S.get(url, params=q, timeout=60)
            print(yr, r.status_code, "rows:", len(r.json()) - 1 if r.ok else r.text[:100])
        except Exception as e:  # noqa: BLE001
            print(yr, "FAILED", repr(e)[:200])


def probe_stac():
    section("Planetary Computer STAC")
    from pystac_client import Client

    cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    bbox = [-73.99, 40.75, -73.98, 40.76]  # ~1 km box; borough-sized boxes time out
    for coll, extra in [
        ("sentinel-2-l2a", {"query": {"eo:cloud_cover": {"lt": 20}}}),
        ("landsat-c2-l2", {"query": {"eo:cloud_cover": {"lt": 30}}}),
        ("sentinel-1-rtc", {}),
        ("sentinel-1-grd", {}),
    ]:
        for yr in (2019, 2024):
            try:
                dt = f"{yr}-06-01/{yr}-08-31"
                s = cat.search(collections=[coll], bbox=bbox, datetime=dt, max_items=100, **extra)
                n = len(list(s.items()))
                print(f"{coll} {yr}: {n} items")
            except Exception as e:  # noqa: BLE001
                print(f"{coll} {yr}: FAILED {repr(e)[:120]}")
    cols = [c.id for c in cat.get_collections()]
    keys = ("viirs", "night", "embed", "alpha", "black")
    print("collections mentioning night/viirs/embed:", [c for c in cols if any(k in c for k in keys)])


def probe_alphaearth():
    section("AlphaEarth embeddings (public bucket check)")
    for url in [
        "https://source.coop/tge-labs/aef",
        "https://data.source.coop/tge-labs/aef/",
        "https://storage.googleapis.com/earthengine-public/",
    ]:
        try:
            r = S.get(url, timeout=30)
            print(url, r.status_code, len(r.content))
        except Exception as e:  # noqa: BLE001
            print(url, "FAILED", repr(e)[:120])


def main():
    steps = {
        "outcomes": probe_outcomes,
        "tracts": probe_tracts,
        "acs": probe_acs,
        "stac": probe_stac,
        "alphaearth": probe_alphaearth,
    }
    only = sys.argv[1:] or list(steps)
    for k in only:
        steps[k]()


if __name__ == "__main__":
    main()
