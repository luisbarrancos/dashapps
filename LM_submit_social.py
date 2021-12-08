#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 11:12:43 2021

@author: cgwork
"""

# Dataframes, DBs
import os
import urllib
from datetime import datetime, timedelta
from random import random

# Dashboards modules
import dash
import dash_bootstrap_components as dbc
import pandas as pd

# for post
import requests
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dotenv import load_dotenv
from sqlalchemy import create_engine

from app import app

# custom classes
from UserData import UserData

# computed stats
df = pd.read_sql_table(
    "UserStats",
    "sqlite:///" + os.path.join(os.getcwd(), "assets", "computed_stats.sql"),
    index_col="index",
)

load_dotenv()

MASTODON_TOKEN = os.environ.get("MASTODON_TOKEN")

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
            html.Div(
                style={
                    "text-align": "left",
                    "font-size": 32,
                    "margin": "auto",
                    "width": "50%",
                    "padding": "20px",
                },
                children=[
                    html.P("Share Your Statistics:", style={"padding-bottom": "2em"}),
                    html.Div(
                        [
                            html.A(
                                [
                                    html.Img(
                                        src=app.get_asset_url("twitter.png"),
                                        style={
                                            "height": "140px",
                                            "width": "140px",
                                            "padding": "10px",
                                        },
                                    ),
                                ],
                                href="https://twitter.com/intent/tweet?text="
                                + urllib.parse.quote(
                                    (
                                        df["time_left"].values[0]
                                        + "\n\n"
                                        + df["life_spent"].values[0]
                                        + "\n\n"
                                        + df["life_compare"].values[0]
                                        + "\n\n"
                                        + df["school"].values[0]
                                        + "\n\n"
                                        + df["co2_stats"].values[0]
                                    )[:276]
                                    + " ...",
                                    safe="/",
                                ),
                            ),
                            html.Img(
                                src=app.get_asset_url("instagram.jpg"),
                                style={
                                    "height": "140px",
                                    "width": "140px",
                                    "padding": "10px",
                                },
                            ),
                            html.Img(
                                src=app.get_asset_url("facebook.png"),
                                style={
                                    "height": "140px",
                                    "width": "140px",
                                    "padding": "10px",
                                },
                            ),
                            html.A(
                                id="a-link",
                                children=[
                                    html.Img(
                                        src=app.get_asset_url("mastodon.png"),
                                        style={
                                            "height": "140px",
                                            "width": "140px",
                                            "padding": "10px",
                                            "cursor": "pointer",
                                        },
                                    )
                                ],
                            ),
                        ],
                        style={"textAlign": "center"},
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
                        "background-color": "#111",
                        "color": "#ffffff",
                    },
                    id="submit-button-state",
                    n_clicks=0,
                    children="Submit",
                    color="Primary",
                    className="me-1",
                    href="/page1",
                ),
                className="d-grip gap-2 d-md-flex justify-content-md-end",
            ),
            html.Div(id="output-submit-social"),
        ],
    )
)


def post_to_mastodon(toot, tags):
    token = MASTODON_TOKEN
    headers = {}
    data = {}
    hashtags = tags

    headers["Authorization"] = "Bearer " + token
    url = "https://botsin.space/api/v1/statuses"

    # toots are 500 chars max
    data["status"] = toot + hashtags
    data["visibility"] = "public"

    retdata = requests.post(url=url, json=data, headers=headers)

    return retdata


@app.callback(
    Output(component_id="output-submit-social", component_property="children"),
    [
        Input(component_id="a-link", component_property="n_clicks"),
    ],
)
def mastodon(n_clicks):

    toot = (
        df["time_left"].values[0]
        + "\n\n"
        + df["life_spent"].values[0]
        + "\n\n"
        + df["life_compare"].values[0]
        + "\n\n"
        + df["school"].values[0]
        + "\n\n"
        + df["co2_stats"].values[0]
        + "\n\n"
    )

    poverty = str(df["poverty"].values[0])

    app.logger.info("Toot lenght (500 chars max) = {}".format(len(toot + poverty)))

    if len(toot + poverty) < 500:
        toot += poverty

        # + df["poverty"].values[0]
        # Toots are limited to 500 chars. the last statistic would make it
        # go over this limit and we still need a safety margin.
        # + "\n"
        # + df["suic"]
        # + "\n"

    # app.logger.info(toot)

    tags = "\n\n#multimedia\n#databiz"

    if n_clicks is None:
        raise PreventUpdate
    else:
        status_code = post_to_mastodon(toot, tags)
        app.logger.info("Tried posting, code = {}".format(status_code))

    return None


# @app.callback(
#     Output(component_id="output-submit-social", component_property="children"),
#     [
#         Input(component_id="submit-button-state", component_property="n_clicks"),
#     ],
# )
# def update_output_div(n_clicks):
#     if n_clicks is None:
#         raise PreventUpdate

#     return ""

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
