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


# Year dropdown
year_picker = dcc.Dropdown(
    id="year-picker",
    options=[{"label": str(year), "value": year} for year in df["Year"].unique()],
    value=df["Year"].min(),
    placeholder="Year",
)

# Scatter graph
scatter_graph = dcc.Graph(id="scatter_graph")

# Layout
scatter_layout = go.Layout(
    title="Life Expectancy vs Satisfaction, Human Development Index & " \
        + "Average Total Schooling Years per Adult",
    xaxis={"type": "log", "title": "Life Satisfaction"},
    yaxis={"title": "Life Expectancy"},
    margin={"l": 40, "b": 40, "t": 40, "r": 40},
    legend={"x": 0, "y": 1},
    hovermode="closest",
    plot_bgcolor="#111111",
    paper_bgcolor="#111111",
    font_family="Sawasdee",
    font_color="#ffffff",
    config= {"displaylogo" : False}
)

app.layout = html.Div(
    style={
        "font-family": "Sawasdee",
        "font-size": 22,
        "background-color": "#111111",
    },
    children =
    [
        html.Br(),
        scatter_graph,
        html.Br(),
        year_picker,
        html.Br(),
    ]
)

@app.callback(Output("graph", "figure"), [Input("year-picker", "value")])
def update_figure(selected_year):

    #if selected_year is None:
    #    raise PreventUpdate()

    filtered_df = df[df["Year"] == selected_year]
    traces = []

    for country in filtered_df["Country"].unique():

        dfc = filtered_df[filtered_df["Country"] == country]

        traces.append(
            go.Scatter(
                x=dfc["Life_satisfaction"],
                y=dfc["Life_expectancy"],
                # text=df[df.index.unique() == i],
                mode="markers",
                opacity=0.8,
                hovertemplate="Life Expectancy: %{y:.2f}<br>"
                + "Life Satisfaction: %{x:.2f}<br>"
                + "Avg. Years Total School: %{marker.size:.2f}<br>"
                + "Human Devel. Index: %{marker.color:.2f}",
                marker={
                    "size": dfc[
                        "Average_total_years_of_schooling_for_adult_population"
                    ],
                    "color": dfc["Human_development_index"],
                    "line": {"width": 2, "color":
                             dfc["Human_development_index"],}
                    #"colorscale" : "Viridis",
                },
                name=country,))

    return {
        "data": traces,
        "layout": scatter_layout
    }

if __name__ == "__main__":
    app.run_server(debug=True)
