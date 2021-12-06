#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 12:35:29 2021

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


# Read the data from the csv file
df = pd.read_sql_table(
    "Deadline_database",
    "sqlite:///deadline_database_nonans.db",
    # index_col="Country"
)
df.sort_values(by=["Year"], inplace=True)


# Dash
external_stylesheets = [dbc.themes.DARKLY]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    assets_url_path=os.path.join(os.getcwd(), "assets"),
)
app.title = "Deadline"


# Create the list of years for the year drop-down
year_options = []
for year in df["Year"].unique():
    year_options.append({"label": str(year), "value": year})


# Layout
scatter_layout = go.Layout(
    title="Life Expectancy vs Satisfaction, Human Development Index & "
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
)

# Scatter graph
scatter_graph = dcc.Graph(id="scatter-graph")

# Year dropdown
year_picker = dcc.Dropdown(
    id="year-picker",
    options=[{"label": str(year), "value": year} for year in df["Year"].unique()],
    value=df["Year"].min(),
    placeholder="Year",
)


# Create the app layout
app.layout = html.Div(
    [
         year_picker,
         scatter_graph,
    ]
)

# Connect the year picker drop down to the graph
@app.callback(Output("scatter-graph", "figure"), [Input("year-picker", "value")])
def update_figure(selected_year):
    # Data only for selected year from the dropdown
    filtered_df = df[df["Year"] == selected_year]

    # Create a trace for each continent
    traces = []
    for continent_name in filtered_df["Country"].unique():
        df_by_continent = filtered_df[filtered_df["Country"] == continent_name]
        traces.append(
            go.Scatter(
                x=df_by_continent["Life_expectancy"],
                y=df_by_continent["Life_satisfaction"],
                mode="markers",
                name=continent_name,
                opacity=0.8,
                hovertemplate="Life Expectancy: %{y:.2f}<br>"
                + "Life Satisfaction: %{x:.2f}<br>"
                + "Avg. Years Total School: %{marker.size:.2f}<br>"
                + "Human Devel. Index: %{marker.color:.2f}",
                marker={
                    "size": df_by_continent[
                        "Average_total_years_of_schooling_for_adult_population"
                    ],
                    "color": df_by_continent["Human_development_index"],
                    "line": {
                        "width": 2,
                        "color": df_by_continent["Human_development_index"],
                    }
                    # "colorscale" : "Viridis",
                },
            )
        )

    # Return the dictionary that will go inside the graph call
    return {
        "data": traces,
        "layout": scatter_layout,
    }


if __name__ == "__main__":
    app.run_server(debug=True)
