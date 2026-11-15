# Project Proposal: Exercise Deserts

Group 8. This is the proposal as submitted, kept here for reference.

## Idea

An exercise desert is an area where residents have little access to places for physical activity, such as parks, recreation centers, or walkable streets. Our project looks at where these areas are and how they relate to health. We plan to start with a county level comparison across the US, then look at the neighborhood level to see how access varies within communities. We may narrow to a specific state or region as the project develops.

## Description of dataset 1

2025 CHR CSV Analytic Data  is published by  University of Wisconsin Population Health Institute and funded by Robert Wood Johnson Foundation. It was released in 2025, but mostly all of the data was conjured up during 2022 except for the exercise_access variable that uses data from 2020 to 2024. 

Of it we only kept the 3152 county rows and kept 9 key variables for our experiment. FIPS(Standard County Id number), state, County name, exercise_access(percentage of residents that live next to a park or a recreational facility), diabetes, obesity, inactivity, median_income, and uninsured. Limitations: undiagnosed diabetes does not count, we cannot differentiate between diabetes 1 and 2(but an estimate of 90% of Americans who are diabetic are type 2), and prediabetes doesn't count to the stats.

## Description of dataset 2

(https://catalog.data.gov/dataset/places-local-data-for-better-health-census-tract-data-2024-release)PLACES was funded by the Robert Wood Johnson Foundation in conjunction with the CDC Foundation. Released in 2025 with most data made in 2023. The file has 3,047,284 rows and 24 columns. It’s large because it covers every census tract (neighborhood) in the U.S., and each tract is repeated once for every health measure. We would filter it to Hidalgo County (to look deeper into this specific county) and three measures (diabetes, obesity, and physical inactivity), then reshape it to one row per tract. This would take it from 633 rows (211 tracts × 3 measures) to 211 rows, one per neighborhood. Values are percentages, and the numbers are model-based estimates. The dataset does not include exercise access, so we would need a separate source of park and facility locations to link neighborhoods to exercise access.

## Main question, hypothesis, problem, or objective

Do US counties with less access to exercise opportunities have higher rates of physical activity, obesity, and diabetes? We hypothesize that they do, and that the relationship holds, though weaker, after accounting for median income and the uninsured rate. Our second objective is to look inside Hidalgo County: how much do these three outcomes vary from one neighborhood to the next, and where are the highest rates concentrated?

## Methods, tools, or approaches

We are still deciding on our exact approach. We expect to work in Python, starting with cleaning and combining the two datasets, then exploring the data through summary statistics and visualizations to see how exercise access relates to physical inactivity, obesity, and diabetes. Depending on what we find, we may add a statistical model or maps later in the project.
