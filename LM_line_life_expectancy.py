#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 22:17:25 2021

@author: cgwork
"""

import logging
import os

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app

# import numpy as np


colorscales = px.colors.named_colorscales()

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


# Dash
external_stylesheets = [dbc.themes.DARKLY]


# Year/range slider
year_min = df["Year"].min()
year_max = df["Year"].max()

year_slider = dcc.RangeSlider(
    id="year-slider",
    min=year_min,
    max=year_max,
    value=[year_min, year_max],
    marks={i: str(i) for i in range(year_min, year_max + 1, 10)},
)

dropdown = dcc.Dropdown(
    # style= dropdown_style,
    id="countries",
    options=[{"label": str(val), "value": str(val)} for val in countries],
    multi=True,
    value=tuple(),
    placeholder="Countries",
    style={
        "fontSize": 14,
        # "width" : "70%",
        "horizontalAlign": "middle",
        "verticalAlign": "middle",
    },
)

graph1 = dcc.Graph(
    id="life_exp_scatter", config={"displayModeBar": True, "displaylogo": False}
)


button = dbc.Button(
    style={
        "fontSize": 18,
        "marginLeft": "20px",
        "marginRight": "80px",
        "backgroundColor": "#111",
        "color": "#ffffff",
    },
    id="next-button-state",
    n_clicks=0,
    children="Next",
    color="Primary",
    className="me-1",
    href="/page2",
)


# Layout
scatter_layout = go.Layout(
    title="Life Expectancy (Yearly Basis)",
    xaxis={
        # "type": "log",
        "title": "Year",
        "gridcolor": "#181818",
        "zerolinecolor": "#181818",
    },
    yaxis={
        "title": "Life Expectancy",
        "gridcolor": "#181818",
        "zerolinecolor": "#181818",
    },
    margin={"l": 60, "b": 60, "t": 60, "r": 60},
    legend={"x": 0, "y": 1},
    hovermode="closest",
    plot_bgcolor="#111111",
    paper_bgcolor="#111111",
    font_family="Sawasdee",
    font_color="#ffffff",
    template="plotly_dark",
)


layout = html.Div(
    style={
        "fontFamily": "Sawasdee",
        "fontSize": 22,
        "backgroundColor": "#111111",
    },
    children=[
        html.Div(
            [
                html.Br(),
                dropdown,
                html.Br(),
                graph1,
                html.Br(),
            ],
        ),
        html.Br(),
        year_slider,
        html.Br(),
        html.Div(
            [
                button,
            ],
            className="d-grip gap-2 d-md-flex justify-content-md-end",
        ),
    ],
)


@app.callback(
    Output("life_exp_scatter", "figure"),
    Input("countries", "value"),
    # State("year-slider", "value"),
)
def color_countries_and_region(
    country,
    # years
):
    if country is None:
        raise PreventUpdate

    mask = (
        df.index.isin(country)
        # & (df["Year"] >= years[0]) & (df["Year"] <= years[1])
    )

    # logging.info(msg=locals())
    df2 = df[mask]
    # df2_region = df[df["map_ref"] == region]

    line_fig = px.line(
        df2,
        x="Year",
        y="Life_expectancy",
        color=df2.index,
        color_discrete_sequence=px.colors.qualitative.G10,
        # mode="markers",
    )

    line_fig.update_layout(scatter_layout)
    return line_fig
