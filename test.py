#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 20:31:21 2021

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
df.sort_values(by=["Year"], inplace=True)

country_list = list(df.index.unique())
migration_years = sorted(df["Year"].unique().tolist())

"""
data = pd.read_csv("migration_population.csv")
country_list = data[data["region"] != "Aggregates"]["country"].unique()
data_countries = (data[data["country"].isin(country_list) &
                       ~data["country"].isin(["Latin America & Caribbean",
                                              "Sub-Saharan Africa"])]
                  .reset_index(drop=True))
migration_years = sorted(data_countries[data_countries["net_migration"].notna()]
                         ["year"].unique().tolist())
"""

metric_translation = {
    "net_migration": "Net migrants",
    "migration_perc": "Net migrants (% of population)",
    "pop_density": "Population density (inhabitants per kilometer square)",
}

# all_countries_regions = df["country"].unique()
all_countries_regions = country_list


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

server = app.server

app.layout = html.Div(
    [
        dbc.Row(
            [
                html.Br(),
                html.Br(),
                dbc.Col(lg=1),
                dbc.Col(
                    [
                        html.Br(),
                        dbc.Label("Select a metric:"),
                        dcc.Dropdown(
                            id="metrics_dropdown_top",
                            placeholder="Select metric",
                            value="migration_perc",
                            options=[
                                {"label": field, "value": field} for field in df.columns
                            ],
                        ),
                    ],
                    lg=4,
                ),
                dbc.Col(
                    [
                        html.Br(),
                        dbc.Label("Select a year:"),
                        dcc.Slider(
                            id="year_slider",
                            tooltip={"always_visible": True},
                            min=min(migration_years),
                            max=max(migration_years),
                            value=2017,
                            included=False,
                            step=None,
                            marks={
                                year: {"label": str(year)} for year in migration_years
                            },
                        ),
                    ],
                    lg=5,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="world_map",
                            config={
                                "displayModeBar": "hover",
                                "displaylogo": False,
                                "showTips": True,
                                "modeBarButtonsToRemove": [
                                    "lasso2d",
                                    "select2d",
                                    "hoverClosestGeo",
                                ],
                                "toImageButtonOptions": {"format": "svg"},
                            },
                        )
                    ],
                    lg=8,
                ),
                dbc.Col(
                    [dcc.Graph(id="top_countries", config={"displayModeBar": False})],
                    lg=4,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col([], lg=2),
                dbc.Col(
                    [
                        dbc.Label("Select a metric:"),
                        dcc.Dropdown(
                            id="metrics_dropdown_bottom",
                            placeholder="Select metric",
                            value="pop_density",
                            options=[
                                {"label": field, "value": field} for field in df.columns
                            ],
                        ),
                    ],
                    lg=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("Select countries and/or regions:"),
                        dcc.Dropdown(
                            id="countries_regions_dropdown",
                            multi=True,
                            value=[
                                "World",
                                "United States",
                                "China",
                                "Japan",
                                "Germany",
                            ],
                            placeholder="Select countries and/or regions",
                            options=[
                                {"label": str(val), "value": str(val)}
                                for val in country_list
                            ],
                        ),
                    ],
                    lg=4,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(lg=1),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="metric_timeseries", config={"displayModeBar": False}
                        )
                    ],
                    lg=10,
                ),
            ]
        ),
    ],
    style={"backgroundColor": "#eeeeee"},
)


@app.callback(
    Output("metric_timeseries", "figure"),
    [
        Input("countries_regions_dropdown", "value"),
        Input("metrics_dropdown_bottom", "value"),
    ],
)
def plot_country_timeseries(countries, metric):
    if not countries or not metric:
        raise PreventUpdate
    fig = go.Figure()
    for country in countries:
        df2 = df[df.index == country].drop_duplicates(subset=[metric])

        if metric == "Life_expectation":
            df[metric] = [format(x, ".1%") + "%" for x in df[metric]]
            fig.layout.yaxis.ticksuffix = "%"

        fig.add_scatter(
            x=df["year"],
            y=df[metric],
            name=country,
            hoverlabel={"namelength": 200},
            mode="markers+lines",
        )

    fig.layout.template = "none"
    fig.layout.paper_bgcolor = "#eeeeee"
    fig.layout.plot_bgcolor = "#eeeeee"
    fig.layout.title = (
        "<b>"
        + metric_translation[metric]
        + "</b><br>"
        + ", ".join(countries)
        + " "
        + df["year"].min().astype(str)
        + " - "
        + df["year"].max().astype(str)
    )
    return fig.to_dict()


@app.callback(
    Output("top_countries", "figure"),
    [Input("year_slider", "value"), Input("metrics_dropdown_top", "value")],
)
def plot_top_countries(year, metric):
    if not metric:
        raise PreventUpdate

    df2 = df[df[metric].notna()].query("year == @year").sort_values(metric)

    if metric == "migration_perc":
        df2[metric] = df2[metric].mul(100).round(1)

    fig = go.Figure()

    df_plot = df2.head(10).append(df2.tail(10))

    fig.add_bar(
        x=df_plot[metric],
        y=df_plot["country"],
        orientation="h",
        marker={
            "color": ["rgba(214, 39, 40, 0.85)"] * 10 + ["rgba(6,54,21, 0.85)"] * 10
            if metric != "pop_density"
            else "#ababab"
        },
    )

    fig.layout.title = (
        "Top and Bottom Countries <br>"
        + metric_translation[metric]
        + "<br>"
        + "Year: "
        + str(year)
    )

    if metric == "Life_expectation":
        fig.layout.xaxis.ticksuffix = "%"

    fig.layout.template = "none"
    fig.layout.margin = {"l": 150}
    fig.layout.height = 650
    fig.layout.yaxis.showgrid = True
    fig.layout.paper_bgcolor = "#eeeeee"
    fig.layout.plot_bgcolor = "#eeeeee"

    return fig.to_dict()


@app.callback(
    Output("world_map", "figure"),
    [Input("year_slider", "value"), Input("metrics_dropdown_top", "value")],
)
def plot_world_map(year, metric):
    if not metric:
        raise PreventUpdate
    df2 = df[df[metric].notna()].sort_values(metric).query("Year == @year")
    zeroidx = df2[metric].sort_values().lt(0).sum()
    fig = go.Figure()

    hover_suffix = "%" if metric == "Life_expectation" else ""

    hover_metric_str = (
        df2[metric].mul(100).round(2).astype(str)
        if metric == "Life_expectation"
        else [format(int(n), ",") for n in df2[metric]]
    )
    fig.add_choropleth(
        locations=df2["Life_satisfaction"],
        z=df2[metric].clip(1, 700) if metric == "Life_satisfaction" else df2[metric],
        name="",
        colorscale="cividis",
        hoverlabel={"namelength": 200, "bgcolorsrc": "blah"},
        # hovertemplate=(
        #    "<b>"
        #    + df2.index,
        #    + "<b><br><br>"
        #    + metric_translation[metric]
        #    + ": "
        #    + hover_metric_str
        #    + hover_suffix
        # ),
        colorbar={
            "lenmode": "fraction",
            "len": 0.5,
            "x": -0.07,
            "ticksuffix": "+" if metric == "pop_density" else "",
            "tickformat": "%" if metric == "migration_perc" else "",
            "showticksuffix": "last" if metric == "pop_density" else "all",
        },
        locationmode="ISO-3",
    )
    fig.layout.geo = {
        "showframe": False,
        "oceancolor": "#eeeeee",
        "showocean": True,
        "lataxis": {"range": [-51, 83]},
    }
    fig.layout.height = 700
    fig.layout.margin = {"r": 10, "l": 10, "t": 0}
    fig.layout.margin.autoexpand = True
    fig.layout.paper_bgcolor = "#eeeeee"
    fig.layout.plot_bgcolor = "#eeeeee"
    fig.layout.title = {
        "text": metric_translation[metric] + ": " + str(year),
        "font": {"color": "black"},
        "x": 0.5,
        "y": 0.9,
        "xanchor": "center",
        "yanchor": "middle",
    }
    return fig.to_dict()



if __name__ == "__main__":
    app.run_server(debug=True)
