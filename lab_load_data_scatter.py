#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 22:17:25 2021

@author: cgwork
"""

import logging
import os
import pandas as pd
import numpy as np

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

#year_slider = dcc.RangeSlider(
#    id="year-slider",
#    min=year_min,
#    max=year_max,
#    value=[year_min, year_max],
#    marks={i: str(i) for i in range(year_min, year_max + 1, 5)},
#    tooltip={"placement": "bottom", "always_visible": True}
#)

year_dropdown = dcc.Dropdown(
    # style= dropdown_style,
    id="years",
    options=[{"label": str(val), "value": str(val)} for val in \
             sorted(df["Year"].unique())],
    multi=False,
    value=df["Year"].min(),
    placeholder="Data Fields",
)

country_dropdown = dcc.Dropdown(
    # style= dropdown_style,
    id="countries",
    options=[{"label": str(val), "value": str(val)} for val in countries],
    multi=True,
    value=tuple(),
    placeholder="Countries",
)

data_dropdown = dcc.Dropdown(
    # style= dropdown_style,
    id="datafields",
    options=[{"label": str(val), "value": str(val)} for val in df.columns],
    multi=False,
    value="Life_satisfaction",
    placeholder="Data Fields",
)



dropdown_style = {
    "margin-left": "20px",
    "margin-right": "50px",
    "color": "#ffffff",
    "background-color": "#000000",
}

scatter_graph = dcc.Graph(id = "scatter_graph")


app.layout = html.Div(
    style = {
        "font-family": "Sawasdee",
        "font-size": 22,
        "background-color" : "#111111",
    },
    children = [
        html.Div([
            year_dropdown,
            country_dropdown,
            data_dropdown,
            ]),
        scatter_graph,
        html.Br(),
        #year_slider,
        html.Br(),
    ]
    )


@app.callback(
    Output("scatter_graph", "figure"),
    [
     Input("years", "value"),
     Input("countries", "value"),
     Input("datafields", "value"),
     ]
)
def color_countries_and_region(years, country, datafields):
    if country is None:
        raise PreventUpdate


    mask = (
        (df.index.isin(country)) & (np.any(df["Year"].values.tolist() == years))
        )

    #app.logger.info(df["Year"].values.tolist())
    #app.logger.info(type(df["Year"]))
    # logging.info(msg=locals())
    df2 = df[mask]
    # df2_region = df[df["map_ref"] == region]

    #line_fig = px.line(
    #    df2,
    #    x="Year",
    #    y="Life_expectancy",
    #    color=df2.index,
    #    template = "plotly_dark",
    #    title = "Life Expectancy",
    #    # width = 640, height = 480,
    #    # mode="markers",
    #    # showlegend=True,
    #)
    #line_fig.update_layout(font_family="Sawasdee")

    figure = {
        "data": [
            go.Scatter(
                x = df2[df2.index == i][datafields],
                y = df2[df2.index == i]["Life_expectancy"],
                #text=df2[df2.index.unique() == i],
                mode = "markers",
                opacity = 0.8,
                marker =
                {
                    "size" : 15,
                    "line" : {"width" : 0.5, "color" : "white"},
                },
                name = i
                ) for i in df2.index.unique()
        ],
        "layout" : go.Layout
        (
            xaxis={
                "title": str(datafields),
                },
            yaxis={
                #"type": "log",
                "title": "Life Expectancy"
                },
            margin={"l": 40, "b": 40, "t": 10, "r": 10},
            legend={"x": 0, "y": 1},
            hovermode="closest",
            font_family="Sawasdee",
        )
    }
    return figure



if __name__ == "__main__":
    app.run_server(debug=True)

