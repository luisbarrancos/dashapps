from dash import dcc, html
from dash.dependencies import Input, Output

import LM_geomap_plot
import LM_intro
import LM_line_datafields
import LM_line_life_expectancy
import LM_scatter_graph2
import LM_submit_social
import LM_user_algo
import LM_user_data
from app import app

server = app.server

app.layout = html.Div(
    children=[
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
    ]
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/page0":
        return LM_user_data.layout

    if pathname == "/page1":
        return LM_line_life_expectancy.layout

    if pathname == "/page2":
        return LM_line_datafields.layout

    if pathname == "/page3":
        return LM_scatter_graph2.layout

    if pathname == "/page4":
        return LM_geomap_plot.layout

    if pathname == "/page5":
        return LM_user_algo.layout

    if pathname == "/page6":
        return LM_submit_social.layout

    return LM_intro.layout
    # page 1


if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server(
        host="127.0.0.1",
        port="8050",
        #proxy=None,
        debug=False,
        #dev_tools_props_check=None,
        #dev_tools_serve_dev_bundles=None,
        #dev_tools_hot_reload=None,
        #dev_tools_hot_reload_interval=None,
        #dev_tools_hot_reload_watch_interval=None,
        #dev_tools_hot_reload_max_retry=None,
        #dev_tools_silence_routes_logging=None,
        #dev_tools_prune_errors=None,
        #**flask_run_options
    )
