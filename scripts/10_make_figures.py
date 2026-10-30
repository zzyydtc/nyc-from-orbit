"""Make the figures used in docs/RESULTS.md. Output goes to docs/figures/."""
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FIG = Path("docs/figures")
YEAR = 2024


def maps(panel):
    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "geometry"]].to_crs(32618)
    d = panel[panel.year == YEAR].copy()
    d["felony_per_1000"] = np.where(d["pop"] >= 500, 1000 * d["felony_complaints"] / d["pop"], np.nan)
    g = tracts.merge(d, on="geoid", how="left")
    layers = [
        ("felony_per_1000", "Felony complaints per 1,000 residents", "magma", (0, 150)),
        ("shootings", "Shooting incidents", "magma", (0, 8)),
        ("ndvi_mean", "Summer vegetation index (NDVI)", "YlGn", None),
        ("lst_mean", "Summer land surface temperature (C)", "inferno", None),
        ("ntl", "Night-light radiance (nW/cm2/sr)", "cividis", (0, 150)),
        ("aef_pc1", "AlphaEarth embedding, first component", "viridis", None),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    for ax, (col, title, cmap, lim) in zip(axes.ravel(), layers, strict=True):
        kw = {"vmin": lim[0], "vmax": lim[1]} if lim else {}
        g.plot(column=col, ax=ax, cmap=cmap, linewidth=0, legend=True, missing_kwds={"color": "#dddddd"},
               legend_kwds={"shrink": 0.6}, **kw)
        ax.set_title(title, fontsize=11)
        ax.set_axis_off()
    fig.suptitle(f"NYC census tracts, {YEAR}", fontsize=14)
    fig.tight_layout()
    fig.savefig(FIG / "maps_2024.png", dpi=110)
    plt.close(fig)


def gains():
    rows = []
    for outcome in ("felony_complaints", "shootings"):
        r = pd.read_csv(f"output/robustness_{outcome}.csv")
        r = r[r.variant.str.startswith("STRONGER BASELINE (")]
        r["outcome"] = outcome
        rows.append(r)
    r = pd.concat(rows)
    feats = ["+env", "+light", "+embed", "+all"]
    labels = ["Vegetation +\ntemperature", "Night lights", "AlphaEarth\nembeddings", "All"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, outcome, title in zip(axes, ("felony_complaints", "shootings"), ("Felony complaints", "Shootings"), strict=True):
        s = r[r.outcome == outcome].set_index("features").loc[feats]
        x = np.arange(len(feats))
        ax.bar(x - 0.19, s["cv_gain_pct"], 0.38, label="Spatial-block CV", color="#4c78a8")
        ax.bar(x + 0.19, s["fwd_gain_pct"], 0.38, label="Forward test 2024-25", color="#f58518")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(x, labels, fontsize=9)
        ax.set_title(title)
    axes[0].set_ylabel("Deviance reduction vs. strong baseline (%)")
    axes[0].legend(frameon=False)
    fig.suptitle("Incremental value of satellite features over last year's outcome and census covariates")
    fig.tight_layout()
    fig.savefig(FIG / "incremental_gain.png", dpi=110)
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv("data/processed/panel.csv", dtype={"geoid": str})
    maps(panel)
    gains()
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
