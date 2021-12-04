#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 11:12:43 2021

@author: cgwork
"""

# Dataframes, DBs
import os
import pandas as pd
import numpy as np


# Dashboards modules
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


class UserData:
    def __init__(self, user_name = None, user_age = None,
                 birthplace = None, residence = None, sex = None,
                 veggie = None, driver = None, smoker = None):
        self.__user_name = user_name
        self.__user_age = user_age
        self.__birthplace = birthplace
        self.__residence = residence
        self.__sex = sex
        self.__veggie = veggie
        self.__driver = driver
        self.__smoker = smoker


    def set_age(self, age):
        self.__age = age

    def set_name(self, name):
        self.__name = name

    def set_birthplace(self, birthplace):
        self.__birthplace = birthplace

    def set_residence(self, residence):
        self.__residence = residence

    def set_sex(self, sex):
        self.__sex = sex

    def set_veggie(self, veggie):
        self.__veggie = veggie

    def set_driver(self, driver):
        self.__driver = driver

    def set_smoker(self, smoker):
        self.__smoker = smoker

    def print_data(self):
        print(self.__name, self.__age, self.__birthplace,
              self.__residence, self.__sex, self.__veggie,
              self.__driver, self.__smoker)

    def get_data(self):
        return [self.__user_name,
                self.__user_age,
                self.__birthplace,
                self.__residence,
                self.__sex,
                self.__veggie,
                self.__driver,
                self.__smoker
                ]




# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


# get the CSV files
datapath = os.path.join(os.getcwd(), "data2")
datadict = dict()


if os.path.isdir(datapath):
    datafiles = [
        f for f in os.listdir(datapath) \
            if os.path.isfile(os.path.join(datapath, f))
    ]

    # For these files, split the extension, capitalize and append them to a
    # dictionary which will contain as key the name minus extension and as
    # value the Pandas DataFrame
    for f in datafiles:
        datadict[((f.rsplit(".", 1)[0]).capitalize())] = pd.read_csv(
            os.path.join(datapath, f), index_col="Country"
        )


# find for each DB, the unique country/index entries
# which we convert to lists and then sets to find the
# intersection of the lists/sets
uniqndx = []
for key, val in datadict.items():
    uniqndx.append(list(datadict[key].index.unique()))

# inter = [i for i in uniqndx[0]]
countries = []
for i, val in enumerate(uniqndx):
    countries = (
        list(set(countries).intersection(set(uniqndx[i])))
        if i != 0
        else [i for i in uniqndx[0]]
    )


app = dash.Dash(__name__)  # , external_stylesheets=external_stylesheets)
server = app.server

country_options = [{"label": str(val), "value": str(val)} for val in countries]

# app.logger.info(country_options)
dropdown_style = {
    "margin-left": "20px",
    "margin-right": "50px",
    "color" : "#ffffff",
    "background-color" : "#000000"
    }


# layout
app.layout = html.Div(
    style={
        "font-family": "Sawasdee",
        "font-size": 22,
        "color" : "#ffffff",
        "background-color": "#000000",
        },
    children=[
        html.H1(style={"text-align": "left"}, children=""),
        # header
        html.P(
            style={"text-align": "left", "font-size": 32},
            children="Please fill-in the data:",
        ),
        # input area frame
        html.Div(
            id="input area",
            style={
                "margin": "0 auto",
                "width": "50%",
                #"background-color": "#99d6ff",
                "padding": "15px",
            },
            # child of input area frame | input fields
            children=[
                dcc.Input(
                    style={
                        "font-size": 22,
                        "margin-left": "20px",
                        "margin-right": "50px",
                        "background-color" : "#000000",
                        "color" : "#ffffff"
                    },
                    id="user_name",
                    value="",
                    type="text",
                    inputMode="latin-name",
                    placeholder="Name",
                ),
                # user age, should be int
                html.Br(),
                html.Br(),
                dcc.Input(
                    style={
                        "font-size": 22,
                        "margin-left": "20px",
                        "margin-right": "50px",
                        "background-color" : "#000000",
                        "color" : "#ffffff"
                    },
                    id="user_age",
                    type="number",
                    min=0,
                    max=120,
                    step=1,
                    inputMode="numeric",
                    value="",
                    placeholder="Age",
                ),
                # period frequency, float?
                html.Br(),
                html.Br(),
                dcc.Dropdown(
                    style= dropdown_style,
                    id="birthplace",
                    options=country_options,
                    value=None,
                    placeholder="Birthplace (Country)",
                ),
                # period frequency, float?
                html.Br(),
                dcc.Dropdown(
                    id="residence",
                    style=dropdown_style,
                    options=country_options,
                    value=None,
                    placeholder="Country of Residence",
                ),
                html.Br(),
                dcc.Dropdown(
                    style=dropdown_style,
                    id="sex",
                    options=[
                        {"label": "M", "value": "M"},
                        {"label": "F", "value": "F"},
                    ],
                    placeholder="Biological Sex",
                ),
                html.Br(),
                dcc.Dropdown(
                    style=dropdown_style,
                    id="veggie",
                    options=[
                        {"label": "Y", "value": "Y"},
                        {"label": "N", "value": "N"},
                    ],
                    placeholder="Are you a vegetarian?",
                ),
                html.Br(),
                dcc.Dropdown(
                    style=dropdown_style,
                    id="driver",
                    options=[
                        {"label": "Y", "value": "Y"},
                        {"label": "N", "value": "N"},
                    ],
                    placeholder="Do you drive a car?",
                ),
                html.Br(),
                dcc.Dropdown(
                    style=dropdown_style,
                    id="smoker",
                    options=[
                        {"label": "Y", "value": "Y"},
                        {"label": "N", "value": "N"},
                    ],
                    placeholder="Are you a Smoker?",
                ),
            ],
        ),
        html.Br(),
        html.Div(id="my-output"),
        html.Div(id="output_graph"),
        html.Div(id="output_text", style={"text-align": "center", "color": "blue"}),
    ],
)


# Narrow options on dropdown
@app.callback(Output("birthplace", "options"), Input("birthplace", "search_value"))
def update_options(search_value):
    if not search_value:
        raise PreventUpdate
    return [o for o in country_options if search_value in o["label"]]


@app.callback(Output("residence", "options"), Input("residence", "search_value"))
def update_options(search_value):
    if not search_value:
        raise PreventUpdate
    return [o for o in country_options if search_value in o["label"]]


"""
# Update output
@app.callback(
    Output('dd-output-container', 'children'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    return 'You have selected "{}"'.format(value)
"""


@app.callback(
    Output(component_id='my-output', component_property='children'),
    [
        Input(component_id="user_name", component_property="value"),
        Input(component_id="user_age", component_property="value"),
        Input(component_id="birthplace", component_property="value"),
        Input(component_id="residence", component_property="value"),
        Input(component_id="sex", component_property="value"),
        Input(component_id="veggie", component_property="value"),
        Input(component_id="driver", component_property="value"),
        Input(component_id="smoker", component_property="value"),
    ],
    )
def update_output_div(
        user_name, user_age, birthplace, residence,
        sex, veggie, driver, smoker):
    userdata_ = UserData(
        user_name, user_age, birthplace, residence,
        sex, veggie, driver, smoker)

    return "Output: {}".format(userdata_.get_data())


"""
@app.callback(
    [
        Output(component_id="output_graph", component_property="children"),
        Output(component_id="output_text", component_property="children"),
    ],
    [
        Input(component_id="user_name", component_property="value"),
        Input(component_id="user_age", component_property="value"),
        Input(component_id="birthplace", component_property="value"),
        Input(component_id="residence", component_property="value"),
        Input(component_id="sex", component_property="value"),
    ],
)
def generate_graph(user_name, user_age, birthplace, residence, age):
    userdata_ = UserData(user_name, user_age, birthplace, residence, age)

    return None

    object_=Payback_Tracker(name=obj,initial_cost=float(cost),usage_benefit=float(benefit),frequency=float(frequency_),period=period_)
    object_.generate_balance_history()
    data=object_.get_balance_data()

    if object_.period !="day":
        fig = px.bar(data, x=data.columns[0], y='Balance History',color="Balance History",color_continuous_scale="pubu",title="{} balance history for your {}".format(object_.period.capitalize()+"ly",object_.name))
    else:
        fig = px.bar(data, x=data.columns[0], y='Balance History',color="Balance History",color_continuous_scale="pubu",title="Daily balance history for your {}".format(object_.name))

    return dcc.Graph(
        figure=fig

    ),
    html.H2(object_.get_result()
    )"""


if __name__ == "__main__":
    app.run_server(debug=True)
