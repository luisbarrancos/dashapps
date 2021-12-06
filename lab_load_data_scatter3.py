#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 10:13:37 2021

@author: cgwork
"""

import logging
import os
import pandas as pd
#import numpy as np

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


app.layout = html.Div(
    style={
        "font-family": "Sawasdee",
        "font-size": 22,
        "background-color": "#111111",
    },
    children =
    [
        dcc.Graph(
            id="life_exp_vs_happy",
            figure={
                "data": [
                    go.Scatter(
                        x=df[df.index == i]["Life_satisfaction"],
                        y=df[df.index == i]["Life_expectancy"],
                        # text=df[df.index.unique() == i],
                        mode="markers",
                        opacity=0.8,
                        hovertemplate="Life Expectancy: %{y:.2f}<br>"
                        + "Life Satisfaction: %{x:.2f}<br>"
                        + "Avg. Years Total School: %{marker.size:.2f}<br>"
                        + "Human Devel. Index: %{marker.color:.2f}",
                        marker={
                            "size": df[df.index == i][
                                "Average_total_years_of_schooling_for_adult_population"
                            ],
                            "color": df[df.index == i]["Human_development_index"],
                            "line": {"width": 2, "color":
                                     df[df.index == i]["Human_development_index"],}
                            #"colorscale" : "Viridis",
                        },
                        name=i,
                    )
                    for i in df.index.unique()
                ],
                "layout": go.Layout(
                    xaxis={"type": "log", "title": "Life Satisfaction"},
                    yaxis={"title": "Life Expectancy"},
                    margin={"l": 40, "b": 40, "t": 10, "r": 10},
                    legend={"x": 0, "y": 1},
                    hovermode="closest",
                    plot_bgcolor="#111111",
                    paper_bgcolor="#111111",
                    font_family="Sawasdee",
                    font_color="#ffffff",
                ),
            },
        )
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
