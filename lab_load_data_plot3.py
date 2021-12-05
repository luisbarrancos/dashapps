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

print(df.columns)


# Dash
app = dash.Dash(__name__)
app.title = "Deadline"


app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(
                    # style= dropdown_style,
                    id="countries",
                    options=[
                        {
                            "label": str(val),
                            "value": str(val)} for val in countries
                    ],
                    multi=True,
                    value=tuple(),
                    placeholder="Countries",
                ),
            ],
            style={
                "width": "35%",
                "display": "inline-block",
                # "background-color": "#eeeeee",
            },
        ),
        dcc.Graph(id="life_exp_scatter", config={"displayModeBar": False}),
    ]
)


"""
    dcc.Graph(
        id="life_exp_vs_happy",
        figure={
            "data": [
                go.Scatter(
                    x = df[df.index == i]["Life_expectancy"],
                    y = df[df.index == i]["Life_satisfaction"],
                    #text=df[df.index.unique() == i],
                    mode = "markers",
                    opacity = 0.8,
                    marker =
                    {
                        "size" : 15,
                        "line" : {"width" : 0.5, "color" : "white"},
                    },
                    name = i
                    ) for i in df.index.unique()
            ],
            "layout" : go.Layout
            (
                xaxis={"type": "log", "title": "Life Satisfaction"},
                yaxis={"title": "Life Expectancy"},
                margin={"l": 40, "b": 40, "t": 10, "r": 10},
                legend={"x": 0, "y": 1},
                hovermode="closest",
            )
        }
    )
"""


@app.callback(
    Output("life_exp_scatter", "figure"),
    [Input("countries", "value")],
)
def color_countries_and_region(countries):

    logging.info(msg=locals())
    df2 = df[df.index.isin(countries)]
    #df2_region = df[df["map_ref"] == region]

    return {
        "data": [
            go.Scatter(
                x=df.index,
                y=df[col],
                mode="markers",
                showlegend=True,
                name=col.replace("_", " ").title(),
            )
            for col in ["Life_expectancy", "Life_satisfaction"]
        ]
    }

if __name__ == "__main__":
    app.run_server(debug=True)
