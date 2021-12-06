import dash

import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.DARKLY]

app = dash.Dash(__name__
                , suppress_callback_exceptions=True
                ,external_stylesheets=external_stylesheets
                ,title="Multimedia Lab - Data Exploration App")
                
server = app.server
