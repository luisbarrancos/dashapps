#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 11:12:43 2021

@author: cgwork
"""

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

import dash_bootstrap_components as dbc

# custom classes
from UserData import UserData


# All the data was previsously processed in jupyterlab notebooks
# and we exported a final No-NaNs SQLite3 database
# So, we load it directly and get the countries.
# There are 158 here, but the intersection gives us 159
#
df = pd.DataFrame()
df = pd.read_sql_table(
    "Deadline_database", "sqlite:///deadline_database_nonans.db",
    index_col="Country"
)
countries = list(df.index.unique())

external_stylesheets = [dbc.themes.DARKLY]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    assets_url_path=os.path.join(os.getcwd(), "assets"),
)

server = app.server

country_options = [{"label": str(val), "value": str(val)} for val in countries]

# app.logger.info(country_options)
dropdown_style = {
    "margin-left": "20px",
    "margin-right": "50px",
    "color": "#ffffff",
    "background-color": "#000000",
}


### Buttons
# buttons = html.Div(
#    [
#        dbc.Button("Regular", color="primary", className="me-1"),
#        dbc.Button("Active", color="primary", active=True, className="me-1"),
#        dbc.Button("Disabled", color="primary", disabled=True),
#    ]
# )


# layout
app.layout = html.Div(
    style={
        #    "font-family": "Sawasdee",
        "font-size": 22,
        #    "color" : "#ffffff",
        #    "background-color": "#000000",
    },
    children=[
        html.H1(style={"text-align": "left"}, children=""),
        # header
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
                    style={
                        "font-size": 22,
                        "margin-left": "20px",
                        "margin-right": "50px",
                        #    "background-color" : "#000000",
                        #    "color" : "#ffffff"
                    },
                    id="user_name",
                    value="",
                    type="text",
                    inputMode="latin-name",
                    placeholder="Name",
                ),
                # user age, should be int
                html.Br(),
                html.Br(),
                dcc.Input(
                    style={
                        "font-size": 22,
                        "margin-left": "20px",
                        "margin-right": "50px",
                        #    "background-color" : "#000000",
                        #    "color" : "#ffffff"
                    },
                    id="user_age",
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
                    # style= dropdown_style,
                    id="birthplace",
                    options=country_options,
                    value=None,
                    placeholder="Birthplace (Country)",
                ),
                # period frequency, float?
                html.Br(),
                dcc.Dropdown(
                    id="residence",
                    # style=dropdown_style,
                    options=country_options,
                    value=None,
                    placeholder="Country of Residence",
                ),
                html.Br(),
                dcc.Dropdown(
                    # style=dropdown_style,
                    id="sex",
                    options=[
                        {"label": "M", "value": "M"},
                        {"label": "F", "value": "F"},
                    ],
                    placeholder="Biological Sex",
                ),
                html.Br(),
                dcc.Dropdown(
                    # style=dropdown_style,
                    id="veggie",
                    options=[
                        {"label": "Y", "value": "Y"},
                        {"label": "N", "value": "N"},
                    ],
                    placeholder="Are you a vegetarian?",
                ),
                html.Br(),
                dcc.Dropdown(
                    # style=dropdown_style,
                    id="driver",
                    options=[
                        {"label": "Y", "value": "Y"},
                        {"label": "N", "value": "N"},
                    ],
                    placeholder="Do you drive a car?",
                ),
                html.Br(),
                dcc.Dropdown(
                    # style=dropdown_style,
                    id="smoker",
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
                style={
                    "font-size": 22,
                    "margin-left": "20px",
                    "margin-right": "80px",
                    "background-color": "#222",
                    "color": "#ffffff",
                },
                id="submit-button-state",
                n_clicks=0,
                children="Submit",
                color="Primary",
                className="me-1",
            ),
            className="d-grip gap-2 d-md-flex justify-content-md-end",
        ),
        html.Div(id="my-output"),
        html.Div(id="output_graph"),
        html.Div(id="output_text", style={"text-align": "center", "color": "blue"}),
    ],
)


# Narrow options on dropdown
@app.callback(Output("birthplace", "options"), Input("birthplace", "search_value"))
def update_options(search_value):
    if not search_value:
        raise PreventUpdate
    return [o for o in country_options if search_value in o["label"]]


@app.callback(Output("residence", "options"), Input("residence", "search_value"))
def update_options(search_value):
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
    else:
        userdata_ = UserData(
            user_name, user_age, birthplace, residence, sex, veggie, driver, smoker
        )

        if userdata_.check_data() is True:
            return "Output: {}".format(userdata_.get_data())
        else:
            return "Failed check"


if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server(
        host="127.0.0.1",
        port="8050",
        proxy=None,
        debug=True,
        # dev_tools_props_check=None,
        # dev_tools_serve_dev_bundles=None,
        # dev_tools_hot_reload=None,
        # dev_tools_hot_reload_interval=None,
        # dev_tools_hot_reload_watch_interval=None,
        # dev_tools_hot_reload_max_retry=None,
        # dev_tools_silence_routes_logging=None,
        # dev_tools_prune_errors=None,
        # **flask_run_options
    )
