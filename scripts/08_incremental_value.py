"""Incremental-value test.

Question: do satellite-derived features, measured in year t-1, improve out-of-sample prediction of
year-t tract outcomes beyond last year's outcome and census covariates?

Models (Poisson GLM, log population offset, year and county effects):
  base      lag outcome + ACS covariates
  +env      base + vegetation and land surface temperature
  +light    base + night lights
  +embed    base + AlphaEarth principal components
  +all      base + all of the above

Validation: spatial-block cross-validation (tracts grouped into spatial clusters, whole clusters held
out), and a forward split (train on targets up to 2023, test on 2024 and 2025 targets).
Metric: out-of-sample Poisson deviance per observation; lower is better. The improvement over base is
reported with a tract-level bootstrap interval.

Usage: python scripts/08_incremental_value.py [outcome]    (default felony_complaints)
"""
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.cluster import KMeans

warnings.filterwarnings("ignore")
OUT = Path("output")
ACS = ["median_income", "median_age", "poverty_rate", "renter_share", "bachelors_plus"]
ENV = ["ndvi_mean_lag1", "green_share_lag1", "lst_mean_lag1"]
LIGHT = ["ntl_lag1"]
EMBED = [f"aef_pc{i}_lag1" for i in range(1, 9)]
N_FOLDS = 5
N_BOOT = 1000


def design(df, cols, mean_std):
    X = (df[cols] - mean_std[0][cols]) / mean_std[1][cols]
    X = pd.concat([X, pd.get_dummies(df["year"], prefix="y", drop_first=True, dtype=float),
                   pd.get_dummies(df["county"], prefix="c", drop_first=True, dtype=float)], axis=1)
    return sm.add_constant(X, has_constant="add")


def fit_predict(train, test, cols, outcome):
    ms = (train[cols].mean(), train[cols].std().replace(0, 1))
    Xtr, Xte = design(train, cols, ms), design(test, cols, ms)
    Xte = Xte.reindex(columns=Xtr.columns, fill_value=0.0)
    model = sm.GLM(train[outcome], Xtr, family=sm.families.Poisson(), offset=np.log(train["pop"])).fit(maxiter=100)
    mu = model.predict(Xte, offset=np.log(test["pop"]))
    return np.asarray(mu)


def deviance(y, mu):
    y, mu = np.asarray(y, float), np.maximum(np.asarray(mu, float), 1e-9)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(y > 0, y * np.log(y / mu), 0.0)
    return 2 * (term - (y - mu))


def spatial_clusters(panel):
    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "geometry"]].to_crs(32618)
    c = tracts.geometry.centroid
    km = KMeans(n_clusters=40, random_state=0, n_init=10).fit(np.c_[c.x, c.y])
    return dict(zip(tracts["geoid"], km.labels_, strict=True))


def main():
    outcome = sys.argv[1] if len(sys.argv) > 1 else "felony_complaints"
    panel = pd.read_csv("data/processed/panel.csv", dtype={"geoid": str, "county": str})
    base_cols = [f"{outcome}_lag1"] + ACS
    all_img = ENV + LIGHT + EMBED
    sets = {"base": base_cols, "+env": base_cols + ENV, "+light": base_cols + LIGHT,
            "+embed": base_cols + EMBED, "+all": base_cols + all_img}
    need = base_cols + all_img + [outcome, "pop"]
    df = panel.dropna(subset=need)
    df = df[(df["pop"] >= 100) & (df["year"] >= 2018)].copy()
    df["cluster"] = df["geoid"].map(spatial_clusters(panel))
    print(f"outcome={outcome} rows={len(df)} tracts={df.geoid.nunique()} years={sorted(df.year.unique())}")

    # Spatial-block cross-validation
    rng = np.random.default_rng(0)
    clusters = df["cluster"].unique()
    rng.shuffle(clusters)
    fold_of = {c: i % N_FOLDS for i, c in enumerate(clusters)}
    folds = df["cluster"].map(fold_of).values
    dev = {k: np.zeros(len(df)) for k in sets}
    for f in range(N_FOLDS):
        tr, te = df[folds != f], df[folds == f]
        for k, cols in sets.items():
            dev[k][folds == f] = deviance(te[outcome], fit_predict(tr, te, cols, outcome))

    # Forward split
    fwd_mask = (df["year"] >= 2024).values
    fdev = {k: deviance(df.loc[fwd_mask, outcome], fit_predict(df[~fwd_mask], df[fwd_mask], cols, outcome))
            for k, cols in sets.items()}

    rows = []
    tract_ids = df["geoid"].values
    codes = pd.factorize(tract_ids)[0]
    for label, d, idx in (("spatial-block CV", dev, np.arange(len(df))), ("forward 2024-25", fdev, np.where(fwd_mask)[0])):
        by_tract = {k: np.bincount(codes[idx], weights=v, minlength=codes.max() + 1) for k, v in d.items()}
        n_tract = np.bincount(codes[idx], minlength=codes.max() + 1)
        present = n_tract > 0
        for k in sets:
            if k == "base":
                continue
            diff = (by_tract["base"] - by_tract[k])[present]
            n = n_tract[present]
            gain = diff.sum() / n.sum()
            boots = []
            m = present.sum()
            for _ in range(N_BOOT):
                s = rng.integers(0, m, m)
                boots.append(diff[s].sum() / n[s].sum())
            lo, hi = np.percentile(boots, [2.5, 97.5])
            rows.append({"validation": label, "model": k, "base_dev": by_tract["base"][present].sum() / n.sum(),
                         "gain_per_obs": gain, "ci_low": lo, "ci_high": hi,
                         "gain_pct": 100 * gain / (by_tract["base"][present].sum() / n.sum())})
    res = pd.DataFrame(rows)
    OUT.mkdir(exist_ok=True)
    res.to_csv(OUT / f"incremental_{outcome}.csv", index=False)
    print(res.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
