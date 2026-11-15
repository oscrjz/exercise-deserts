"""Filter CDC PLACES tract data and reshape it to one row per tract.

The raw file has one row per tract per measure. We keep one county and three
measures, then pivot so each measure becomes its own column. For Hidalgo
County this goes from 633 rows (211 tracts x 3 measures) to 211 rows.

Usage:
    python -m src.load_places                  # Hidalgo County, from config
    python -m src.load_places --sample         # fake data
    python -m src.load_places --county 48061   # a different county
    python -m src.load_places --all            # every tract in the US
"""

import argparse

import pandas as pd

from src import config

KEEP = ["StateAbbr", "CountyName", "CountyFIPS", "LocationName",
        "MeasureId", "Data_Value", "TotalPopulation"]


def load_places(sample: bool = False, county_fips: str | None = None) -> pd.DataFrame:
    folder = config.SAMPLE_DIR if sample else config.RAW_DIR
    path = folder / config.PLACES_FILE

    # The full file is about 3 million rows, so read it in chunks and filter as we go.
    # A file already filtered to one county on data.cdc.gov works the same way.
    chunks = []
    for chunk in pd.read_csv(path, usecols=KEEP, chunksize=500_000,
                             dtype={"CountyFIPS": str, "LocationName": str},
                             thousands=","):
        chunk = chunk[chunk["MeasureId"].isin(config.PLACES_MEASURES)]
        if county_fips:
            chunk = chunk[chunk["CountyFIPS"].str.zfill(5) == county_fips]
        chunks.append(chunk)
    long = pd.concat(chunks, ignore_index=True)

    if long.empty:
        raise ValueError("No rows left after filtering. Check the county FIPS and file name.")
    print(f"Rows after filtering: {len(long):,} (tract x measure)")

    wide = long.pivot_table(
        index=["LocationName", "StateAbbr", "CountyName", "CountyFIPS", "TotalPopulation"],
        columns="MeasureId",
        values="Data_Value",
    ).rename(columns=config.PLACES_MEASURES).reset_index()

    wide.columns.name = None
    wide = wide.rename(columns={
        "LocationName": "tract_fips",
        "StateAbbr": "state",
        "CountyName": "county",
        "CountyFIPS": "county_fips",
        "TotalPopulation": "population",
    })
    wide["tract_fips"] = wide["tract_fips"].str.zfill(11)
    wide["county_fips"] = wide["county_fips"].str.zfill(5)
    return wide


def output_name(county: str | None, sample: bool) -> str:
    scope = county if county else "all"
    return f"places_tracts_{scope}{'_sample' if sample else ''}.csv"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="use fake sample data")
    parser.add_argument("--county", default=config.TARGET_COUNTY_FIPS,
                        help="5-digit county FIPS to keep. Default comes from config.py.")
    parser.add_argument("--all", action="store_true", help="keep every tract in the US")
    args = parser.parse_args()
    county = None if args.all else args.county

    df = load_places(sample=args.sample, county_fips=county)
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = config.PROCESSED_DIR / output_name(county, args.sample)
    df.to_csv(out, index=False)

    print(f"Saved {len(df):,} tracts x {df.shape[1]} columns to {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
