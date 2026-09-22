"""
Brisbane River (Colmslie site) water-quality analysis.

Reads the raw monitoring-buoy CSV, cleans it, computes summary/seasonal/
diurnal statistics, and writes all figures used in the report to ../figures.

Usage:
    python analysis.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "brisbane_water_quality.csv"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

MEAS = [
    "Average Water Speed",
    "Average Water Direction",
    "Chlorophyll",
    "Temperature",
    "Dissolved Oxygen",
    "Dissolved Oxygen (%Saturation)",
    "pH",
    "Salinity",
    "Specific Conductance",
    "Turbidity",
]

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 10,
})


# ----------------------------------------------------------------------
# Load & clean
# ----------------------------------------------------------------------
def load() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"]).sort_values("Timestamp")
    # A small number of rows share a timestamp (logging quirk); keep the first.
    df = df.drop_duplicates(subset=["Timestamp"], keep="first")
    df = df.set_index("Timestamp")
    # Specific Conductance is ~perfectly collinear with Salinity (r = 1.00);
    # keep it in the raw frame but flag it as redundant for modelling.
    df["month"] = df.index.to_period("M")
    df["hour"] = df.index.hour
    return df


def summary(df: pd.DataFrame) -> pd.DataFrame:
    out = df[MEAS].describe().T[["count", "mean", "std", "min", "50%", "max"]]
    out["pct_missing"] = 100 * df[MEAS].isna().mean().values
    return out.round(3)


# ----------------------------------------------------------------------
# Figures
# ----------------------------------------------------------------------
def fig_timeseries(df: pd.DataFrame):
    cols = ["Temperature", "Dissolved Oxygen", "Salinity", "Turbidity"]
    daily = df[cols].resample("D").mean()
    fig, axes = plt.subplots(len(cols), 1, figsize=(11, 9), sharex=True)
    for ax, c in zip(axes, cols):
        ax.plot(daily.index, daily[c], lw=1.1)
        ax.set_ylabel(c, fontsize=9)
    axes[0].set_title("Daily-mean water quality — Brisbane River, Colmslie "
                      "(Aug 2023 – Jun 2024)")
    axes[-1].set_xlabel("Date")
    fig.savefig(FIG / "01_timeseries.png")
    plt.close(fig)


def fig_monthly(df: pd.DataFrame):
    cols = ["Temperature", "Dissolved Oxygen", "Salinity", "Turbidity"]
    m = df.groupby(df.index.to_period("M"))[cols].mean()
    m.index = m.index.to_timestamp()
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    for ax, c in zip(axes.ravel(), cols):
        ax.bar(m.index, m[c], width=20)
        ax.set_title(c)
        ax.tick_params(axis="x", rotation=45)
    fig.suptitle("Monthly means — seasonal cycle", y=1.02, fontsize=13)
    fig.savefig(FIG / "02_monthly_means.png")
    plt.close(fig)


def fig_corr(df: pd.DataFrame):
    cols = ["Temperature", "Dissolved Oxygen", "Dissolved Oxygen (%Saturation)",
            "pH", "Salinity", "Chlorophyll", "Turbidity",
            "Specific Conductance", "Average Water Speed"]
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(8.5, 7))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(cols, fontsize=8)
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                    fontsize=7,
                    color="white" if abs(corr.iloc[i, j]) > 0.55 else "black")
    fig.colorbar(im, fraction=0.046, pad=0.04, label="Pearson r")
    ax.set_title("Correlation between parameters")
    ax.grid(False)
    fig.savefig(FIG / "03_correlation.png")
    plt.close(fig)


def fig_diurnal(df: pd.DataFrame):
    h = df.groupby("hour")[["Dissolved Oxygen", "Chlorophyll"]].mean()
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.plot(h.index, h["Dissolved Oxygen"], "o-", color="tab:blue",
             label="Dissolved Oxygen")
    ax1.set_xlabel("Hour of day")
    ax1.set_ylabel("Dissolved Oxygen (mg/L)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax2 = ax1.twinx()
    ax2.plot(h.index, h["Chlorophyll"], "s--", color="tab:green",
             label="Chlorophyll")
    ax2.set_ylabel("Chlorophyll (µg/L)", color="tab:green")
    ax2.tick_params(axis="y", labelcolor="tab:green")
    ax2.grid(False)
    ax1.set_title("Diurnal cycle — photosynthesis / respiration signature")
    ax1.set_xticks(range(0, 24, 2))
    fig.savefig(FIG / "04_diurnal.png")
    plt.close(fig)


def fig_flow_rose(df: pd.DataFrame):
    d = df.dropna(subset=["Average Water Direction", "Average Water Speed"])
    theta = np.deg2rad(d["Average Water Direction"].values)
    bins = np.linspace(0, 2 * np.pi, 17)
    idx = np.digitize(theta, bins) - 1
    counts = np.array([(idx == i).sum() for i in range(16)])
    centres = (bins[:-1] + bins[1:]) / 2
    fig = plt.figure(figsize=(6.5, 6.5))
    ax = fig.add_subplot(111, projection="polar")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.bar(centres, counts, width=2 * np.pi / 16, alpha=0.8,
           edgecolor="k", color="tab:cyan")
    ax.set_title("Flow-direction distribution (tidal flood/ebb axis)")
    fig.savefig(FIG / "05_flow_rose.png")
    plt.close(fig)


# ----------------------------------------------------------------------
def main():
    df = load()
    print(f"Rows: {len(df):,}  |  {df.index.min()} -> {df.index.max()}")
    s = summary(df)
    print("\nSummary statistics:\n", s.to_string())
    s.to_csv(ROOT / "reports" / "summary_statistics.csv")

    fig_timeseries(df)
    fig_monthly(df)
    fig_corr(df)
    fig_diurnal(df)
    fig_flow_rose(df)
    print(f"\nFigures written to {FIG}")


if __name__ == "__main__":
    main()
