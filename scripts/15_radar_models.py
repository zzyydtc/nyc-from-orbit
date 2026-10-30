"""Do Sentinel-1 radar features add predictive value beyond the strong baseline?

Reuses the strong baseline and validation of 09_robustness.py (Poisson, spatial-block CV and 2024-25 forward test).
Sets: radar level (VV, VH of the previous summer), radar level plus one-year change, and all imagery with radar.
The change feature needs two prior years, so the change comparison runs on target years 2020 onward, with its own
baseline on the same rows. A placebo shuffles the radar columns across tracts within each year.

Usage: python scripts/15_radar_models.py [outcome]
Writes output/radar_models_<outcome>.csv.
"""
import sys
import warnings
from importlib import import_module
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
m8 = import_module("08_incremental_value")
m9 = import_module("09_robustness")
RADAR = ["vv_db_lag1", "vh_db_lag1"]
RADAR_CHG = ["vv_change_lag1"]


def main():
    outcome = sys.argv[1] if len(sys.argv) > 1 else "felony_complaints"
    other = "shootings" if outcome == "felony_complaints" else "felony_complaints"
    panel = pd.read_csv("data/processed/panel.csv", dtype={"geoid": str, "county": str})
    base = [f"{outcome}_lag1"] + m8.ACS
    need = base + m8.ENV + m8.LIGHT + m8.EMBED + RADAR + [outcome, "pop", f"{other}_lag1"]
    df = panel.dropna(subset=need)
    df = df[(df["pop"] >= 100) & (df["year"] >= 2018)].copy()
    df["lag_log"] = np.log1p(df[f"{outcome}_lag1"])
    df["other_lag_log"] = np.log1p(df[f"{other}_lag1"])
    df["log_pop"] = np.log(df["pop"])
    df["log_income"] = np.log(df["median_income"].clip(lower=1))
    sb = ["lag_log", "other_lag_log", "log_pop", "log_income", "median_age", "poverty_rate", "renter_share",
          "bachelors_plus"]
    prior = sb + m8.ENV + m8.LIGHT + m8.EMBED

    placebo = df.copy()
    rng = np.random.default_rng(1)
    for _, idx in placebo.groupby("year").groups.items():
        perm = rng.permutation(len(idx))
        placebo.loc[idx, RADAR + RADAR_CHG] = placebo.loc[idx, RADAR + RADAR_CHG].values[perm]

    levels = {"base": sb, "+radar": sb + RADAR, "+all optical, light, embed": prior,
              "+all with radar": prior + RADAR}
    chg_sets = {"base": sb, "+radar level": sb + RADAR, "+radar level and change": sb + RADAR + RADAR_CHG}
    chg_rows = df.dropna(subset=RADAR_CHG)
    placebo_chg = placebo.loc[chg_rows.index].dropna(subset=RADAR_CHG)

    runs = [("strong baseline, radar level", df, levels, {}),
            ("strong baseline, radar level, negative binomial", df, levels, {"model": "nb"}),
            ("strong baseline, radar level, other fold seed", df, levels, {"seed": 1}),
            ("target years 2020 on, radar level and change", chg_rows, chg_sets, {}),
            ("PLACEBO: radar shuffled across tracts", placebo, levels, {}),
            ("PLACEBO: radar level and change shuffled", placebo_chg, chg_sets, {})]
    records = []
    for label, data, sets, kw in runs:
        res = m9.run(data, sets, outcome, **kw)
        for name, (cv, fw) in res.items():
            records.append({"outcome": outcome, "variant": label, "features": name, "cv_gain_pct": cv,
                            "fwd_gain_pct": fw})
        print(label, {k: (round(v[0], 1), round(v[1], 1)) for k, v in res.items()}, flush=True)
    Path("output").mkdir(exist_ok=True)
    pd.DataFrame(records).to_csv(f"output/radar_models_{outcome}.csv", index=False)


if __name__ == "__main__":
    main()
