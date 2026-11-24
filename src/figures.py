"""Presentation figures: one function per graph, all in the same style.

Usage:
    python -m src.figures
Figures are saved to figures/final/.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from src import config

# Shared style so every slide looks like it belongs to the same deck.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Segoe UI", "DejaVu Sans"],
    "font.size": 13,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.dpi": 150,
})

OUT = config.FIGURES_DIR / "final"


def titles(fig, title, subtitle):
    """Finding as the title, what the data is as the subtitle."""
    fig.text(0.06, 0.95, title, fontsize=17, fontweight="bold", color=INK, va="top")
    fig.text(0.06, 0.885, subtitle, fontsize=12, color=MUTED, va="top")


def access_histogram(df: pd.DataFrame):
    """Graph 1: how exercise access varies across US counties."""
    access = df["exercise_access"].dropna()
    q1, median = access.quantile(0.25), access.median()
    hidalgo = df.loc[df["fips"] == config.TARGET_COUNTY_FIPS, "exercise_access"].iloc[0]

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.subplots_adjust(top=0.80, left=0.07, right=0.97, bottom=0.12)

    # Each bar = number of counties in a 2.5-point range of access.
    bins = [i * 2.5 for i in range(41)]
    _, edges, bars = ax.hist(access, bins=bins, color=BLUE, edgecolor="white", linewidth=1.5)
    for bar, left in zip(bars, edges[:-1]):
        if left + 1.25 < q1:  # bar's midpoint is in the lowest quarter
            bar.set_color(ORANGE)
            bar.set_edgecolor("white")

    top = ax.get_ylim()[1] * 1.18  # headroom so labels sit above the bars
    ax.set_ylim(0, top)
    ax.axvline(median, ymax=0.93, color=INK, linestyle=":", linewidth=1.5)
    ax.text(median + 1, top * 0.95, f"US median {median:.1f}%",
            ha="left", va="top", color=INK, fontsize=12)
    ax.axvline(hidalgo, ymax=0.93, color=AQUA, linewidth=2.5)
    ax.text(hidalgo - 1, top * 0.95, f"Hidalgo County {hidalgo:.1f}%",
            ha="right", va="top", color=INK, fontsize=12, fontweight="bold")

    ax.text(q1 / 2, top * 0.55,
            f"Lowest-access\n25% of counties\n(under {q1:.0f}%)",
            ha="center", color=ORANGE, fontsize=12, fontweight="bold")

    ax.set_xlabel("Residents with access to exercise opportunities, %")
    ax.set_ylabel("Number of counties")
    ax.set_xlim(0, 100)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)

    titles(fig, "Access to exercise varies widely, and Hidalgo sits near the middle",
           f"{len(access):,} US counties, County Health Rankings 2025")
    fig.savefig(OUT / "01_access_histogram.png")
    plt.close(fig)


def access_vs_outcomes(df: pd.DataFrame):
    """Graph 2: access vs each health outcome, one county per dot, with the best-fit line."""
    names = {"inactivity": "Physically inactive", "obesity": "Obese", "diabetes": "Diabetic"}
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.subplots_adjust(top=0.78, left=0.05, right=0.98, bottom=0.14, wspace=0.25)

    for ax, outcome in zip(axes, config.OUTCOMES):
        d = df[["fips", "exercise_access", outcome]].dropna()
        fit = stats.linregress(d["exercise_access"], d[outcome])

        # Each dot = one county
        ax.scatter(d["exercise_access"], d[outcome], s=8, color=BLUE, alpha=0.25, linewidth=0)
        xs = np.array([0, 100])
        ax.plot(xs, fit.intercept + fit.slope * xs, color=INK, linewidth=2.5)

        h = d[d["fips"] == config.TARGET_COUNTY_FIPS]
        ax.scatter(h["exercise_access"], h[outcome], s=110, color=ORANGE,
                   edgecolor="white", linewidth=1.5, zorder=3)
        ax.annotate("Hidalgo", (h["exercise_access"].iloc[0], h[outcome].iloc[0]),
                    xytext=(-10, 6), textcoords="offset points", ha="right",
                    color=ORANGE, fontsize=12, fontweight="bold")

        p_text = "p < 0.001" if fit.pvalue < 0.001 else f"p = {fit.pvalue:.3f}"
        ax.text(0.97, 0.97, f"r = {fit.rvalue:.2f}\n{p_text}", transform=ax.transAxes,
                ha="right", va="top", fontsize=12, color=INK,
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=GRID))

        ax.set_title(f"{names[outcome]} adults, %", loc="left", fontsize=13, color=INK, pad=10)
        ax.set_xlabel("Access to exercise, %")
        ax.set_xlim(0, 100)
        ax.grid(color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)

    titles(fig, "Counties with less access to exercise tend to be less healthy",
           "Each dot is one US county; the line is the best-fit trend. "
           "Hidalgo is far above the line on all three.")
    fig.savefig(OUT / "02_access_vs_outcomes.png")
    plt.close(fig)


def access_groups_boxplot(df: pd.DataFrame):
    """Graph 3: counties split into thirds by access, health compared across the thirds."""
    names = {"inactivity": "Physically inactive", "obesity": "Obese", "diabetes": "Diabetic"}
    groups = ["Low", "Medium", "High"]
    shades = ["#9ec5f4", "#5a9be6", "#1d5fb0"]  # light to dark blue = low to high access
    d = df.dropna(subset=["exercise_access"]).copy()
    d["group"] = pd.qcut(d["exercise_access"], 3, labels=groups)
    cuts = d["exercise_access"].quantile([1 / 3, 2 / 3])

    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.subplots_adjust(top=0.78, left=0.05, right=0.98, bottom=0.12, wspace=0.25)

    for ax, outcome in zip(axes, config.OUTCOMES):
        data = [d.loc[d["group"] == g, outcome].dropna() for g in groups]
        box = ax.boxplot(data, patch_artist=True, widths=0.6, showfliers=False,
                         medianprops=dict(color=INK, linewidth=2),
                         whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED))
        for patch, shade in zip(box["boxes"], shades):
            patch.set_facecolor(shade)
            patch.set_edgecolor("white")
        for i, values in enumerate(data, start=1):
            ax.text(i + 0.33, values.median(), f"{values.median():.1f}",
                    va="center", fontsize=11, color=INK)

        ax.set_xticks([1, 2, 3], [f"{g}\naccess" for g in groups])
        ax.set_title(f"{names[outcome]} adults, %", loc="left", fontsize=13, color=INK, pad=10)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)

    titles(fig, "Low-access counties have higher inactivity, obesity, and diabetes",
           f"Counties split into thirds by access: Low under {cuts.iloc[0]:.0f}%, "
           f"Medium {cuts.iloc[0]:.0f}-{cuts.iloc[1]:.0f}%, High over {cuts.iloc[1]:.0f}%. "
           "Line in each box = median county.")
    fig.savefig(OUT / "03_access_groups_boxplot.png")
    plt.close(fig)

def partial_corr(df: pd.DataFrame, x: str, y: str, controls: list[str]) -> float:
    """Correlation between x and y after removing the linear effect of the controls."""
    d = df[[x, y, *controls]].dropna()
    Z = np.column_stack([np.ones(len(d)), d[controls].to_numpy()])
    resid = lambda v: v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]
    return float(np.corrcoef(resid(d[x].to_numpy()), resid(d[y].to_numpy()))[0, 1])


def correlation_before_after(df: pd.DataFrame):
    """Graph 4: the access-health link before and after controlling for income and uninsured."""
    names = {"inactivity": "Inactivity", "obesity": "Obesity", "diabetes": "Diabetes"}
    before = [df["exercise_access"].corr(df[o]) for o in config.OUTCOMES]
    after = [partial_corr(df, "exercise_access", o, config.CONTROLS) for o in config.OUTCOMES]

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.subplots_adjust(top=0.78, left=0.07, right=0.97, bottom=0.12)

    # Bars show the strength of the link (size of r); all the r values are negative.
    x = np.arange(len(config.OUTCOMES))
    w = 0.36
    b1 = ax.bar(x - w / 2 - 0.01, [abs(v) for v in before], w, color="#b8b7b2", label="Before controlling")
    b2 = ax.bar(x + w / 2 + 0.01, [abs(v) for v in after], w, color=BLUE, label="After controlling for income and uninsured")
    for bars, values in ((b1, before), (b2, after)):
        for bar, v in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                    f"r = {v:.2f}", ha="center", fontsize=12, color=INK)

    ax.set_xticks(x, [names[o] for o in config.OUTCOMES], fontsize=13, color=INK)
    ax.set_ylabel("Strength of link with access (size of r)")
    ax.set_ylim(0, 0.5)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right", fontsize=12)

    titles(fig, "Once income is accounted for, the access-health link shrinks by more than half",
           "Correlation of exercise access with each outcome, US counties. "
           "All are negative: more access, lower rates.")
    fig.savefig(OUT / "04_correlation_before_after.png")
    plt.close(fig)
    
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(config.PROCESSED_DIR / "chr_counties.csv", dtype={"fips": str})
    access_histogram(df)
    access_vs_outcomes(df)
    access_groups_boxplot(df)
    correlation_before_after(df)
    print(f"Figures saved to {OUT.relative_to(config.ROOT)}/")
    

if __name__ == "__main__":
    main()