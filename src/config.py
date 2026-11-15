"""Shared settings for the project: file paths, column names, and scope."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
SAMPLE_DIR = RAW_DIR / "sample"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "figures"

# Raw file names. Put the real downloads in data/raw/ with these names.
CHR_FILE = "2025_County_Health_Rankings_Data_v4.xlsx"
PLACES_FILE = "places_tract_2025.csv"

# County Health Rankings 2025 data workbook (dataset 1).
# Each sheet has two header rows: a measure group on row 1 and column names
# on row 2, so we read with header=1. The 9 variables from our proposal are
# split across two sheets. Values are already percentages.
CHR_SHEETS = {
    "Select Measure Data": {
        "% With Access to Exercise Opportunities": "exercise_access",
        "% Uninsured": "uninsured",               # % under 65 without health insurance
    },
    "Additional Measure Data": {
        "% Adults with Diabetes": "diabetes",
        "% Adults with Obesity": "obesity",
        "% Physically Inactive": "inactivity",    # no leisure-time physical activity
        "Median Household Income": "median_income",
    },
}
CHR_ID_COLUMNS = {"FIPS": "fips", "State": "state", "County": "county"}

# CDC PLACES census tract data, 2025 release (dataset 2).
# Long format: one row per tract per measure. We keep these three.
PLACES_MEASURES = {
    "DIABETES": "diabetes",
    "OBESITY": "obesity",
    "LPA": "inactivity",  # LPA = no leisure-time physical activity
}

# Tract-level focus from the proposal: Hidalgo County, Texas.
# Change this one value to study a different county.
TARGET_COUNTY_FIPS = "48215"
TARGET_COUNTY_NAME = "Hidalgo County, TX"

OUTCOMES = ["inactivity", "obesity", "diabetes"]
CONTROLS = ["median_income", "uninsured"]
