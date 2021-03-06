#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 11:12:43 2021

@author: cgwork
"""

# Dataframes, DBs
import os
import random as rng
from datetime import datetime, timedelta
from random import random

# Dashboards modules
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine

from app import app

# All the code for data filtering, processing, done in jupyterlab
# notebooks (already in github), but now we can bypass all the processing
# and go straight to the final SQLite3 DB

datapath = os.path.join(os.getcwd(), "resources", "dbs")

df1 = pd.read_sql_table(
    "Deadline_database",
    "sqlite:///" + os.path.join(datapath, "deadline_database_nonans_geo.db"),
    index_col="Country",
)

df1.dropna(inplace=True)
# df1.sort_values(by=["Year"], inplace=True)

# problem is in some dbs, like nonans_geo, we have 600 years of data
# leading to nulls everywhere except the last 15 years or so for most cols
df1 = df1[df1["Year"] >= 2000]

countries = list(df1.index.unique())
country_options = [{"label": str(val), "value": str(val)} for val in countries]


summary = {
    "time_left": "",
    "life_spent": "",
    "life_compare": "",
    "school": "",
    "co2_stats": "",
    "poverty": "",
    "suic": "",
}

# country dropdowns require list of unique names
countries = list(df1.index.unique())
country_options = [{"label": str(val), "value": str(val)} for val in countries]

# app.logger.info(country_options)
dropdown_style = {
    "marginLeft": "20px",
    "marginRight": "50px",
    "color": "#ffffff",
    "backgroundColor": "#000000",
}


def convert_partial_year(number):
    year = int(number)
    d = timedelta(days=(number - year) * 365)
    # year 0 issue in datetime
    day_one = datetime(max(1, year), 1, 1)
    date = d + day_one
    return date


# functions to create user assessment vs statistical data
def generate_stats(dfc, dfu):

    # dfc = country DB, dfu = user database

    dfn = dfc.loc[dfu["birthplace"]]

    # latest value for life expectation (we can do LR later)
    max_user_age = dfn[dfn["Year"] == dfn["Year"].max()]["Life_expectancy"].values[0]
    user_age = dfu["age"].values[0]

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

    # datetime object for max user age
    t1 = convert_partial_year(max_user_age)

    # jitter a tiny bit, convert to datetime object
    eps = random() * 0.001
    t2 = convert_partial_year(user_age + eps)

    # time left
    t3 = convert_partial_year(max_user_age - user_age - eps)

    data["birth_year"] = t1.year - user_age

    # set the target date for the event, and start the countdown
    years_to_secs = 31536000
    delta_secs = (max_user_age - user_age - eps) * years_to_secs
    data["target_data"] = current_date + timedelta(seconds=delta_secs)

    # build time left string from delta t3
    data["time_left"] = t3
    data["time_left_str"] = (
        "You're expected to live another {} year, "
        "{} month, {} days and {} hours".format(t3.year, t3.month, t3.day, t3.hour)
    )

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

    data["total_CO2"] = totalco2

    # suicide data (% population, adjusted)
    latest_suic = dfn[dfn["Year"] == maxyear][
        "Suicidy_mortality_rate_per_100000_population"
    ].values[0]

    population_adjusted = latest_tpop / 100000.0
    suic_rate = latest_suic * population_adjusted
    data["suicide_rate"] = latest_suic
    data["suicide_num"] = suic_rate

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

    # of your time left to live, on average you spent these in schooling, time
    # well spent
    ts = convert_partial_year(last_school_avg)
    data["avg_schooling_years"] = ts

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

    # max user age - sampled country max age for a +/- delta
    tm = convert_partial_year(max_age)

    # store max age and its datetime object
    data["sampled_country_max_age"] = max_age
    data["sampled_country_max_age_obj"] = tm

    # Compared with someone from Country, you'll live +/- years, abs delta
    delta = convert_partial_year(
        abs(data["max_age"] - data["sampled_country_max_age"] - random() * 0.001)
    )

    # store delta datetime object
    data["sampled_country_delta_age"] = delta
    data["sampled_country_delta_age_positive"] = (
        True if data["max_age"] < data["sampled_country_max_age"] else False
    )

    return data


def start_countdown(target_date):
    countdown = target_date - datetime.now()

def summarize_data(user_data_local): 
    # app.logger.info("========user_data_local=====")
    # app.logger.info(user_data_local)
    # app.logger.info("===========================")
    df2 = pd.DataFrame({
        "name": [user_data_local[0]],
        "age": [user_data_local[1]],
        "birthplace": [user_data_local[2]],
        "residence": [user_data_local[3]],
        "sex": [user_data_local[4]],
        "veggie": [user_data_local[5]],
        "driver": [user_data_local[6]],
        "smoker": [user_data_local[7]],
    },)



    data = generate_stats(df1, df2)

    time_left = (
        "{}, {} years old, natural from {} has {} years,"
        " {} months and {} days left to live.".format(
            df2["name"].values[0],
            df2["age"].values[0],
            df2["birthplace"].values[0],
            data["time_left"].year,
            data["time_left"].month,
            data["time_left"].day,
        )
    )

    life_spent = "{} spent {:.3f}% of his lifetime already.".format(
        "He" if df2["sex"].values[0] == "M" else "She", float(data["life_spent"])
    )

    life_compare = (
        "{} live until {} years old. Were {} born in {}"
        " {} would live {} years, {} months, {} days, "
        "{} hours {}".format(
            "He'll" if df2["sex"].values[0] == "M" else "She'll",
            data["max_age"],
            "he" if df2["sex"].values[0] == "M" else "she",
            data["sampled_country"][0],
            "he" if df2["sex"].values[0] == "M" else "she",
            data["sampled_country_delta_age"].year,
            data["sampled_country_delta_age"].month,
            data["sampled_country_delta_age"].day,
            data["sampled_country_delta_age"].hour,
            "more." if data["sampled_country_delta_age_positive"] is True else "less.",
        )
    )

    school = "{} years, {} months, {} days were " " (well) spent in school".format(
        data["avg_schooling_years"].year,
        data["avg_schooling_years"].month,
        data["avg_schooling_years"].day,
    )

    co2_stats = (
        "{} last CO2 fingerprint was {:.3f} tons and"
        " {} emitted {:.3f} tons of CO2 "
        "from {} to {}.".format(
            "His" if df2["sex"].values[0] == "M" else "Her",
            data["latest_CO2_fingerprint"],
            "he" if df2["sex"].values[0] == "M" else "she",
            data["total_CO2"],
            data["minyear"],
            data["maxyear"],
        )
    )

    if data["num_people_below_poverty"] == 0:
        poverty = "No poverty data available."
    else:
        poverty = "Around {}, {} people below the poverty line.".format(
            "him" if df2["sex"].values[0] == "M" else "her",
            data["num_people_below_poverty"],
        )

    suic = "The number of suicides is {}, the last data shows" " {} suicides.".format(
        "decreasing" if data["suicide_tendency"] < 1 else "increasing",
        round(data["suicide_num"]),
    )

    # create a dataframe with the formatted output for social media
    strdata = {
        "time_left": time_left,
        "life_spent": life_spent,
        "life_compare": life_compare,
        "school": school,
        "co2_stats": co2_stats,
        "poverty": poverty,
        "suic": suic,
    }
    # df = pd.DataFrame.from_dict(strdata, orient="columns")

    # summary = {
    #     "time_left" : "",
    #     "life_spent" : "",
    #     "life_compare" : "",
    #     "school" : "",
    #     "co2_stats" : "",
    #     "poverty" : "",
    #     "suic" : "",
    # }

    return strdata


layout = html.Form(
    html.Div(
        style={
            "fontFamily": "Sawasdee",
            "fontSize": 22,
            "color": "#ffffff",
            "backgroundColor": "#111111",
        },
        children=[
            html.Br(),
            html.H1(style={"textAlign": "left"}, children=""),
            # header
            html.Br(),
            html.P(
                style={
                    "textAlign": "left",
                    "fontSize": 32,
                    "marginLeft": "20px",
                },
                children="Available data shows that",
            ),
            html.Div(
                id="output-textbox-div",
                style={
                    "fontFamily": "Sawasdee",
                    "fontSize": 18,
                    "color": "#ffffff",
                    "backgroundColor": "#111111",
                    "padding": "5%",
                },
                children=[
                    html.P(id="output-time-left"),
                    html.P(id="output-life-spent"),
                    html.P(id="output-life-compare"),
                    html.P(id="output-school"),
                    html.P(id="output-co2-stats"),
                    html.P(id="output-poverty"),
                    html.P(id="output-suicides"),
                ],
            ),
            html.Br(),
            html.Div(
                dbc.Button(
                    style={
                        "fontSize": 22,
                        "marginLeft": "20px",
                        "marginRight": "80px",
                        "backgroundColor": "#111",
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
                id="div_submit",
            ),
            html.Div(
                id="div_restart",
                children=[],
            ),
            html.Div(id="output-user-algo"),
        ],
    )
)


@app.callback(
    Output("dccstore_summary", "data"),
    [Input("dccstore_user", "data")],
)
def trigger_stats_generation(user_data):
    if user_data is None:
        raise PreventUpdate

    # app.logger.info("summarizing1 ... ")
    data = summarize_data(user_data)
    # app.logger.info(data)
    # app.logger.info("--end1--- ... ")

    return data


@app.callback(
    Output(component_id="output-time-left", component_property="children"),
    Output(component_id="output-life-spent", component_property="children"),
    Output(component_id="output-life-compare", component_property="children"),
    Output(component_id="output-school", component_property="children"),
    Output(component_id="output-co2-stats", component_property="children"),
    Output(component_id="output-poverty", component_property="children"),
    Output(component_id="output-suicides", component_property="children"),
    Output(component_id="div_submit", component_property="children"),
    [Input("dccstore_summary", "data"), Input("url", "pathname")],
)
def update_display_summary(summary,urlpath):
    # app.logger.info(urlpath)
    # dynamically add restart/submit  based on whether data exists
    restart = (
        dbc.Button(
            style={
                "fontSize": 22,
                "marginLeft": "20px",
                "marginRight": "80px",
                "backgroundColor": "#111",
                "color": "#ffffff",
            },
            id="submit-button-state",
            n_clicks=0,
            children="Restart",
            color="Primary",
            className="me-1",
            href="/page0",
        ),
    )
    submit = (
        dbc.Button(
            style={
                "fontSize": 22,
                "marginLeft": "20px",
                "marginRight": "80px",
                "backgroundColor": "#111",
                "color": "#ffffff",
            },
            id="submit-button-state",
            n_clicks=0,
            children="Submit",
            color="Primary",
            className="me-1",
            href="/page6",
        ),
    )
    if summary is None:
        if urlpath == "/page5":
            return (
                "There is no user data. Please restart.",
                "",
                "",
                "",
                "",
                "",
                "",
                restart,
            )
        else:
            raise PreventUpdate

    return (
        summary["time_left"],
        summary["life_spent"],
        summary["life_compare"],
        summary["school"],
        summary["co2_stats"],
        summary["poverty"],
        summary["suic"],
        submit,
    )
