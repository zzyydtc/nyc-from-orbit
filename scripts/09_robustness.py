"""Robustness checks for the incremental-value test.

Reruns the comparison under alternative choices and prints the percent deviance gain over the base
model for each feature set, under spatial-block CV ("cv") and the forward split ("fwd").
A placebo variant shuffles the imagery features across tracts within each year; any real gain there
would indicate a pipeline problem, not a signal.

Usage: python scripts/09_robustness.py [outcome]
"""
import sys
import warnings
from importlib import import_module
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.cluster import KMeans

warnings.filterwarnings("ignore")
m8 = import_module("08_incremental_value")
OUT = Path("output")


def fit_predict(train, test, cols, outcome, model, ridge=0.0, nb_alpha=None):
    ms = (train[cols].mean(), train[cols].std().replace(0, 1))
    Xtr, Xte = m8.design(train, cols, ms), m8.design(test, cols, ms)
    Xte = Xte.reindex(columns=Xtr.columns, fill_value=0.0)
    off_tr, off_te = np.log(train["pop"]), np.log(test["pop"])
    family = sm.families.NegativeBinomial(alpha=nb_alpha) if model == "nb" else sm.families.Poisson()
    glm = sm.GLM(train[outcome], Xtr, family=family, offset=off_tr)
    if ridge > 0:
        img = set(m8.ENV + m8.LIGHT + m8.EMBED)
        pen = np.array([ridge if c in img else 0.0 for c in Xtr.columns])
        res = glm.fit_regularized(alpha=pen, L1_wt=0.0, maxiter=200)
        return np.exp(np.asarray(Xte) @ np.asarray(res.params) + off_te)
    res = glm.fit(maxiter=100)
    return np.asarray(res.predict(Xte, offset=off_te))


def clusters_for(n, seed):
    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "geometry"]].to_crs(32618)
    c = tracts.geometry.centroid
    km = KMeans(n_clusters=n, random_state=seed, n_init=10).fit(np.c_[c.x, c.y])
    return dict(zip(tracts["geoid"], km.labels_, strict=True))


def loss(y, mu, metric):
    if metric == "log_se":
        return (np.log1p(np.asarray(y, float)) - np.log1p(np.asarray(mu, float))) ** 2
    return m8.deviance(y, mu)


def run(df, sets, outcome, n_clusters=40, seed=0, model="poisson", ridge=0.0, metric="deviance", trim=False):
    df = df.copy()
    df["cluster"] = df["geoid"].map(clusters_for(n_clusters, seed))
    nb_alpha = None
    if model == "nb":
        mu = fit_predict(df, df, sets["base"], outcome, "poisson")
        nb_alpha = max(float((((df[outcome] - mu) ** 2 - mu) / mu**2).mean()), 0.01)
    cl = df["cluster"].unique()
    np.random.default_rng(seed).shuffle(cl)
    fold_of = {c: i % m8.N_FOLDS for i, c in enumerate(cl)}
    folds = df["cluster"].map(fold_of).values
    fwd = (df["year"] >= 2024).values
    keep = np.ones(len(df), bool)
    if trim:
        tot = df.groupby("geoid")[outcome].transform("sum")
        keep = (tot <= tot.quantile(0.99)).values
    out = {}
    for name, cols in sets.items():
        l_cv = np.zeros(len(df))
        for f in range(m8.N_FOLDS):
            tr, te = df[(folds != f) & keep], df[folds == f]
            l_cv[folds == f] = loss(te[outcome], fit_predict(tr, te, cols, outcome, model, ridge, nb_alpha), metric)
        tr, te = df[~fwd & keep], df[fwd]
        l_fw = loss(te[outcome], fit_predict(tr, te, cols, outcome, model, ridge, nb_alpha), metric)
        out[name] = (l_cv[keep].mean(), l_fw[keep[fwd]].mean())
    rows = {}
    for name in sets:
        if name == "base":
            continue
        rows[name] = (100 * (1 - out[name][0] / out["base"][0]), 100 * (1 - out[name][1] / out["base"][1]))
    return rows


def main():
    outcome = sys.argv[1] if len(sys.argv) > 1 else "felony_complaints"
    panel = pd.read_csv("data/processed/panel.csv", dtype={"geoid": str, "county": str})
    base = [f"{outcome}_lag1"] + m8.ACS
    sets = {"base": base, "+env": base + m8.ENV, "+light": base + m8.LIGHT, "+embed": base + m8.EMBED,
            "+all": base + m8.ENV + m8.LIGHT + m8.EMBED}
    other_lag = "shootings_lag1" if outcome == "felony_complaints" else "felony_complaints_lag1"
    need = base + m8.ENV + m8.LIGHT + m8.EMBED + [outcome, "pop", other_lag]
    df = panel.dropna(subset=need)
    df = df[(df["pop"] >= 100) & (df["year"] >= 2018)].copy()

    img_cols = m8.ENV + m8.LIGHT + m8.EMBED
    placebo = df.copy()
    rng = np.random.default_rng(1)
    for _, idx in placebo.groupby("year").groups.items():
        perm = rng.permutation(len(idx))
        placebo.loc[idx, img_cols] = placebo.loc[idx, img_cols].values[perm]

    # Stronger baseline: log-transformed lag and skewed covariates, plus lag of the other outcome.
    strong = df.copy()
    other = "shootings" if outcome == "felony_complaints" else "felony_complaints"
    strong["lag_log"] = np.log1p(strong[f"{outcome}_lag1"])
    strong["other_lag_log"] = np.log1p(strong[f"{other}_lag1"])
    strong["log_pop"] = np.log(strong["pop"])
    strong["log_income"] = np.log(strong["median_income"].clip(lower=1))
    strong_base = ["lag_log", "other_lag_log", "log_pop", "log_income", "median_age", "poverty_rate",
                   "renter_share", "bachelors_plus"]
    strong_sets = {"base": strong_base, "+env": strong_base + m8.ENV, "+light": strong_base + m8.LIGHT,
                   "+embed": strong_base + m8.EMBED, "+all": strong_base + m8.ENV + m8.LIGHT + m8.EMBED}

    variants = [
        ("STRONGER BASELINE (log lag, both outcomes, Poisson)", strong, {"sets": strong_sets}),
        ("STRONGER BASELINE, negative binomial", strong, {"sets": strong_sets, "model": "nb"}),
        ("STRONGER BASELINE, drop top 1% tracts", strong, {"sets": strong_sets, "trim": True}),
        ("reference (Poisson, 40 clusters, seed 0)", df, {}),
        ("different folds (seed 1)", df, {"seed": 1}),
        ("different folds (seed 2)", df, {"seed": 2}),
        ("20 spatial clusters", df, {"n_clusters": 20}),
        ("80 spatial clusters", df, {"n_clusters": 80}),
        ("negative binomial", df, {"model": "nb"}),
        ("ridge penalty on imagery (0.05)", df, {"ridge": 0.05}),
        ("log-scale squared error", df, {"metric": "log_se"}),
        ("drop top 1% tracts by total", df, {"trim": True}),
        ("drop target years 2020-2021", df[~df["year"].isin([2020, 2021])], {}),
        ("PLACEBO: imagery shuffled across tracts", placebo, {}),
    ]
    records = []
    for label, data, kw in variants:
        kw = dict(kw)
        res = run(data, kw.pop("sets", sets), outcome, **kw)
        for model_name, (cv, fw) in res.items():
            records.append({"variant": label, "features": model_name, "cv_gain_pct": cv, "fwd_gain_pct": fw})
        print(label, {k: (round(v[0], 1), round(v[1], 1)) for k, v in res.items()}, flush=True)
    OUT.mkdir(exist_ok=True)
    pd.DataFrame(records).to_csv(OUT / f"robustness_{outcome}.csv", index=False)


if __name__ == "__main__":
    main()
