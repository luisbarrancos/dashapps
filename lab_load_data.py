#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 22:17:25 2021

@author: cgwork
"""

import os
import pandas as pd

datapath = os.path.join(os.getcwd(), "data2")
if os.path.isdir(datapath):
    datafiles = [f for f in os.listdir(datapath) if \
                 os.path.isfile(os.path.join(datapath, f))]

# For these files, split the extension, capitalize and append them to
# a dictionary which will contain as key the name minus extension and as
# value the # Pandas DataFrame
datadict = dict()

for f in datafiles:
    datadict[((f.rsplit(".", 1)[0]).capitalize())] = \
        pd.read_csv(os.path.join(datapath, f), index_col = "Country")

for key, val in datadict.items():
    print(key)
"""
Anual_number_of_deaths_by_cause
Life_satisfaction_in_cantril_ladder_world_happiness_report_2021
Life_expectancy
Life_expectancy_at_birth
Extreme_poverty_headcount_ratio_vs_life_expectancy_at_birth
Human_development_index
Mortality_rate_under_5_per_1000_live_births
Suicide_mortality_rate_per_100000_population
Annual_co2_emissions
Average_total_years_of_schooling_for_adult_population

"""

# find for each DB, the unique country/index entries
# which we convert to lists and then sets to find the
# intersection of the lists/sets

uniqndx = []

for key, val in datadict.items():
    uniqndx.append(list(datadict[key].index.unique()))

#inter = [i for i in uniqndx[0]]
countries = []

for i, val in enumerate(uniqndx):
    countries = list(set(countries).intersection(set(uniqndx[i]))) \
        if i != 0 else [i for i in uniqndx[0]]

print(len(countries))


