#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 11:12:43 2021

@author: cgwork
"""

from app import app

# Dataframes, DBs
import os
import pandas as pd
import numpy as np


# Dashboards modules
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime

import random as rng

from sqlalchemy import create_engine

import dash_bootstrap_components as dbc

# custom classes
from UserData import UserData


# All the data was previsously processed in jupyterlab notebooks
# and we exported a final No-NaNs SQLite3 database
# So, we load it directly and get the countries.
# There are 158 here, but the intersection gives us 159
#
df1 = pd.read_sql_table(
    "Deadline_database", "sqlite:///deadline_database_nonans.db", index_col="Country"
)

df2 = pd.read_sql_table(
    "UserData",
    "sqlite:///" + os.path.join(os.getcwd(), "assets", "userdata.sql"),
    index_col="index",
)

# =============================================================================
#
# external_stylesheets = [dbc.themes.DARKLY]
#
# app = dash.Dash(
#     __name__,
#     external_stylesheets=external_stylesheets,
#     # assets_url_path=os.path.join(os.getcwd(), "assets",
# )
#
# server = app.server
#
# =============================================================================

# country dropdowns require list of unique names
countries = list(df1.index.unique())
country_options = [{"label": str(val), "value": str(val)} for val in countries]

# app.logger.info(country_options)
dropdown_style = {
    "margin-left": "20px",
    "margin-right": "50px",
    "color": "#ffffff",
    "background-color": "#000000",
}


def get_time(max_age):
    # max age is float years, get months, days, hours, secs, mins
    total_seconds = max_age * 31536000  # 365 * 24 * 60 * 60
    tmins, tsecs = divmod(total_seconds, 60)
    thours, tmins = divmod(tmins, 60)
    tdays, thours = divmod(thours, 24)
    tmonths, tdays = divmod(tdays, 30)
    tyears, tmonths = divmod(tmonths, 12)

    tyears = int(tyears)
    tmonths = int(tmonths)
    tdays = int(tdays)
    thours = int(thours)
    tmins = int(tmins)
    tsecs = int(tsecs)

    return (tyears, tmonths, tdays, thours, tmins, tsecs)


# functions to create user assessment vs statistical data
def generate_stats(dfc, dfu):

    # dfc = country DB, dfu = user database

    dfn = dfc.loc[dfu["birthplace"]]

    # latest value for life expectation (we can do LR later)
    max_user_age = dfn[dfn["Year"] == dfn["Year"].max()]["Life_expectancy"].values[0]
    user_age = dfu["age"]

    # store life spent (percentage)
    life_spent = (user_age / float(max_user_age)) * 100
    data = dict()
    data["life_spent"] = life_spent
    data["max_age"] = max_user_age

    # stat date at 1/1/year, i.e, 1/1/2017, but no linear regression yet
    # we also know birth date (year at least)
    # and we know life expectancy
    # and current time

    # get the current Y/M/D
    current_date = datetime.today()
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day

    user_birth_year = current_year - user_age
    data["birth_year"] = user_birth_year

    # max age is float years, get months, days, hours, secs, mins
    ti = get_time(max_user_age * 31536000)  # 365 * 24 * 60 * 60

    # build time left string
    time_left = (
        "You're expected to live another {} year, "
        + "{} month, {} days and {} hours".format(ti[0], ti[1], ti[2], ti[3])
    )

    data["time_left"] = (ti[0], ti[1], ti[2], ti[3], ti[4])
    data["time_left_str"] = time_left

    # now set the target date for the countdown, adjust for date overflow
    fmonth, fday = divmod(current_day + ti[2], 30)
    fyear, fmonth = divmod(current_month + ti[1] + fmonth, 12)

    fyear = int(fyear)
    fmonth = int(fmonth)
    fday = int(fday)

    # set the target date for the event, and start the countdown
    app.logger.info("year {}, month {}, day {}".format(fyear, fmonth, fday))
    target_date = datetime(year=fyear, month=fmonth+1, day=fday+1)
    data["target_date"] = target_date

    # compute user expected CO2 fingerprint
    minyear = dfn["Year"].min()
    maxyear = dfn["Year"].max()
    data["minyear"] = minyear
    data["maxyear"] = maxyear

    latest_yco2 = dfn[dfn["Year"] == maxyear]["Annual_CO2_emissions"].values[0]
    latest_tpop = dfn[dfn["Year"] == maxyear]["Total_population"].values[0]

    user_co2 = latest_yco2 / float(latest_tpop)
    data["latest_CO2_fingerprint"] = user_co2

    totalco2 = dfn["Annual_CO2_emissions"].sum() / (
        dfn["Total_population"].sum() / len(dfn["Total_population"])
    )

    data["total_CO2_from_{}_to_{}".format(minyear, maxyear)] = totalco2

    # suicide data (% population, adjusted)
    latest_suic = dfn[dfn["Year"] == maxyear][
        "Suicidy_mortality_rate_per_100000_population"
    ].values[0]

    population_adjusted = latest_tpop / 100000.0
    suic_rate = latest_suic / population_adjusted
    data["suicide_rate"] = suic_rate

    # is it an increasing or decreasing likelyhood?
    if minyear < maxyear:
        tsuic = dfn[dfn["Year"] == maxyear - 1][
            "Suicidy_mortality_rate_per_100000_population"
        ].values[0]

        # if latest data < previous, ratio < 1, tendency decreasing
        # else ratio > 1, tendency increasing
        data["suicide_tendency"] = latest_suic / max(0.0000001, tsuic)

    # Average_total_year_of_schooling_for_adult_population
    key = "Average_total_years_of_schooling_for_adult_population"
    last_school_avg = dfn[dfn["Year"] == maxyear][key].values[0]
    ts = get_time(last_school_avg * 31536000)  # 365 * 24 * 60 * 60
    data["avg_schooling_years"] = ts # (Y, M, D, H, S)

    # of your time left to live, on average you spent these in schooling, time
    # well spent

    # poverty share % pop, latest only, 1 element
    key = "Share_of_population_below_poverty_line_2USD_per_day"
    poverty_rate = dfn[dfn["Year"] == maxyear][key].values[0]
    poverty_num = (latest_tpop / 100.0) * poverty_rate
    # there are N persons around you living below the poverty line with
    # less than 2USD per day
    data["num_people_below_poverty"] = int(poverty_num)

    # compare with other countries, only one
    sampled_country = rng.sample(list(dfc.index.unique()), 1)

    dfn = dfc.loc[sampled_country]
    data["sampled_country"] = sampled_country

    # latest value for life expectation (we can do LR later)
    max_age = dfn[dfn["Year"] == dfn["Year"].max()]["Life_expectancy"].values[0]
    tm = get_time(max_age * 31536000)  # 365 * 24 * 60 * 60

    data["sampled_country_max_age"] = max_age  # (Y, M, D, H, S)
    # Compared with someone from Country, you'll live +/- years
    delta = get_time(max_user_age * 31536000 - max_age * 31536000)

    data["sampled_country_delta_age"] = delta  # (Y, M, D, H, S)
    app.logger.info(data)

    return data


def start_countdown(target_date):
    countdown = target_date - datetime.now()


### Buttons
# buttons = html.Div(
#    [
#        dbc.Button("Regular", color="primary", className="me-1"),
#        dbc.Button("Active", color="primary", active=True, className="+me-1"),
#        dbc.Button("Disabled", color="primary", disabled=True),
#    ]
# )

# layout
layout = html.Form(
    html.Div(
        style={
            "font-family": "Sawasdee",
            "font-size": 22,
            "color": "#ffffff",
            "background-color": "#111111",
        },
        children=[
            html.Br(),
            html.H1(style={"text-align": "left"}, children=""),
            # header
            html.Br(),
            html.P(
                style={
                    "text-align": "left",
                    "font-size": 32,
                    "margin-left": "20px",
                },
                children="Your data shows that:",
            ),
            html.Br(),
            html.Div(
                dbc.Button(
                    style={
                        "font-size": 22,
                        "margin-left": "20px",
                        "margin-right": "80px",
                        "background-color": "#111",
                        "color": "#ffffff",
                    },
                    id="submit-button-state",
                    n_clicks=0,
                    children="Submit",
                    color="Primary",
                    className="me-1",
                    href="/page6",
                ),
                className="d-grip gap-2 d-md-flex justify-content-md-end",
            ),
            html.Div(id="output-user-algo"),
        ],
    )
)


@app.callback(
    Output(component_id="output-user-algo", component_property="component"),
    [
        Input(component_id="submit-button-state", component_property="n_clicks"),
    ],
)
def update_output_div(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    data = generate_stats(df1, df2)
    # app.logger.info(data)

    time_left = (
        "{}, {} years old, natural from {} has "
        + "approximately {} years,"
        + " {} months and {} days left to live".format(
            df2["name"],
            df2["age"],
            df2["birthplace"],
            data["time_left"][0],
            data["time_left"][1],
            data["time_left"][2],
        )
    )

    delta = 1
    for f in data["sampled_country_delta_age"]:
        if f < 0:
            delta = -1
            break

    life_cmp = \
        "He'll get to live until {} years old. Were he born in {}" \
        + " and he would get to live {} years, {} months, {} days, " \
        + "{} hours, {} seconds {}".format(
            data["max_age"],
            data["sampled_country"],
            data["sampled_country_delta_age"][0],
            data["sampled_country_delta_age"][1],
            data["sampled_country_delta_age"][2],
            data["sampled_country_delta_age"][3],
            data["sampled_country_delta_age"][4],
            "more." if delta == 1 else "less.",
        )

    school = "Of that time, {} years, {} months, {} days, {} hours will be" \
        + "(well) spent in school".format(
            data["avg_schooling_years"][0],
            data["avg_schooling_years"][1],
            data["avg_schooling_years"][2],
            data["avg_schooling_years"][3])


    if df2["sex"].values[0] == "F":
        life_cmp.replace("He'll ", "She'll ")
        life_cmp.replace(" he ", " she ")

    co2_stats = (
        "His last CO2 fingerprint was {.3f} tons and"
        + " he emitted a combined {.3f} tons of CO2 "
        + "from {} to {}.".format(
            data["latest_CO2_fingerprint"],
            data["total_CO2_from_2006_to_2017"],
            data["minyear"],
            data["maxyear"],
        )
    )

    if df2["sex"].values[0] == "F":
        co2_stats.replace("His ", "Her ")
        co2_stats.replace(" his ", " her ")

    poverty = "Around {}, there are {} people below the poverty line.".format(
        "him" if df2["sex"].values[0] == "M" else "her",
        data["num_people_below_poverty"])

    suic = "Thought the number of suicides is {}, there are {} suicies".format(
        "decreasing" if data["suicide_tendency"] < 1 else "increasing", 2, 3)

    return data


# =============================================================================
#
# if __name__ == "__main__":
#     # app.run_server(debug=True)
#     app.run_server(
#         host="127.0.0.1",
#         port="8050",
#         proxy=None,
#         debug=True,
#         # dev_tools_props_check=None,
#         # dev_tools_serve_dev_bundles=None,
#         # dev_tools_hot_reload=None,
#         # dev_tools_hot_reload_interval=None,
#         # dev_tools_hot_reload_watch_interval=None,
#         # dev_tools_hot_reload_max_retry=None,
#         # dev_tools_silence_routes_logging=None,
#         # dev_tools_prune_errors=None,
#         # **flask_run_options
#     )
#
# =============================================================================
