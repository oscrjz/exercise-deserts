"""Clean the County Health Rankings workbook down to one row per county.

The 9 variables we use are split across two sheets of the 2025 workbook, so
we read both, keep the columns we need, and join them on FIPS.

Usage:
    python -m src.load_chr            # real data in data/raw/
    python -m src.load_chr --sample   # fake data in data/raw/sample/
"""

import argparse

import pandas as pd

from src import config


def read_sheet(path, sheet: str, columns: dict) -> pd.DataFrame:
    # header=1 skips the measure-group row and uses the column names on row 2.
    df = pd.read_excel(path, sheet_name=sheet, header=1, dtype={"FIPS": str})
    wanted = [*config.CHR_ID_COLUMNS, *columns]
    missing = [c for c in wanted if c not in df.columns]
    if missing:
        raise KeyError(f"Columns not found on sheet '{sheet}': {missing}")
    return df[wanted].rename(columns={**config.CHR_ID_COLUMNS, **columns})


def load_chr(sample: bool = False) -> pd.DataFrame:
    folder = config.SAMPLE_DIR if sample else config.RAW_DIR
    path = folder / config.CHR_FILE

    sheets = [read_sheet(path, name, cols) for name, cols in config.CHR_SHEETS.items()]
    df = sheets[0]
    for other in sheets[1:]:
        df = df.merge(other.drop(columns=["state", "county"]), on="fips", how="left")

    df["fips"] = df["fips"].str.zfill(5)

    # Drop the national row and state summary rows. Those have no county name
    # and their FIPS ends in 000.
    df = df[df["county"].notna() & ~df["fips"].str.endswith("000")]

    for col in ["exercise_access", *config.OUTCOMES, *config.CONTROLS]:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

    return df.reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="use fake sample data")
    args = parser.parse_args()

    df = load_chr(sample=args.sample)
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = config.PROCESSED_DIR / ("chr_counties_sample.csv" if args.sample else "chr_counties.csv")
    df.to_csv(out, index=False)

    print(f"Saved {len(df):,} counties x {df.shape[1]} columns to {out.relative_to(config.ROOT)}")
    print("Missing values per column:")
    print(df.isna().sum().to_string())


if __name__ == "__main__":
    main()
