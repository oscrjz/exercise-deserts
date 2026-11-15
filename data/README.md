# Data

The cleaned files in `data/processed/` are committed, so you can start analyzing right away without downloading anything.

The raw files in `data/raw/` are not committed. You only need them if you change a loader and want to rebuild the cleaned files. To do that, download them, save them in `data/raw/` with the names below, and rerun the loaders.

## Cleaned files

| File | Rows | Columns |
| --- | --- | --- |
| `processed/chr_counties.csv` | 3,159 US counties | fips, state, county, exercise_access, uninsured, diabetes, obesity, inactivity, median_income |
| `processed/places_tracts_48215.csv` | 211 Hidalgo County tracts | tract_fips, state, county, county_fips, population, diabetes, inactivity, obesity |

All values except income and population are percentages.

## County Health Rankings 2025 data workbook

- Download: https://www.countyhealthrankings.org/health-data/methodology-and-sources/data-documentation
- Pick the 2025 County Health Rankings Excel data file
- Save as: `data/raw/2025_County_Health_Rankings_Data_v4.xlsx`
- Backup copy: https://zenodo.org/records/17832488

The countyhealthrankings.org site is only guaranteed to stay up through December 2026.

The columns we use are split across two sheets:

| Sheet | Column in the workbook | Our name |
| --- | --- | --- |
| Select Measure Data | % With Access to Exercise Opportunities | exercise_access |
| Select Measure Data | % Uninsured | uninsured |
| Additional Measure Data | % Adults with Diabetes | diabetes |
| Additional Measure Data | % Adults with Obesity | obesity |
| Additional Measure Data | % Physically Inactive | inactivity |
| Additional Measure Data | Median Household Income | median_income |

`load_chr.py` reads both sheets, joins them on FIPS, and drops the national and state summary rows. Some counties are missing values, mostly for exercise access, which is blank for 62 counties.

## CDC PLACES census tract data, 2025 release

- Dataset page: https://data.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-Census-Tract-D/cwsq-ngmh
- Save as: `data/raw/places_tract_2025.csv`

The full file is about 3 million rows. You don't need all of it. On the dataset page, use **Actions > Query data**, filter CountyFIPS to `48215`, and export as CSV. That gives about 7,000 rows covering every PLACES measure for Hidalgo County.

`load_places.py` keeps three measures and pivots to one row per tract:

| MeasureId | Our name | Meaning |
| --- | --- | --- |
| DIABETES | diabetes | Percent of adults with diagnosed diabetes |
| OBESITY | obesity | Percent of adults with obesity |
| LPA | inactivity | Percent of adults with no leisure-time physical activity |

That goes from 633 rows to 211 tracts. Values are model-based estimates, not direct counts. The 2025 release uses mostly 2023 survey data, with a few measures from 2022.

PLACES has no exercise access measure, so linking tracts to access needs a separate source of park and facility locations. Two options to look at are the Trust for Public Land ParkServe data at https://www.tpl.org/park-data-downloads and OpenStreetMap.
