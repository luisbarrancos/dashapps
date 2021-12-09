#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 11:12:43 2021

@author: cgwork
"""

import os

import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from app import app

# layout
layout = html.Div(
    children=[
        html.Video(
            controls=False,
            id="movie_player",
            src=os.path.join("/", "assets", "mockup_video_final.mp4"),
            autoPlay=True,
            width=1200,
        ),
        html.Div(
            dbc.Button(
                style={
                    "fontSize": 22,
                    "marginLeft": "20px",
                    "marginRight": "80px",
                    "backgroundColor": "#000",
                    "color": "#ffffff",
                },
                id="submit-button-state",
                n_clicks=0,
                children="Submit",
                color="Primary",
                className="me-1",
                href="/page0",
            ),
            className="d-grip gap-2 d-md-flex justify-content-md-end",
        ),
        html.Div(id="video-intro-output"),
    ],
    style={
        "textAlign": "center",
        "backgroundColor": "#000",
    },
)
