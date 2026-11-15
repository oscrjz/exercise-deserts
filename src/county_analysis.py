"""Research question 1: county-level comparison across the US.

Do counties with less access to exercise opportunities have higher rates of
physical inactivity, obesity, and diabetes? A first look only, not a final
method: summary stats, correlations (plain and after controlling for income
and uninsured rate), scatterplots, and a low / medium / high access comparison.

Usage:
    python -m src.county_analysis
    python -m src.county_analysis --sample
"""

import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src import config


def partial_corr(df: pd.DataFrame, x: str, y: str, controls: list[str]) -> float:
    """Correlation between x and y after removing the linear effect of the controls."""
    d = df[[x, y, *controls]].dropna()
    Z = np.column_stack([np.ones(len(d)), d[controls].to_numpy()])
    resid = lambda v: v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]
    return float(np.corrcoef(resid(d[x].to_numpy()), resid(d[y].to_numpy()))[0, 1])


def ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="use fake sample data")
    args = parser.parse_args()

    name = "chr_counties_sample.csv" if args.sample else "chr_counties.csv"
    df = pd.read_csv(config.PROCESSED_DIR / name, dtype={"fips": str})
    fig_dir = config.FIGURES_DIR / "county"
    fig_dir.mkdir(parents=True, exist_ok=True)
    tag = "_sample" if args.sample else ""

    numeric = ["exercise_access", *config.OUTCOMES, *config.CONTROLS]

    print("Summary statistics")
    print(df[numeric].describe().round(1).to_string(), "\n")

    # Hypothesis: relationship holds, though weaker, after accounting for income and uninsured
    print("Correlation of exercise_access with each outcome")
    rows = []
    for outcome in config.OUTCOMES:
        rows.append({"outcome": outcome,
                     "plain": round(df["exercise_access"].corr(df[outcome]), 2),
                     "controlling_income_uninsured": round(
                         partial_corr(df, "exercise_access", outcome, config.CONTROLS), 2)})
    print(pd.DataFrame(rows).to_string(index=False), "\n")

    # Scatterplots: access vs each outcome
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, outcome in zip(axes, config.OUTCOMES):
        sns.regplot(data=df, x="exercise_access", y=outcome, ax=ax,
                    scatter_kws={"s": 8, "alpha": 0.4}, line_kws={"color": "black"})
        ax.set_xlabel("Access to exercise opportunities, %")
        ax.set_ylabel(f"{outcome.capitalize()}, %")
    fig.suptitle("County exercise access vs health outcomes")
    fig.tight_layout()
    fig.savefig(fig_dir / f"access_vs_outcomes{tag}.png", dpi=150)
    plt.close(fig)

    # Split counties into thirds by access and compare outcomes
    df["access_group"] = pd.qcut(df["exercise_access"], 3, labels=["Low", "Medium", "High"])
    print("Mean outcomes by access group")
    print(df.groupby("access_group", observed=True)[[*config.OUTCOMES, *config.CONTROLS]]
            .mean().round(1).to_string(), "\n")

    long = df.melt(id_vars="access_group", value_vars=config.OUTCOMES,
                   var_name="outcome", value_name="percent")
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(data=long, x="outcome", y="percent", hue="access_group", ax=ax)
    ax.set_title("Health outcomes by county access group")
    ax.set_xlabel("")
    ax.set_ylabel("Percent of adults")
    fig.tight_layout()
    fig.savefig(fig_dir / f"outcomes_by_access_group{tag}.png", dpi=150)
    plt.close(fig)

    # Where does the target county sit nationally?
    target = df[df["fips"] == config.TARGET_COUNTY_FIPS]
    if not target.empty:
        note = " (FAKE sample values)" if args.sample else ""
        print(f"{config.TARGET_COUNTY_NAME} percentile among US counties{note}")
        for col in numeric:
            pct = (df[col] < target[col].iloc[0]).mean() * 100
            print(f"  {col:16s} {target[col].iloc[0]:>10.1f}   {ordinal(round(pct)):>5s} percentile")
        print()

    print("States with the lowest average access")
    print(df.groupby("state")["exercise_access"].mean().nsmallest(10).round(1).to_string())
    print(f"\nFigures saved to {fig_dir.relative_to(config.ROOT)}/")


if __name__ == "__main__":
    main()
