#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 11:12:43 2021

@author: cgwork
"""

# Dataframes, DBs
import os
import urllib

# Dashboards modules
import dash_bootstrap_components as dbc
import pandas as pd
import webbrowser

# for post
import requests
from dash import html,dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dotenv import load_dotenv

from app import app


# computed stats
# datapath = os.path.join(os.getcwd(), "resources", "dbs")

# df = pd.read_sql_table(
#     "UserStats",
#     "sqlite:///" + os.path.join(datapath, "computed_stats.db"),
#     index_col="index",
# )

load_dotenv()

# Tokens
MASTODON_TOKEN = os.environ.get("MASTODON_TOKEN")


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
                    html.P("Share Your Statistics:", style={"paddingBottom": "2em"}),
                    html.Div(
                        [
                            html.A(
                                id="tw-link",
                                children=[
                                    html.Img(
                                        src=app.get_asset_url("twitter.png"),
                                        style={
                                            "height": "140px",
                                            "width": "140px",
                                            "padding": "10px",
                                            "cursor": "pointer"
                                        },
                                    ),
                                ],
                                
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
                    children="Restart",
                    color="Primary",
                    className="me-1",
                    href="/page0",
                ),
                className="d-grip gap-2 d-md-flex justify-content-md-end",
            ),
            html.Div(id="output-submit-social", style={"textAlign":"center"}),
            html.Div(id="output-submit-social-tw", style={"textAlign":"center"}),
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

def no_data(): 
    return "There is no user data to post. Please click on \"Restart\"."

@app.callback(
    Output(component_id="output-submit-social", component_property="children"),
    [
        Input(component_id="a-link", component_property="n_clicks"),
        Input("dccstore_summary", "data"),
    ],
)
def mastodon(n_clicks, summary):
    # df = pd.read_sql_table(
    #     "UserStats",
    #     "sqlite:///" + os.path.join(datapath, "computed_stats.db"),
    #     index_col="index",
    # )
    if n_clicks == 0 or n_clicks is None:
        raise PreventUpdate
    
    if summary is None:
        return no_data()

    # app.loggin.info("========")
    # app.loggin.info(type(summary))

    # app.loggin.info("========")

    toot = (
        summary["time_left"]
        + "\n\n"
        + summary["life_spent"]
        + "\n\n"
        + summary["life_compare"]
        + "\n\n"
        + summary["school"]
        + "\n\n"
        + summary["co2_stats"]
        + "\n\n"
    )

    poverty = str(summary["poverty"])

    if len(toot + poverty) < 500:
        toot += poverty

        # + df["poverty"]
        # Toots are limited to 500 chars. the last statistic would make it
        # go over this limit and we still need a safety margin.
        # + "\n"
        # + df["suic"]
        # + "\n"

    if len(toot + poverty) < 477: # all URLS are 23 chars long, all
        toot += "https://datavizmultlab.herokuapp.com"


    app.logger.info(toot)

    # app.logger.info(toot)

    tags = "\n\n#multimedia\n#databiz"

    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    else:
        #pass
        status_code = post_to_mastodon(toot, tags)
        app.logger.info("Tried posting, code = {}".format(status_code))

    return None


@app.callback(
    Output(component_id="output-submit-social-tw", component_property="children"),
    #Output("twitterLink","href"),
    [
        Input(component_id="tw-link", component_property="n_clicks"),
        Input("dccstore_summary", "data"),
    ],
)
def tweet(n_clicks, summary):
    if n_clicks == 0 or n_clicks is None :
        raise PreventUpdate

    if summary is None:
        return no_data()
    
    url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(
            (
                summary["time_left"]
                + "\n\n"
                + summary["life_spent"]
                + "\n\n"
                + summary["life_compare"]
                + "\n\n"
                + summary["school"]
                + "\n\n"
                + summary["co2_stats"]
            )[:276]
            + " ...",
            safe="/",
            )

    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    else:
        webbrowser.open(url,new=2, autoraise=True)
        return "";
