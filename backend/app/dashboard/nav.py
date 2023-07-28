import dash
import dash_auth
import dash_bootstrap_components as dbc
import dash_html_components as html

navbar = dbc.NavbarSimple(
    children=[
    ],
    brand="Graph Viewer",
    brand_href="#",
    color="primary",
    dark=True,
    fluid=True,
    style=dict(height='5vh')
)