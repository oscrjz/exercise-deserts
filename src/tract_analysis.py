"""Research question 2: neighborhood-level variation inside one county.

How much do inactivity, obesity, and diabetes vary from one tract to the next
in Hidalgo County, and where are the highest rates concentrated? A first look
only: spread of each measure, the highest-rate tracts, and how the three
measures move together. Maps need tract boundaries and are a later step.

Usage:
    python -m src.tract_analysis
    python -m src.tract_analysis --sample
    python -m src.tract_analysis --county 48061
"""

import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src import config
from src.load_places import output_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="use fake sample data")
    parser.add_argument("--county", default=config.TARGET_COUNTY_FIPS)
    args = parser.parse_args()

    path = config.PROCESSED_DIR / output_name(args.county, args.sample)
    df = pd.read_csv(path, dtype={"tract_fips": str, "county_fips": str})
    label = df["county"].iloc[0] if "county" in df else args.county
    fig_dir = config.FIGURES_DIR / "tracts"
    fig_dir.mkdir(parents=True, exist_ok=True)
    tag = f"_{args.county}{'_sample' if args.sample else ''}"

    print(f"{label}: {len(df)} tracts\n")

    # How much do outcomes vary across neighborhoods?
    spread = df[config.OUTCOMES].agg(["min", "median", "max", "std"]).T
    spread["range"] = spread["max"] - spread["min"]
    spread["iqr"] = df[config.OUTCOMES].quantile(0.75) - df[config.OUTCOMES].quantile(0.25)
    print("Spread across tracts, percent of adults")
    print(spread.round(1).to_string(), "\n")

    # Where are the highest rates concentrated?
    for outcome in config.OUTCOMES:
        top = df.nlargest(10, outcome)[["tract_fips", outcome, "population"]]
        print(f"Top 10 tracts by {outcome}")
        print(top.to_string(index=False), "\n")

    # Tracts in the top quarter for all three outcomes
    high = pd.concat([df[o] >= df[o].quantile(0.75) for o in config.OUTCOMES], axis=1).all(axis=1)
    print(f"Tracts in the top 25% for all three outcomes: {high.sum()}")
    print(df.loc[high, ["tract_fips", *config.OUTCOMES]].to_string(index=False), "\n")

    print("Correlation between the three outcomes")
    print(df[config.OUTCOMES].corr().round(2).to_string())

    # Distributions
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, outcome in zip(axes, config.OUTCOMES):
        sns.histplot(df[outcome], bins=25, ax=ax)
        ax.axvline(df[outcome].median(), color="black", linestyle=":", label="median")
        ax.set_xlabel(f"{outcome.capitalize()}, % of adults")
        ax.set_ylabel("Number of tracts")
        ax.legend()
    fig.suptitle(f"Tract-level health outcomes in {label}")
    fig.tight_layout()
    fig.savefig(fig_dir / f"outcome_distributions{tag}.png", dpi=150)
    plt.close(fig)

    print(f"\nFigures saved to {fig_dir.relative_to(config.ROOT)}/")


if __name__ == "__main__":
    main()
