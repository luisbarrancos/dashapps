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
df.dropna(inplace=True)
df.sort_values(by=["Country", "Year"], inplace=True)

countries = list(df.index.unique())

print(df.columns)


# Dash
app = dash.Dash(__name__)
app.title = "Deadline"


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

dropdown = dcc.Dropdown(
    # style= dropdown_style,
    id="countries",
    options=[{"label": str(val), "value": str(val)} for val in countries],
    multi=True,
    value=tuple(),
    placeholder="Countries",
)

graph1 = dcc.Graph(id="life_exp_scatter", config={"displayModeBar": False})

app.layout = html.Div(
    [
        html.Br(),
        year_slider,
        html.Div(
            [
                html.Br(),
                dropdown,
                html.Br(),
                graph1,
                html.Br(),
            ],
        ),
    ],
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

"""
@app.callback(
    Output('life-expectancy-graph', 'figure'),
    Input('submit-button', 'n_clicks'),
    State('country-dropdown', 'value'),
    State('year-slider', 'value'))
def update_outputs(button_click, selected_country, selected_years):
    if selected_country is None:
       raise PreventUpdate
    msk = (life_expectancy['country'].isin(selected_country)) & \
          (life_expectancy['year'] >= selected_years[0]) & \
          (life_expectancy['year'] <= selected_years[1])
    life_expectancy_filtered = life_expectancy[msk]
    line_fig = px.line(life_expectancy_filtered,
                       x='year', y='life expectancy',
                       title='Life expectancy',
                       color='country')
    return line_fig
"""


@app.callback(
    Output("life_exp_scatter", "figure"),
    Input("countries", "value"),
    State("year-slider", "value"),
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

        line_fig =  px.line(
                            df2,
                            x = "Year",
                            y = "Life_expectancy",
                            color = df2.index,
                            # mode="markers",
                            # showlegend=True,
                        )

        #return {"data": []}
        return line_fig


if __name__ == "__main__":
    app.run_server(debug=True)
