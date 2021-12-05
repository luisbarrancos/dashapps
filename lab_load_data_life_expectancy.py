#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 22:17:25 2021

@author: cgwork
"""

import logging
import os
import pandas as pd

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objs as go

# All the code for data filtering, processing, done in jupyterlab
# notebooks (already in github), but now we can bypass all the processing
# and go straight to the final SQLite3 DB

df = pd.DataFrame()
df = pd.read_sql_table(
    "Deadline_database", "sqlite:///deadline_database_nonans.db", index_col="Country"
)
df.dropna(inplace=True)
df.sort_values(by=["Country", "Year"], inplace=True)

countries = list(df.index.unique())

print(df.columns)


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
    marks={i: str(i) for i in range(year_min, year_max + 1, 5)},
    tooltip={"placement": "bottom", "always_visible": True}
)

dropdown = dcc.Dropdown(
    # style= dropdown_style,
    id="countries",
    options=[{"label": str(val), "value": str(val)} for val in countries],
    multi=True,
    value=tuple(),
    placeholder="Countries",
)

dropdown_style = {
    "margin-left": "20px",
    "margin-right": "50px",
    "color": "#ffffff",
    "background-color": "#000000",
}

graph1 = dcc.Graph(id="life_exp_scatter", config={"displayModeBar": False})

app.layout = html.Div(
    style = {
        "font-family": "Sawasdee",
        "font-size": 22,
        "background-color" : "#111111",
    },
    children = [
        html.Div(
            [
                html.Br(),
                html.Div(
                    [dropdown],
                    style={
                        "width": "35%",
                        "display": "inline-block",
                        "background-color": "#eeeeee",
                    },
                ),
                # dropdown,
                html.Br(),
                graph1,
                html.Br(),
            ],
        ),
        year_slider,
        html.Br(),
    ],
)


@app.callback(
    Output("life_exp_scatter", "figure"),
    Input("countries", "value"),
    Input("year-slider", "value"),
)
def color_countries_and_region(country, years):
    if country is None:
        raise PreventUpdate
    else:
        mask = (
            (df.index.isin(country))
            & (df["Year"] >= years[0])
            & (df["Year"] <= years[1])
        )

        # logging.info(msg=locals())
        df2 = df[mask]
        # df2_region = df[df["map_ref"] == region]

        line_fig = px.line(
            df2,
            x="Year",
            y="Life_expectancy",
            color=df2.index,
            template = "plotly_dark",
            title = "Life Expectancy",
            # width = 640, height = 480,
            # mode="markers",
            # showlegend=True,
        )
        line_fig.update_layout(font_family="Sawasdee")

        # return {"data": []}
        return line_fig


if __name__ == "__main__":
    app.run_server(debug=True)
