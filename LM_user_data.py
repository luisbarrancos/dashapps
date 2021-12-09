#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 11:12:43 2021

@author: cgwork
"""

# Dataframes, DBs
import os

import dash_bootstrap_components as dbc
import pandas as pd

# Dashboards modules
from dash import dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine

from app import app

# custom classes
from UserData import UserData

# All the code for data filtering, processing, done in jupyterlab
# notebooks (already in github), but now we can bypass all the processing
# and go straight to the final SQLite3 DB

datapath = os.path.join(os.getcwd(), "resources", "dbs")

df = pd.read_sql_table(
    "Deadline_database",
    "sqlite:///" + os.path.join(datapath, "deadline_database_nonans_geo.db"),
    index_col="Country",
)

# df.dropna(inplace=True)
df.sort_values(by=["Year"], inplace=True)

# problem is in some dbs, like nonans_geo, we have 600 years of data
# leading to nulls everywhere except the last 15 years or so for most cols
df = df[df["Year"] >= 2000]

countries = list(df.index.unique())
country_options = [{"label": str(val), "value": str(val)} for val in countries]

# app.logger.info(country_options)
dropdown_style = {
    "margin-left": "20px",
    "margin-right": "50px",
    "color": "#ffffff",
    "background-color": "#000000",
}

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
            html.H1(style={"text-align": "left"}, children=""),
            # header
            html.Br(),
            html.P(
                style={
                    "text-align": "left",
                    "font-size": 32,
                    "margin-left": "20px",
                },
                children="Please fill-in the data:",
            ),
            # input area frame
            html.Div(
                id="input area",
                style={
                    "margin": "0 auto",
                    "width": "50%",
                    #    #"background-color": "#99d6ff",
                    "padding": "15px",
                },
                # child of input area frame | input fields
                children=[
                    dcc.Input(
                        id="user_name",
                        style={
                            "font-size": 22,
                            # "margin-left": "20px",
                            "margin-right": "50px",
                            #    "background-color" : "#000000",
                            #    "color" : "#ffffff"
                        },
                        value=None,
                        type="text",
                        inputMode="latin-name",
                        placeholder="Name",
                    ),
                    # user age, should be int
                    html.Br(),
                    html.Br(),
                    dcc.Input(
                        id="user_age",
                        style={
                            "font-size": 22,
                            # "margin-left": "20px",
                            "margin-right": "50px",
                            #    "background-color" : "#000000",
                            #    "color" : "#ffffff"
                        },
                        type="number",
                        min=0,
                        max=120,
                        step=1,
                        inputMode="numeric",
                        value=None,
                        placeholder="Age",
                    ),
                    # period frequency, float?
                    html.Br(),
                    html.Br(),
                    dcc.Dropdown(
                        id="birthplace",
                        options=country_options,
                        value=None,
                        placeholder="Birthplace (Country)",
                    ),
                    # period frequency, float?
                    html.Br(),
                    dcc.Dropdown(
                        id="residence",
                        options=country_options,
                        value=None,
                        placeholder="Country of Residence",
                    ),
                    html.Br(),
                    dcc.Dropdown(
                        id="sex",
                        value=None,
                        options=[
                            {"label": "M", "value": "M"},
                            {"label": "F", "value": "F"},
                        ],
                        placeholder="Biological Sex",
                    ),
                    html.Br(),
                    dcc.Dropdown(
                        id="veggie",
                        value=None,
                        options=[
                            {"label": "Y", "value": "Y"},
                            {"label": "N", "value": "N"},
                        ],
                        placeholder="Are you a vegetarian?",
                    ),
                    html.Br(),
                    dcc.Dropdown(
                        id="driver",
                        value=None,
                        options=[
                            {"label": "Y", "value": "Y"},
                            {"label": "N", "value": "N"},
                        ],
                        placeholder="Do you drive a car?",
                    ),
                    html.Br(),
                    dcc.Dropdown(
                        id="smoker",
                        value=None,
                        options=[
                            {"label": "Y", "value": "Y"},
                            {"label": "N", "value": "N"},
                        ],
                        placeholder="Are you a Smoker?",
                    ),
                ],
            ),
            html.Br(),
            html.Div(
                dbc.Button(
                    id="submit-button-state",
                    style={
                        "font-size": 22,
                        "margin-left": "20px",
                        "margin-right": "80px",
                        "background-color": "#111",
                        "color": "#ffffff",
                    },
                    n_clicks=0,
                    children="Submit",
                    color="Primary",
                    className="me-1",
                    href="/page1",
                ),
                className="d-grip gap-2 d-md-flex justify-content-md-end",
            ),
            html.Div(id="my-output"),
            html.Div(id="output_graph"),
            html.Div(id="output_text", style={"text-align": "center", "color": "blue"}),
        ],
    )
)


# Narrow options on dropdown
@app.callback(Output("birthplace", "options"), Input("birthplace", "search_value"))
def update_options_b(search_value):
    if not search_value:
        raise PreventUpdate
    return [o for o in country_options if search_value in o["label"]]


@app.callback(Output("residence", "options"), Input("residence", "search_value"))
def update_options_r(search_value):
    if not search_value:
        raise PreventUpdate
    return [o for o in country_options if search_value in o["label"]]


@app.callback(
    Output(component_id="my-output", component_property="children"),
    [
        Input(component_id="user_name", component_property="value"),
        Input(component_id="user_age", component_property="value"),
        Input(component_id="birthplace", component_property="value"),
        Input(component_id="residence", component_property="value"),
        Input(component_id="sex", component_property="value"),
        Input(component_id="veggie", component_property="value"),
        Input(component_id="driver", component_property="value"),
        Input(component_id="smoker", component_property="value"),
        Input(component_id="submit-button-state", component_property="n_clicks"),
    ],
)
def update_output_div(
    user_name, user_age, birthplace, residence, sex, veggie, driver, smoker, n_clicks
):
    if (
        user_name is None
        or user_age is None
        or birthplace is None
        or residence is None
        or sex is None
        or veggie is None
        or driver is None
        or smoker is None
        or n_clicks is None
    ):
        raise PreventUpdate

    userdata_ = UserData(
        user_name, user_age, birthplace, residence, sex, veggie, driver, smoker
    )

    # for now, create a dataframe from user data/dictionary and write to
    # a sql DB, then load it.
    df = pd.DataFrame.from_dict(userdata_.get_dict(), orient="columns")
    # app.logger.info(df)

    sqldb = os.path.join(datapath, "userdata.db")
    engine = create_engine("sqlite:///" + sqldb, echo=False)
    conn = engine.connect()

    df.to_sql("UserData", conn, if_exists="replace")
    conn.close()
