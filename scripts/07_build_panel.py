"""Assemble the tract-year panel from the interim files.

Writes data/processed/panel.csv with outcomes, static ACS covariates, imagery features, and
one-year lags. Imagery columns are for the same year; the analysis lags them explicitly.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

INTERIM = Path("data/interim")
OUT = Path("data/processed")
N_PCS = 8


def stack(prefix):
    frames = [pd.read_csv(p, dtype={"geoid": str}) for p in sorted(INTERIM.glob(f"{prefix}_*.csv"))]
    return pd.concat(frames, ignore_index=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out = pd.read_csv(INTERIM / "outcomes_tract_year.csv", dtype={"geoid": str})
    acs = pd.read_csv(INTERIM / "acs2023.csv", dtype={"geoid": str})
    s2 = stack("s2")[["geoid", "year", "ndvi_mean", "ndvi_p90", "green_share"]]
    lst = stack("lst")[["geoid", "year", "lst_mean", "lst_p90"]]
    viirs = stack("viirs")[["geoid", "year", "ntl"]]
    s1 = stack("s1")[["geoid", "year", "vv_db", "vh_db"]]
    aef = stack("aef")
    a_cols = [f"a{b:02d}" for b in range(64)]
    ok = aef[a_cols].notna().all(axis=1)
    pca = PCA(n_components=N_PCS, random_state=0).fit(aef.loc[ok, a_cols])
    print("AEF PCA explained variance:", pca.explained_variance_ratio_.round(3).tolist())
    pcs = pd.DataFrame(pca.transform(aef[a_cols].fillna(aef[a_cols].mean())), columns=[f"aef_pc{i + 1}" for i in range(N_PCS)])
    pcs[["geoid", "year"]] = aef[["geoid", "year"]].values
    pcs.loc[~ok.values, [c for c in pcs if c.startswith("aef_pc")]] = np.nan

    panel = out.merge(acs, on="geoid", how="left")
    for df in (s2, lst, viirs, s1, pcs):
        panel = panel.merge(df, on=["geoid", "year"], how="left")
    panel["county"] = panel["geoid"].str[2:5]
    panel = panel.sort_values(["geoid", "year"])
    for col in ("felony_complaints", "shootings"):
        panel[f"{col}_lag1"] = panel.groupby("geoid")[col].shift(1)
    panel["vv_change"] = panel.groupby("geoid")["vv_db"].diff()
    img = ["ndvi_mean", "ndvi_p90", "green_share", "lst_mean", "lst_p90", "ntl", "vv_db", "vh_db", "vv_change"] + [
        c for c in pcs if c.startswith("aef_pc")]
    for col in img:
        panel[f"{col}_lag1"] = panel.groupby("geoid")[col].shift(1)
    panel.to_csv(OUT / "panel.csv", index=False)
    print(panel.shape, "missing share by column:")
    print(panel.isna().mean().round(3)[lambda s: s > 0].to_string())


if __name__ == "__main__":
    main()
