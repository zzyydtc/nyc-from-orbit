"""Probe: does Sentinel-1 summer backscatter change track new-building and demolition filings?

Run after 12_fetch_dob.py and 13_features_s1.py. Writes output/radar_probe.csv and prints a summary.
Two views: a long difference (2025 minus 2018 backscatter vs cumulative filings 2018-2023, which leaves time for
construction) and a tract-year panel (backscatter change t-1 to t vs filings in the two preceding years).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr

YEARS = range(2018, 2026)


def load():
    s1 = pd.concat([pd.read_csv(f"data/interim/s1_{y}.csv", dtype={"geoid": str}) for y in YEARS])
    dob = pd.read_csv("data/interim/dob_tract_year.csv", dtype={"geoid": str})
    panel = pd.read_csv("data/processed/panel.csv", dtype={"geoid": str})
    pop = panel.drop_duplicates("geoid").set_index("geoid")["pop"]
    return s1, dob, pop


def long_difference(s1, dob, pop):
    w = s1.pivot(index="geoid", columns="year", values="vv_db")
    d = pd.DataFrame({"d_vv": w[2025] - w[2018], "vv_2018": w[2018]})
    f = dob[dob.year.between(2018, 2023)].groupby("geoid")[["new_buildings", "demolitions"]].sum()
    d = d.join(f).fillna({"new_buildings": 0, "demolitions": 0}).join(pop).dropna()
    d["any_nb"] = (d.new_buildings > 0).astype(int)
    d["log_pop"] = np.log(d["pop"].clip(lower=1))
    rows = []
    for col in ("new_buildings", "demolitions"):
        rho, p = spearmanr(d[col], d.d_vv)
        rows.append({"view": "long_difference", "test": f"spearman d_vv vs {col}", "estimate": rho, "p": p, "n": len(d)})
    x = sm.add_constant(d[["new_buildings", "demolitions", "vv_2018", "log_pop"]])
    m = sm.OLS(d.d_vv, x).fit(cov_type="HC1")
    for c in ("new_buildings", "demolitions"):
        rows.append({"view": "long_difference", "test": f"ols d_vv ~ {c} (controls: vv_2018, log_pop), dB per filing",
                     "estimate": m.params[c], "p": m.pvalues[c], "n": int(m.nobs)})
    top = d[d.new_buildings >= d.new_buildings.quantile(0.95)]
    none = d[d.new_buildings == 0]
    rows.append({"view": "long_difference", "test": "mean d_vv, top-5% filings minus zero-filings tracts (dB)",
                 "estimate": top.d_vv.mean() - none.d_vv.mean(), "p": np.nan, "n": len(top)})
    return rows


def panel_view(s1, dob, pop):
    s = s1.sort_values(["geoid", "year"]).copy()
    s["d_vv"] = s.groupby("geoid").vv_db.diff()
    full = pd.MultiIndex.from_product([s.geoid.unique(), YEARS], names=["geoid", "year"]).to_frame(index=False)
    f = full.merge(dob, on=["geoid", "year"], how="left").fillna({"new_buildings": 0, "demolitions": 0})
    f = f.sort_values(["geoid", "year"])
    for c in ("new_buildings", "demolitions"):
        g = f.groupby("geoid")[c]
        f[f"{c}_prev2"] = g.shift(1) + g.shift(2)
    d = s.merge(f.drop(columns=["new_buildings", "demolitions"]), on=["geoid", "year"]).dropna(subset=["d_vv", "new_buildings_prev2"])
    d = d.join(pop, on="geoid").dropna()
    d["log_pop"] = np.log(d["pop"].clip(lower=1))
    rows = []
    x = sm.add_constant(pd.concat([d[["new_buildings_prev2", "demolitions_prev2", "log_pop"]],
                                   pd.get_dummies(d.year, prefix="y", drop_first=True).astype(float)], axis=1))
    m = sm.OLS(d.d_vv, x).fit(cov_type="cluster", cov_kwds={"groups": d.geoid})
    for c in ("new_buildings_prev2", "demolitions_prev2"):
        rows.append({"view": "panel", "test": f"ols d_vv ~ {c} (year effects, tract-clustered SE), dB per filing",
                     "estimate": m.params[c], "p": m.pvalues[c], "n": int(m.nobs)})
    return rows


def main():
    s1, dob, pop = load()
    rows = long_difference(s1, dob, pop) + panel_view(s1, dob, pop)
    out = pd.DataFrame(rows)
    Path("output").mkdir(exist_ok=True)
    out.to_csv("output/radar_probe.csv", index=False)
    pd.set_option("display.width", 200, "display.max_colwidth", 90)
    print(out.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
