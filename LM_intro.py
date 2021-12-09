#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 11:12:43 2021

@author: cgwork
"""

# Dataframes, DBs


# Dashboards modules
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
            src=os.path.join(
                "/", "assets", "mockup_video_final.mp4"
            ),
            autoPlay=True,
            width=1200,
        ),
        html.Div(
            dbc.Button(
                style={
                    "font-size": 22,
                    "margin-left": "20px",
                    "margin-right": "80px",
                    "background-color": "#000",
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
    ]
)


@app.callback(
    Output(component_id="video-intro-output", component_property="children"),
    [
        Input(component_id="submit-button-state", component_property="n_clicks"),
    ],
)
def update_output_div(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    return "Ok"


# =============================================================================
#
# if __name__ == "__main__":
#     # app.run_server(debug=True)
#     app.run_server(
#         host="127.0.0.1",
#         port="8050",
#         proxy=None,
#         debug=True,
#         # dev_tools_props_check=None,
#         # dev_tools_serve_dev_bundles=None,
#         # dev_tools_hot_reload=None,
#         # dev_tools_hot_reload_interval=None,
#         # dev_tools_hot_reload_watch_interval=None,
#         # dev_tools_hot_reload_max_retry=None,
#         # dev_tools_silence_routes_logging=None,
#         # dev_tools_prune_errors=None,
#         # **flask_run_options
#     )
#
# =============================================================================
