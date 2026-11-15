"""Generate FAKE data in the same layout as the real CHR and PLACES files.

This lets everyone run and test the pipeline before downloading the real
files. The numbers are random and mean nothing. Never use them in results.

Usage:
    python scripts/make_sample_data.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config  # noqa: E402

rng = np.random.default_rng(42)
STATES = {"01": "AL", "06": "CA", "13": "GA", "17": "IL", "36": "NY", "48": "TX"}
COUNTIES_PER_STATE = 40
TRACTS_PER_COUNTY = 12
TARGET_TRACTS = 211  # tract count for the target county in our proposal


def make_chr() -> list[dict]:
    rows = [{"statecode": "00", "countycode": "000", "fipscode": "00000",
             "state": "US", "county": "United States"}]
    counties = []
    for sc, abbr in STATES.items():
        rows.append({"statecode": sc, "countycode": "000", "fipscode": f"{sc}000",
                     "state": abbr, "county": f"State of {abbr}"})
        for i in range(1, COUNTIES_PER_STATE + 1):
            cc = f"{2 * i - 1:03d}"
            access = rng.uniform(0.2, 1.0)
            income = rng.normal(65000, 15000)
            inactivity = np.clip(0.38 - 0.15 * access - (income - 65000) / 600000
                                 + rng.normal(0, 0.03), 0.1, 0.5)
            obesity = np.clip(0.25 + 0.5 * inactivity + rng.normal(0, 0.03), 0.15, 0.5)
            diabetes = np.clip(0.04 + 0.2 * inactivity + rng.normal(0, 0.015), 0.05, 0.2)
            row = {"statecode": sc, "countycode": cc, "fipscode": f"{sc}{cc}",
                   "state": abbr, "county": f"Sample County {i}",
                   "v132_rawvalue": round(access, 4), "v060_rawvalue": round(diabetes, 4),
                   "v011_rawvalue": round(obesity, 4), "v070_rawvalue": round(inactivity, 4),
                   "v063_rawvalue": round(income), "v085_rawvalue": round(rng.uniform(0.05, 0.3), 4)}
            # Leave some values blank, like the real file
            if rng.random() < 0.03:
                row["v132_rawvalue"] = None
            rows.append(row)
            counties.append(row)

    # Fake stand-in for the target county so the default tract runs work.
    # Values are random like everything else here, NOT the real county's numbers.
    sc, cc = config.TARGET_COUNTY_FIPS[:2], config.TARGET_COUNTY_FIPS[2:]
    target = {"statecode": sc, "countycode": cc, "fipscode": config.TARGET_COUNTY_FIPS,
              "state": "TX", "county": "Sample Target County",
              "v132_rawvalue": 0.45, "v060_rawvalue": 0.13, "v011_rawvalue": 0.42,
              "v070_rawvalue": 0.34, "v063_rawvalue": 50000, "v085_rawvalue": 0.28}
    rows.append(target)
    counties.append(target)
    return rows, counties


def write_chr(rows):
    """Write a workbook laid out like the real 2025 CHR file: two sheets,
    each with column names on row 2 and values as percentages."""
    src = pd.DataFrame(rows)
    ids = pd.DataFrame({
        "FIPS": src["fipscode"],
        "State": src["state"],
        # State and national summary rows have a blank county name in the real file
        "County": src["county"].where(src["countycode"] != "000"),
    })
    pct = lambda col: (src[col] * 100).round(2)
    select = ids.assign(**{
        "% With Access to Exercise Opportunities": pct("v132_rawvalue"),
        "% Uninsured": pct("v085_rawvalue"),
    })
    additional = ids.assign(**{
        "% Adults with Diabetes": pct("v060_rawvalue"),
        "% Adults with Obesity": pct("v011_rawvalue"),
        "% Physically Inactive": pct("v070_rawvalue"),
        "Median Household Income": src["v063_rawvalue"],
    })
    path = config.SAMPLE_DIR / config.CHR_FILE
    with pd.ExcelWriter(path) as xl:
        # startrow=1 leaves row 1 for the measure-group labels, like the real file
        select.to_excel(xl, sheet_name="Select Measure Data", index=False, startrow=1)
        additional.to_excel(xl, sheet_name="Additional Measure Data", index=False, startrow=1)
    return path


def write_places(counties):
    measure_names = {"DIABETES": "Diagnosed diabetes among adults",
                     "OBESITY": "Obesity among adults",
                     "LPA": "No leisure-time physical activity among adults",
                     "CSMOKING": "Current cigarette smoking among adults"}
    out = []
    for c in counties:
        n_tracts = TARGET_TRACTS if c["fipscode"] == config.TARGET_COUNTY_FIPS else TRACTS_PER_COUNTY
        for t in range(1, n_tracts + 1):
            tract = f"{c['fipscode']}{t * 100:06d}"
            base = c["v070_rawvalue"] * 100
            values = {"LPA": base + rng.normal(0, 4)}
            values["OBESITY"] = 25 + 0.5 * values["LPA"] + rng.normal(0, 3)
            values["DIABETES"] = 4 + 0.2 * values["LPA"] + rng.normal(0, 1.5)
            values["CSMOKING"] = rng.uniform(8, 25)  # extra measure the loader should drop
            pop = int(rng.integers(1500, 8000))
            for mid, val in values.items():
                out.append({"Year": 2022, "StateAbbr": c["state"], "CountyName": c["county"],
                            "CountyFIPS": c["fipscode"], "LocationName": tract,
                            "Measure": measure_names[mid], "MeasureId": mid,
                            "Data_Value_Type": "Crude prevalence",
                            "Data_Value": round(float(np.clip(val, 1, 70)), 1),
                            "TotalPopulation": pop})
    path = config.SAMPLE_DIR / config.PLACES_FILE
    pd.DataFrame(out).to_csv(path, index=False)
    return path, len(out)


def main():
    config.SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    rows, counties = make_chr()
    chr_path = write_chr(rows)
    places_path, n = write_places(counties)
    print(f"Wrote {len(counties)} fake counties to {chr_path.relative_to(config.ROOT)}")
    print(f"Wrote {n:,} fake tract rows to {places_path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
