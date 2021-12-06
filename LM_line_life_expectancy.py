#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 22:17:25 2021

@author: cgwork
"""

import logging
import os
import pandas as pd

# import numpy as np

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objs as go

colorscales = px.colors.named_colorscales()

# All the code for data filtering, processing, done in jupyterlab
# notebooks (already in github), but now we can bypass all the processing
# and go straight to the final SQLite3 DB

df = pd.DataFrame()
df = pd.read_sql_table(
    "Deadline_database", "sqlite:///deadline_database_nonans.db", index_col="Country"
)
df.dropna(inplace=True)
df.sort_values(by=["Year"], inplace=True)

countries = list(df.index.unique())
# print(df.columns)


# Dash
external_stylesheets = [dbc.themes.DARKLY]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    assets_url_path=os.path.join(os.getcwd(), "assets"),
)
app.title = "Deadline"


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
)

graph1 = dcc.Graph(id="life_exp_scatter",
                   config={"displayModeBar" : True,
                           "displaylogo" : False}
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


app.layout = html.Div(
    style={
        "font-family": "Sawasdee",
        "font-size": 22,
        "background-color": "#111111",
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
    ],
)


@app.callback(
    Output("life_exp_scatter", "figure"),
    Input("countries", "value"),
    State("year-slider", "value"),
)
def color_countries_and_region(country, years):
    if country is None:
        raise PreventUpdate

    mask = (
        (df.index.isin(country)) & (df["Year"] >= years[0]) & (df["Year"] <= years[1])
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
