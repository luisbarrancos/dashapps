#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 19:09:31 2021

@author: cgwork
"""
# -*- coding: utf-8 -*-
"""


Dash Graph,
With callbacks
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
    "Deadline_database", "sqlite:///deadline_database_nonans.db",
    index_col="Country"
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


year_picker = dcc.Dropdown(
    id="year-picker",
    options=[{"label": str(val), "value": str(val)} for \
             val in df["Year"].unique()],
    value=df["Year"].min(),
    placeholder="Year",
)

scatter_graph = dcc.Graph(id="scatter_graph")

app.layout = html.Div(
    style={
        "font-family": "Sawasdee",
        "font-size": 22,
        "background-color": "#111111",
    },
    children=[
        scatter_graph,
        html.Br(),
        year_picker,
        # html.Br()
    ],
)


@app.callback(
    Output("scatter_graph", "figure"),
    [
         Input("year-picker", "value")
    ]
    )
def update_figuer(selected_year):
    if selected_year is None:
        raise PreventUpdate()

    filtered_df = df[df["Year"] == selected_year]
    traces = []

    # SQL db loaded with Country as index
    for country in filtered_df.index.unique():
        df_country = filtered_df[filtered_df.index == country]

        traces.append(
            go.Scatter(
                x=df_country["Life_expectancy"],
                y=df_country["Life_satisfaction"],
                mode="markers",
                opacity=0.7,
                name=country,
            )
        )

    return {
        "data": traces,
        "layout": go.Layout(
            title="Life Expectancy vs Life Satisfaction",
            xaxis={
                "title": "Life Satisfaction",
                # "type" : "log"
            },
            yaxis={"title": "Life Expectancy"},
        ),
    }


if __name__ == "__main__":
    app.run_server(debug=True)
