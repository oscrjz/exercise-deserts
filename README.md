# Exercise Deserts

Group 8 data science project.

An exercise desert is an area where residents have little access to places for physical activity, such as parks, recreation centers, or walkable streets. We look at where these areas are and how they relate to health, starting with a county level comparison across the US and then looking at the neighborhood level inside Hidalgo County, Texas.

The full proposal is in `docs/proposal.md`.

## Research questions

**1. County level, across the US.** Do counties with less access to exercise opportunities have higher rates of physical inactivity, obesity, and diabetes?

*Hypothesis:* they do, and the relationship holds, though weaker, after accounting for median income and the uninsured rate.

**2. Neighborhood level, inside Hidalgo County.** How much do these three outcomes vary from one census tract to the next, and where are the highest rates concentrated?

## Datasets

| | Dataset | Level | What we keep |
| --- | --- | --- | --- |
| 1 | County Health Rankings 2025 data workbook | One row per US county | 3,159 counties, 9 variables |
| 2 | CDC PLACES census tract data, 2025 release | One row per tract per measure | Hidalgo County, 3 measures, 211 tracts |

The cleaned versions of both are already in `data/processed/`, so you can start without downloading anything. Download links, file names, and column details are in `data/README.md`.

## Folders

```
exercise-deserts/
├── data/
│   ├── raw/                 original downloads, not committed
│   │   └── sample/          fake data from make_sample_data.py
│   └── processed/           cleaned data, committed and ready to use
├── docs/
│   └── proposal.md          our submitted proposal
├── figures/
│   ├── county/              plots for question 1
│   └── tracts/              plots for question 2
├── notebooks/
│   ├── 01_county_comparison.ipynb    scratch work for question 1
│   └── 02_hidalgo_tracts.ipynb       scratch work for question 2
├── scripts/
│   └── make_sample_data.py  fake data for testing
└── src/
    ├── config.py            paths, column names, target county
    ├── load_chr.py          dataset 1 to one row per county
    ├── load_places.py       dataset 2 to one row per tract
    ├── county_analysis.py   first look for question 1
    └── tract_analysis.py    first look for question 2
```

How the pieces connect:

```
data/raw/  ──load_chr.py──────▶  data/processed/chr_counties.csv  ──county_analysis.py──▶  figures/county/
data/raw/  ──load_places.py───▶  data/processed/places_tracts_48215.csv  ──tract_analysis.py──▶  figures/tracts/
```

## Setup

```bash
git clone <repo-url>
cd exercise-deserts
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Quick start with fake data

You can run everything before downloading the real files. The sample data is randomly generated and only exists to test the code. Its numbers mean nothing.

```bash
python scripts/make_sample_data.py
python -m src.load_chr --sample
python -m src.load_places --sample
python -m src.county_analysis --sample
python -m src.tract_analysis --sample
```

## Running on the real data

The cleaned data is already in the repo, so you can go straight to the analysis:

```bash
python -m src.county_analysis
python -m src.tract_analysis
```

To rebuild the cleaned files, put the raw downloads in `data/raw/` using the names in `data/README.md`, then run:

```bash
python -m src.load_chr
python -m src.load_places
```

The target county is set once in `src/config.py` as `TARGET_COUNTY_FIPS = "48215"`. To try a different county, change that value or pass `--county` with another 5-digit FIPS code.

## Status

- [x] Repo structure, loaders, and first-look scripts
- [x] Download real data and build the cleaned files
- [ ] Agree on analysis methods
- [ ] Find a park and facility location source to measure access per tract
- [ ] Get tract boundary files for maps
- [ ] Write up results

The analysis approach is still open. The two analysis scripts only cover summary stats, correlations, and simple plots, so change them freely once the group decides on methods.

## Team

- Oscar Juarez
- Luis
- Yusuf Oraby
- Add your name here
