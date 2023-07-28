import dash
import dash_bootstrap_components as dbc
import dash_html_components as html

from app.dashboard import base
from app.dashboard.nav import navbar

dash_app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    requests_pathname_prefix=None if __name__ == "__main__" else '/dash/',
)

dash_app.layout = html.Div([
    navbar, base.layout, html.Div(id="output-clientside"),
], className='app')

base.callbacks(dash_app)

# setup_auth(dash_app)
dash_server = dash_app.server

if __name__ == "__main__":
    dash_app.run_server(debug=True, use_reloader=True, port=8888)
