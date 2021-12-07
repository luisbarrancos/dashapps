import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
import LM_intro, LM_user_data, LM_line_life_expectancy, LM_line_datafields, LM_scatter_graph2, LM_geomap_plot


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page0':
        return LM_user_data.layout
    elif pathname == '/page1':
        return LM_line_life_expectancy.layout
    elif pathname == '/page2':
        return LM_line_datafields.layout
    elif pathname == '/page3':
        return LM_scatter_graph2.layout
    elif pathname == '/page4':
        return LM_geomap_plot.layout
    else:
        return LM_intro.layout
        # page 1

if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server(
        host="127.0.0.1",
        port="8050",
        proxy=None,
        debug=True,
        # dev_tools_props_check=None,
        # dev_tools_serve_dev_bundles=None,
        # dev_tools_hot_reload=None,
        # dev_tools_hot_reload_interval=None,
        # dev_tools_hot_reload_watch_interval=None,
        # dev_tools_hot_reload_max_retry=None,
        # dev_tools_silence_routes_logging=None,
        # dev_tools_prune_errors=None,
        # **flask_run_options
    )
