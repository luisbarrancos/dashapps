#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 22:17:25 2021

@author: cgwork
"""
import os

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output
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

# Year single slider
year_single_slider = dcc.Slider(
    id="year-single-slider",
    min=year_min,
    max=year_max,
    value=year_min,
    marks={i: str(i) for i in range(year_min, year_max + 1, 10)},
)


dropdown = dcc.Dropdown(
    # style= dropdown_style,
    id="countries",
    options=[{"label": str(val), "value": str(val)} for val in countries],
    multi=True,
    value=tuple(),  # list(df.index.unique()),
    placeholder="Countries",
    style={
        "fontSize": 14,
        # "width" : "70%",
        "horizontalAlign": "middle",
        "verticalAlign": "middle",
    },
)

data_picker = dcc.Dropdown(
    id="data-picker",
    options=[
        {
            "label": str(val).replace("_", " ").title(),
            "value": val,
        }
        for val in df.columns[2 : len(df.columns) - 3]  # 2=1st statistic
    ],
    multi=False,
    value=df.columns[2],
    placeholder="Statistic",
    style={
        "fontSize": 14,
        # "width" : "70%",
        "horizontalAlign": "middle",
        "verticalAlign": "middle",
    },
)

# app.logger.info(df.columns[2])

button = dbc.Button(
    id="next-button-state",
    style={
        "fontSize": 18,
        "marginLeft": "20px",
        "marginRight": "80px",
        "backgroundColor": "#111",
        "color": "#ffffff",
    },
    n_clicks=0,
    children="Next",
    color="Primary",
    className="me-1",
    href="/page5",
)

scatter_graph = dcc.Graph(
    id="geomap_plot", config={"displayModeBar": True, "displaylogo": False}
)


# Layout
scatter_layout = go.Layout(
    # title="Life Expectancy (Yearly Basis)",
    xaxis={
        # "type": "log",
        # "title": "Year",
        "gridcolor": "#181818",
        "zerolinecolor": "#181818",
    },
    yaxis={
        # "title": "Life Expectancy",
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


# Create the app layout
layout = html.Div(
    style={
        "fontFamily": "Sawasdee",
        "fontSize": 22,
        "backgroundColor": "#111111",
    },
    children=[
        html.Div(
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                dropdown,
                            ],
                            style={"padding": 10, "flex": 1, "width": "50%"},
                        ),
                        html.Div(
                            [
                                data_picker,
                            ],
                            style={"padding": 10, "flex": 1, "width": "50%"},
                        ),
                    ],
                    style={"display": "flex"},
                ),
                html.Div(
                    [
                        html.Br(),
                        scatter_graph,
                        # html.Br(),
                    ]
                ),
                html.Div(
                    [
                        # year_slider,
                        year_single_slider,
                    ],
                    style={"padding": 10, "flex": 1},
                ),
                html.Br(),
                html.Div(
                    [
                        button,
                    ],
                    className="d-grip gap-2 d-md-flex justify-content-md-end",
                ),
            ],
        ),
    ],
)


projections = [
    "equirectangular",
    "mercator",
    "orthographic",
    "natural earth",
    "kavrayskiy7",
    "miller",
    "robinson",
    "eckert4",
    "azimuthal equal area",
    "azimuthal equidistant",
    "conic equal area",
    "conic conformal",
    "conic equidistant",
    "gnomonic",
    "stereographic",
    "mollweide",
    "hammer",
    "transverse mercator",
    "albers usa",
    "winkel tripel",
    "aitoff",
    "sinusoidal",
]


@app.callback(
    Output("geomap_plot", "figure"),
    [
        Input("countries", "value"),
        Input("year-single-slider", "value"),
        Input("data-picker", "value"),
        Input("next-button-state", "n_clicks"),
    ],
)
def color_countries_and_region(country, years, datafield, n_clicks):
    if country is None:
        raise PreventUpdate

    # app.logger.info(df.index.unique())

    mask = (
        (df.index.isin(country))
        & (df["Year"] == years)
        # & (df["Year"] >= years[0]) & (df["Year"] <= years[1])
    )

    # logging.info(msg=locals())
    df2 = df[mask]

    # line_fig = px.line(
    #    df2,
    #    x="Year",
    #    y=datafield,
    #    color=df2.index,
    #    color_discrete_sequence=px.colors.qualitative.G10,
    #    # mode="markers",
    # )
    # https://plotly.github.io/plotly.py-docs/generated/plotly.express.choropleth.html

    line_fig = px.choropleth(
        df2,
        locations=df2.index,
        locationmode="country names",  # or ISO-3
        color=datafield,  # lifeExp is a column of gapminder
        hover_name=df2.index,  # column to add to hover information
        # hover_data
        # projection="robinson",
        projection=projections[6],
        scope="world",
        labels={str(datafield).replace("_", " ").title(): datafield},
        # text = df["text],
        # marker_line_color="white",
        color_continuous_scale=px.colors.sequential.Turbo,
    )

    line_fig.update_layout(scatter_layout)
    line_fig.update_layout(
        title=str(datafield).replace("_", " ").title() + " (World Map)"
    )
    # https://plotly.com/python/colorscales/
    line_fig.update_layout(
        coloraxis_colorbar=dict(
            title=datafield.replace("_", " ").title(),
            titleside="right",
            thicknessmode="pixels",
            thickness=20,
            # lenmode="pixels", len=200,
            # yanchor="top", y=1,
            # xanchor="right", x=0.3,
            # ticks="inside",
            # ticksuffix=" bills",
            # dtick=5
        )
    )

    return line_fig
