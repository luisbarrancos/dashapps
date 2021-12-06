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
    margin={"l": 60, "b": 60, "t": 60, "r": 60},
    legend={"x": 0, "y": 1},
    hovermode="closest",
    plot_bgcolor="#111111",
    paper_bgcolor="#111111",
    font_family="Sawasdee",
    font_color="#ffffff",
)

# Scatter graph
scatter_graph = dcc.Graph(id="scatter-graph", config={"displaylogo": False})

# Year dropdown
year_picker = dcc.Dropdown(
    id="year-picker",
    options=[{"label": str(year), "value": year} for year in df["Year"].unique()],
    value=df["Year"].min(),
    placeholder="Year",
)

# fields available for marker size
fields = {
    "Average_total_years_of_schooling_for_adult_population":
        "Avg Total School Year",
    "Mortality_rate_under_5_per_1000_live_births":
        "Mortality Under 5 (per 1000)",
    "Suicidy_mortality_rate_per_100000_population":
        "Suicidy Mortality (per 100000)",
    "Share_of_population_below_poverty_line_2USD_per_day":
        "% Below Poverty (2USD/day)",
    "Life_expectancy_at_birth":
        "Life Expectancy at Birth",
}

# hoverdata = [
#    ]


data_picker = dcc.Dropdown(
    id="data-picker",
    options=[
        {
            "label": str(val).replace("_", " ").title(),
            "value": val,
        }
        for val in fields.keys()
    ],
    multi=False,
    value=list(fields.keys())[0],
    placeholder="Year",
)

# Year/range slider
year_min = df["Year"].min()
year_max = df["Year"].max()

year_slider = dcc.RangeSlider(
    id="year-slider",
    min=year_min,
    max=year_max,
    value=[year_min, year_max],
    marks={i: str(i) for i in range(year_min, year_max + 1, 5)},
    tooltip={"placement": "bottom", "always_visible": True},
)

# Create the app layout
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
                scatter_graph,
                html.Br(),
            ]
        ),
        html.Div(
            [
                data_picker,
                year_slider,
            ]
        ),
        year_picker,
        html.Br(),
    ],
)

# Connect the year picker drop down to the graph
@app.callback(
    Output("scatter-graph", "figure"),
    [
        Input("data-picker", "value"),
        Input("year-slider", "value"),
        Input("year-picker", "value"),
    ],
)
def update_figure(datafield, years, selected_year):
    # Data only for selected year from the dropdown
    # if selected_year is None:
    #    raise PreventUpdate

    mask = (df["Year"] >= years[0]) & (df["Year"] <= years[1])

    # filtered_df = df[df["Year"] == selected_year]
    filtered_df = df[mask]

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
                + str(fields.get(datafield)) + ": %{marker.size:.2f}<br>"
                + "Human Devel. Index: %{marker.color:.2f}",
                marker={
                    "size": df_by_continent[datafield],
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
