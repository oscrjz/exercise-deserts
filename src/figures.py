"""Presentation figures: one function per graph, all in the same style.

Usage:
    python -m src.figures
Figures are saved to figures/final/ (01 to 09).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
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


# ---------------------------------------------------------------------------
# Graphs 5 to 8: how access, income and health relate
# ---------------------------------------------------------------------------
PREDICTORS = ["exercise_access", "income_10k", "uninsured"]
NICE = {"exercise_access": "Exercise access", "income_10k": "Median income",
        "uninsured": "Uninsured rate"}


def complete_counties(df: pd.DataFrame) -> pd.DataFrame:
    """Counties with every variable the regression needs. Income in $10,000s,
    so its slope reads as "per $10,000 more income"."""
    d = df.assign(income_10k=df["median_income"] / 10_000)
    return d.dropna(subset=[*PREDICTORS, *config.OUTCOMES])


def ols_fit(X: np.ndarray, y: np.ndarray):
    """Least-squares fit of y on X, where X already has a column of 1s.
    Returns coefficients, standard errors and residuals."""
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ b
    n, k = X.shape
    se = np.sqrt(np.diag(resid @ resid / (n - k) * np.linalg.inv(X.T @ X)))
    return b, se, resid


def with_intercept(df: pd.DataFrame, cols: list[str]) -> np.ndarray:
    return np.column_stack([np.ones(len(df)), df[cols].to_numpy()])


def scatter_by_income(df: pd.DataFrame):
    """Graph 5: access vs inactivity, colored by county income third.
    If the colored lines sit at different heights and are flatter than the
    dashed overall line, income is doing much of the work access got credit for."""
    d = complete_counties(df)
    d["income_group"] = pd.qcut(d["median_income"], 3,
                                labels=["Lowest income", "Middle income", "Highest income"])
    colors = {"Lowest income": ORANGE, "Middle income": AQUA, "Highest income": BLUE}
    xs = np.array([0, 100])

    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.subplots_adjust(top=0.80, left=0.07, right=0.97, bottom=0.11)

    fit = stats.linregress(d["exercise_access"], d["inactivity"])
    ax.plot(xs, fit.intercept + fit.slope * xs, color=INK, linewidth=2, linestyle="--",
            label=f"All counties: {fit.slope * 10:+.2f} per 10 pts of access")

    for name, group in d.groupby("income_group", observed=True):
        ax.scatter(group["exercise_access"], group["inactivity"], s=8, alpha=0.25,
                   color=colors[name], linewidth=0)
        fit = stats.linregress(group["exercise_access"], group["inactivity"])
        ax.plot(xs, fit.intercept + fit.slope * xs, color=colors[name], linewidth=3,
                label=f"{name}: {fit.slope * 10:+.2f} per 10 pts")

    ax.set_xlim(0, 100)
    ax.set_xlabel("Residents with access to exercise opportunities, %")
    ax.set_ylabel("Physically inactive adults, %")
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right", fontsize=12)

    titles(fig, "Income sets the level, and within each income group access matters less",
           f"{len(d):,} US counties, split into thirds by median household income. "
           "Lines are best-fit trends.")
    fig.savefig(OUT / "05_scatter_by_income.png")
    plt.close(fig)


def added_variable_plot(df: pd.DataFrame):
    """Graph 6: the access-inactivity relationship before and after removing
    everything income and insurance explain from BOTH variables. The slope on
    the right equals the access coefficient in the full regression."""
    d = complete_counties(df)
    controls = with_intercept(d, ["income_10k", "uninsured"])
    _, _, access_left = ols_fit(controls, d["exercise_access"].to_numpy())
    _, _, inactive_left = ols_fit(controls, d["inactivity"].to_numpy())

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.subplots_adjust(top=0.76, left=0.06, right=0.98, bottom=0.13, wspace=0.22)
    panels = [
        (axes[0], d["exercise_access"].to_numpy(), d["inactivity"].to_numpy(),
         "Before: raw data", "Access to exercise, %", "Physically inactive adults, %"),
        (axes[1], access_left, inactive_left, "After: income and insurance removed",
         "Access left over, points", "Inactivity left over, points"),
    ]
    for ax, x, y, name, xlabel, ylabel in panels:
        fit = stats.linregress(x, y)
        ax.scatter(x, y, s=8, color=BLUE, alpha=0.25, linewidth=0)
        line_x = np.array([x.min(), x.max()])
        ax.plot(line_x, fit.intercept + fit.slope * line_x, color=ORANGE, linewidth=3)
        ax.set_title(f"{name}: {fit.slope * 10:+.2f} per 10 pts of access",
                     loc="left", fontsize=13, color=INK, pad=10)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)

    titles(fig, "Once money is accounted for, the access line nearly flattens",
           "Right panel: what is left of access and inactivity after removing what "
           "median income and the uninsured rate explain.")
    fig.savefig(OUT / "06_added_variable_plot.png")
    plt.close(fig)


def predicted_vs_actual(df: pd.DataFrame):
    """Graph 7: inactivity predicted from access, income and insurance vs actual.
    Dots above the diagonal are more inactive than the model expects."""
    d = complete_counties(df)
    X = with_intercept(d, PREDICTORS)
    b, _, resid = ols_fit(X, d["inactivity"].to_numpy())
    d = d.assign(predicted=X @ b, leftover=resid)
    h = d[d["fips"] == config.TARGET_COUNTY_FIPS].iloc[0]

    fig, ax = plt.subplots(figsize=(9, 8))
    fig.subplots_adjust(top=0.84, left=0.10, right=0.96, bottom=0.10)
    ax.scatter(d["predicted"], d["inactivity"], s=8, color=BLUE, alpha=0.25, linewidth=0)
    ax.plot([10, 50], [10, 50], color=INK, linewidth=2, linestyle="--",
            label="Prediction is exactly right")
    ax.scatter(h["predicted"], h["inactivity"], s=130, color=ORANGE,
               edgecolor="white", linewidth=1.5, zorder=3)
    ax.annotate(f"Hidalgo County\n{h['leftover']:+.1f} points above prediction",
                (h["predicted"], h["inactivity"]), xytext=(-160, 20),
                textcoords="offset points", color=ORANGE, fontsize=12, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=ORANGE))
    ax.set_xlim(10, 50)
    ax.set_ylim(10, 50)
    ax.set_aspect("equal")
    ax.set_xlabel("Predicted inactivity from access, income and insurance, %")
    ax.set_ylabel("Actual inactivity, %")
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower right", fontsize=12)

    titles(fig, "Hidalgo is more inactive than the model predicts",
           f"Each dot is one US county. Hidalgo: predicted {h['predicted']:.1f}%, "
           f"actual {h['inactivity']:.1f}%.")
    fig.savefig(OUT / "07_predicted_vs_actual.png")
    plt.close(fig)


def coefficient_plot(df: pd.DataFrame):
    """Graph 8: standardized regression coefficients with 95% confidence intervals.
    Standardizing puts access, income and insurance on the same scale, so the
    dots can be compared directly. A grey bar crosses zero: no clear effect."""
    d = complete_counties(df)
    cols = [*PREDICTORS, *config.OUTCOMES]
    z = (d[cols] - d[cols].mean()) / d[cols].std()
    X = with_intercept(z, PREDICTORS)
    names = {"inactivity": "Inactivity", "obesity": "Obesity", "diabetes": "Diabetes"}

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), sharex=True)
    fig.subplots_adjust(top=0.76, left=0.11, right=0.98, bottom=0.15, wspace=0.12)
    for ax, outcome in zip(axes, config.OUTCOMES):
        b, se, _ = ols_fit(X, z[outcome].to_numpy())
        beta, low, high = b[1:], b[1:] - 1.96 * se[1:], b[1:] + 1.96 * se[1:]
        y = np.arange(len(PREDICTORS))
        colors = [BLUE if lo > 0 or hi < 0 else "#b8b7b2" for lo, hi in zip(low, high)]
        ax.axvline(0, color=INK, linewidth=1.2)
        ax.hlines(y, low, high, color=colors, linewidth=4)
        ax.scatter(beta, y, s=90, color=colors, zorder=3, edgecolor="white", linewidth=1.5)
        for yi, bi in zip(y, beta):
            ax.text(bi, yi - 0.3, f"{bi:+.2f}", ha="center", fontsize=12, color=INK)
        ax.set_yticks(y, [NICE[p] for p in PREDICTORS] if ax is axes[0] else [])
        ax.invert_yaxis()
        ax.set_ylim(len(PREDICTORS) - 0.5, -0.8)
        ax.set_title(names[outcome], loc="left", fontsize=13, color=INK, pad=10)
        ax.set_xlabel("Standardized coefficient")
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)

    titles(fig, "Income has the biggest effect on every outcome",
           "Standardized coefficients with 95% confidence intervals. "
           "Grey means the interval crosses zero, so no clear effect.")
    fig.savefig(OUT / "08_coefficient_plot.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 09: tile map of the states, a "heat check" of access and inactivity
# ---------------------------------------------------------------------------
# Each state is one equal-size square placed roughly where it sits on a map.
# Equal squares keep small states readable and need no map files to install.
STATE_TILES = {
    "AK": (0, 0), "ME": (0, 11),
    "VT": (1, 10), "NH": (1, 11),
    "WA": (2, 1), "ID": (2, 2), "MT": (2, 3), "ND": (2, 4), "MN": (2, 5),
    "IL": (2, 6), "WI": (2, 7), "MI": (2, 8), "NY": (2, 9), "RI": (2, 10), "MA": (2, 11),
    "OR": (3, 1), "NV": (3, 2), "WY": (3, 3), "SD": (3, 4), "IA": (3, 5),
    "IN": (3, 6), "OH": (3, 7), "PA": (3, 8), "NJ": (3, 9), "CT": (3, 10),
    "CA": (4, 1), "UT": (4, 2), "CO": (4, 3), "NE": (4, 4), "MO": (4, 5),
    "KY": (4, 6), "WV": (4, 7), "VA": (4, 8), "MD": (4, 9), "DE": (4, 10),
    "AZ": (5, 2), "NM": (5, 3), "KS": (5, 4), "AR": (5, 5), "TN": (5, 6),
    "NC": (5, 7), "SC": (5, 8), "DC": (5, 9),
    "OK": (6, 4), "LA": (6, 5), "MS": (6, 6), "AL": (6, 7), "GA": (6, 8),
    "HI": (7, 0), "TX": (7, 4), "FL": (7, 9),
}

STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


def draw_tiles(ax, values: pd.Series, cmap: str, label: str):
    """One square per state, colored by its value, with the state and value written on it."""
    lo, hi = values.min(), values.max()
    # Skip the palest and darkest ends so every tile stays visible and readable
    colors = ListedColormap(plt.get_cmap(cmap)(np.linspace(0.12, 0.92, 256)))
    for abbr, (row, col) in STATE_TILES.items():
        if abbr not in values:
            continue
        v = values[abbr]
        shade = (v - lo) / (hi - lo)
        ax.add_patch(plt.Rectangle((col, -row), 0.92, 0.92, facecolor=colors(shade),
                                   linewidth=2.5 if abbr == "TX" else 0,
                                   edgecolor=INK if abbr == "TX" else "none"))
        text = "white" if shade > 0.55 else INK
        ax.text(col + 0.46, -row + 0.6, abbr, ha="center", va="center",
                fontsize=10, fontweight="bold", color=text)
        ax.text(col + 0.46, -row + 0.28, f"{v:.0f}", ha="center", va="center",
                fontsize=9, color=text)
    ax.set_xlim(-0.2, 12.1)
    ax.set_ylim(-7.3, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(label, fontsize=13, color=INK, loc="left", pad=4)
    # Small legend bar: light = low, dark = high
    sm = plt.cm.ScalarMappable(cmap=colors, norm=plt.Normalize(lo, hi))
    bar = plt.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.05, pad=0.02, aspect=40)
    bar.outline.set_visible(False)
    bar.ax.tick_params(labelsize=10, colors=MUTED)


def state_tile_map(df: pd.DataFrame):
    """09: state averages of county access next to state averages of county inactivity."""
    states = df.assign(abbr=df["state"].map(STATE_ABBR)).dropna(subset=["abbr"])
    access = states.groupby("abbr")["exercise_access"].mean()
    inactive = states.groupby("abbr")["inactivity"].mean()

    fig, (left, right) = plt.subplots(1, 2, figsize=(16, 6.8))
    fig.subplots_adjust(top=0.80, bottom=0.04, left=0.04, right=0.98, wspace=0.08)
    draw_tiles(left, access, "Blues", "Access to exercise opportunities, % (darker = more access)")
    draw_tiles(right, inactive, "Oranges", "Physical inactivity, % of adults (darker = more inactive)")

    low = ", ".join(access.nsmallest(3).index)
    high = ", ".join(inactive.nlargest(3).index)
    titles(fig, f"The South runs dry: least access ({low}) and most inactivity ({high})",
           "Average of each state's counties, County Health Rankings 2025. Texas is outlined.")
    fig.savefig(OUT / "09_state_tile_map.png")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(config.PROCESSED_DIR / "chr_counties.csv", dtype={"fips": str})
    access_histogram(df)
    access_vs_outcomes(df)
    access_groups_boxplot(df)
    correlation_before_after(df)
    scatter_by_income(df)
    added_variable_plot(df)
    predicted_vs_actual(df)
    coefficient_plot(df)
    state_tile_map(df)
    print(f"Figures saved to {OUT.relative_to(config.ROOT)}/")
    

if __name__ == "__main__":
    main()